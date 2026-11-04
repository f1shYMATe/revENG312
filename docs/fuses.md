# Fuse settings (ATmega16A / ATmega32A)

> ⚠️ **Wrong fuses can lock you out of the chip.**
> Wrong setting of `SPIEN` will disable ISP programming, and lock you out. A wrong `CKSEL` value potentially leaves the chip without a working clock.
> If you just wrote a wrong value and have **not** reset/power-cycled yet, ISP still works: write the correct value immediately.

I recommend using a [fuse calculator](https://www.engbedded.com/fusecalc/) for a better overview and convenient flash command generation.

## Settings for revENG312

I recommend enabling BOD (brown out-detection). This prevents flash memory/EEPROM corruption that happens on rare occasions. Check out this [report](brownout_memory_corruption.md) for more details.

The table below shows the fuses used for MCU with external crystal, SPI and BOD enabled.

| MCU | Bootloader | lfuse | hfuse | avrdude arguments |
|---|---|---|---|---|
| ATmega16A | ❌ no | `0xBF` | `0xDF` | `-U lfuse:w:0xbf:m -U hfuse:w:0xdf:m` |
| ATmega16A | ✅ yes | `0xBF` | `0xDC` | `-U lfuse:w:0xbf:m -U hfuse:w:0xdc:m` |
| _ATmega32A (planned, untested)_ | ❌ no | `0xBF` | `0xDF` | `-U lfuse:w:0xbf:m -U hfuse:w:0xdf:m` |
| _ATmega32A (planned, untested)_ | ✅ yes | `0xBF` | `0xDA` | `-U lfuse:w:0xbf:m -U hfuse:w:0xda:m` |


## Reading and writing fuses with avrdude

In all commands below, replace `-c usbasp` with your programmer (`-c stk500v1 -P COMx -b 19200` for Arduino-as-ISP, `-c atmelice_isp`, …) and `-p m16a` for different MCU (`-p m32a` for ATmega32A).

Read the current values:

```sh
avrdude -c usbasp -p m16a -U lfuse:r:-:h -U hfuse:r:-:h
```

Write (example for ATmega16A with bootloader):

```sh
avrdude -c usbasp -p m16a -U lfuse:w:0xBF:m -U hfuse:w:0xDC:m
```
