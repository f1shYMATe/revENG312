# revENG312 – Execute Commands

This document lists the execute commands of revENG312 and compares them with the original firmware. It belongs to the [revENG312 Reference Manual](README.md).

All addresses are given as they are exposed over the serial interface, starting at `0x4000`.

---

## 1. How commands are executed

revENG312 has two command registers, `0x4070` and `0x4071`, as on the original. Writing a command code to either register executes that command.

- `0xFF` means "no command".
- The firmware checks `0x4070` first, then `0x4071`. After executing a command, it writes `0xFF` back to that register. Once a tool reads `0xFF` from the register again, the command has been executed.
- Codes that are not implemented are ignored.

---

## 2. Simulating button presses

To operate the menu from a remote-control tool, simulate button presses instead of executing menu commands directly. The firmware then does exactly what it would do if the button had been pressed on the box, on whatever screen is currently shown.

To simulate a button press, write one of these values to `0x4068`:

| Value | Button |
|---|---|
| `0x10` | Left |
| `0x20` | OK |
| `0x40` | Right |
| `0x80` | Menu |

The firmware handles the press and writes `0x00` back to `0x4068`. Write one button at a time; combined values are ignored.

---

## 3. Choosing the right command

Most execute commands were designed for the firmware's own menu handling, not for remote control. Many of them depend on the current menu state or on values in RAM. Executed in the wrong order or with the wrong values, they can leave the box on an unexpected screen.

This document therefore splits the commands into three groups:

- **General-use commands (section 5)** are self-contained and safe to execute at any time.
- **Menu and state-dependent commands (section 6)** are documented for completeness. For remote control, simulated button presses (section 2) or writing the values directly to RAM or EEPROM are usually the better choice. For example, to change an advanced parameter, write the new value directly instead of going through the editing commands.
- **Unavailable commands (section 7)** are not implemented, or only available in debug builds.

---

## 4. About the original descriptions

The descriptions of the original firmware come from community reverse-engineering. Some of them are vague, and not all of them have been re-tested against the original.

The **Status** column therefore only marks a difference where one is known. Where the status is "Same", the revENG312 description is a more detailed account of the same function.

| Status | Meaning |
|---|---|
| Same | Same function as on the original |
| Differs | Known difference from the original, explained in the table |
| New | Not available on the original |
| Not in release | Only available in debug builds, which are not published |
| Not implemented | Ignored by revENG312 |

---

## 5. General-use commands

| Code | revENG312 | Original description | Status |
|---|---|---|---|
| `0x00` | Load the favourite routine (see section 5.2) | Start "Favourite" routine | Same, except that the routine starts muted |
| `0x01` | Do nothing | Do nothing | Same |
| `0x02` | Show the status screen | Display status screen | Same |
| `0x04` | Exit the menu and show the status screen | Exit menu | Same |
| `0x05` | Same as `0x00` | Same as `0x00` | Same, except that the routine starts muted |
| `0x0A` | Show the main menu | Show main menu | Same |
| `0x13` | Write a character to the LCD (see section 5.1) | Write character to LCD | Same |
| `0x17` | Restart the box | Not used (error) | New |
| `0x18` | Reset the channel A and channel B parameter regions. This stops the output. | Clear module (mute) | Same |
| `0x19` | Swap channel A and channel B | Swap channel A and B | Same |
| `0x1A` | Copy channel A to channel B | Copy channel A to channel B | Same |
| `0x1B` | Copy channel B to channel A | Copy channel B to channel A | Same |
| `0x1C` | Load the settings from EEPROM into RAM | Copy defaults from EEPROM | Same |
| `0x21` | Start the ramp | Start ramp | Same |
| `0x2A` | Mute or unmute the output, like pressing OK (see section 5.2) | — | New |
| `0xFF` | No command | No command | Same |

### 5.1 `0x13` – Write a character to the LCD

1. Write the character code to `0x4180`.
2. Write the position to `0x4181`.
3. Write `0x13` to a command register.

The LCD has two rows of 16 characters. The position selects the row and column:

| Position | Row | Column |
|---|---|---|
| `0x00`–`0x0F` | 1 | 0–15 |
| `0x40`–`0x4F` | 2 | 0–15 |

