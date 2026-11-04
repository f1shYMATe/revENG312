# revENG312

Replacement firmware for the ET-312 / MK-312 / micro312 family of devices, written from scratch in bare-metal C and AVR assembly. It reimplements all of the original features and adds some new ones and bug fixes, while keeping most but not all of the memory map and serial commands.

It is a clean-room reimplementation based on black-box behavioural analysis, the ET312 specification from stpihkal and source code analysis of fenbyfluid's three-twelve-bee — no original code is contained in this repository.

> **Not affiliated with Erostek** or any manufacturer of ET-312/MK-312/micro312 compatible hardware. All product names are used for identification only.

---

## Acknowledgements

Many thanks to everyone who tested revENG312 and reported bugs before the public beta release.

If you appreciate this work, you can [buy me a coffee](https://buymeacoffee.com/fishymate) ☕

---

## Feature highlights and bug fixes
### Firmware
#### Added features:
- [Multi Adjust calibration](docs/reference_manual/README.md#24-calibrating-multi-adjust) - say goodbye to matching R16 (and R17) to the potentiometer's tolerance. Easily calibrate the MA range from the menu
- [Mute function](docs/reference_manual/README.md#22-muting-a-running-routine) - pressing OK button while routine is running mutes the output
- [Phaselock mode](docs/reference_manual/README.md#74-phaselock-mode) (accessible via serial) - allows defining the exact phaseshift in μs between the two outputs
- [Detune](docs/reference_manual/README.md#75-frequency-detune-experimental) (accessible via serial) - allows to detune a channel individually
- [Higher baud rates](docs/reference_manual/README.md#61-baud-rates) - 38'400 and 250'000 baud for the serial interface (in addition to 19'200), selectable in the menu
- [Link recovery](docs/reference_manual/README.md#5-linking-two-boxes) - If linking two boxes fails/times out, no need to power cycle the box
- [User routines 7 and 8](docs/reference_manual/README.md#21-routines-and-modes) - all eight user routine slots are available (stock only supports 1–6)
- [Settings saved immediately](docs/reference_manual/README.md#23-menu-and-settings) - every setting is written to EEPROM as soon as it is confirmed, no more "Save settings" menu entry
- [Seamless upgrade](docs/reference_manual/memory_map.md#52-initialisation) - when upgrading from the original firmware, settings, advanced parameters and user routines are kept
- [Zero-output self-test](docs/reference_manual/README.md#41-self-test-at-start-up) - at start-up, checks that the output is zero when it should be, detecting a faulty op-amp that would otherwise drive the output at full power

#### Fixed bugs:
- [Split mode](docs/reference_manual/README.md#21-routines-and-modes) - All modes now work correctly on any channel with the correct Multi Adjust scaling
- [Value clamping](docs/reference_manual/README.md#33-value-clamping) - Frequency, width, intensity and ramp values are clamped to their valid ranges
- [Module loading](docs/reference_manual/README.md#81-instructions-apply-once-per-channel) - Module opcodes apply only once per instruction

For the full list, see the [Reference Manual](docs/reference_manual/README.md#whats-new-or-different-at-a-glance).

---

### Bootloader
The `.upg` files in this repo are fully compatible for flashing via stock bootloader.

***[revENG312 bootloader](docs/reference_manual/README.md#12-reveng312-bootloader)*** allows you to flash at higher speeds, has no LCD backlight flicker during flashing process and protects the bootloader section from being overwritten by wrong upload file size (stock doesn't).

## Quick start — which path is mine?
> ### ⚠️ Caution: This repo does not contain any original firmware. If you're not in possession of the files to revert to the original state, you're on your own.

| Your situation | What to do |
|---|---|
| I have an ISP programmer (USBasp, Arduino, etc.) and want easy updates in the future | 1. [Install the bootloader](docs/flashing_isp.md#a-install-the-bootloader) → 2. [Upload the .upg](docs/updating.md) |
| I have an ISP programmer and don't want a bootloader | [Flash the .bin directly](docs/flashing_isp.md#b-flash-the-application-only-no-bootloader) |
| The stock bootloader is already installed (e.g. on the micro312) | [Upload the .upg](docs/updating.md) — no programmer needed |
| The revENG312 bootloader is already installed | [Upload the .upg](docs/updating.md) — no programmer needed |

Not sure whether you want the bootloader? See [docs/bootloader.md](docs/bootloader.md) — short answer: yes, you probably do.

## Supported hardware

| Target | MCU | Status |
|---|---|---|
| MK-312 | ATmega16A @ 8 MHz | ✅ beta |
| micro312 | ATmega16A @ 8 MHz | ✅ beta |
| _ET-312_ | _ATmega16A @ 8 MHz_ | _🧪 untested, probably works, try at own risk_ |
| MK-312 | _ATmega32A @ 8 MHz_ | _🚧 planned_ |

## What's in this repo
```
firmware/
├─ bootloader/<mcu>/   Bootloaders, one per MCU and baud rate
├─ mk312/m16a/         MK-312 with ATmega16A
├─ mk312/m32a/         MK-312 with ATmega32A (planned)
├─ u312/               micro312
└─ SHA256SUMS          Checksums for all release files
tools/                 Upload tool (fw-utils.py)
docs/                  Detailed documentation
```

File names and formats are described in [firmware/README.md](firmware/README.md).

## Documentation

- [docs/reference_manual/](docs/reference_manual/README.md) — reference manual: operation, output behaviour, serial interface, execute commands, module system, and all differences from the original firmware
  - [Memory Map](docs/reference_manual/memory_map.md) — virtual address mapping, all RAM and EEPROM locations a tool can access, differences from the original
  - [Execute Commands](docs/reference_manual/execute_commands.md) — all execute commands and simulated button presses, compared with the original
  - [Module Instruction Reference](docs/reference_manual/module_opcode_reference.md) — opcodes, address ranges, channel selection, conditional loading and module storage for writing your own modules
- [docs/bootloader.md](docs/bootloader.md) — why use a bootloader, the three bootloader builds, bootloader vs. application baud rate
- [docs/brownout_memory_corruption.md](docs/brownout_memory_corruption.md) — why brown-out detection should be enabled
- [docs/fuses.md](docs/fuses.md) — recommended fuse settings and how to read and write them with avrdude
- [docs/flashing_isp.md](docs/flashing_isp.md) — flashing with an ISP programmer (bootloader or application only)
- [docs/updating.md](docs/updating.md) — updating the firmware via the bootloader
- [tools/README.md](tools/README.md) — the `fw-utils.py` upload tool
- [CHANGELOG.md](CHANGELOG.md) — what changed between releases

## ⚠️ Warning

- This firmware drives a device that delivers electrical current to the human body. **You use it entirely at your own risk.** It is not a medical device and comes with no warranty of any kind (see [LICENSE](LICENSE.md)).
- **Disconnect all electrodes** before flashing, updating or changing fuses.
- Writing wrong fuse values can make the chip unresponsive. Read [docs/fuses.md](docs/fuses.md) before touching them.

---

## License

revENG312 is **free for personal and other non-commercial use** under the [PolyForm Strict License 1.0.0](LICENSE.md). Unmodified copies may be shared for noncommercial purposes; modifying, decompiling or reverse-engineering the binary is not permitted.

**Commercial use** (selling devices with this firmware pre-installed, offering flashing as a paid service, bundling it with a product, …) requires a separate license. See [COMMERCIAL.md](COMMERCIAL.md) — terms are discussed case by case and are meant to be fair.
