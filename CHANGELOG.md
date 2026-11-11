# Changelog

Firmware and bootloader are versioned separately. Firmware versions use the format `major.minor.patch`, with a two-digit patch number (e.g. `1.0.00`). Public beta builds carry a `b` suffix (e.g. `1.0.00b`).

<br>

# revENG312 Firmware
- Full reimplementation of the original's main features, plus additional features and bug fixes listed in the [Reference Manual](docs/reference_manual/README.md#whats-new-or-different-at-a-glance).

## [Unreleased]

Version for ATmega32A

## [v1.0.01b] — 2026-11-11

Bug-fix release. Updating is recommended for all users.

### Fixed
- The start vectors of user routines 7 and 8 weren't cleared correctly, neither on a fresh initialisation nor when upgrading from the original firmware.
- Split mode: channel A could go silent with Audio 3 on one channel.
- Split mode: linked to the slave even when one channel's routine isn't linkable.
- Out-of-range settings sent over serial could be saved under certain conditions, causing Failure 26/28 at every start-up.
- Corrupt settings in EEPROM could leave the box silent or show garbled text. They are now replaced with valid fallback values at start-up.

### Changed
- Smaller code size; no visible change.

### Notes for app developers
- Execute commands `0x06`, `0x0B`, `0x0C` and `0x2B` now ignore values derived from `CURRENT_MENU` that are outside `[LOWEST_MENU, HIGHEST_MENU]`, instead of saving them.
- Execute command `0x07` limits the advanced-parameter index to 0–7. Before, any `CURRENT_MENU` value caused out-of-range reads, and a following `0x0F` could write outside the advanced parameters (`0x800D + index`) and corrupt user module data.
- When loading from EEPROM, top mode and favourite routine are clamped to `0x76`–`0x8F`, split A/B to `0x76`–`0x7E`, power level to 1–3 and baud rate to 0–2.

### Known issue
Boxes set up with v1.0.00b keep the wrong user routine 7/8 start vectors; a factory reset doesn't clear them. To fix this, write `0x55` to EEPROM `0x8001` and restart the box.

## [v1.0.00b] — 2026-11-04

First public beta release.

<br>

# revENG312 Bootloader
- XMODEM-CRC bootloader, compatible with the `.upg` format
- Three builds: 19'200, 38'400, 250'000 baud

## [Unreleased]

Version for ATmega32A

## [v1.1] — 2026-11-04

First public beta release.