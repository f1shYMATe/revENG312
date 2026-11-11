# tools/

| File | Purpose |
|---|---|
| `fw-utils.py` | Upload a `.upg` to a device running the revENG312 bootloader (19'200 / 38'400 / 250'000 baud) |
| `xmodem_crc.py` | XMODEM-CRC sender used by `fw-utils.py` (no external xmodem package needed) |
| `requirements.txt` | Python dependencies |

## Setup

Should work with Python 3.6+ and pyserial 3.x.
Tested with Python 3.14 and pyserial 3.5.

```sh
pip install -r requirements.txt
```

## Usage

```sh
python fw-utils.py -i <file.upg> -u <port> -b <baud>
```

| Option | Meaning |
|---|---|
| `-i`, `--input` | Input file (`.upg` for upload/decrypt, `.bin` for encrypt/crc) |
| `-u`, `--upload` | Serial port to upload the input file to (e.g. `COM3`, `/dev/ttyUSB0`) |
| `-b`, `--baudrate` | Baud rate for upload — must match the installed bootloader build (default: 19200) |
| `-e`, `--encrypt` | Encrypt the input `.bin` into a `.upg` (needs `-o`). Adds the checksum |
| `-d`, `--decrypt` | Decrypt the input `.upg` into a `.bin` (needs `-o`) |
| `-o`, `--output` | Output file for `-e` / `-d` |
| `-c`, `--crc` | Print the xor/checksum bytes of the input file |
| `-s`, `--size` | Image size in bytes, decimal or hex (default: 15872 = `0x3E00`, the ATmega16A with bootloader) |
| `-v`, `--verbose` | Log every byte exchanged during upload (for troubleshooting) |

Example:

```sh
python fw-utils.py -i ../firmware/mk312/m16a/revENG312_mk312_m16a_1.0.01b.upg -u COM3 -b 38400
```

## License
These tools are licensed separately from the rest of this repository:
- `fw-utils.py`: BSD-3-Clause, based on code by The Buttshock Project
- `xmodem_crc.py`: 0BSD

Full texts in `LICENSES/`.
