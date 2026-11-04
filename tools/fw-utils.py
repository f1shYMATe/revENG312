#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2016, The Buttshock Project
# Copyright (c) 2026, fishYMATe (modifications)
# Full license text: LICENSES/BSD-3-Clause.txt
#
# Based on scripts/fw-utils.py from
# https://github.com/teledildonics/buttshock-et312-firmware
#
# Changes: custom xmodem_crc uploader, configurable image size/baud rate,
#          removed firmware downloader

import argparse
import copy
import logging
import sys

class ET312FirmwareUtils(object):

    KEYS = [0x65, 0xed, 0x83]
    IV = [0xb9, 0xfe, 0x8f]

    def __init__(self, input_file, output_file=None, size=15872):
        self.size = size
        self.iv = copy.copy(ET312FirmwareUtils.IV)
        with open(input_file, "rb") as f:
            self.input_file = bytearray(f.read())
        self.fill_space()
        self.output_file = open(output_file, "wb") if output_file else None

    def close(self):
        if self.output_file:
            self.output_file.close()

    def generate_crc(self):
        xor = 0
        add = 0
        for c in range(self.size - 16):
            xor ^= self.input_file[c]
            add += self.input_file[c]
        return [xor, (add & 0xff), ((add >> 8) & 0xff)]

    def encrypt(self, write_crc=True):
        funcs = {0: lambda x: ((x - 0x41 if x >= 0x41
                                else ((x - 0x41) + 0x100)) ^ 0x62) & 0xff,
                 1: lambda x: (x >> 4) | ((x & 0x0f) << 4),
                 2: lambda x: x}

        if write_crc:
            crc = self.generate_crc()
            for i in range(3):
                self.input_file[-16 + i] = crc[i]

        for i in range(0, len(self.input_file)):
            n = self.input_file[i]
            choice = i % 3
            output = funcs[choice](n ^ self.iv[choice] ^ self.KEYS[choice])
            self.output_file.write(bytearray([output]))
            self.iv[choice] = output

    def decrypt(self):
        funcs = {0: lambda x: ((x ^ 0x62) + 0x41) & 0xff,
                 1: lambda x: (x >> 4) | ((x & 0x0f) << 4),
                 2: lambda x: x}

        for i in range(0, len(self.input_file)):
            n = self.input_file[i]
            choice = i % 3
            output = funcs[choice](n) ^ self.iv[choice] ^ self.KEYS[choice]
            self.output_file.write(bytearray([output]))
            self.iv[choice] = n

    def fill_space(self):
        if len(self.input_file) > self.size:
            raise ValueError("Input is %d bytes, larger than image size %d"
                             % (len(self.input_file), self.size))
        self.input_file += bytearray([0] * (self.size - len(self.input_file)))

    def upload(self, port, baudrate=19200):
        import serial
        from xmodem_crc import XmodemCRC
        import io

        s = serial.Serial(port, baudrate, timeout=1,
                          parity=serial.PARITY_NONE,
                          bytesize=8, stopbits=1,
                          xonxoff=0, rtscts=0)

        def getc(size, timeout=1):
            return s.read(size)

        def putc(data, timeout=1):
            return s.write(data)

        modem = XmodemCRC(getc, putc)
        try:
            return modem.send(io.BytesIO(self.input_file))
        finally:
            s.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", dest="input_file",
                        help="File to take action on")
    parser.add_argument("-o", "--output", dest="output_file",
                        help="File to output, if needed by action")
    parser.add_argument("-d", "--decrypt", dest="decrypt", action="store_true",
                        help="Decrypt input file, store in output file")
    parser.add_argument("-e", "--encrypt", dest="encrypt", action="store_true",
                        help="Encrypt input file, store in output file."
                        " Adds checksum to output by default.")
    parser.add_argument("-u", "--upload", dest="upload",
                        help="Upload input file to box, expects com port as " +
                        "argument. (requires the pyserial package)")
    parser.add_argument("-c", "--crc", dest="crc", action="store_true",
                        help="Output xor/checksum for input file")
    parser.add_argument("-b", "--baudrate", dest="baudrate", type=int, default=19200,
                        help="Baud rate for upload (default: 19200)")
    parser.add_argument("-s", "--size", dest="size", type=lambda x: int(x, 0), default=15872,
                        help="Firmware image size in bytes (e.g. 30720 or 0x7800, default: 15872)")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true",
                        help="Log every byte exchanged during upload")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING)

    if not args.input_file:
        print("ERROR: Input file required to run.")
        parser.print_help()
        return 1

    if (args.decrypt or args.encrypt) and not args.output_file:
        print("ERROR: Output file required for encryption/decryption.")
        parser.print_help()
        return 1

    etfw = ET312FirmwareUtils(args.input_file, args.output_file, args.size)
    try:
        if args.encrypt:
            etfw.encrypt()
        elif args.decrypt:
            etfw.decrypt()
        elif args.upload:
            if not etfw.upload(args.upload, args.baudrate):
                print("ERROR: Upload failed.")
                return 1
            print("Upload complete.")
        elif args.crc:
            print(["0x%.02x" % x for x in etfw.generate_crc()])
    finally:
        etfw.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
