# AVR BOD EEPROM Corruption — Empirical Confirmation

## Background

Brown-Out Detection (BOD) on AVR devices exists partly to prevent EEPROM corruption during power loss. The ATmega16 EEPROM write cycle is atomic erase+write (~8ms), triggered by setting EEMWE followed by EEWE in EECR. If power drops mid-cycle, the erase phase may complete while the write phase does not, leaving the cell at 0xFF. BOD is supposed to reset the MCU before this can happen. This test confirms that behaviour empirically.

## Test Setup

**Hardware:** ATmega16  
**EEPROM size:** 512 bytes (0x000–0x1FF)

A small firmware binary was written that:
1. Displays "Boot okay" and the reset value of EEAR on an LCD
2. Sets EEAR to a known target address (0x17)
3. Enters a while(1) LED toggle loop

The remainder of the 16KB flash was padded with a repeating EEPROM write sequence:

```
e1 99  ; sbic 0x1c, 1   — poll EEWE (wait for previous write)
fe cf  ; rjmp .-4        — loop until ready
e2 9a  ; sbi  0x1c, 2   — set EEMWE (master write enable)
e1 9a  ; sbi  0x1c, 1   — set EEWE  (trigger write)
```

This padding never executes under normal conditions — the while(1) loop holds the PC. It only becomes relevant if the PC goes haywire during an uncontrolled brownout.

The entire EEPROM was pre-filled with 0x17 before each test run, so any 0xFF result is unambiguously a corruption event and not an uninitialised cell.

## EEAR Reset Value

Reading EEAR at the top of main (before any other code) showed **0x03FF** in most test runs. The ATmega16 datasheet does not guarantee a reset value for EEAR, and this should not be relied upon. With EEARH masked to 1 bit, 0x03FF translates to address 0x01FF — the last valid byte of the 512-byte EEPROM. This is why earlier tests without a controlled EEAR value showed corruption at byte 511, and also why explicitly setting EEAR to a known address is essential for a controlled test — an out-of-range value would cause rogue writes to be silently ignored by the hardware.

## Results

| Condition | EEPROM byte 0x17 after power cut |
|---|---|
| No padding in flash, BOD disabled | 0x17 — intact |
| Padding present, BOD enabled | 0x17 — intact |
| Padding present, BOD disabled | **0xFF — corrupted** |

Observed EEPROM dump (padding present, BOD disabled):

```
17 17 17 17 17 17 17 17 17 17 17 17 17 17 17 17
17 17 17 17 17 17 17 FF 17 17 17 17 17 17 17 17
```

Byte at address 0x17 erased to 0xFF, all surrounding bytes intact.

## Conclusions

1. **BOD prevents EEPROM corruption during power loss.** With BOD enabled, the MCU is held in reset before the supply falls into the danger zone, and no corruption is observed.

2. **Without BOD, an uncontrolled brownout causes the PC to run into flash padding.** The no-padding control test shows that a wandering PC alone is not sufficient — there must be EEMWE/EEWE sequences in flash for corruption to occur. The padding provides those sequences, and corruption is reliably reproduced.

3. **The erase-without-write mechanism is confirmed.** The corrupted cell reads 0xFF, consistent with the erase phase completing and the write phase not completing before power was lost.
