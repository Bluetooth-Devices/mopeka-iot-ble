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
MOKPEKA_PRO_SERVICE_UUID = "0000fee5-0000-1000-8000-00805f9b34fb"

# --- Standard "Check" sensor (TI chip, service 0xADA0) -----------------------
# Unlike the Pro line, the Standard sensor broadcasts raw ultrasonic echo data
# and the client runs the peak-detection + speed-of-sound math (a port of
# ESPHome's mopeka_std_check component).
MOPEKA_STD_SERVICE_UUID = "0000ada0-0000-1000-8000-00805f9b34fb"
# hardware id = manufacturer_data[1] & 0xCF
MOPEKA_STD_SENSOR_TYPES = {
    0x02: "Standard",
    0x03: "XL",
    0x44: "Standard",  # STANDARD_ALT
    0x46: "eTrailer",
}
# 19-byte packed manufacturer payload.
MOPEKA_STD_PACKAGE_LEN = 19
# 1.0 = 100% propane (ESPHome default).
MOPEKA_PROPANE_BUTANE_MIX = 1.0


def std_speed_of_sound(temp_c: float, mix: float = MOPEKA_PROPANE_BUTANE_MIX) -> float:
    """Return the LPG speed of sound (m/s) for the Standard distance calc."""
    return (
        1040.71
        - 4.87 * temp_c
        - 137.5 * mix
        - 0.0107 * temp_c * temp_c
        - 1.63 * temp_c * mix
    )


@dataclass
class MopekaDevice:
    model: str
    name: str
    adv_length: int


DEVICE_TYPES = {
    0x3: MopekaDevice("M1017", "Pro Check", 10),
    0x4: MopekaDevice("Pro-200", "Pro-200", 10),
    0x5: MopekaDevice("Pro H20", "Pro Check H2O", 10),
    0x6: MopekaDevice("M1017", "Lippert BottleCheck", 10),
    0x8: MopekaDevice("M1015", "Pro Plus", 10),
    0x9: MopekaDevice("M1015", "Pro Plus with Cellular", 10),
    0xA: MopekaDevice("TD40/TD200", "TD40/TD200", 10),
    0xB: MopekaDevice("TD40/TD200", "TD40/TD200 with Cellular", 10),
    0xC: MopekaDevice("M1017", "Pro Check Universal", 10),
    0x12: MopekaDevice("Pro-200", "Pro-200B", 10),
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
        if MOPEKA_STD_SERVICE_UUID in service_uuids:
            self._update_std(service_info)
            return
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

    def _update_std(self, service_info: BluetoothServiceInfo) -> None:
        """Decode a Standard "Check" advertisement (ported from ESPHome)."""
        address = service_info.address
        # The Standard sensor emits one manufacturer-data payload; ESPHome does
        # not check the company id, only the length + hardware id byte.
        data: bytes | None = None
        for payload in service_info.manufacturer_data.values():
            if (
                len(payload) >= MOPEKA_STD_PACKAGE_LEN
                and (payload[1] & 0xCF) in MOPEKA_STD_SENSOR_TYPES
            ):
                data = payload
                break
        if data is None:
            _LOGGER.debug("Unsupported Mopeka Standard advertisement: %s", service_info)
            return

        model = MOPEKA_STD_SENSOR_TYPES[data[1] & 0xCF]
        self.set_device_manufacturer("Mopeka IOT")
        self.set_device_type(f"{model} Check")
        self.set_device_name(f"{model} Check {short_address(address)}")

        raw_voltage = data[2]
        raw_temp = data[3] & 0x3F
        temp_celsius = -40.0 if raw_temp == 0 else (raw_temp - 25.0) * 1.776964
        battery_voltage = (raw_voltage / 256.0) * 2.0 + 1.5
        battery_percentage = round(
            max(0.0, min(100.0, (battery_voltage - 2.2) / 0.65 * 100.0)), 1
        )

        # Unpack 12 (time, amplitude) pairs from three little-endian 40-bit
        # blocks of eight 5-bit fields (LSB first).
        times: list[int] = []
        values: list[int] = []
        for blk in range(3):
            start = 4 + blk * 5
            end = start + 5
            raw = int.from_bytes(data[start:end], "little")
            for m in range(4):
                times.append(((raw >> (10 * m)) & 0x1F) + 1)
                values.append((raw >> (10 * m + 5)) & 0x1F)

        number_usable = 0
        best_value = 0
        best_time = 0
        measurement_time = 0
        for i in range(12):
            measurement_time += times[i]
            if values[i] != 0:
                number_usable += 1
                if values[i] > best_value:
                    best_value = values[i]
                    best_time = measurement_time
                measurement_time = 0

        distance_mm = round(std_speed_of_sound(temp_celsius) * best_time / 100.0)
        valid = number_usable >= 1 and best_value >= 2 and best_time >= 2

        self.update_predefined_sensor(
            SensorLibrary.TEMPERATURE__CELSIUS, round(temp_celsius, 1)
        )
        self.update_predefined_sensor(
            SensorLibrary.BATTERY__PERCENTAGE, battery_percentage
        )
        self.update_predefined_sensor(
            SensorLibrary.VOLTAGE__ELECTRIC_POTENTIAL_VOLT,
            round(battery_voltage, 3),
            name="Battery Voltage",
            key="battery_voltage",
        )
        self.update_sensor(
            "tank_level",
            Units.LENGTH_MILLIMETERS,
            distance_mm if valid else None,
            SensorDeviceClass.DISTANCE,
            "Tank Level",
        )
        self.update_sensor(
            "reading_quality_raw",
            None,
            best_value,
            None,
            "Reading quality raw",
        )
        self.update_sensor(
            "reading_quality",
            Units.PERCENTAGE,
            round(best_value / 31 * 100),
            None,
            "Reading quality",
        )
