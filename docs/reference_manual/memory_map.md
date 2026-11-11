# revENG312 – Memory Map

This document describes the memory that revENG312 exposes over the serial interface, and compares it with the original firmware. It belongs to the [revENG312 Reference Manual](README.md).

The descriptions of the original firmware come from community reverse-engineering, mainly the ET312 documentation from stpihkal. revENG312 may name a location differently. In some places, revENG312 also stores something else at a location that the original uses for a value revENG312 doesn't need.

The tables in section 3 use these columns:

- **revENG312:** what revENG312 stores at the location.
- **Default:** the value after start-up. At start-up, revENG312 clears `0x4060`–`0x4237` to `0x00` and then loads the defaults. When the channel regions are reset, it clears the channel A region (`0x4080`–`0x40BF`), sets its defaults and copies the region to channel B.
- **Original:** "same" if the location has the same function on the original. Otherwise the original's description, and its default where it differs.

Locations marked **(internal)** are used internally by revENG312. The protocol allows writing them, but doing so can disturb the firmware.

---

## 1. Virtual address space

The serial protocol reads and writes 16-bit virtual addresses. These are mapped to three windows:

| Window | Virtual addresses | Contents |
|---|---|---|
| Flash | `0x0000`–`0x00FF` | Identification bytes only (see section 1.1) |
| RAM | `0x4000`–`0x43FF` | RAM; tools can access `0x4060`–`0x4237` (see section 1.2) |
| EEPROM | `0x8000`–`0x81FF` | The complete 512-byte EEPROM (see section 1.3) |

### 1.1 Flash window

On the original, the flash window shows 256 bytes of the firmware's flash: part of the string table, a data segment and the identification bytes. revENG312 only returns the identification bytes:

| Address | revENG312 | Original |
|---|---|---|
| `0x00FC` | Box model: `0x0C` | Box model: `0x0C` |
| `0x00FD`–`0x00FF` | Firmware version: major, minor, patch. revENG312 reports its own version, currently `0x01 0x00 0x01` for v1.0.01. | Firmware version, e.g. `0x01 0x06 0x00` for v1.6 |
| Everything else | Returns `0x18` | Flash contents |

No community tool is known to have problems with the revENG312 version number.

### 1.2 RAM window

On the original, the first 96 bytes of the RAM window (`0x4000`–`0x405F`) are the CPU and I/O registers of the microcontroller. revENG312 does not give direct access to hardware registers. Everything a tool needs is in the range `0x4060`–`0x4237`.