Positions from `0x80` upwards are ignored. Positions between these ranges point to columns beyond the visible 16 and do not appear on the display.

The character stays on the LCD until the firmware redraws that part of the screen.

### 5.2 Mute and unmute (`0x00`, `0x05`, `0x2A`)

When the favourite routine is loaded with `0x00` or `0x05`, it starts muted. `0x2A` mutes or unmutes the output, the same as pressing OK while a routine is running. When the output is unmuted, it comes back with the normal ramp.

---

## 6. Menu and state-dependent commands

These commands only work as intended when the box is in the right state. The **Requires** column lists what must be true before executing them. Most of them act on the current menu item, which is stored at `0x4078`.

| Code | revENG312 | Requires | Original description | Status |
|---|---|---|---|---|
| `0x03` | Select the current menu item (see section 6.1) | Main menu shown; `0x4078` holds a main menu item | Select current menu item | Same |
| `0x06` | Set the power level and save it to EEPROM | `0x4078` holds a power level (section 6.2) | Set power level | Differs: saved immediately |
| `0x07` | Start editing an advanced parameter | Current menu item is an advanced parameter (section 6.2) | Edit advanced parameter | Same |
| `0x08` | Show the next menu item | A menu is shown | Display next menu item | Same |
| `0x09` | Show the previous menu item | A menu is shown | Display previous menu item | Same |
| `0x0B` | Save split mode A, then continue to the split mode B selection | `0x4078` holds a routine (section 6.2) | Jump to split mode settings menu | Differs: saved immediately |
| `0x0C` | Save split mode B. If split mode is running, reload it with the new settings. | `0x4078` holds a routine (section 6.2) | Activates split mode | Differs |
| `0x0D` | Increase the advanced parameter being edited | Editing started with `0x07` | Advanced value up | Same |
| `0x0E` | Decrease the advanced parameter being edited | Editing started with `0x07` | Advanced value down | Same |
| `0x0F` | Save the edited advanced parameter to EEPROM and return to the advanced menu | Editing started with `0x07` | Show advanced menu | Differs: stays in the advanced menu |
| `0x10` | Load the next routine | Status screen shown | Switch to next mode | Same |
| `0x11` | Load the previous routine | Status screen shown | Switch to previous mode | Same |
| `0x12` | Load the routine in the current menu item | `0x4078` holds a routine (section 6.2) | New mode | Same |
| `0x20` | Cancel the edit: restore the previous value and return to the advanced menu | Editing started with `0x07` | Advanced setting update | Differs |
| `0x2B` | Set the baud rate, save it to EEPROM and apply it immediately | `0x4078` holds a baud rate (section 6.2) | — | New |
| `0x2C` | Store the current raw Multi Adjust reading (`0x4061`) as the calibration value in RAM (`0x4208`) and EEPROM (`0x8016`) | Multi Adjust dial at its maximum, or the full-scale value written to `0x4061` (see note) | — | New |

After `0x2B`, the box communicates at the new baud rate straight away, so the tool must switch to it before sending anything else.

