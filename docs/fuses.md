# Fuse settings (ATmega16A / ATmega32A)

> ⚠️ **Wrong fuses can lock you out of the chip.**
> Wrong setting of `SPIEN` will disable ISP programming, and lock you out. A wrong `CKSEL` value potentially leaves the chip without a working clock.
> If you just wrote a wrong value and have **not** reset/power-cycled yet, ISP still works: write the correct value immediately.

I recommend using a [fuse calculator](https://www.engbedded.com/fusecalc/) for a better overview and convenient flash command generation.

## Settings for revENG312

I recommend enabling BOD (brown out-detection). This prevents flash memory/EEPROM corruption that happens on rare occasions. Check out this [report](brownout_memory_corruption.md) for more details.

The table below shows the fuses used for MCU with external crystal, SPI and BOD enabled. The BOD threshold is selected with the `BODLEVEL` bit (bit 7) of the low fuse; `0xBF` and `0x3F` differ only in that bit. The high fuse does not depend on the BOD threshold.

| MCU | Bootloader | BOD threshold | lfuse | hfuse | avrdude arguments |
|---|---|---|---|---|---|
| ATmega16A | ❌ no | 2.7 V | `0xBF` | `0xDF` | `-U lfuse:w:0xbf:m -U hfuse:w:0xdf:m` |
| ATmega16A | ❌ no | 4.0 V | `0x3F` | `0xDF` | `-U lfuse:w:0x3f:m -U hfuse:w:0xdf:m` |
| ATmega16A | ✅ yes | 2.7 V | `0xBF` | `0xDC` | `-U lfuse:w:0xbf:m -U hfuse:w:0xdc:m` |
| ATmega16A | ✅ yes | 4.0 V | `0x3F` | `0xDC` | `-U lfuse:w:0x3f:m -U hfuse:w:0xdc:m` |
| _ATmega32A (planned, untested)_ | ❌ no | 2.7 V | `0xBF` | `0xDF` | `-U lfuse:w:0xbf:m -U hfuse:w:0xdf:m` |
| _ATmega32A (planned, untested)_ | ❌ no | 4.0 V | `0x3F` | `0xDF` | `-U lfuse:w:0x3f:m -U hfuse:w:0xdf:m` |
| _ATmega32A (planned, untested)_ | ✅ yes | 2.7 V | `0xBF` | `0xDA` | `-U lfuse:w:0xbf:m -U hfuse:w:0xda:m` |
| _ATmega32A (planned, untested)_ | ✅ yes | 4.0 V | `0x3F` | `0xDA` | `-U lfuse:w:0x3f:m -U hfuse:w:0xda:m` |

### Choosing the BOD threshold (2.7 V or 4.0 V)

Both thresholds protect against the memory corruption described in the [report](brownout_memory_corruption.md). They differ in how much the supply voltage may sag before the MCU is held in reset. Datasheet tolerances: 2.7 V setting = 2.5–2.9 V, 4.0 V setting = 3.7–4.5 V; hysteresis is only about 50 mV.

**2.7 V (`0xBF`): the default choice.**

- At 8 MHz, the ATmega16A/32A is specified down to 2.7 V, so this threshold keeps the MCU itself within its operating range.
- It tolerates short supply dips without a reset, for example load spikes from the output stage, a weak battery, or a noisy supply.
- The drawback: between about 4.5 V and 2.7 V the MCU keeps running while the rest of the 5 V circuitry (LCD, ADC readings referenced to the supply, output stage control) may already misbehave.

**4.0 V (`0x3F`): when you want the device to stop early.**

- The MCU resets as soon as the 5 V rail is clearly out of regulation, so firmware never runs with a sagging supply. EEPROM writes keep a larger voltage margin.
- The drawback: the margin to the nominal 5 V is small. In the worst case the threshold is 4.5 V, only 0.25 V below a 5 V ±5 % rail. Supply ripple, load spikes, or regulator dropout on a low battery can then cause unexpected resets during operation.
- Check your supply first: measure the 5 V rail under load (output running at high levels, battery near empty). Only choose 4.0 V if it stays well above 4.5 V.

If unsure, use 2.7 V. Change to 4.0 V only if your supply is known to be stable, or if you prefer a clean reset over running with a degraded supply.


## Reading and writing fuses with avrdude

In all commands below, replace `-c usbasp` with your programmer (`-c stk500v1 -P COMx -b 19200` for Arduino-as-ISP, `-c atmelice_isp`, …) and `-p m16a` for different MCU (`-p m32a` for ATmega32A).

Read the current values:

```sh
avrdude -c usbasp -p m16a -U lfuse:r:-:h -U hfuse:r:-:h
```

Write (example for ATmega16A with bootloader, BOD at 2.7 V):

```sh
avrdude -c usbasp -p m16a -U lfuse:w:0xBF:m -U hfuse:w:0xDC:m
```

For BOD at 4.0 V, use `-U lfuse:w:0x3F:m` instead.