| Address | Contents | Read | Write |
|---|---|---|---|
| `0x4000`–`0x4003` | CPU registers r0–r3 on the original | — | — |
| `0x4004`–`0x400E` | Channel values sent by a linked master (CPU registers r4–r14 on the original) | — | Only when the box is a linked slave (see [Reference Manual, section 7.7](README.md#77-real-time-streaming)) |
| `0x400F` | Control flags (see section 4.4; CPU register r15 on the original) | Yes | Single-byte writes only |
| `0x4010`–`0x405F` | CPU registers r16–r31 and I/O registers on the original | — | — |
| `0x4060`–`0x4237` | RAM documented in section 3 | Yes | Yes |
| `0x4238`–`0x43FF` | Internal variables and stack | — | — |

Where the original keeps a meaningful value in a CPU register (for example the button actions in r19–r22, or the flags in r16 and r17), revENG312 uses internal variables instead. Except for the flags at `0x400F`, these are not exposed.

The range `0x4060`–`0x4237` also contains locations the firmware only uses internally, such as buffers and driver state. They are listed in section 3 and marked as **internal**. The protocol allows writing them, but doing so can disturb the firmware.

### 1.3 EEPROM window

The complete EEPROM can be read and written over the serial interface, as on the original.

The magic byte at `0x8001` is `0x22` on revENG312, while the original uses `0x55`. This tells the two firmwares apart. It also makes sure that the settings are reset to their defaults when you switch from one firmware to the other.

### 1.4 Invalid accesses

| Access | revENG312 | Original |
|---|---|---|
| Read outside the accessible ranges | Returns `0xEE` | Addresses beyond the end of a window repeat the window's contents |
| Write outside the accessible ranges | Ignored, no ACK | Not documented |
| Write that would run past the end of an accessible range | Ignored as a whole, no ACK | Not documented |

A rejected write is not answered at all, so a tool sees a timeout instead of an error code. Answering with an error code would break some existing community tools.

---

## 2. Overview

### 2.1 RAM

| Address | Region | Section |
|---|---|---|
| `0x4060`–`0x4067` | ADC readings: current sense, Multi Adjust, supply voltages, level pots, audio | 3.1 |
| `0x4068`–`0x407F` | System and user interface: buttons, timers, calibration, LCD state, commands, random numbers, menu, detune | 3.2 |
| `0x4080`–`0x408F` | Channel A header: phase shift, output flags, module control, Multi Adjust range, module timers | 3.3 |
| `0x4090`–`0x40BF` | Channel A block: gate, next module, ramp, intensity, frequency, width | 3.4 |
| `0x40C0`–`0x417F` | User module scratchpad | 3.5 |
| `0x4180`–`0x418F` | Channel B header: LCD and command parameters, Random 1, Multi Adjust range for channel B | 3.3 |
| `0x4190`–`0x41BF` | Channel B block: same layout as channel A | 3.4 |
| `0x41C0`–`0x41F2` | Multi Adjust averaging, scratchpad pointers, buffer pointers | 3.6 |
| `0x41F3`–`0x41FF` | Settings: top mode, power level, split mode, favourite, advanced parameters | 3.7 |
| `0x4200`–`0x4237` | Mixed: parameter editing, battery, Multi Adjust calibration and value, internal driver and serial state | 3.8 |

### 2.2 EEPROM

| Address | Region |
|---|---|
| `0x8000`–`0x8007` | Identification: magic byte, box serial, ErosLink signature |
| `0x8008`–`0x8014` | Settings: top mode, power level, split mode, favourite, advanced parameters |
| `0x8015` | Baud rate setting (new in revENG312) |
| `0x8016` | Multi Adjust calibration (new in revENG312) |
| `0x8017` | Unused |
| `0x8018`–`0x801F` | Start vectors of user routines 1–8 |
| `0x8020`–`0x803F` | Module pointers for modules `0x80`–`0x9F` |
| `0x8040`–`0x80FF` | User modules |
| `0x8100`–`0x811F` | Module pointers for modules `0xA0`–`0xBF` |
| `0x8120`–`0x81FF` | User modules |

---

## 3. RAM in detail

### 3.1 ADC readings (`0x4060`–`0x4067`)

| Address | revENG312 | Default | Original |
|---|---|---|---|
| `0x4060` | Output current sense (ADC0) | `0x00` | same |
| `0x4061` | Multi Adjust knob reading (ADC1) | `0x00` | same |
| `0x4062` | Power supply voltage (ADC2) | `0x00` | same |
| `0x4063` | Battery voltage (ADC3) | `0x00` | same |
| `0x4064` | Level pot A (ADC4) | `0x00` | same |
| `0x4065` | Level pot B (ADC5) | `0x00` | same |
| `0x4066` | Audio input, right (ADC6) | `0x00` | Audio input level A (half wave) |
| `0x4067` | Audio input, left (ADC7) | `0x00` | Audio input level B (half wave) |

**Audio inputs.** The left audio input is read by ADC7 and the right one by ADC6, on both firmwares. Channel B always uses the right input. Channel A uses the right input when mono mode is set (`0x4083` bit 6), otherwise the left input.

### 3.2 System and user interface (`0x4068`–`0x407F`)

| Address | revENG312 | Default | Original |
|---|---|---|---|
| `0x4068` | Button trigger (see note) | `0x00` | Current pushed buttons |
| `0x4069` | Raw button state, updated at each poll | `0x00` | Last pushed buttons |
| `0x406A` | Master timer MSB, ticks every 512 ms | `0x00` | Ticks every 524.288 ms |
| `0x406B` | Channel A calibration (DAC offset) | `0x00` | same |
| `0x406C` | Channel B calibration (DAC offset) | `0x00` | same |
| `0x406D` | LCD state (see note) **(internal)** | `0x00` | Menu state |
| `0x406E` | Link timeout counter **(internal)** | `0x00` | Unused |
| `0x406F` | Multi Adjust value of channel B in split mode **(internal)** | `0x00` | Unused |
| `0x4070` | Execute command 1 (see [Execute Commands](execute_commands.md)) | `0xFF` | same |
| `0x4071` | Execute command 2 | `0xFF` | same |
| `0x4072` | Last random number picked | `0x00` | same |
| `0x4073` | Master timer LSB, ticks every 2 ms | `0x00` | Ticks every 2.048 ms |
| `0x4074` | Random 1: current mode | `0x00` | same |
| `0x4075` | Random 1: time of the next mode change | `0x00` | same |
| `0x4076` | Index of the advanced parameter being edited **(internal)** | `0x00` | Unused |
| `0x4077` | Previous menu **(internal)** | `0xFF` | Unused |
| `0x4078` | Current menu item (displayed, not yet selected) | `0x00` | same |
| `0x4079` | Lowest selectable menu item | `0x00` | same |
| `0x407A` | Highest selectable menu item | `0x00` | same |
| `0x407B` | Current routine (see [Execute Commands, section 6.2](execute_commands.md#62-menu-item-values)) | `0x00` | same |
| `0x407C`–`0x407D` | Frequency detune, channel A (16 bit, LSB first) | `0x0000` | Oscillator ch A (updated but unused) |
| `0x407E`–`0x407F` | Frequency detune, channel B (16 bit, LSB first) | `0x0000` | Oscillator ch B (updated but unused) |

**Button trigger.** `0x4068` is set when a button press is detected (also on auto-repeat), and cleared once the button's action has been executed. Writing a button value simulates a press (see [Execute Commands, section 2](execute_commands.md#2-simulating-button-presses)).

**LCD state.** Bits 0–3 of `0x406D` hold the display state: `0` failure, `1` start-up, `2` routine running, `3` menu, `4` no update. Bits 4–7 are update flags. The original uses `0x01` for the start-up screen or a menu, and `0x02` while a routine is running. A tool that polls this byte should only look at bits 0–3.

**Timer rates.** revENG312's master timer ticks every 2 ms, while the original's ticks every 2.048 ms. All timers derived from it, including the module timers at `0x4088`–`0x408B`, therefore run about 2.4 % faster than on the original. Timed routine effects are correspondingly slightly faster.

### 3.3 Channel headers (`0x4080`–`0x408F`, `0x4180`–`0x418F`)

Each channel region starts with a 16-byte header. Unlike the channel blocks that follow (section 3.4), the two headers are used differently.

When the channel regions are reset, revENG312 sets up the complete 64-byte region of channel A and then copies it to channel B. The defaults of the channel B header are therefore the same as those of the channel A header, even where channel B doesn't use the location.

Modules may write both headers, but because some locations have other functions, this can have unexpected effects in rare combinations. Writing the channel blocks (section 3.4) is always safe.

#### Channel A header

| Address | revENG312 | Default | Original |
|---|---|---|---|
| `0x4080`–`0x4081` | Phase shift in phaselock mode, in µs (16 bit, LSB first; see [Reference Manual, section 7.4](README.md#74-phaselock-mode)) | `0x0000` | Unused |
| `0x4082` | Not used | `0x00` | Retry counter when communicating with slave, default `0x02` |
| `0x4083` | Output control flags (see section 4) | `0x00` | Output control flags; some bits differ (see section 4) |
| `0x4084` | Module to load when a condition is met | `0x00` | same |
| `0x4085` | Channel selection for module instructions (see note) | `0x03` | same |
| `0x4086` | Multi Adjust range, minimum | `0x0F` | same |
| `0x4087` | Multi Adjust range, maximum | `0xFF` | same |
| `0x4088` | Module timer LSB, ticks every 4 ms | `0x00` | Ticks every 4.096 ms |
| `0x4089` | Module timer middle byte, ticks every 1.024 s | `0x00` | Ticks every 1.048576 s |
| `0x408A` | Module timer MSB, ticks every 262.144 s | `0x00` | Ticks every 268.435456 s |
| `0x408B` | Module timer ÷ 8, ticks every 32 ms | `0x00` | Ticks every 32.768 ms |
| `0x408C` | Module accumulator, channel A | `0x00` | Module temporary byte store |
| `0x408D` | Random number, minimum | `0x00` | same |
| `0x408E` | Random number, maximum | `0x08` | same |
| `0x408F` | Module to load on an audio trigger | `0x00` | same |

**Channel selection.** `0x4085` accepts `0x01` (channel A), `0x02` (channel B) and `0x03` (both). With `0x00`, module instructions are ignored. It is reset to `0x03` when a module ends and after a conditional load has finished. Unlike all other addresses, a module instruction writing `0x4085` is never redirected to channel B. See [Reference Manual, section 8.2](README.md#82-channel-selection) and the [Module Instruction Reference, section 3](module_opcode_reference.md#3-channel-selection).

**Module registers.** `0x4084` is the only location for the module to load on a condition; `0x4184` has no such function. The random number limits at `0x408D`–`0x408E` apply to both channels. See the [Module Instruction Reference, section 2.3](module_opcode_reference.md#23-special-addresses).

#### Channel B header

| Address | revENG312 | Default | Original |
|---|---|---|---|
| `0x4180` | LCD character for command `0x13` (see [Execute Commands, section 5.1](execute_commands.md#51-0x13--write-a-character-to-the-lcd)) | `0x00` | same |
| `0x4181` | LCD position for command `0x13` | `0x00` | same |
| `0x4182` | Not used in release builds | `0x00` | Parameter r26 for box commands |
| `0x4183` | Not used | `0x00` | Parameter r27 for box commands |
| `0x4184` | Random 1: random Multi Adjust value | `0x00` | Set to random number during Random 1 program |
| `0x4185` | Not used | `0x03` | Unused; set to `0x0F` while the ramp is displayed |
| `0x4186` | Multi Adjust range of channel B in split mode, minimum **(internal)** | `0x0F` | Unused |
| `0x4187` | Multi Adjust range of channel B in split mode, maximum **(internal)** | `0xFF` | Unused |
| `0x4188`–`0x418B` | Not used | `0x00` | same |
| `0x418C` | Module accumulator, channel B | `0x00` | Unused |
| `0x418D` | Not used | `0x00` | same |
| `0x418E` | Not used | `0x08` | same |
| `0x418F` | Not used | `0x00` | same |

### 3.4 Channel blocks (`0x4090`–`0x40BF`, `0x4190`–`0x41BF`)

The channel blocks of channel A and channel B have the same 48-byte layout. Commands `0x19`–`0x1B` (swap and copy channels) act on exactly these blocks.

| Address A / B | revENG312 | Default | Original |
|---|---|---|---|
| `0x4090` / `0x4190` | Gate value (see section 4) | `0x06` | same |
| `0x4091` / `0x4191` | Not used | `0x00` | A: module wants to change channel A gates (not used by revENG312). B: unused. |
| `0x4092` / `0x4192` | Not used | `0x00` | A: module wants to change channel B gates (not used by revENG312). B: unused. |
| `0x4093` / `0x4193` | Not used | `0x00` | same |
| `0x4094` / `0x4194` | Next module timer | `0x00` | same |
| `0x4095` / `0x4195` | Next module timer compare value | `0xFF` | Next module timer max |
| `0x4096` / `0x4196` | Next module timer select | `0x00` | Next module flag |
| `0x4097` / `0x4197` | Next module number | `0x00` | same |
| `0x4098` / `0x4198` | Gate on time | `0x3E` | same |
| `0x4099` / `0x4199` | Gate off time | `0x3E` | same |
| `0x409A` / `0x419A` | Gate select | `0x00` | same |
| `0x409B` / `0x419B` | Gate timer | `0x00` | Number of gate transitions done |
| `0x409C`–`0x40A4` / `0x419C`–`0x41A4` | Ramp parameter group | see below | same |
| `0x40A5`–`0x40AD` / `0x41A5`–`0x41AD` | Intensity parameter group | see below | same |
| `0x40AE`–`0x40B6` / `0x41AE`–`0x41B6` | Frequency parameter group | see below | same |
| `0x40B7`–`0x40BF` / `0x41B7`–`0x41BF` | Width parameter group | see below | same |

#### Parameter groups

Ramp, intensity, frequency and width each use a group of nine bytes with the same layout. The encodings of select, rate and the actions at min and max are the same as on the original and are described in the community documentation. All defaults are the same as on the original.

| Byte | Parameter | Ramp | Intensity | Frequency | Width |
|---|---|---|---|---|---|
| 1 | Value | `0x9C` | `0xFF` | `0x16` | `0x82` |
| 2 | Min | `0x9C` | `0xCD` | `0x09` | `0x32` |
| 3 | Max | `0xFF` | `0xFF` | `0x64` | `0xC8` |
| 4 | Rate | `0x07` | `0x01` | `0x01` | `0x01` |
| 5 | Step | `0x01` | `0x01` | `0x01` | `0x01` |
| 6 | Action at min | `0xFC` | `0xFF` | `0xFF` | `0xFF` |
| 7 | Action at max | `0xFC` | `0xFF` | `0xFF` | `0xFF` |
| 8 | Select | `0x01` | `0x00` | `0x08` | `0x04` |
| 9 | Timer | `0x00` | `0x00` | `0x00` | `0x00` |

The frequency and width values are subject to the hard limits described in the [Reference Manual, section 3.4](README.md#34-valid-parameter-ranges).

### 3.5 User module scratchpad (`0x40C0`–`0x417F`)

The scratchpad holds module data in RAM, for example to test a user module before storing it in EEPROM. It is 192 bytes long. The original is documented with a scratchpad of `0x40C0`–`0x4177` (184 bytes), but nothing is known to use the 8 bytes up to `0x417F`, so they are most likely usable on the original as well.

- Modules in the scratchpad have the numbers `0xC0`–`0xDF`.
- The start of each module is given by its offset at `0x41D0`–`0x41EF` (one byte per module: `0x41D0` for module `0xC0`, `0x41D1` for `0xC1`, and so on). The offset is relative to `0x40C0`.
- A module may not start or continue beyond `0x417F`. A module whose data would run past that end stops the firmware with error code 55 (see [Reference Manual, section 4.3](README.md#43-error-codes)).

How modules are encoded and stored is described in the [Module Instruction Reference](module_opcode_reference.md#8-storing-modules).

### 3.6 Averaging, pointers and buffer heads (`0x41C0`–`0x41F2`)

| Address | revENG312 | Default | Original |
|---|---|---|---|
| `0x41C0`–`0x41CF` | Last 16 Multi Adjust readings, for averaging **(internal)** | `0x00` | same |
| `0x41D0`–`0x41EF` | Start offsets of scratchpad modules `0xC0`–`0xDF` (see section 3.5) | `0x00` | User module scratchpad pointers |
| `0x41F0` | Index for Multi Adjust averaging **(internal)** | `0x00` | Pointer for Multi Adjust averaging, default `0xC0` |
| `0x41F1` | Serial transmit buffer head **(internal)** | `0x00` | Pointer for serial output buffer, default `0x2C` |
| `0x41F2` | Serial receive buffer head **(internal)** | `0x00` | Pointer for serial input buffer, default `0x20` |

### 3.7 Settings (`0x41F3`–`0x41FF`)

These settings are loaded from EEPROM (`0x8008`–`0x8014`) at start-up. Writing them in RAM changes them only until the next restart. To keep a change, write the EEPROM location as well (see section 5).

| Address | revENG312 | Default | Original |
|---|---|---|---|
| `0x41F3` | Top mode: highest selectable routine | `0x87` | same |
| `0x41F4` | Power level (see note) | `0x02` | same (community documentation lists other values, see note) |
| `0x41F5` | Split mode, channel A | `0x77` | same |
| `0x41F6` | Split mode, channel B | `0x76` | same |
| `0x41F7` | Favourite routine | `0x76` | same |
| `0x41F8` | Advanced parameter: ramp level | `0xE1` | same |
| `0x41F9` | Advanced parameter: ramp time | `0x14` | same |
| `0x41FA` | Advanced parameter: depth | `0xD7` | same |
| `0x41FB` | Advanced parameter: tempo | `0x01` | same |
| `0x41FC` | Advanced parameter: frequency | `0x19` | same |
| `0x41FD` | Advanced parameter: effect | `0x05` | same |
| `0x41FE` | Advanced parameter: width | `0x82` | same |
| `0x41FF` | Advanced parameter: pace | `0x05` | same |

**Power level.** revENG312 uses `0x01` for low, `0x02` for normal and `0x03` for high. `0x00` is an even lower level that cannot be selected in the menu; it is kept to match the original. The original uses the same values. The community documentation, which lists `0x00` low, `0x01` normal, `0x02` high and `0x03` unknown, is wrong here.

The defaults are the factory settings. The valid ranges of the advanced parameters are listed in the [Reference Manual, section 3.4](README.md#34-valid-parameter-ranges). The routine numbers are listed in [Execute Commands, section 6.2](execute_commands.md#62-menu-item-values).

### 3.8 Editing, status and internal state (`0x4200`–`0x4237`)

| Address | revENG312 | Default | Original |
|---|---|---|---|
| `0x4200` | Previous value of the advanced parameter being edited, restored if the edit is cancelled **(internal)** | `0x00` | Value of advanced parameter being edited |
| `0x4201` | Minimum of the advanced parameter being edited **(internal)** | `0x00` | same |
| `0x4202` | Maximum of the advanced parameter being edited **(internal)** | `0x00` | same |
| `0x4203` | Battery level in percent (0–99) | `0x00` | same |
| `0x4204` | Frequency shown while editing the advanced frequency parameter **(internal)** | `0x00` | Calculated PWM frequency |
| `0x4205` | Ramp-scaled output level, channel A **(internal)** | `0x00` | Channel A DAC level |
| `0x4206` | Ramp-scaled output level, channel B **(internal)** | `0x00` | Channel B DAC level |
| `0x4207` | Not used in release builds (debug: shows the current module number) | `0x00` | Debug mode: displays current module number if not `0` |
| `0x4208` | Multi Adjust calibration: raw reading at the dial's maximum (see note) | `0x55` | Used for DAC SPI transfer |
| `0x4209`–`0x420C` | Output driver state, channel A **(internal)** | — | Channel A PWM mark and space |
| `0x420D` | Current Multi Adjust value | `0x00` | same |
| `0x420E`–`0x4211` | Output driver state, channel B **(internal)** | — | Channel B PWM mark and space |
| `0x4212` | Expected length of the serial message being received **(internal)** | `0x00` | same |
| `0x4213` | Serial cipher key **(internal)** | `0x00` | same |
| `0x4214` | Baud rate setting: `0` 19'200, `1` 38'400, `2` 250'000 | `0x00` | Serial buffer incrementer |
| `0x4215` | Power status bits (see section 4) | `0x00` | same |
| `0x4216` | Serial transmit buffer tail **(internal)** | `0x00` | Unused |
| `0x4217` | Serial receive buffer tail **(internal)** | `0x00` | Unused |
| `0x4218`–`0x421F` | Module instruction being executed **(internal)** | `0x00` | same |
| `0x4220`–`0x422B` | Serial receive buffer, 12 bytes **(internal)** | `0x00` | same |
| `0x422C`–`0x4237` | Serial transmit buffer, 12 bytes **(internal)** | `0x00` | same |

**Baud rate.** `0x4214` is loaded from EEPROM (`0x8015`) at start-up. The serial interface only applies it when it is initialised: at start-up, after command `0x2B` and when a link is recovered. Writing `0x4214` alone therefore does not change the active baud rate. To change it, use the menu or command `0x2B` (see [Execute Commands, section 6](execute_commands.md#6-menu-and-state-dependent-commands)).

In split mode, `0x4214` also decides whether Rhythm is passed on to a linked slave: this only happens at 250'000 baud.

**Multi Adjust calibration.** `0x4208` is loaded from EEPROM (`0x8016`) at start-up. It is the raw reading (`0x4061`) at the dial's maximum and is used as the full-scale value when the Multi Adjust reading is scaled. Because of the dial's circuit, this reading is only about a third of the ADC range: nominally `0x55`, which is also the default, and typically not much above `0x5F`. It is set from the menu or with command `0x2C`, which writes both `0x4208` and `0x8016` (see [Reference Manual, section 2.4](README.md#24-calibrating-multi-adjust)). Writing `0x4208` alone changes the calibration only until the next restart.

---

## 4. Bit fields

### 4.1 Output control flags (`0x4083`)

| Bit | Mask | revENG312 | Original |
|---|---|---|---|
| 0 | `0x01` | Phase mode: sweep. The phase shift sweeps back and forth; speed and turning point follow the Multi Adjust dial. | Phase control |
| 1 | `0x02` | An audio trigger loads the module given at `0x408F` | Mute (see note) |
| 2 | `0x04` | Master switch for the phase modes | Phase control 2 |
| 3 | `0x08` | Phase mode: channel B is a clone of the inverted channel A | Phase control 3 |
| 4 | `0x10` | Phase mode: phaselock (see [Reference Manual, section 7.4](README.md#74-phaselock-mode)) | Unused |
| 5 | `0x20` | Disable the front panel buttons | same |
| 6 | `0x40` | Mono mode: channel A also uses the right audio input (see section 3.1) | same |
| 7 | `0x80` | Not used | Unused |

**Phase modes.** Bit 2 switches the phase modes on. One additional bit selects the mode: bit 0 (sweep), bit 3 (inverted clone) or bit 4 (phaselock). For example, `0x14` enables phaselock and `0x05` enables the sweep.

**Bit 1.** The community documentation describes bit 1 as "mute". On both firmwares, it actually enables loading a module on an audio trigger. If no module number is set at `0x408F`, the trigger loads module `0`, which mutes the outputs. This is most likely where the description comes from.

### 4.2 Gate value (`0x4090`, `0x4190`)

The gate value selects the waveform and controls the output of a channel. The community documentation does not describe its bits.

| Bit | Mask | revENG312 |
|---|---|---|
| 0 | `0x01` | Gate on: output active |
| 1–2 | `0x06` | Waveform: `0` off, `1` negative monophasic, `2` positive monophasic, `3` biphasic |
| 3 | `0x08` | Alternating pulses. Overrides the waveform selected in bits 1–2. |
| 4 | `0x10` | Invert polarity |
| 5 | `0x20` | Audio controls the channel's frequency |
| 6 | `0x40` | Audio controls the channel's intensity |
| 7 | `0x80` | Channel A only: switch off the channel B oscillator and clone channel A's output to channel B. Not used on channel B. |

The default `0x06` selects the biphasic waveform with the gate off.

### 4.3 Power status (`0x4215`)

| Bit | Mask | revENG312 | Original |
|---|---|---|---|
| 0 | `0x01` | Battery present | same |
| 1 | `0x02` | Power supply connected | same |
| 2–7 | | Not used | same |

### 4.4 Control flags (`0x400F`)

| Bit | Mask | revENG312 | Original |
|---|---|---|---|
| 0 | `0x01` | Stop sampling the level pots, and stop averaging and scaling the Multi Adjust value | same |
| 1 | `0x02` | Load the module given at `0x4084` | same |
| 2 | `0x04` | The current routine can be shared with a linked slave | same |
| 3 | `0x08` | Stop sampling the Multi Adjust dial | same |
| 4–7 | | Not used | same |

With bits 0 and 3 both set, revENG312 keeps scaling the Multi Adjust value, while the original doesn't. How a control app should use these flags is described in the [Reference Manual, section 7.6](README.md#76-remote-control-of-levels-and-multi-adjust).

### 4.5 Encodings shared with the original

The following encodings are identical to the original and are described in the community documentation:

- the select byte of the parameter groups, including the rate and min/max selection bits
- the actions at min and max
- the gate select byte (`0x409A`, `0x419A`)

---

## 5. EEPROM

### 5.1 EEPROM layout

| Address | revENG312 | Default | Original |
|---|---|---|---|
| `0x8000` | Not used | `0x00` | same |
| `0x8001` | Magic byte (see section 5.2) | `0x22` | Magic byte `0x55` |
| `0x8002`–`0x8003` | Box serial number, a random value written at initialisation | random | same |
| `0x8004`–`0x8005` | Not used | `0x00` | same |
| `0x8006`–`0x8007` | ErosLink signature | `0x01` | same |
| `0x8008` | Top mode: highest selectable routine | `0x87` | same |
| `0x8009` | Power level | `0x02` | same |
| `0x800A` | Split mode, channel A | `0x77` | same |
| `0x800B` | Split mode, channel B | `0x76` | same |
| `0x800C` | Favourite routine | `0x76` | same |
| `0x800D` | Advanced parameter: ramp level | `0xE1` | same |
| `0x800E` | Advanced parameter: ramp time | `0x14` | same |
| `0x800F` | Advanced parameter: depth | `0xD7` | same |
| `0x8010` | Advanced parameter: tempo | `0x01` | same |
| `0x8011` | Advanced parameter: frequency | `0x19` | same |
| `0x8012` | Advanced parameter: effect | `0x05` | same |
| `0x8013` | Advanced parameter: width | `0x82` | same |
| `0x8014` | Advanced parameter: pace | `0x05` | same |
| `0x8015` | Baud rate setting: `0` 19'200, `1` 38'400, `2` 250'000 | `0x00` | Not used |
| `0x8016` | Multi Adjust calibration: raw reading at the dial's maximum (see section 3.8) | `0x55` | Not used |
| `0x8017` | Not used | `0x00` | same |
| `0x8018`–`0x801F` | Start vectors of user routines 1–8: the number of each routine's first module | `0x00` | Start vectors of user routines 1–8; 7 and 8 not implemented |
| `0x8020`–`0x803F` | Start offsets of user modules `0x80`–`0x9F`, relative to `0x8040` | — | User routine module pointers `0x80`–`0x9F` |
| `0x8040`–`0x80FF` | User module data, bank A | — | same |
| `0x8100`–`0x811F` | Start offsets of user modules `0xA0`–`0xBF`, relative to `0x8120` | — | User routine module pointers `0xA0`–`0xBF` |
| `0x8120`–`0x81FF` | User module data, bank B | — | same |

At start-up, the settings at `0x8008`–`0x8014` are copied to RAM (section 3.7), the baud rate at `0x8015` to `0x4214` and the Multi Adjust calibration at `0x8016` to `0x4208` (section 3.8). A user module may not start or continue beyond the end of its bank (`0x80FF` or `0x81FF`); otherwise the firmware stops with error code 55.

### 5.2 Initialisation

At start-up, revENG312 checks the magic byte at `0x8001`. If it is `0x22`, the EEPROM is used as it is. Otherwise, it is prepared in one of two ways.

**Upgrade from the original firmware (magic byte `0x55`).** The EEPROM layout of the original is compatible, so revENG312 keeps its content and only adds what the original doesn't have:

1. The baud rate at `0x8015` is set to `0x00` (19'200).
2. The Multi Adjust calibration at `0x8016` is set to its default value `0x55`.
3. The start vectors of user routines 7 and 8 (`0x801E`–`0x801F`) are set to `0x00`, as the original doesn't use them.
4. The magic byte is set to `0x22`.

Everything else is kept: the box serial number, the settings and advanced parameters at `0x8008`–`0x8014`, the start vectors of user routines 1–6 and all user module data. User routines stored by the original remain available. Settings outside their valid range are clamped when they are used.

**Full initialisation (any other magic byte).** This happens, for example, on a blank or corrupted EEPROM:

1. `0x8000`–`0x801F` is cleared. This resets all settings and the start vectors of the user routines.
2. A new random box serial number is written to `0x8002`–`0x8003`, as the original does.
3. The ErosLink signature at `0x8006`–`0x8007` is set to `0x01`.
4. The factory settings are written, including the default Multi Adjust calibration (`0x55`).
5. The magic byte is set to `0x22`.

The user module data from `0x8020` onwards is not touched, but because the start vectors are cleared, user routines have to be set up again.

**Switching back to the original.** The original firmware expects its magic byte `0x55` and sees `0x22` instead, so it initialises its settings and clears the start vectors of the user routines. Unlike the upgrade, switching back therefore doesn't keep your user routines available.

**Factory reset.** Holding the left and right buttons while switching on the box resets the settings (`0x8008`–`0x8014`) to their factory values and the baud rate to 19'200. The LEDs blink three times to confirm.

Unlike the original, the factory reset keeps the Multi Adjust calibration and the start vectors of the user routines:

- The calibration depends on the hardware, not on your preferences, so you don't need to calibrate again after a reset. To change it, use **Calibrate MA** in the menu (see the [Reference Manual, section 2.4](README.md#24-calibrating-multi-adjust)).
- The original clears the start vectors but keeps the user module data, so the user routines aren't really deleted. User routines are managed by external tools, which can also manage this part of the EEPROM. The factory reset therefore leaves both the start vectors and the module data untouched.

Because the top mode is reset to `0x87`, the user routines can no longer be selected in the menu after a factory reset. They are hidden, not deleted. To make them selectable again, use your tool to set the top mode to the highest user routine you want to use, e.g. `0x88` for User 1. Write it to `0x8008` so that it is kept after a restart, and to `0x41F3` so that it applies immediately.

