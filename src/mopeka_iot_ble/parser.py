"""
Parser for Gmopeka_iot BLE advertisements.

Thanks to https://github.com/spbrogan/mopeka_pro_check for
help decoding the advertisements.

MIT License applies.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from bluetooth_data_tools import short_address
from bluetooth_sensor_state_data import BluetoothData
from home_assistant_bluetooth import BluetoothServiceInfo
from sensor_state_data import (
    BinarySensorDeviceClass,
    SensorDeviceClass,
    SensorLibrary,
    Units,
)

from .models import MediumType

_LOGGER = logging.getLogger(__name__)


# converting sensor value to height
MOPEKA_TANK_LEVEL_COEFFICIENTS = {
    MediumType.PROPANE: (0.573045, -0.002822, -0.00000535),
    MediumType.AIR: (0.153096, 0.000327, -0.000000294),
    MediumType.FRESH_WATER: (0.600592, 0.003124, -0.00001368),
    MediumType.WASTE_WATER: (0.600592, 0.003124, -0.00001368),
    MediumType.LIVE_WELL: (0.600592, 0.003124, -0.00001368),
    MediumType.BLACK_WATER: (0.600592, 0.003124, -0.00001368),
    MediumType.RAW_WATER: (0.600592, 0.003124, -0.00001368),
    MediumType.GASOLINE: (0.7373417462, -0.001978229885, 0.00000202162),
    MediumType.DIESEL: (0.7373417462, -0.001978229885, 0.00000202162),
    MediumType.LNG: (0.7373417462, -0.001978229885, 0.00000202162),
    MediumType.OIL: (0.7373417462, -0.001978229885, 0.00000202162),
    MediumType.HYDRAULIC_OIL: (0.7373417462, -0.001978229885, 0.00000202162),
}

MOPEKA_MANUFACTURER = 89
MOPEKA_M1001_MANUFACTURER = 13
MOKPEKA_PRO_SERVICE_UUID = "0000fee5-0000-1000-8000-00805f9b34fb"
MOPEKA_M1001_SERVICE_UUID = "0000ada0-0000-1000-8000-00805f9b34fb"
M1001_ADV_LENGTH = 23  # M1001 advertisement data length (excluding trailing MAC bytes)


@dataclass
class MopekaDevice:
    model: str
    name: str
    adv_length: int


DEVICE_TYPES = {
    0x2: MopekaDevice("M1001", "M1001", M1001_ADV_LENGTH),
    0x3: MopekaDevice("M1017", "Pro Check", 10),
    0x4: MopekaDevice("Pro-200", "Pro-200", 10),
    0x5: MopekaDevice("Pro H20", "Pro Check H2O", 10),
    0x6: MopekaDevice("M1017", "Lippert BottleCheck", 10),
    0x8: MopekaDevice("M1015", "Pro Plus", 10),
    0x9: MopekaDevice("M1015", "Pro Plus with Cellular", 10),
    0xA: MopekaDevice("TD40/TD200", "TD40/TD200", 10),
    0xB: MopekaDevice("TD40/TD200", "TD40/TD200 with Cellular", 10),
    0xC: MopekaDevice("M1017", "Pro Check Universal", 10),
}


def hex(data: bytes) -> str:
    """Return a string object containing two hexadecimal digits for each byte in the instance."""
    return "b'{}'".format("".join(f"\\x{b:02x}" for b in data))


def battery_to_voltage(battery: int) -> float:
    """Convert battery value to voltage"""
    return battery / 32.0


def battery_to_percentage(battery: int) -> float:
    """Convert battery value to percentage."""
    return round(max(0, min(100, (((battery / 32.0) - 2.2) / 0.65) * 100)), 1)


def temp_to_celsius(temp: int) -> int:
    """Convert temperature value to celsius."""
    return temp - 40


def tank_level_to_mm(tank_level: int) -> int:
    """Convert tank level value to mm."""
    return tank_level * 10


def tank_level_and_temp_to_mm(
    tank_level: int, temp: int, medium: MediumType = MediumType.PROPANE
) -> int:
    """Get the tank level in mm for a given fluid type."""
    coefs = MOPEKA_TANK_LEVEL_COEFFICIENTS[medium]
    return int(tank_level * (coefs[0] + (coefs[1] * temp) + (coefs[2] * (temp**2))))


class MopekaIOTBluetoothDeviceData(BluetoothData):
    """Data for Mopeka IOT BLE sensors."""

    def __init__(self, medium_type: MediumType = MediumType.PROPANE) -> None:
        super().__init__()
        self._medium_type = medium_type

    def _start_update(self, service_info: BluetoothServiceInfo) -> None:
        """Update from BLE advertisement data."""
        _LOGGER.debug(
            "Parsing Mopeka IOT BLE advertisement data: %s, MediumType is: %s",
            service_info,
            self._medium_type,
        )
        manufacturer_data = service_info.manufacturer_data
        service_uuids = service_info.service_uuids
        address = service_info.address

        # Check for M1001 (uses manufacturer ID 13 and different service UUID)
        if (
            MOPEKA_M1001_MANUFACTURER in manufacturer_data
            and MOPEKA_M1001_SERVICE_UUID in service_uuids
        ):
            self._parse_m1001(manufacturer_data, address)
            return

        # Check for standard Mopeka devices (manufacturer ID 89)
        if MOPEKA_MANUFACTURER not in manufacturer_data or (
            MOKPEKA_PRO_SERVICE_UUID not in service_uuids
        ):
            _LOGGER.debug("Not a Mopeka IOT BLE advertisement: %s", service_info)
            return

        self._parse_standard(manufacturer_data, address)

    def _parse_m1001(self, manufacturer_data: dict[int, bytes], address: str) -> None:
        """
        Parse M1001 advertisement data.

        M1001 uses a different protocol with manufacturer ID 13 and a 23-byte
        advertisement format (plus 3 bytes for MAC suffix, totaling 26 bytes).
        """
        data = manufacturer_data[MOPEKA_M1001_MANUFACTURER]

        # M1001 data format (23+ bytes):
        # Byte 0: Header (0x00)
        # Byte 1: Device type (0x02 for M1001)
        # Byte 2: Battery (raw value, different formula than standard)
        # Byte 3: Temperature
        # Bytes 4-5: Tank level (14-bit) + quality (2-bit)
        # Bytes 6+: Additional sensor data
        # Last 3 bytes: MAC address suffix

        model_num = data[1]  # Device type is in byte 1 for M1001
        if not (device_type := DEVICE_TYPES.get(model_num)):
            _LOGGER.debug("Unsupported M1001 device type: 0x%02x", model_num)
            return

        if len(data) < M1001_ADV_LENGTH:
            _LOGGER.debug(
                "M1001 advertisement too short: %d bytes (expected >= %d)",
                len(data),
                M1001_ADV_LENGTH,
            )
            return

        self.set_device_manufacturer("Mopeka IOT")
        self.set_device_type(device_type.model)
        self.set_device_name(f"{device_type.name} {short_address(address)}")

        # Battery: M1001 uses different encoding
        # Formula derived from observed values: (raw - 50) / 32
        battery_raw = data[2]
        battery_voltage = (battery_raw - 50) / 32
        battery_percentage = round(
            max(0, min(100, ((battery_voltage - 2.2) / 0.65) * 100)), 1
        )

        # Temperature: byte 3
        temp = data[3] & 0x7F
        button_pressed = bool(data[3] & 0x80)
        temp_celsius = temp_to_celsius(temp)

        # Tank level: bytes 4-5 (14-bit little-endian) + quality (2-bit)
        tank_level = ((int(data[5]) << 8) + data[4]) & 0x3FFF
        reading_quality = data[5] >> 6
        tank_level_mm = tank_level_and_temp_to_mm(tank_level, temp, self._medium_type)

        self.update_predefined_sensor(SensorLibrary.TEMPERATURE__CELSIUS, temp_celsius)
        self.update_predefined_sensor(
            SensorLibrary.BATTERY__PERCENTAGE, battery_percentage
        )
        self.update_predefined_sensor(
            SensorLibrary.VOLTAGE__ELECTRIC_POTENTIAL_VOLT,
            battery_voltage,
            name="Battery Voltage",
            key="battery_voltage",
        )
        self.update_predefined_binary_sensor(
            BinarySensorDeviceClass.OCCUPANCY,
            button_pressed,
            key="button_pressed",
            name="Button pressed",
        )
        self.update_sensor(
            "tank_level",
            Units.LENGTH_MILLIMETERS,
            tank_level_mm if reading_quality >= 1 else None,
            SensorDeviceClass.DISTANCE,
            "Tank Level",
        )
        self.update_sensor(
            "reading_quality_raw",
            None,
            reading_quality,
            None,
            "Reading quality raw",
        )
        self.update_sensor(
            "reading_quality",
            Units.PERCENTAGE,
            round(reading_quality / 3 * 100),
            None,
            "Reading quality",
        )
        # Reading stars = (3-reading_quality) * "★" + (reading_quality * "⭐")

    def _parse_standard(
        self, manufacturer_data: dict[int, bytes], address: str
    ) -> None:
        """Parse standard Mopeka advertisement data (Pro, Pro Plus, etc.)."""
        data = manufacturer_data[MOPEKA_MANUFACTURER]
        model_num = data[0]
        if not (device_type := DEVICE_TYPES.get(model_num)):
            _LOGGER.debug(
                "Unsupported Mopeka IOT BLE advertisement: model 0x%02x", model_num
            )
            return
        adv_length = device_type.adv_length
        if len(data) != adv_length:
            return

        self.set_device_manufacturer("Mopeka IOT")
        self.set_device_type(device_type.model)
        self.set_device_name(f"{device_type.name} {short_address(address)}")
        battery = data[1]
        battery_voltage = battery_to_voltage(battery)
        battery_percentage = battery_to_percentage(battery)
        button_pressed = bool(data[2] & 0x80 > 0)
        temp = data[2] & 0x7F
        temp_celsius = temp_to_celsius(temp)
        tank_level = ((int(data[4]) << 8) + data[3]) & 0x3FFF
        tank_level_mm = tank_level_and_temp_to_mm(tank_level, temp, self._medium_type)
        reading_quality = data[4] >> 6
        accelerometer_x = data[8]
        accelerometer_y = data[9]

        self.update_predefined_sensor(SensorLibrary.TEMPERATURE__CELSIUS, temp_celsius)
        self.update_predefined_sensor(
            SensorLibrary.BATTERY__PERCENTAGE, battery_percentage
        )
        self.update_predefined_sensor(
            SensorLibrary.VOLTAGE__ELECTRIC_POTENTIAL_VOLT,
            battery_voltage,
            name="Battery Voltage",
            key="battery_voltage",
        )
        self.update_predefined_binary_sensor(
            BinarySensorDeviceClass.OCCUPANCY,
            button_pressed,
            key="button_pressed",
            name="Button pressed",
        )
        self.update_sensor(
            "tank_level",
            Units.LENGTH_MILLIMETERS,
            tank_level_mm if reading_quality >= 1 else None,
            SensorDeviceClass.DISTANCE,
            "Tank Level",
        )
        self.update_sensor(
            "accelerometer_x",
            None,
            accelerometer_x,
            None,
            "Position X",
        )
        self.update_sensor(
            "accelerometer_y",
            None,
            accelerometer_y,
            None,
            "Position Y",
        )
        self.update_sensor(
            "reading_quality_raw",
            None,
            reading_quality,
            None,
            "Reading quality raw",
        )
        self.update_sensor(
            "reading_quality",
            Units.PERCENTAGE,
            round(reading_quality / 3 * 100),
            None,
            "Reading quality",
        )
        # Reading stars = (3-reading_quality) * "★" + (reading_quality * "⭐")
