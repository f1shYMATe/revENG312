# revENG312 – Reference Manual

This manual describes the revENG312 replacement firmware for the ET-312, the MK-312 and the micro312. It is written for users who already know the original firmware. It covers what revENG312 takes over from the original, and where it behaves differently.

The manual starts with everyday operation and gets more technical towards the end. The later sections are aimed at expert users and at developers of remote-control software.

All addresses in this manual are given as they are exposed over the serial interface, starting at `0x4000`. For example, the RAM location the firmware itself calls `0x0180` is written here as `0x4180`.

---

## What's new or different at a glance

| Area | Change | Section |
|---|---|---|
| Bootloader | Faster flashing, no backlight flicker, protected bootloader section | [1.2](#12-reveng312-bootloader) |
| Routines | All routine combinations work in split mode | [2.1](#21-routines-and-modes) |
| Routines | Multi Adjust range follows each channel's own routine in split mode | [2.1](#21-routines-and-modes) |
| Routines | User routines 7 and 8 are available | [2.1](#21-routines-and-modes) |
| Operation | OK mutes and unmutes a running routine | [2.2](#22-muting-a-running-routine) |
| Menu | Settings are saved to EEPROM immediately; "Save settings" removed | [2.3](#23-menu-and-settings) |
| Menu | You stay in advanced parameter editing after confirming a value | [2.3](#23-menu-and-settings) |
| Menu | Auto-repeat when holding the arrow keys | [2.3](#23-menu-and-settings) |
| Menu | Multi Adjust calibration; no more matching the internal resistor to the potentiometer | [2.4](#24-calibrating-multi-adjust) |
| Settings | Upgrading from the original keeps settings, advanced parameters and user routines | [Memory Map 5.2](memory_map.md#52-initialisation) |
| Settings | Factory reset keeps the Multi Adjust calibration and the user routine start vectors | [Memory Map 5.2](memory_map.md#52-initialisation) |
| Output | Dead time between the halves of a biphasic pulse | [3.1](#31-waveforms) |
| Output | Output frequency no longer depends on width | [3.2](#32-frequency-accuracy) |
| Output | Multi Adjust can no longer push the frequency above 250 Hz | [3.3](#33-value-clamping) |
| Self-test | Zero-output check at start-up | [4.1](#41-self-test-at-start-up) |
| Self-test | Additional error codes on the failure screen | [4.3](#43-error-codes) |
| Link | More robust connection setup; recovery from timeouts without power cycling | [5](#5-linking-two-boxes) |
| Serial | 38'400 and 250'000 baud, selectable in the menu | [6.1](#61-baud-rates) |
| Control apps | New possibilities: mute command, phaselock mode, frequency detune, real-time streaming | [7.1](#71-overview) |
| Control apps | Multi Adjust can be controlled with raw values that the box scales; differs from the original when both control flags are set | [7.6](#76-remote-control-of-levels-and-multi-adjust) |
| Modules | Instructions apply exactly once per channel | [8.1](#81-instructions-apply-once-per-channel) |
| Modules | Protection against out-of-range reads and writes | [8.3](#83-valid-address-ranges) |
| Modules | Instruction reference for writing your own modules | [Module Instruction Reference](module_opcode_reference.md) |

---

## 1. Overview

revENG312 implements all core functions of the original firmware:

- all built-in routines, including audio and triphase modes, split mode and the random modes
- the three power levels
- advanced parameter settings and favourite routine selection in the menu
- self-calibration of the output stage at start-up
- the serial protocol used by ErosLink and community tools
- linking two boxes over a serial cable
- the modulation engine and the module system for built-in and user routines

If you know the original, the box will feel familiar. Where revENG312 behaves differently, it is because a weakness of the original was corrected or a new option was added. Each difference is described in the section it belongs to.

### 1.1 Compatibility at a glance

| Combination | Works |
|---|---|
| revENG312 `.upg` image → original Erostek bootloader | Yes |
| Original `.upg` image → revENG312 bootloader | Yes |
| Linked boxes, one running revENG312, the other the original firmware | Yes, in either master/slave role |
| ErosLink and community tools using the original serial protocol | Yes |

How to install or update the firmware is described in [Updating](../updating.md).

### 1.2 revENG312 bootloader

revENG312 comes with its own bootloader. You don't need it to run revENG312, since the `.upg` images also install through the original bootloader. Compared with the original bootloader, the revENG312 bootloader:

- **flashes faster.** It is available in builds for 19'200, 38'400 and 250'000 baud. Each build uses one fixed baud rate.
- **doesn't make the LCD backlight flicker** during flashing.
- **protects itself.** An upload file of the wrong size cannot overwrite the bootloader section. The original bootloader has no such protection.

For details and installation, see [Bootloader](../bootloader.md).

---

## 2. Operation and menu

### 2.1 Routines and modes

All built-in routines, audio and triphase modes, split mode and the random modes behave as on the original firmware. The exceptions are listed below.

**Split mode.** On the original, not every combination of routines works in split mode: Rhythm and Climb interfere with the routine on the other channel. In revENG312, every selectable routine can be combined with any other, and each channel runs independently.

**Multi Adjust in split mode.** On the original, when two different routines run in split mode, the Multi Adjust range is taken from channel B only (and is altered when Climb runs on channel A). In revENG312, each channel follows the Multi Adjust range of its own routine.

**User routines 7 and 8.** The original only supports user routines 1–6. revENG312 supports all eight user routine slots.

### 2.2 Muting a running routine

Pressing **OK** while a routine is running mutes the output. The LCD shows `-MUTE- OK=unmute`. Pressing **OK** again unmutes the output, which comes back with the normal ramp.

### 2.3 Menu and settings

**Settings are saved immediately.** On the original, changed settings only persist after selecting "Save settings" from the menu. In revENG312, every setting is written to EEPROM as soon as you confirm it, so the "Save settings" menu entry has been removed.

**Staying in the menu.** On the original, confirming an advanced parameter with OK returns you to the main screen. In revENG312 you stay in advanced parameter editing, so you can change several values in a row.

**Auto-repeat on the arrow keys.** Pressing and holding an arrow key moves through the value range continuously. You no longer need to press the key repeatedly to cover a large range.

### 2.4 Calibrating Multi Adjust

The Multi Adjust dial is a 10 kΩ potentiometer between ground and a 20 kΩ resistor to +5 V. At the dial's maximum, the raw reading at `0x4061` is therefore only about a third of the ADC range: nominally `0x55`, and with the potentiometer's tolerance typically not much above `0x5F`. The firmware treats the reading at the dial's maximum as full scale. On the original, this value is fixed, so the dial only covers the full range of a routine if the internal resistor matches the tolerance of the potentiometer. If they don't match, part of the range can't be reached, or the top of the range is reached before the end of the dial.

revENG312 lets you calibrate the dial from the menu instead:

1. Unplug any audio source and wired remote control.
2. In the main menu, select **Calibrate MA**.
3. Turn the Multi Adjust dial to its maximum.
4. Press **OK**.

The raw reading at the dial's maximum is stored as the calibration value and saved to EEPROM immediately. From then on, the dial covers the full range of each routine. Pressing **Menu** instead of OK cancels without changing the calibration. **Left** and **Right** have no function in the calibration screen.

The default calibration value is the nominal `0x55`. It is written when the EEPROM is initialised, including on the first start after upgrading from the original firmware. The factory reset keeps the calibration, as it depends on the hardware (see the [Memory Map, section 5.2](memory_map.md#52-initialisation)). The calibration value is located at `0x4208` (RAM) and `0x8016` (EEPROM), see the [Memory Map](memory_map.md#38-editing-status-and-internal-state-0x42000x4237).

---

## 3. Output behaviour

### 3.1 Waveforms

The selectable waveforms are the same as on the original: biphasic, positive, negative and alternating.

**Dead time in biphasic pulses.** revENG312 inserts a short dead time between the positive and the negative half of a biphasic pulse.

### 3.2 Frequency accuracy

On the original, the actual output frequency depends on the width setting: the oscillator does not account for the accumulated pulse width, so increasing the width lowers the frequency slightly. In revENG312, the output frequency matches the selected frequency precisely, regardless of the width.

In the advanced settings, the frequency can be set between 15 and 250 Hz. Some built-in routines go higher, up to about 405 Hz (see section 3.4).

For even finer frequency control, a control app can detune each channel over the serial interface (see section 7.5).

### 3.3 Value clamping

The nominal frequency range of the box is 15–250 Hz, and that is what the advanced settings allow. On the original, some routines let Multi Adjust push the frequency above 250 Hz continuously, because the value is not clamped when the frequency follows Multi Adjust. In revENG312, the frequency set by Multi Adjust is clamped at 250 Hz.

A few built-in routines briefly peak above 250 Hz. revENG312 keeps these peaks so the routines behave as on the original. With revENG312 they reach up to about 405 Hz. On the original, the same values only reach about 335 Hz, because there the pulse width adds to the period (see section 3.2).

Width, frequency, intensity and ramp values are clamped to their valid ranges (see section 3.4).

### 3.4 Valid parameter ranges

Parameters are stored as 8-bit values. The table shows the valid range of each parameter in the advanced settings, and how the stored value relates to what the display shows.

| Parameter | Valid range (hex) | Valid range (dec) | Display |
|---|---|---|---|
| Frequency | `0x0F`–`0xFA` | 15–250 | Approx. 250–15 Hz (higher value = lower frequency) |
| Width | `0x46`–`0xFA` | 70–250 | Stored value |
| Ramp time | `0x01`–`0x78` | 1–120 | Stored value |
| Effect | `0x01`–`0x64` | 1–100 | Stored value |
| Pace | `0x01`–`0x64` | 1–100 | Stored value |
| Tempo | `0x01`–`0x64` | 1–100 | Stored value |
| Depth | `0xA5`–`0xFF` | 165–255 | Stored value − 155 (10–100) |
| Ramp level | `0xCD`–`0xFF` | 205–255 | Stored value − 155 (50–100) |

**Hard limits.** Independently of the ranges above, frequency and width have hard limits that apply to every value, as on the original firmware:

| Parameter | Minimum value | Limit |
|---|---|---|
| Frequency | `0x09` | Max. approx. 405 Hz |
| Width | `0x32` | Min. 50 µs |

Writing frequency or width directly to RAM over the serial interface is limited only by these hard limits. Continuous output above 250 Hz is therefore possible this way, as on the original. A tool that writes these values directly is responsible for keeping them within the nominal range.

**Frequency is a period.** Strictly speaking, the frequency parameter is a period, not a frequency. The firmware expands the 8-bit value into a 16-bit period as follows:

```
period = (frequency_value << 8) | 0xA0
```

This maps the 8-bit range as closely as possible onto 15–250 Hz. Because the value is a period, a larger value gives a lower frequency.

---

## 4. Self-test and failure screen

### 4.1 Self-test at start-up

Like the original, revENG312 self-calibrates the output MOSFETs at start-up.

In addition, revENG312 checks that the output is zero when it should be. This detects a faulty op-amp that would otherwise drive the output at full power regardless of the dial position.

### 4.2 Failure screen

When the firmware detects a serious fault, it switches the output off, stops execution and shows a failure screen. The LCD backlight flashes. To recover, power cycle the box.

The first line of the failure screen shows the error code (see section 4.3). The second line always reads `Shut Off Power!`. For example, error code 53 looks like this:

```
Failure 53
Shut Off Power!
```

A low battery is the only exception: instead of an error code, the first line reads `Battery: Low`. Otherwise the screen behaves the same way.

### 4.3 Error codes

**Codes known from the original firmware:**

| Code | Name | Meaning | Start-up | Runtime |
|---|---|---|---|---|
| 15 | Module | Invalid module number when loading a module | | ✕ |
| 16 | Power level | Invalid power level setting | | ✕ |
| 20 | Calibration | Output calibration failed | ✕ | |
| 21 | PSU range | Supply voltage out of range | ✕ | ✕ |

**Codes added by revENG312:**

| Code | Name | Meaning | Start-up | Runtime |
|---|---|---|---|---|
| 18 | Baud rate | Invalid baud rate setting | | ✕ |
| 22 | Zero output | Output not zero when it should be (see section 4.1) | ✕ | |
| 26 | Power level (init) | Invalid power level setting | ✕ | |
| 28 | Baud rate (init) | Invalid baud rate setting | ✕ | |
| 51 | Module block | Module data exceeds the maximum module size (256 bytes, e.g. missing terminator) | | ✕ |
| 52 | Module nesting | Too many nested modules (maximum 3) | | ✕ |
| 53 | Module address | Instruction address outside the permitted range (see section 8.3) | | ✕ |
| 54 | Module copy | COPY instruction has an invalid length or overflows the permitted address range | | ✕ |
| 55 | Module offset | Module offset leads outside the module's memory area | | ✕ |
| 80 | RX buffer | Serial receive buffer overflow | | ✕ |
| 81 | TX buffer | Serial transmit buffer overflow | | ✕ |

---

## 5. Linking two boxes

Two boxes can be linked with a serial crossover cable, as on the original. Each box can run either revENG312 or the original firmware, in either the master or the slave role.

revENG312 makes the link considerably more reliable:

- **More robust connection setup.** Connections fail much less often, including when cables are plugged in or boxes are switched on in a different order.
- **Timeout recovery.** If the link times out, the box returns to a "press any key" screen, from where you can resume normal operation. On the original, every link failure ends on the failure screen, so you have to power cycle the box each time.

**Rhythm in split mode.** When the master runs split mode, a channel running Rhythm is only passed on to the slave at 250'000 baud. At lower baud rates, the link is too slow to switch the gates accurately at Rhythm's fast pace.

The more stable link also lets a control app stream channel values to the box in real time (see section 7.7).

---

## 6. Serial interface

This section is aimed at users of remote-control software. Developers find more details in section 7.

revENG312 implements the serial protocol of the original firmware, so ErosLink and community-built tools work unchanged.

### 6.1 Baud rates

The original firmware only communicates at 19'200 baud. revENG312 also supports 38'400 and 250'000 baud. You select the baud rate in the menu, and the change takes effect immediately.

The default is 19'200 baud, which keeps compatibility with existing tools.

### 6.2 Memory map and execute commands

Most documented RAM parameters are mapped to the same locations as on the original. The memory map is described in a separate document, [revENG312 – Memory Map](memory_map.md). It covers the virtual address mapping, all locations a tool can access, and the differences from the original.

The execute commands are described in [revENG312 – Execute Commands](execute_commands.md). It compares every command with the original firmware.

---

## 7. Developing control apps

This section is aimed at developers of remote-control software. It describes what revENG312 offers beyond the original firmware, and how a tool should use it.

### 7.1 Overview

| Feature | What it does | Section |
|---|---|---|
| Mute command | Mutes and unmutes the output remotely, like pressing OK | [7.3](#73-new-execute-commands) |
| Phaselock mode | Sets an exact phase shift between channel A and channel B | [7.4](#74-phaselock-mode) |
| Frequency detune | Fine-tunes the frequency of each channel (experimental) | [7.5](#75-frequency-detune-experimental) |
| Multi Adjust with box-side scaling | The tool writes a raw Multi Adjust value; the box scales it for both channels | [7.6](#76-remote-control-of-levels-and-multi-adjust) |
| Real-time streaming | Streams gate, ramp, intensity, frequency and width of both channels to the box | [7.7](#77-real-time-streaming) |
| Higher baud rates | 38'400 and 250'000 baud | [6.1](#61-baud-rates) |

> **Worth trying:** phaselock mode and real-time streaming open up possibilities that go beyond what the built-in routines and modules can do.

### 7.2 Quick reference

| Topic | Address | Where to find it |
|---|---|---|
| Execute commands | `0x4070`, `0x4071` | [Execute Commands](execute_commands.md) |
| Simulated button presses | `0x4068` | [Execute Commands, section 2](execute_commands.md#2-simulating-button-presses) |
| Current menu item | `0x4078` | [Execute Commands, section 6.2](execute_commands.md#62-menu-item-values) |
| LCD character output | `0x4180`, `0x4181` | [Execute Commands, section 5.1](execute_commands.md#51-0x13--write-a-character-to-the-lcd) |
| Phase mode | `0x4083` | [7.4](#74-phaselock-mode) |
| Phase shift (phaselock) | `0x4080`, `0x4081` | [7.4](#74-phaselock-mode) |
| Frequency detune | `0x407C`–`0x407F` | [7.5](#75-frequency-detune-experimental) |
| Control flags for pots and Multi Adjust | `0x400F` | [7.6](#76-remote-control-of-levels-and-multi-adjust) |
| Level pots | `0x4064`, `0x4065` | [7.6](#76-remote-control-of-levels-and-multi-adjust) |
| Multi Adjust: raw value, range, scaled value | `0x4061`, `0x4086`–`0x4087`, `0x420D` | [7.6](#76-remote-control-of-levels-and-multi-adjust) |
| Multi Adjust calibration | `0x4208`, `0x8016` | [2.4](#24-calibrating-multi-adjust) |
| Real-time streaming | `0x4004`, `0x400A` | [7.7](#77-real-time-streaming) |
| Module channel selection | `0x4085` | [8.2](#82-channel-selection) |
| Module accumulators, conditional load, random limits | `0x408C`, `0x418C`, `0x4084`, `0x408D`–`0x408E` | [Module Instruction Reference](module_opcode_reference.md#23-special-addresses) |
| Memory map | `0x4000`–`0x43FF`, `0x8000`–`0x81FF` | [Memory Map](memory_map.md) |

### 7.3 New execute commands

revENG312 adds four execute commands. All commands are listed in [revENG312 – Execute Commands](execute_commands.md).

| Code | Function |
|---|---|
| `0x2A` | Mute or unmute the output, the same as pressing OK while a routine is running. Unmuting brings the output back with the normal ramp. |
| `0x17` | Restart the box |
| `0x2B` | Set the baud rate from the current menu item at `0x4078`, save it and apply it immediately. The tool must switch to the new baud rate straight away. |
| `0x2C` | Store the current raw Multi Adjust reading (`0x4061`) as the calibration value in RAM (`0x4208`) and EEPROM (`0x8016`) (see section 2.4) |

Loading the favourite routine with command `0x00` or `0x05` starts it muted. Use `0x2A` to unmute it.

To operate the menu remotely, simulating button presses at `0x4068` is usually easier and safer than executing menu commands directly (see [Execute Commands, section 2](execute_commands.md#2-simulating-button-presses)).

### 7.4 Phaselock mode

Phaselock mode is new in revENG312. It extends triphase by letting you set the exact phase shift between channel A and channel B over the serial link.

To use phaselock mode:

1. Set the channel A and channel B frequencies to the same value.
2. Write `0x14` to `0x4083` to enable phaselock mode.
3. Write the phase shift between the channels to `0x4080` (LSB) and `0x4081` (MSB).

The phase shift is an absolute 16-bit value in microseconds.

To leave phaselock mode, write `0x00` to `0x4083`.

Two bits of `0x4083` control the mode: bit 2 is the master switch for the phase modes, and bit 4 selects phaselock.

### 7.5 Frequency detune (experimental)

Each channel's frequency can be detuned by a 16-bit value, which gives finer control over the output frequency than the 8-bit frequency parameter. The detune values can only be set over the serial interface:

| Channel | LSB | MSB |
|---|---|---|
| A | `0x407C` | `0x407D` |
| B | `0x407E` | `0x407F` |

This feature is experimental and not yet fully tested.

### 7.6 Remote control of levels and Multi Adjust

A control app can take over the two level pots and the Multi Adjust dial. The easiest and most reliable way is to let the box do the scaling: the tool only writes the raw dial position, just as if it were turning the dial. revENG312 still supports the method existing tools use, but new tools should use the recommended method.

**How the box produces the values.** The level pots are sampled directly into `0x4064` (channel A) and `0x4065` (channel B). The Multi Adjust value goes through several steps:

1. The dial is sampled into `0x4061` (raw value).
2. The last 16 raw values are averaged.
3. The average is scaled to the range of the running routine, from `0x4086` (minimum) to `0x4087` (maximum). The calibration value at `0x4208` is the full-scale reading (see section 2.4).
4. The result is stored at `0x420D`.

In split mode, each channel has its own range. revENG312 scales the value for channel B separately, using the range at `0x4186`/`0x4187`.

**Control flags.** Two bits at `0x400F` stop parts of this process:

- **Bit 0** stops sampling the level pots, and stops averaging and scaling the Multi Adjust value.
- **Bit 3** stops sampling the Multi Adjust dial.

| `0x400F` | Level pots | Multi Adjust | The tool writes |
|---|---|---|---|
| Neither bit set | From the dials | From the dial, scaled by the box | Nothing |
| Bit 0 (`0x01`) | From the tool | Not scaled | Levels to `0x4064`/`0x4065`, scaled value to `0x420D` |
| Bit 3 (`0x08`) | From the dials | From the tool, scaled by the box | Raw value to `0x4061` |
| Both bits (`0x09`) | From the tool | From the tool, scaled by the box | Levels to `0x4064`/`0x4065`, raw value to `0x4061` |

**Recommended: let the box scale (set both bits).** Write the levels to `0x4064`/`0x4065` and the raw Multi Adjust value to `0x4061`, from `0x00` up to the calibration value at `0x4208` (see section 2.4). The box scales the value to the range of the running routine, so the tool never has to know or follow the range. This is also the only method that works correctly for both channels in split mode. Because the value is averaged like the dial, a new value takes effect smoothly over 16 averaging steps.

**Legacy method: set bit 0 only.** Existing tools read the range at `0x4086`/`0x4087`, scale the value themselves and write the result to `0x420D`. This works as on the original, but the tool has to follow every range change when the routine changes.

In split mode, the legacy method only works correctly for channel A. Channel B has its own range at `0x4186`/`0x4187`, which legacy tools don't take into account, so channel B doesn't follow correctly. On the original, Multi Adjust in split mode doesn't work properly in the first place (see section 2.1), so this is still an improvement. New tools should nevertheless use the recommended method.

**Difference from the original.** With both bits set, the original doesn't scale the Multi Adjust value, so a tool would have to write `0x420D` itself. revENG312 scales the raw value instead and overwrites `0x420D`. No known community tool sets both bits.

To give control back to the dials, clear both bits.

### 7.7 Real-time streaming

With the link now much more stable (see section 5), a control app can take the role of a linked master and stream the output values of both channels to the box in real time. The box behaves like a linked slave and follows the values it receives.

1. **Handshake:** send `0x0E` to the box and wait for `0x05` in reply. The box then enters link mode and waits for the stream. Link messages are not encrypted.
2. **Start the stream within 20 ms.** Otherwise the box times out.
3. **Stream:** send the message for channel A and wait for `0x06`. Then send the message for channel B and wait for `0x06`. Start over with channel A.

| Channel | Message |
|---|---|
| A | `0x9D 0x40 0x04 0x00` [gate] [ramp] [intensity] [frequency] [width] [checksum] |
| B | `0x9D 0x40 0x0A` [gate] [ramp] [intensity] [frequency] [width] `0x00` [checksum] |

- The checksum is the sum of all preceding bytes of the message, modulo 256.
- The last data byte of the channel B message must be `0x00`. It is written to the flags at `0x400F`, and none of these flags should be set while streaming.
- Frequency values below `0x09` and width values below `0x32` are raised to these limits.
- Keep the stream going. If it stops, the box times out (see section 5).
- To mute the output, send `0x00` for all values, or at least `0x00` or `0x06` as the gate value.

---

## 8. Module system

This section is aimed at expert users and developers writing their own modules. It summarises what differs from the original. The instruction encoding, address ranges, channel selection, conditional loading, where modules are stored and all module error codes are described in [revENG312 – Module Instruction Reference](module_opcode_reference.md).

revENG312 uses the same module system as the original:

- Every built-in and user routine consists of one or more modules, which are loaded when you select the routine. Modules can also be loaded by audio and timer triggers. In addition, a module can load another module in its place when a condition is met (the value at an address equals the module accumulator). This is a jump, not a call: the rest of the original module is not executed. Up to three conditional loads may follow each other (see error code 52).
- A module is at most 256 bytes long, including its terminator (see error code 51).
- User routines are stored in EEPROM, or temporarily in the RAM scratchpad for testing (see [Module Instruction Reference, section 8](module_opcode_reference.md#8-storing-modules)).
- The modulation engine for frequency, width, intensity, ramp and gate works as on the original.

### 8.1 Instructions apply once per channel

On the original firmware, an instruction can be applied to the same value up to four times. For example, `ADD 1` can end up adding 4.

In revENG312, each instruction is applied exactly once per channel.

### 8.2 Channel selection

The "apply to" setting at `0x4085` decides which channel an instruction acts on. What happens also depends on whether the instruction uses a low address or a high address:

- **Low addresses** (`0x4000`–`0x40FF` and `0x4200`–`0x42FF`) are relative to the channel being processed.
- **High addresses** (`0x4100`–`0x41FF` and `0x4300`–`0x43FF`) always refer to channel B.

The module accumulator is at `0x408C` for channel A and at `0x418C` for channel B.

| `0x4085` | Low address | High address |
|---|---|---|
| `0x00` – no channel | Instruction skipped | Instruction skipped |
| `0x01` – apply to A | Channel A value, channel A accumulator | Channel B value, channel A accumulator |
| `0x02` – apply to B | Channel B value, channel B accumulator | Channel B value, channel B accumulator |
| `0x03` – apply to both | Channel A and channel B values, each with its own accumulator | Channel B value, channel A accumulator |

What follows from this:

- **A high address is used exactly once**, whatever the selection (except `0x00`). A module running with apply to A can therefore still write channel B through a high address. STORE, LOAD and CONDEXEC with a high address use the channel A accumulator under apply to A and apply to both.
- **Apply to B shifts every address** to its high counterpart, including read addresses and the registers `0x4080`–`0x408B`. The only exception is `0x4085` itself.
- **`0x4085` is never redirected**, so a module can change the selection in the middle and the change takes effect with the next instruction. The selection is reset to apply to both when a module ends and after a conditional load has finished.
- **The module to load on a condition** can only be stored at `0x4084`. Under apply to B, a write to `0x4084` ends up at `0x4184`, which has no such function: switch the selection first by writing `0x4085`. Under apply to both, a write to `0x4084` also writes `0x4184`.
- **RAND** draws a separate random number for each channel. The limits always come from `0x408D` and `0x408E`.
- **CONDEXEC** under apply to both checks channel A first and loads the module on a match; otherwise it checks channel B.
- **With `0x00`**, the module is still read up to its terminator, but no instruction is executed and CONDEXEC cannot fire.

Step-by-step details and examples are in the [Module Instruction Reference, section 3](module_opcode_reference.md#3-channel-selection).

### 8.3 Valid address ranges

revENG312 restricts which addresses a module may access.

**Write instructions** may only write to these ranges:

| | Range |
|---|---|
| Low addresses | `0x4080`–`0x40BF` |
| High addresses | `0x4180`–`0x41BF` |

**STORE and CONDEXEC** may read from `0x4060` to `0x43FF`:

| | Ranges |
|---|---|
| Low addresses | `0x4060`–`0x40FF` and `0x4200`–`0x42FF` |
| High addresses | `0x4100`–`0x41FF` and `0x4300`–`0x43FF` |

The check is made on the address as written in the instruction, before the channel selection shifts it (see section 8.2).

Writing the channel blocks (`0x4090`–`0x40BF`, `0x4190`–`0x41BF`) is always safe. Writing the channel headers (`0x4080`–`0x408F`, `0x4180`–`0x418F`) can have unexpected effects in rare combinations, because the firmware also uses some of these locations for other purposes (see the [Memory Map, section 3.3](memory_map.md#33-channel-headers-0x40800x408f-0x41800x418f)).

An instruction that accesses an address outside these ranges stops the firmware and shows the failure screen with error code 53 (see section 4.3). A COPY instruction with an invalid length, or one that would run past the permitted range, triggers error code 54. All instructions before the faulty one have already been executed.

The ranges per instruction and the unused opcodes are described in the [Module Instruction Reference, section 2.2](module_opcode_reference.md#22-valid-ranges).
