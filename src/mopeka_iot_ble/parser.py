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

# The Standard Check family advertises under Texas Instruments' company ID
# rather than Mopeka's, so the service UUID and length are part of the gate.
MOPEKA_STD_MANUFACTURER = 0x000D
MOPEKA_STD_SERVICE_UUID = "0000ada0-0000-1000-8000-00805f9b34fb"
MOPEKA_STD_ADV_LENGTH = 23


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

# Standard Check sensor types, keyed on byte 1 of the advertisement.
STD_DEVICE_TYPES = {
    0x02: MopekaDevice("M1001", "Standard Check", MOPEKA_STD_ADV_LENGTH),
    0x03: MopekaDevice("M1001", "Standard Check XL", MOPEKA_STD_ADV_LENGTH),
    0x44: MopekaDevice("M1001", "Standard Check", MOPEKA_STD_ADV_LENGTH),
    0x46: MopekaDevice("M1001", "Standard Check E-Trailer", MOPEKA_STD_ADV_LENGTH),
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


def std_raw_voltage_to_voltage(raw_voltage: int) -> float:
    """Convert a Standard Check raw voltage byte to volts."""
    return raw_voltage / 256.0 * 2.0 + 1.5


def std_raw_temp_to_celsius(raw_temp: int) -> float:
    """Convert a Standard Check 6-bit raw temperature to celsius.

    Zero is the sensor's out-of-range sentinel and means -40C, not the -44.4C
    the linear scale would extrapolate to.
    """
    return -40.0 if raw_temp == 0 else (raw_temp - 25) * 1.776964


def std_echo_sweep(data: bytes) -> list[tuple[int, int]]:
    """Return the 12 (time, amplitude) echo pairs of a Standard Check advert.

    Bytes 4-18 are exactly 120 bits, packed little-endian as twelve 10-bit
    entries: a 5-bit time delta in 10us ticks followed by a 5-bit amplitude.
    Layout confirmed against ESPHome's ``mopeka_std_check`` component, which
    decodes the same manufacturer payload.
    """
    packed = int.from_bytes(data[4:19], "little")
    return [
        ((packed >> (10 * i)) & 0x1F, (packed >> (10 * i + 5)) & 0x1F)
        for i in range(12)
    ]


def std_speed_of_sound(temp_celsius: float) -> float:
    """Return the speed of sound in m/s through pure propane at a temperature."""
    return (
        1040.71
        - 4.87 * temp_celsius
        - 137.5
        - 0.0107 * temp_celsius * temp_celsius
        - 1.63 * temp_celsius
    )


def std_distance_mm(sweep: list[tuple[int, int]], temp_celsius: float) -> int | None:
    """Return the reading distance in mm, or None when the read is too weak.

    Silent entries only advance the clock, so their time accumulates into the
    next entry that does report an amplitude; the strongest echo wins.
    """
    elapsed = 0
    best_amplitude = best_time = 0
    for time_delta, amplitude in sweep:
        elapsed += time_delta + 1
        if amplitude:
            if amplitude > best_amplitude:
                best_amplitude, best_time = amplitude, elapsed
            elapsed = 0
    if best_amplitude < 2 or best_time < 2:
        return None
    return int(std_speed_of_sound(temp_celsius) * best_time / 100)


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
        if (
            MOPEKA_STD_MANUFACTURER in manufacturer_data
            and MOPEKA_STD_SERVICE_UUID in service_uuids
        ):
            self._update_std_check(
                manufacturer_data[MOPEKA_STD_MANUFACTURER], address, service_info
            )
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

    def _update_std_check(
        self, data: bytes, address: str, service_info: BluetoothServiceInfo
    ) -> None:
        """Update from a Mopeka Standard Check advertisement.

        Layout (23 bytes): byte 1 is the sensor type, byte 2 the raw battery
        voltage, byte 3 packs a 6-bit raw temperature with the slow-update and
        sync-pressed flags. Bytes 4-18 carry the ultrasonic echo sweep as twelve
        10-bit entries, from which the reading distance is derived. Unlike the
        Pro models these report a distance to the fluid surface rather than a
        percentage, so the tank geometry stays the consumer's business.
        """
        if len(data) != MOPEKA_STD_ADV_LENGTH:
            _LOGGER.debug(
                "Unexpected Mopeka Standard Check advertisement length: %s",
                service_info,
            )
            return
        if not (device_type := STD_DEVICE_TYPES.get(data[1] & 0xCF)):
            _LOGGER.debug(
                "Unsupported Mopeka Standard Check advertisement: %s", service_info
            )
            return

        self.set_device_manufacturer("Mopeka IOT")
        self.set_device_type(device_type.model)
        self.set_device_name(f"{device_type.name} {short_address(address)}")

        battery_voltage = std_raw_voltage_to_voltage(data[2])
        temp_celsius = std_raw_temp_to_celsius(data[3] & 0x3F)
        self.update_predefined_sensor(
            SensorLibrary.TEMPERATURE__CELSIUS, round(temp_celsius, 1)
        )
        self.update_predefined_sensor(
            SensorLibrary.BATTERY__PERCENTAGE,
            round(max(0, min(100, ((battery_voltage - 2.2) / 0.65) * 100)), 1),
        )
        self.update_predefined_sensor(
            SensorLibrary.VOLTAGE__ELECTRIC_POTENTIAL_VOLT,
            round(battery_voltage, 2),
            name="Battery Voltage",
            key="battery_voltage",
        )
        self.update_predefined_binary_sensor(
            BinarySensorDeviceClass.OCCUPANCY,
            bool(data[3] & 0x80),
            key="button_pressed",
            name="Button pressed",
        )
        sweep = std_echo_sweep(data)
        self.update_sensor(
            "echo_strength",
            None,
            max(amplitude for _, amplitude in sweep),
            None,
            "Echo strength",
        )
        self.update_sensor(
            "tank_level",
            Units.LENGTH_MILLIMETERS,
            std_distance_mm(sweep, temp_celsius),
            SensorDeviceClass.DISTANCE,
            "Tank Level",
        )
