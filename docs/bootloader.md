# The revENG312 bootloader

The bootloader is a small program that lives in the boot section at the top of flash. On reset it decides whether to start the application or to wait for a firmware update over the serial port.

## Why use it?

You only need an ISP programmer **once**, to install the bootloader. After that, every update goes through the serial port. Additionally it reduces the risk of mistyped flash commands and checks the flash contents for integrity on every boot.

## Entering update mode

Hold down **MENU** and **RIGHT** buttons while powering on the device. If both LEDs are blinking simultaneously (and serial advertises `0x43 ("C")` every second), the device is in bootloader mode. Note that the LCD stays **uninitialized** in bootloader mode. If you don't see the above behaviour, either there's no bootloader present, or the high fuse is not programmed correctly (see [fuses](fuses.md)).

## Three bootloader builds — pick one

Choose the correct bootloader version for your MCU. This is important, as the memory sizes and addresses are different for each MCU.

The bootloader's baud rate is **fixed at build time**. There is no room in the tiny bootloader size (at least on the ATmega16) for a runtime setting, so it is shipped in three versions.

| Baud rate | Notes |
|---|---|
| 19'200 | **Recommended default.** Works with three-twelve-bee *and* `fw-utils.py`. Matches the original bootloader's rate. |
| 38'400 | Faster uploads. `fw-utils.py` only. |
| 250'000 | Fastest. `fw-utils.py` only; needs a USB-serial adapter that does 250k cleanly (FTDI, CP2102 and CH340 generally do). |

> If you are unsure, take **19'200**. An update of a ~16 KB image takes well under a minute even at that rate, and it keeps every upload tool available to you.

All three builds are otherwise identical: same entry condition, same `.upg` format, same checksum. How the revENG312 bootloader differs from the stock one is summarized in [Reference Manual 1.2](reference_manual/README.md#12-reveng312-bootloader).

## Bootloader baud rate vs. application baud rate

These are **two independent settings**, and they are easy to confuse:

| | Bootloader | Application (revENG312 firmware) |
|---|---|---|
| Used for | Uploading new firmware (`.upg`) | Runtime serial link (remote control, master/slave link, …) |
| Values | 19'200 / 38'400 / 250'000 | 19'200 / 38'400 / 250'000 |
| How it is chosen | Fixed — depends on which `.hex` you flashed | Selectable in the device menu (see [Reference Manual 6.1](reference_manual/README.md#61-baud-rates)) |
| Default | — | 19'200 |
| Changing it | Re-flash a different bootloader `.hex` via ISP | Menu, takes effect immediately |

Changing the baud rate in the device menu does **not** change the rate the bootloader uses, and vice versa. If an upload fails, the first thing to check is that your upload tool uses the rate of the *bootloader* you installed.
