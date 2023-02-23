"""Parser for Gmopeka_iot BLE advertisements.

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

_LOGGER = logging.getLogger(__name__)


# converting sensor value to height - contact Mopeka for other fluids/gases
MOPEKA_TANK_LEVEL_COEFFICIENTS_PROPANE = (0.573045, -0.002822, -0.00000535)

MOPEKA_MANUFACTURER = 89
MOKPEKA_PRO_SERVICE_UUID = "0000fee5-0000-1000-8000-00805f9b34fb"


@dataclass
class MopekaDevice:

    model: str
    name: str
    adv_length: int


DEVICE_TYPES = {
    0x3: MopekaDevice("M1017", "Pro Check", 10),
    0x4: MopekaDevice("", "Top down air space", 10),
    0x5: MopekaDevice("", "Bottom up water", 10),
    0x8: MopekaDevice("M1015", "Pro Plus", 10),
}

SUPPORTED_DEVICE_TYPES = {0x3, 0x8}


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


def tank_level_and_temp_to_mm(tank_level: int, temp: int) -> int:
    """Get the tank level in mm."""
    return int(
        tank_level
        * (
            MOPEKA_TANK_LEVEL_COEFFICIENTS_PROPANE[0]
            + (MOPEKA_TANK_LEVEL_COEFFICIENTS_PROPANE[1] * temp)
            + (MOPEKA_TANK_LEVEL_COEFFICIENTS_PROPANE[2] * (temp**2))
        )
    )


class MopekaIOTBluetoothDeviceData(BluetoothData):
    """Data for Mopeka IOT BLE sensors."""

    def _start_update(self, service_info: BluetoothServiceInfo) -> None:
        """Update from BLE advertisement data."""
        _LOGGER.debug("Parsing Mopeka IOT BLE advertisement data: %s", service_info)
        manufacturer_data = service_info.manufacturer_data
        service_uuids = service_info.service_uuids
        address = service_info.address
        if (
            MOPEKA_MANUFACTURER not in manufacturer_data
            or MOKPEKA_PRO_SERVICE_UUID not in service_uuids
        ):
            _LOGGER.debug("Not a Mopeka IOT BLE advertisement: %s", service_info)
            return
        data = manufacturer_data[MOPEKA_MANUFACTURER]
        model_num = data[0]
        if not (device_type := DEVICE_TYPES.get(model_num)):
            _LOGGER.debug("Unsupported Mopeka IOT BLE advertisement: %s", service_info)
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
        tank_level_mm = tank_level_and_temp_to_mm(tank_level, temp)
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
