# SPDX-License-Identifier: 0BSD
# Copyright (c) 2026, fishYMATe
# Full license text: LICENSES/0BSD.txt

"""
xmodem_crc.py - minimal xmodem-CRC sender
Drop-in replacement for the xmodem PyPI library.

"""

import logging
import time

XMODEM_SOH = 0x01
XMODEM_EOT = 0x04
XMODEM_ACK = 0x06
XMODEM_NAK = 0x15
XMODEM_CAN = 0x18
XMODEM_C   = 0x43

MAX_RETRIES    = 16
BLOCK_SIZE     = 128
TIMEOUT        = 2.0   # seconds per byte read
EOT_RETRIES    = 3
INTER_BLOCK_MS = 0     # ms delay after ACK before sending next block

logger = logging.getLogger('xmodem_crc')


def crc16(data):
    """CRC-16/CCITT, init=0x0000, poly=0x1021."""
    crc = 0x0000
    for b in data:
        crc ^= (b << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


class XmodemCRC:
    def __init__(self, getc, putc):
        """
        getc(size) -> bytes: read up to size bytes from serial
        putc(data) -> int:   write bytes to serial, return bytes written
        """
        self.getc = getc
        self.putc = putc

    def _send_byte(self, b):
        self.putc(bytes([b]))
        logger.debug('TX: 0x%02X', b)

    def _recv_byte(self, timeout=TIMEOUT):
        b = self.getc(1)
        if b:
            logger.debug('RX: 0x%02X', b[0])
            return b[0]
        return None

    def _build_block(self, block_num, payload):
        """Build 133-byte xmodem-CRC block."""
        # Pad payload to BLOCK_SIZE with 0x1A
        payload = payload.ljust(BLOCK_SIZE, b'\x1a')[:BLOCK_SIZE]
        crc = crc16(payload)
        block = bytes([
            XMODEM_SOH,
            block_num & 0xFF,
            (~block_num) & 0xFF,
        ]) + payload + bytes([
            (crc >> 8) & 0xFF,
            crc & 0xFF,
        ])
        return block

    def _wait_for_c(self, timeout=60):
        """Wait for box to advertise 'C' (xmodem-CRC initiation)."""
        logger.debug('Waiting for C...')
        deadline = time.time() + timeout
        while time.time() < deadline:
            b = self._recv_byte(timeout=1)
            if b == XMODEM_C:
                logger.debug('Got C, starting transfer')
                return True
            elif b is not None:
                logger.debug('Waiting for C, got 0x%02X', b)
        logger.error('Timeout waiting for C')
        return False

    def _send_can(self):
        """Send CAN twice to abort."""
        logger.debug('Sending CAN')
        self._send_byte(XMODEM_CAN)
        self._send_byte(XMODEM_CAN)

    def send(self, stream, retry=MAX_RETRIES):
        """
        Send a file-like object via xmodem-CRC.
        Returns True on success, False on failure.
        """
        data = stream.read()
        total_blocks = (len(data) + BLOCK_SIZE - 1) // BLOCK_SIZE
        logger.debug('File size: %d bytes, %d blocks', len(data), total_blocks)

        # Wait for box to advertise C
        if not self._wait_for_c():
            return False

        block_num = 1
        offset = 0

        while offset < len(data):
            payload = data[offset:offset + BLOCK_SIZE]
            block = self._build_block(block_num, payload)

            retries = 0
            while retries < retry:
                logger.debug('send: block %d (attempt %d)', block_num, retries + 1)
                self.putc(block)

                response = self._recv_byte()

                if response == XMODEM_ACK:
                    logger.debug('Block %d ACKed', block_num)
                    break
                elif response == XMODEM_NAK:
                    logger.warning('Block %d NAKed, retrying', block_num)
                    retries += 1
                elif response == XMODEM_CAN:
                    logger.error('CAN received from box, aborting')
                    return False
                elif response is None:
                    logger.warning('Timeout waiting for response to block %d', block_num)
                    retries += 1
                else:
                    logger.warning('Unexpected response 0x%02X to block %d', response, block_num)
                    retries += 1

            else:
                logger.error('Max retries reached on block %d, aborting', block_num)
                self._send_can()
                return False

            if INTER_BLOCK_MS > 0:
                time.sleep(INTER_BLOCK_MS / 1000.0)

            block_num = (block_num + 1) & 0xFF
            offset += BLOCK_SIZE

        # Send EOT
        for attempt in range(EOT_RETRIES):
            logger.debug('Sending EOT (attempt %d)', attempt + 1)
            self._send_byte(XMODEM_EOT)
            response = self._recv_byte()
            if response == XMODEM_ACK:
                logger.debug('EOT ACKed, transfer complete')
                return True
            elif response == XMODEM_CAN:
                logger.error('CAN received after EOT')
                return False
            else:
                logger.warning('No ACK for EOT, retrying')

        logger.error('Failed to get ACK for EOT')
        return False
