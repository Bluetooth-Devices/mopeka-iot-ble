#!/usr/bin/env python3
"""Decode a raw Mopeka BLE advertisement into human-readable sensor values.

This is a thin wrapper around :class:`mopeka_iot_ble.MopekaIOTBluetoothDeviceData`
aimed at people who capture advertisements outside Home Assistant (for example via
nRF Connect, ``bluetoothctl``, or an MQTT gateway / MQTT Explorer) and just want to
see what the bytes mean.

You provide the device address and the manufacturer-specific payload that ships
under Mopeka's company id ``89`` (``0x0059``). That is the value that appears after
the company id in the advertisement's manufacturer data field.

Examples
--------
Decode a Pro Plus advertisement (payload bytes only, any common separator works)::

    python examples/decode_advertisement.py C9:F3:32:E0:F5:09 0872 46 00 c0 e0 f5 09 f0 d8

    python examples/decode_advertisement.py C9:F3:32:E0:F5:09 08:72:46:00:c0:e0:f5:09:f0:d8

Pick the stored medium so the tank level is converted with the right curve::

    python examples/decode_advertisement.py --medium fresh_water \\
        C9:F3:32:E0:F5:09 0872460100e0f509f0d8
"""

from __future__ import annotations

import argparse
import sys

from bluetooth_sensor_state_data import BluetoothServiceInfo

from mopeka_iot_ble import MediumType, MopekaIOTBluetoothDeviceData, SensorUpdate
from mopeka_iot_ble.parser import MOKPEKA_PRO_SERVICE_UUID, MOPEKA_MANUFACTURER


def parse_hex_payload(raw: str) -> bytes:
    """Parse a manufacturer-data payload from a flexible hex string.

    Accepts the byte string with or without ``0x`` / ``\\x`` prefixes and with
    spaces, colons, or dashes as separators, e.g. ``"0872460..."``,
    ``"08 72 46 ..."`` or ``"08:72:46:..."``.
    """
    cleaned = raw.strip().lower()
    for token in (" ", ":", "-", "0x", "\\x"):
        cleaned = cleaned.replace(token, "")
    if not cleaned:
        raise ValueError("empty payload")
    try:
        return bytes.fromhex(cleaned)
    except ValueError as err:
        raise ValueError(f"not a valid hex payload: {raw!r}") from err


def decode(
    address: str, payload: bytes, medium: MediumType, rssi: int = -60
) -> SensorUpdate:
    """Run the Mopeka parser over a single synthetic advertisement."""
    service_info = BluetoothServiceInfo(
        name="",
        address=address,
        rssi=rssi,
        manufacturer_data={MOPEKA_MANUFACTURER: payload},
        service_uuids=[MOKPEKA_PRO_SERVICE_UUID],
        service_data={},
        source="local",
    )
    return MopekaIOTBluetoothDeviceData(medium).update(service_info)


def format_update(update: SensorUpdate) -> str:
    """Render a SensorUpdate as a readable multi-line report."""
    lines: list[str] = []
    for device in update.devices.values():
        lines.append(f"Device : {device.name}")
        lines.append(f"Model  : {device.model}")
        lines.append(f"Maker  : {device.manufacturer}")
    lines.append("")
    lines.append("Sensors:")
    for key, value in update.entity_values.items():
        desc = update.entity_descriptions.get(key)
        unit = desc.native_unit_of_measurement if desc else None
        unit_str = f" {unit}" if unit else ""
        lines.append(f"  {value.name}: {value.native_value}{unit_str}")
    for value in update.binary_entity_values.values():
        lines.append(f"  {value.name}: {value.native_value}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Decode a raw Mopeka BLE advertisement payload.",
    )
    parser.add_argument(
        "address",
        help="device MAC address, e.g. C9:F3:32:E0:F5:09",
    )
    parser.add_argument(
        "payload",
        nargs="+",
        help="manufacturer-data payload (hex), with or without separators",
    )
    parser.add_argument(
        "--medium",
        choices=[m.value for m in MediumType],
        default=MediumType.PROPANE.value,
        help="stored medium used to convert the tank level (default: propane)",
    )
    parser.add_argument(
        "--rssi",
        type=int,
        default=-60,
        help="advertisement RSSI in dBm (default: -60)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = parse_hex_payload(" ".join(args.payload))
    except ValueError as err:
        print(f"error: {err}", file=sys.stderr)
        return 2

    update = decode(args.address, payload, MediumType(args.medium), args.rssi)
    if not update.devices:
        print(
            "error: payload was not recognised as a supported Mopeka "
            "advertisement (wrong length or unknown model byte)",
            file=sys.stderr,
        )
        return 1

    print(format_update(update))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
