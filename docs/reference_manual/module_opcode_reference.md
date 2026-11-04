# revENG312 – Module Instruction Reference

This reference is for anyone writing their own modules. It covers how instructions are encoded, which addresses they may use, how the channel selection changes their effect, and which errors to expect. It belongs to the [revENG312 Reference Manual](README.md#8-module-system).

---

## 1. Overview

A module is a sequence of instructions followed by a terminator. Every built-in and user routine consists of one or more modules; modules are also loaded by audio and timer triggers, and a module can load another module when a condition is met (section 7).

- Instructions are executed one after the other while the module is read. If an error stops the firmware, all instructions before the faulty one have already been executed.
- A module may be at most **256 bytes** long, including the terminator (error 51 otherwise). A module without a terminator ends this way.
- Every instruction is applied exactly once per channel (section 3).

### Instruction lengths

| Instruction | Length (bytes) |
|-------------|----------------|
| Terminator | 1 |
| SET | 2 |
| COPY | 2 + N (N = 1 to 7 values) |
| STORE, LOAD, DIV2, RAND | 2 |
| ADD, AND, OR, XOR | 3 |
| CONDEXEC | 2 |

### Writing a module in short

1. Choose the addresses you want to change (section 2).
2. Encode each instruction (sections 4 and 5).
3. End the module with a terminator byte `00`.
4. Store it under a module number (section 8). To test it from the scratchpad, see [Execute Commands, section 7.1](execute_commands.md#71-running-a-user-module-from-the-scratchpad).

---

## 2. Memory and Addresses

### 2.1 Address notation

Addresses in this manual are the raw addresses as used inside instructions: 10 bits, `0x000`-`0x3FF`. The memory map and serial link documentation show RAM addresses with a virtual `0x4000` base. For example, `0x0085` appears there as `0x4085`.

- Address `0x0Hll`: the digit `H` (0-3) is added to the **opcode**, and `ll` is the **first operand byte**. Example: `0x018C` is stored as `H = 1` in the opcode and `8C` as operand.
- SET is encoded differently (see section 5).

**Low addresses** are `0x0000`-`0x00FF` and `0x0200`-`0x02FF`. **High addresses** are `0x0100`-`0x01FF` and `0x0300`-`0x03FF`.

- Low addresses are relative to the channel being processed.
- High addresses always refer to channel B.

Section 3 explains this in detail.

### 2.2 Valid ranges

| Range | Access | Notes |
|-------|--------|-------|
| `0x0000`-`0x005F` | none | any access raises error 53 |
| `0x0060`-`0x007F` | read | |
| `0x0080`-`0x00BF` | read / write | channel A configuration values (ramp, intensity, width, frequency, ...) |
| `0x00C0`-`0x017F` | read | contains the scratchpad data area |
| `0x0180`-`0x01BF` | read / write | channel B configuration values (same layout as channel A) |
| `0x01C0`-`0x03FF` | read | |

- **Write instructions** (SET, COPY, LOAD, DIV2, RAND, ADD, AND, OR, XOR) may only write to `0x0080`-`0x00BF` and `0x0180`-`0x01BF`.
- **STORE and CONDEXEC** may read from `0x0060` to `0x03FF`.
- Any other access stops the firmware with error 53.
- The check is made on the address as written in the instruction, before the channel selection shifts it (section 3).
- Writing the channel blocks (`0x0090`-`0x00BF`, `0x0190`-`0x01BF`) is always safe. Writing the channel headers (`0x0080`-`0x008F`, `0x0180`-`0x018F`) can have unexpected effects in rare combinations, because the firmware also uses some of these locations for other purposes.

The meaning of the individual addresses is described in the [Memory Map](memory_map.md#3-ram-in-detail).

### 2.3 Special addresses

| Address | Purpose |
|---------|---------|
| `0x0084` | Module to load when a condition is met. This is the only place where this module number can be stored; the high counterpart `0x0184` has no such function. |
| `0x0085` | Channel selection for module instructions. This address is never redirected (section 3). |
| `0x008C` / `0x018C` | Module accumulator, channel A / B |
| `0x008D` / `0x008E` | Random number, minimum / maximum |

The accumulator is an ordinary one-byte memory location. Besides STORE, LOAD and CONDEXEC, it can also be written directly with SET, COPY, ADD and so on.

---

## 3. Channel Selection

The setting at `0x0085` decides which channel an instruction acts on:

| Value | Meaning |
|-------|---------|
| `0x00` | no channel: every instruction is skipped (the module is still read up to the terminator; CONDEXEC cannot fire) |
| `0x01` | apply to A |
| `0x02` | apply to B |
| `0x03` | apply to both (normal behavior) |

It is reset to "apply to both" when a module ends and after a conditional load has finished. A module can also change it itself by writing `0x0085`; this address is never redirected, so it works under every selection.

### How an instruction is executed

1. The instruction's address is taken as written. Together with it, the accumulator of channel A (`0x008C`) is prepared.
2. If **apply to B** is selected, the address is replaced by its high counterpart (bit 8 is set: `0x0090` becomes `0x0190`, and a high address stays as it is) and the channel B accumulator (`0x018C`) is used. The only exception is address `0x0085` itself, which is left unchanged.
3. The instruction is executed on that address.
4. If the address is a high address, or if apply to both is not selected, the instruction is finished.
5. Otherwise (apply to both, low address) it is executed a second time with the high counterpart of the address and the channel B accumulator.

The selection is read before each instruction and again after each execution, so a write to `0x0085` takes effect immediately.

### Overview

| `0x0085` | Low address | High address |
|----------|-------------|--------------|
| `0x01` apply to A | Channel A value and accumulator | Channel B value, channel A accumulator |
| `0x02` apply to B | Channel B value and accumulator | Channel B value and accumulator |
| `0x03` apply to both | Channel A and channel B values, each with its own accumulator | Channel B value, channel A accumulator |

### Consequences

1. **Apply to both, low address:** the instruction runs twice, first on A, then on B.
2. **High address:** the instruction runs exactly once on that address, whatever the selection (except `0x00`). A module running with "apply to A" can therefore still write channel B through a high address.
3. **Accumulator with high addresses:** channel A's accumulator is used for a high address under apply to A and apply to both. Channel B's accumulator is used under apply to B, and in the second run under apply to both. STORE, LOAD and CONDEXEC with a high address therefore work with the A accumulator in those modes.
4. **Apply to B shifts everything:** all addresses except `0x0085` are shifted, including read addresses and the common registers below `0x008C`. Because `0x0085` is never redirected, a module can switch the selection within the same module, for example back to apply to both after a section that was applied to channel B only.
5. **Module number for CONDEXEC:** it can only be stored at `0x0084`. Under apply to B, a write to `0x0084` ends up at `0x0184`, which has no such function. Switch the selection first by writing `0x0085`, then write `0x0084`.
6. **Second run under apply to both:** every address is shifted, so a write to a register below `0x008C` (such as `0x0084`) also writes its high counterpart.
7. **RAND** draws a separate random number per run, so channels A and B receive different values.
8. **CONDEXEC** checks channel A first and loads the module on a match; otherwise channel B is checked.

### Compared to the original firmware

- On the original firmware an instruction could be applied to the same value up to four times, so `ADD 1` could add 4. In revENG312 each instruction is applied exactly once per channel.
- The valid address ranges (section 2.2) and error codes 51 to 55 are new in revENG312.

---

## 4. Opcode Overview

| Opcode | Bits | Instruction | Bytes | Operands |
|--------|------|-------------|-------|----------|
| `0x00`-`0x1F` | `000x xxxx` | Terminator | 1 | none |
| `0x20`-`0x3F` | `001L LLAA` | COPY | 2 + N | address low byte, N values |
| `0x40`-`0x43` | `0100 00AA` | STORE | 2 | address low byte |
| `0x44`-`0x47` | `0100 01AA` | LOAD | 2 | address low byte |
| `0x48`-`0x4B` | `0100 10AA` | DIV2 | 2 | address low byte |
| `0x4C`-`0x4F` | `0100 11AA` | RAND | 2 | address low byte |
| `0x50`-`0x53` | `0101 00AA` | ADD | 3 | address low byte, value |
| `0x54`-`0x57` | `0101 01AA` | AND | 3 | address low byte, value |
| `0x58`-`0x5B` | `0101 10AA` | OR | 3 | address low byte, value |
| `0x5C`-`0x5F` | `0101 11AA` | XOR | 3 | address low byte, value |
| `0x60`-`0x6F` | `0110 xxAA` | unused | 2 | address low byte |
| `0x70`-`0x73` | `0111 00AA` | CONDEXEC | 2 | address low byte |
| `0x74`-`0x7F` | `0111 xxAA` (xx not 00) | unused | 2 | address low byte |
| `0x80`-`0xBF` | `10oo oooo` | SET, low address | 2 | value |
| `0xC0`-`0xFF` | `11oo oooo` | SET, high address | 2 | value |

Legend: `L` = number of values to copy, `A` = address bits 9-8 (the digit `H` of `0x0Hll`), `o` = address offset, `x` = any value.

---

## 5. Instruction Reference

Notation: `<address>` is a full address such as `0x008C`, `<value>` is one byte.

### Terminator

**Opcodes** `0x00`-`0x1F`, 1 byte. Always use `00`; all values in the range behave the same. Ends the module.

### SET `<address>`, `<value>`

Writes `<value>` to `<address>`.

- **Encoding:** 2 bytes: opcode, value.
- **Opcode:** for a low address (`0x0080`-`0x00BF`) it equals the low byte of the address (`0x80`-`0xBF`); for a high address (`0x0180`-`0x01BF`) it is the low byte plus `0x40` (`0xC0`-`0xFF`).
- **Restriction:** none; the encoding cannot leave the writable range.

### COPY `<address>`, `<v1>` ... `<vN>`

Writes N bytes to consecutive addresses starting at `<address>`.

- **Encoding:** `0x20 + 4*N + H`, address low byte, N values. N is 1 to 7.
- **Restriction:** the first and the last address must lie in the writable range. N = 0, or a copy that would run past the end of the range (for example from `0x00BF` into `0x00C0`), raises error 54.

### STORE `<address>`

Copies the value at `<address>` into the module accumulator.

- **Encoding:** `0x40 + H`, address low byte.
- **Restriction:** read range (`0x0060`-`0x03FF`).

### LOAD `<address>`

Copies the module accumulator to `<address>`.

- **Encoding:** `0x44 + H`, address low byte.
- **Restriction:** write range.

### DIV2 `<address>`

Divides the value at `<address>` by two (shifts right one bit, rounding down; `0x03` becomes `0x01`).

- **Encoding:** `0x48 + H`, address low byte.
- **Restriction:** write range.

### RAND `<address>`

Writes a random number between the minimum (`0x008D`) and the maximum (`0x008E`), both included, to `<address>`. The limits always come from these two addresses; there are no separate limits for channel B.

- **Encoding:** `0x4C + H`, address low byte.
- **Restriction:** write range.
- **Equal limits:** if minimum and maximum are equal, that value is written.
- **Swapped limits:** if the minimum is greater than the maximum, the two are swapped.
- **Distribution:** the number is a random byte modulo the size of the range, so the values are not perfectly evenly distributed unless the size of the range divides 256.

### ADD, AND, OR, XOR `<address>`, `<value>`

Combine the value at `<address>` with `<value>` and store the result at `<address>`. All operations work on one unsigned byte.

| Instruction | Opcode base | Effect |
|-------------|-------------|--------|
| ADD | `0x50` | adds the value; wraps around past `0xFF`, no clamping |
| AND | `0x54` | bitwise AND |
| OR | `0x58` | bitwise OR |
| XOR | `0x5C` | bitwise XOR |

- **Encoding:** base + H, address low byte, value.
- **Restriction:** write range.
- **Subtracting:** there is no subtract instruction. To subtract n, ADD (256 - n).

### CONDEXEC `<address>`

If the value at `<address>` equals the module accumulator, execution of the current module stops and the module from `0x0084` is loaded instead (section 7).

- **Encoding:** `0x70 + H`, address low byte.
- **Restriction:** read range.

### Unused opcodes

`0x60`-`0x6F` and `0x74`-`0x7F` have no function. The firmware still checks their address as for a write instruction (error 53 if outside the writable range) and otherwise ignores them. Do not use them.

---

## 6. Encoding Examples

```
98 3F        SET 0x0098, 0x3F        selected channel(s)
D8 3F        SET 0x0198, 0x3F        channel B only (high address)
24 8C 01     COPY 0x008C, 01         1 value
28 8C 01 02  COPY 0x008C, 01 02      2 values
40 8C        STORE 0x008C
44 8C        LOAD 0x008C
48 8C        DIV2 0x008C
4C 8C        RAND 0x008C
50 8C 10     ADD 0x008C, 0x10
51 8C 10     ADD 0x018C, 0x10        high address: H = 1
54 8C 0F     AND 0x008C, 0x0F
58 8C 80     OR 0x008C, 0x80
5C 8C FF     XOR 0x008C, 0xFF
41 05        STORE 0x0105
70 A0        CONDEXEC 0x00A0
00           terminator
```

Errors:

```
50 40 01     ADD 0x0040, 0x01        error 53: outside the writable range
40 20        STORE 0x0020            error 53: below 0x0060
20 8C        COPY with N = 0         error 54
```

### Example module: conditional load

Load module 5 if the value at `0x00A0` equals `0x10`:

```
84 05        SET 0x0084, 0x05        module to load on condition
8C 10        SET 0x008C, 0x10        accumulator = 0x10
70 A0        CONDEXEC 0x00A0         load module 5 if (0x00A0) = accumulator
00           terminator
```

Under apply to both, the SET instructions set both accumulators, and CONDEXEC compares `0x00A0` with the A accumulator and `0x01A0` with the B accumulator.

### Example module: switching the selection

```
85 02        SET 0x0085, 0x02        apply to B
90 10        SET 0x0090, 0x10        written to 0x0190 (channel B only)
85 03        SET 0x0085, 0x03        back to apply to both (0x0085 is never redirected)
84 05        SET 0x0084, 0x05        written to 0x0084 (and 0x0184, which has no function)
00           terminator
```

`0x0090` is an example address.

---

## 7. Conditional Loading (CONDEXEC)

When the condition is met, execution of the current module stops and the module whose number is stored at `0x0084` is loaded in its place. CONDEXEC is therefore a conditional **jump** to another module, not a call: the remaining instructions of the module containing it are never executed, and there is no return into it.

- The module number is read at the moment CONDEXEC fires, so earlier instructions of the same module can set it.
- The loaded module runs with the current channel selection.
- Under apply to both, channel A is checked first. If it matches, the module is loaded immediately; otherwise channel B is checked.
- After the loaded module has finished, the channel selection is reset to apply to both.
- The loaded module can itself contain a CONDEXEC. Up to three conditional loads may follow each other; a fourth raises error 52. The limit prevents a stack overflow in the firmware: each conditional load is processed while the previous one is still active on the stack.

---

## 8. Storing Modules

Module number -> location (all addresses raw):

| Module number | Location | Start vector table | Data area |
|---------------|----------|--------------------|-----------|
| `0x00`-`0x23` (0-35) | built-in routines, flash | table in flash; entries are word offsets | start = module data + 2 x entry |
| `0x80`-`0x9F` | user bank A, EEPROM | `0x020`-`0x03F` | EEPROM `0x040`-`0x0FF` |
| `0xA0`-`0xBF` | user bank B, EEPROM | `0x100`-`0x11F` | EEPROM `0x120`-`0x1FF` |
| `0xC0`-`0xDF` | scratchpad, RAM | `0x01D0`-`0x01EF` | RAM `0x00C0`-`0x017F` |
| all others | invalid | | error 15 |

**Start of a user module:**

The start vector table holds one byte per module: the offset of that module within the data area. The entries follow the module numbers in order. In bank A, entry `0x020` holds the offset of module `0x80`, entry `0x021` the offset of module `0x81`, and so on up to entry `0x03F` for module `0x9F`. Bank B (entry `0x100` for module `0xA0`) and the scratchpad (entry `0x01D0` for module `0xC0`) work the same way.

- A module starts at the **start of its data area plus the offset from its table entry**. Example: module `0x81` has the offset `0x10` in entry `0x021`, so it starts at EEPROM address `0x040 + 0x10 = 0x050`.
- To store a module: write its bytes into the data area, then write the offset where they start into the table entry of its module number.
- A start vector that points outside the data area, or a module that runs on beyond its end, raises error 55.

---

## 9. Error Codes (Quick Reference)

Errors in modules are shown on the failure screen with their error code (see the [Reference Manual, section 4](README.md#4-self-test-and-failure-screen)). Instructions before the faulty one have already been executed.

| Code | Name | Meaning |
|------|------|---------|
| 15 | Module | Invalid module number when loading a module |
| 51 | Module block | Module data exceeds the maximum module size (256 bytes, e.g. missing terminator) |
| 52 | Module nesting | Too many nested modules (maximum 3) |
| 53 | Module address | Instruction address outside the permitted range (section 2.2) |
| 54 | Module copy | COPY instruction has an invalid length or overflows the permitted address range |
| 55 | Module offset | Module offset leads outside the module's memory area |