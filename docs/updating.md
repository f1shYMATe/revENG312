# Updating the firmware via the bootloader

Requires revENG312 or stock bootloader to be installed ([Installation steps](flashing_isp.md#a-install-the-bootloader)). No programmer needed. Both bootloaders accept the revENG312 `.upg` images (see [compatibility](reference_manual/README.md#11-compatibility-at-a-glance)).

> **Note** Upgrading from the original firmware keeps your settings and user routines. Switching back to the original resets its settings and clears the user routine start vectors. See [EEPROM initialisation](reference_manual/memory_map.md#52-initialisation) for details.

## What you need

- The `.upg` file for your device, e.g. `firmware/u312/revENG312_u312_m16a_1.0.00b.upg` for the micro312
- A serial connection to the device's 3.5 mm link jack. The link is **RS-232**, so use a USB-to-RS-232 adapter with a cable to the 3.5 mm plug (Tip: RXD, Ring: TXD, Sleeve: GND).
- To know **which bootloader build** is installed (19'200 / 38'400 / 250'000) — the upload tool must use exactly that rate.

## Choose an upload tool

| Tool | 19'200 | 38'400 | 250'000 | Install needed |
|---|---|---|---|---|
| [three-twelve-bee](https://three-twelve-bee.netlify.app/) | ✅ | ❌ | ❌ | none (browser with Web Serial, e.g. Chrome/Edge) |
| [`tools/fw-utils.py`](../tools/README.md) | ✅ | ✅ | ✅ | Python 3 + `pyserial` |

## 1. Put the device into update mode

Hold down **MENU** and **RIGHT** while powering on the device. Both LEDs blink simultaneously and the device sends `0x43` ("C") every second. The LCD stays **uninitialized** in bootloader mode. See [Entering update mode](bootloader.md#entering-update-mode) if this doesn't happen.

## 2a. Upload with the web uploader (19'200 baud only)

1. Click the 'Connect' button and select your serial adapter from the web serial list.
2. Click the 'Firmware update' button.
3. Browse to your `.upg` file.
4. Click 'Write Firmware' button.

## 2b. Upload with fw-utils.py (any baud rate)

```sh
pip install -r tools/requirements.txt
python tools/fw-utils.py -i firmware/u312/revENG312_u312_m16a_1.0.00b.upg -u COM3 -b 19200
```

- `-u` — serial port (`COM3` on Windows, `/dev/ttyUSB0` on Linux, `/dev/cu.usbserial-…` on macOS)
- `-b` — baud rate of your **bootloader**: `19200`, `38400` or `250000`

See [tools/README.md](../tools/README.md) for all options.

## 3. After the upload

**Success:** the box reboots and starts the new firmware, and you see the firmware splash screen.

**Failure:** the XMODEM transfer itself is protected block by block (a corrupted block is NAKed and resent). If the bootloader's own checksum verification of the flashed image fails, the device stays in update mode (LEDs blinking, `0x43` "C" sent every second). Upload again.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| Tool waits forever, nothing happens | Device not in update mode, wrong port, or **baud rate does not match the bootloader build** |
| Transfer starts, then aborts with errors | Cable/adapter problem; at 250'000 baud try a better adapter or use a lower-rate bootloader |
| Upload completes but device stays in update mode | Checksum failed — re-download the `.upg` and compare against `SHA256SUMS` |
| Wrong firmware variant | Make sure you picked the `.upg` that matches your box model and MCU |

An interrupted or failed upload is not dangerous: the bootloader itself is never overwritten, so you can simply retry.
