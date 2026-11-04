# Flashing with an ISP programmer

You need an ISP programmer (USBasp, Arduino-as-ISP, AVRISP mkII, Atmel-ICE, …), [avrdude](https://github.com/avrdudes/avrdude), and access to the ISP header on the board.

In all commands below, replace `-c usbasp` with your programmer (`-c stk500v1 -P COMx -b 19200` for Arduino-as-ISP, `-c atmelice_isp`, …) and `-p m16a` for different MCU (`-p m32a` for ATmega32A).

### Before you start:

1. You could **back up the original firmware**, but only if the chip is not read-protected. If you didn't build the device yourself, chances are high that this won't work. If it is locked, the read returns garbage — that's expected.
   ```sh
   avrdude -c usbasp -p m16a -U flash:r:original_flash.bin:r -U eeprom:r:original_eeprom.bin:r
   ```
2. **Note the current fuses** — also see [fuses.md](fuses.md#reading-and-writing-fuses-with-avrdude).
   ```sh
   avrdude -c usbasp -p m16a -U lfuse:r:-:h -U hfuse:r:-:h
   ```


## A) Install the bootloader

*Recommended. One-time ISP session; all later updates go over the serial port.*

1. Pick a bootloader build — see [bootloader.md](bootloader.md#three-bootloader-builds--pick-one).
2. Set the fuses to enable bootloader — according [fuses.md](fuses.md):
   ```sh
   avrdude -c usbasp -p m16a -U lfuse:w:<desired_value>:m -U hfuse:w:<desired_value>:m
   ```
3. Erase the chip & flash the bootloader:
   ```sh
   avrdude -c usbasp -p m16a -e -U flash:w:firmware/bootloader/m16a/revENG312_bootloader_m16a_19200_v1.1.hex:i
   ```
   The `.hex` file carries its own load address (e.g. `0x3E00`), so it lands in the boot section. Always use the `.hex` here — never convert it to `.bin`.

4. Disconnect the programmer and continue with [updating.md](updating.md) to upload the application.

**Expected result:** the flash now contains only the bootloader. With no valid application present, the device stays in update mode after power-on (both LEDs blinking simultaneously).

> **Note** ISP programming always erases the whole flash (and the EEPROM unless `EESAVE` fuse is programmed) — that is how the AVR serial programming protocol works. So the application is gone after this step, regardless of programmer. This is why the application is installed *afterwards*, through the bootloader.

## B) Flash the application only (no bootloader)

*For people who always have a programmer at hand and want no bootloader.*

1. Set the fuses for the application-only configuration  — see [fuses.md](fuses.md).
   ```sh
   avrdude -c usbasp -p m16a -U lfuse:w:<desired_value>:m -U hfuse:w:<desired_value>:m
   ```
2. Erase the chip & flash the plain binary:
   ```sh
   avrdude -c usbasp -p m16a -e -U flash:w:firmware/mk312/m16a/revENG312_mk312_m16a_1.0.00b.bin:r
   ```