`0x2C` stores whatever reading is at `0x4061` when it is executed. Audio sources and wired remote controls must be unplugged. If the dial is not at its maximum, the dial can no longer reach the top of the range. While a tool controls Multi Adjust (`0x400F` bit 3 set), `0x4061` holds the value written by the tool, not the dial reading. See [Reference Manual, section 2.4](README.md#24-calibrating-multi-adjust).

### 6.1 `0x03` – Select current menu item

What `0x03` does depends on the main menu item that is currently selected, which is stored at `0x4078`:

| Menu item | Name | Action |
|---|---|---|
| `0x07` | Start ramp | Start the ramp and show the status screen |
| `0x08` | Set split mode | Open the split mode A selection |
| `0x09` | Set as favourite | Save the current routine as the favourite routine (EEPROM) |
| `0x0A` | Set power level | Open the power level selection |
| `0x0B` | Set baud rate | Open the baud rate selection (new in revENG312) |
| `0x0C` | Link slave unit | Reset both channels and start the link handshake |
| `0x0D` | Calibrate MA | Open the Multi Adjust calibration (new in revENG312) |
| `0x0E` | Reset settings | Reset the settings in EEPROM to their defaults and restart the box |
| `0x0F` | Adjust advanced parameters | Open the advanced menu |

### 6.2 Menu item values

Several commands act on the value of the current menu item at `0x4078`. These are the values they expect:

**Power level (`0x06`):**

| Menu item | Power level |
|---|---|
| `0x6B` | Low |
| `0x6C` | Normal |
| `0x6D` | High |

**Baud rate (`0x2B`):**

| Menu item | Baud rate |
|---|---|
| `0x92` | 19'200 |
| `0x93` | 38'400 |
| `0x94` | 250'000 |

**Advanced parameters (`0x07`):**

| Menu item | Parameter |
|---|---|
| `0xD2` | Ramp level |
| `0xD3` | Ramp time |
| `0xD4` | Depth |
| `0xD5` | Tempo |
| `0xD6` | Frequency |
| `0xD7` | Effect |
| `0xD8` | Width |
| `0xD9` | Pace |

**Routines (`0x0B`, `0x0C`, `0x12`):**

| Menu item | Routine | Menu item | Routine |
|---|---|---|---|
| `0x76` | Waves | `0x83` | Orgasm |
| `0x77` | Stroke | `0x84` | Torment |
| `0x78` | Climb | `0x85` | Phase 1 |
| `0x79` | Combo | `0x86` | Phase 2 |
| `0x7A` | Intense | `0x87` | Phase 3 |
| `0x7B` | Rhythm | `0x88` | User 1 |
| `0x7C` | Audio 1 | `0x89` | User 2 |
| `0x7D` | Audio 2 | `0x8A` | User 3 |
| `0x7E` | Audio 3 | `0x8B` | User 4 |
| `0x7F` | Split | `0x8C` | User 5 |
| `0x80` | Random 1 | `0x8D` | User 6 |
| `0x81` | Random 2 | `0x8E` | User 7 |
| `0x82` | Toggle | `0x8F` | User 8 |

The current menu item is stored at `0x4078`. To use one of these commands without going through the menu, write the value to `0x4078` first, then execute the command.

---

## 7. Unavailable commands

| Code | Original description | Status |
|---|---|---|
| `0x14` | Write number to LCD | Not in release |
| `0x15` | Write string from string table to LCD | Not in release |
| `0x16` | Load module | Not in release (see section 7.1) |
| `0x1D` | Sets up running module registers | Not implemented |
| `0x1E` | Handles single instruction from a module | Not implemented |
| `0x1F` | General way to call these functions | Not implemented |
| `0x22` | Does an ADC conversion | Not implemented |
| `0x23` | Set LCD position | Not implemented |
| `0x24` | Redundant | Not implemented |
| `0x25`–`0x27` | Not used (error) | Not implemented |
| `0x28`–`0x29` | — | Not in release |

### 7.1 Running a user module from the scratchpad

`0x16` (load module) is not available in release builds. To test a user module, load it through a user routine instead:

1. Write the module data to the scratchpad (`0x40C0`–`0x417F`).
2. Write the module's start offset, relative to `0x40C0`, to `0x41D0`. This makes it module `0xC0`; offsets for modules `0xC1`–`0xDF` follow at `0x41D1`–`0x41EF`.
3. Write `0xC0` to the start vector of a user routine, e.g. `0x8018` for User 1.
4. Load that user routine: write its routine number to `0x4078` (e.g. `0x88` for User 1) and execute `0x12`. This works even if the routine is above the top mode and therefore can't be selected in the menu.

Alternatively, set the top mode (`0x41F3`, or `0x8008` to keep it after a restart) to the user routine, e.g. `0x88` for User 1. The routine then becomes selectable on the box: you can move through the routines with the arrow keys and come back to it at any time.

The start vector is stored in EEPROM, so it persists until it is changed. Details of the scratchpad and the EEPROM layout are in the [Memory Map](memory_map.md#35-user-module-scratchpad-0x40c00x417f). How to write the module data itself is described in the [Module Instruction Reference](module_opcode_reference.md).
