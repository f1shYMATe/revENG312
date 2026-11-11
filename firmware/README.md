# Firmware files

| File | Format | Flash with | Docs |
|---|---|---|---|
| `revENG312_<target>_<mcu>_X.Y.ZZ[b].bin` | Raw binary, unencrypted | ISP programmer (avrdude `:r`), **no** bootloader | [flashing_isp.md § B](../docs/flashing_isp.md#b-flash-the-application-only-no-bootloader) |
| `revENG312_<target>_<mcu>_X.Y.ZZ[b].upg` | Encrypted update image incl. checksum | Bootloader (web uploader or `fw-utils.py`) | [updating.md](../docs/updating.md) |
| `bootloader/<mcu>/revENG312_bootloader_<mcu>_<baudrate>_vX.Y.hex` | Intel HEX, load address `0x3E00` (ATmega16A) | ISP programmer (avrdude `:i`) | [flashing_isp.md § A](../docs/flashing_isp.md#a-install-the-bootloader) |
| `SHA256SUMS` | Checksums | — | see below |

Example: `mk312/m16a/revENG312_mk312_m16a_1.0.01b.upg` (`b` = public beta)

Bootloader baud rates: `19200`, `38400`, `250k`, for example `bootloader/m16a/revENG312_bootloader_m16a_19200_v1.1.hex`.

## Verifying downloads

```sh
sha256sum -c SHA256SUMS                                          # Linux / macOS
certutil -hashfile revENG312_mk312_m16a_X.Y.ZZ.upg SHA256         # Windows, compare by hand
```

## Versions

| Firmware | Bootloader | Date | Notes |
|---|---|---|---|
| v1.0.01 | v1.1 | 2026-11-11 | Bug-fix release |
| v1.0.00 | v1.1 | 2026-11-04 | First public beta release |

Older versions are available from the [Releases](../../../releases) page.
