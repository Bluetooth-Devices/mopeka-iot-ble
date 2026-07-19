from bluetooth_sensor_state_data import BluetoothServiceInfo, SensorUpdate
from mopeka_iot_ble import MediumType

# Consider renaming the hex method to avoid the override complaint
from mopeka_iot_ble.parser import (
    MopekaIOTBluetoothDeviceData,
    battery_to_percentage,
    battery_to_voltage,
    hex,
    tank_level_and_temp_to_mm,
    tank_level_to_mm,
    temp_to_celsius,
)
from sensor_state_data import (
    BinarySensorDescription,
    BinarySensorDeviceClass,
    BinarySensorValue,
    DeviceKey,
    SensorDescription,
    SensorDeviceClass,
    SensorDeviceInfo,
    SensorValue,
    Units,
)

import pytest

PRO_SERVICE_BAD_QUALITY_INFO = BluetoothServiceInfo(
    name="",
    address="C9:F3:32:E0:F5:09",
    rssi=-63,
    manufacturer_data={89: b"\x08rF\x000\xe0\xf5\t\xf0\xd8"},
    service_uuids=["0000fee5-0000-1000-8000-00805f9b34fb"],
    service_data={},
    source="local",
)

PRO_SERVICE_LOW_QUALITY_INFO = BluetoothServiceInfo(
    name="",
    address="C9:F3:32:E0:F5:09",
    rssi=-63,
    manufacturer_data={89: b"\x08rF\x00@\xe0\xf5\t\xf0\xd8"},
    service_uuids=["0000fee5-0000-1000-8000-00805f9b34fb"],
    service_data={},
    source="local",
)
TDR40_AIR_LOW_QUALITY_INFO_2 = BluetoothServiceInfo(
    name="",
    address="DA:D8:AC:6A:75:10",
    rssi=-49,
    manufacturer_data={89: b"\x0c`8<\x83*\xea\x8c1\xf8"},
    service_uuids=["0000fee5-0000-1000-8000-00805f9b34fb"],
    service_data={},
    source="local",
)


PRO_SERVICE_GOOD_QUALITY_INFO = BluetoothServiceInfo(
    name="",
    address="C9:F3:32:E0:F5:09",
    rssi=-63,
    manufacturer_data={89: b"\x08rF\x00\xc0\xe0\xf5\t\xf0\xd8"},
    service_uuids=["0000fee5-0000-1000-8000-00805f9b34fb"],
    service_data={},
    source="local",
)

PRO_INSTALLED_SERVICE_INFO = BluetoothServiceInfo(
    name="",
    address="C9:F3:32:E0:F5:09",
    rssi=-63,
    manufacturer_data={89: b"\x08pC\xb6\xc3\xe0\xf5\t\xfa\xe3"},
    service_uuids=["0000fee5-0000-1000-8000-00805f9b34fb"],
    service_data={},
    source="local",
)


LIPPERT_SERVICE_INFO = BluetoothServiceInfo(
    name="",
    address="C9:F3:32:E0:F5:09",
    rssi=-63,
    manufacturer_data={89: b"\x06pC\xb6\xc3\xe0\xf5\t\xfa\xe3"},
    service_uuids=["0000fee5-0000-1000-8000-00805f9b34fb"],
    service_data={},
    source="local",
)

CHECK_INSTALLED_SERVICE_INFO = BluetoothServiceInfo(
    name="",
    address="C9:F3:32:E0:F5:09",
    rssi=-63,
    manufacturer_data={89: b"\x03pC\xb6\xc3\xe0\xf5\t\xfa\xe3"},
    service_uuids=["0000fee5-0000-1000-8000-00805f9b34fb"],
    service_data={},
    source="local",
)


CHECK_UNIVERSAL_INSTALLED_SERVICE_INFO = BluetoothServiceInfo(
    name="",
    address="C9:F3:32:E0:F5:09",
    rssi=-63,
    manufacturer_data={89: b"\x0cpC\xb6\xc3\xe0\xf5\t\xfa\xe3"},
    service_uuids=["0000fee5-0000-1000-8000-00805f9b34fb"],
    service_data={},
    source="local",
)


PRO_200B_SERVICE_INFO = BluetoothServiceInfo(
    name="",
    address="CB:A1:6C:CC:E5:2B",
    rssi=-63,
    manufacturer_data={89: b"\x12\x5f\x31\x78\xc7\xcc\xe5\x2b\xa8\x3f"},
    service_uuids=["0000fee5-0000-1000-8000-00805f9b34fb"],
    service_data={},
    source="local",
)

TDR40_AIR_BAD_QUALITY_INFO = BluetoothServiceInfo(
    name="",
    address="DA:D8:AC:6A:75:10",
    rssi=-60,
    manufacturer_data={89: b"\ns@NMju\x10\x7f\x80"},
    service_uuids=["0000fee5-0000-1000-8000-00805f9b34fb"],
    service_data={},
    source="local",
)

TDR40_AIR_LOW_QUALITY_INFO = BluetoothServiceInfo(
    name="",
    address="DA:D8:AC:6A:75:10",
    rssi=-44,
    manufacturer_data={89: b"\x0c`8<\x83*\xea\x8c1\xf8"},
    service_uuids=["0000fee5-0000-1000-8000-00805f9b34fb"],
    service_data={},
    source="local",
)

TDR40_AIR_GOOD_QUALITY_INFO = BluetoothServiceInfo(
    name="",
    address="DA:D8:AC:6A:75:10",
    rssi=-50,
    manufacturer_data={89: b"\nq@}\xd0ju\x10\x80 "},
    service_uuids=["0000fee5-0000-1000-8000-00805f9b34fb"],
    service_data={},
    source="local",
)


def test_hex():
    assert (
        hex(b"\x08rF\x000\xe0\xf5\t\xf0\xd8")
        == "b'\\x08\\x72\\x46\\x00\\x30\\xe0\\xf5\\x09\\xf0\\xd8'"
    )


def test_can_create():
    MopekaIOTBluetoothDeviceData()


def test_pro_bad_quality():
    parser = MopekaIOTBluetoothDeviceData()
    service_info = PRO_SERVICE_BAD_QUALITY_INFO
    result = parser.update(service_info)
    assert result == SensorUpdate(
        title=None,
        devices={
            None: SensorDeviceInfo(
                name="Pro Plus F509",
                model="M1015",
                manufacturer="Mopeka IOT",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="battery_voltage", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery_voltage", device_id=None),
                device_class=SensorDeviceClass.VOLTAGE,
                native_unit_of_measurement=Units.ELECTRIC_POTENTIAL_VOLT,
            ),
            DeviceKey(key="tank_level", device_id=None): SensorDescription(
                device_key=DeviceKey(key="tank_level", device_id=None),
                device_class=SensorDeviceClass.DISTANCE,
                native_unit_of_measurement=Units.LENGTH_MILLIMETERS,
            ),
            DeviceKey(key="temperature", device_id=None): SensorDescription(
                device_key=DeviceKey(key="temperature", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="battery", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(key="reading_quality", device_id=None): SensorDescription(
                device_key=DeviceKey(key="reading_quality", device_id=None),
                device_class=None,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="reading_quality_raw", device_id=None): SensorDescription(
                device_key=DeviceKey(key="reading_quality_raw", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="accelerometer_y", device_id=None): SensorDescription(
                device_key=DeviceKey(key="accelerometer_y", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="accelerometer_x", device_id=None): SensorDescription(
                device_key=DeviceKey(key="accelerometer_x", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
        },
        entity_values={
            DeviceKey(key="battery_voltage", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery_voltage", device_id=None),
                name="Battery Voltage",
                native_value=3.5625,
            ),
            DeviceKey(key="tank_level", device_id=None): SensorValue(
                device_key=DeviceKey(key="tank_level", device_id=None),
                name="Tank Level",
                native_value=None,
            ),
            DeviceKey(key="temperature", device_id=None): SensorValue(
                device_key=DeviceKey(key="temperature", device_id=None),
                name="Temperature",
                native_value=30,
            ),
            DeviceKey(key="battery", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery", device_id=None),
                name="Battery",
                native_value=100,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-63,
            ),
            DeviceKey(key="reading_quality", device_id=None): SensorValue(
                device_key=DeviceKey(key="reading_quality", device_id=None),
                name="Reading quality",
                native_value=0,
            ),
            DeviceKey(key="reading_quality_raw", device_id=None): SensorValue(
                device_key=DeviceKey(key="reading_quality_raw", device_id=None),
                name="Reading quality raw",
                native_value=0,
            ),
            DeviceKey(key="accelerometer_y", device_id=None): SensorValue(
                device_key=DeviceKey(key="accelerometer_y", device_id=None),
                name="Position Y",
                native_value=216,
            ),
            DeviceKey(key="accelerometer_x", device_id=None): SensorValue(
                device_key=DeviceKey(key="accelerometer_x", device_id=None),
                name="Position X",
                native_value=240,
            ),
        },
        binary_entity_descriptions={
            DeviceKey(key="button_pressed", device_id=None): BinarySensorDescription(
                device_key=DeviceKey(key="button_pressed", device_id=None),
                device_class=BinarySensorDeviceClass.OCCUPANCY,
            )
        },
        binary_entity_values={
            DeviceKey(key="button_pressed", device_id=None): BinarySensorValue(
                device_key=DeviceKey(key="button_pressed", device_id=None),
                name="Button pressed",
                native_value=False,
            )
        },
        events={},
    )


def test_pro_low_quality():
    parser = MopekaIOTBluetoothDeviceData()
    service_info = PRO_SERVICE_LOW_QUALITY_INFO
    result = parser.update(service_info)
    assert result == SensorUpdate(
        title=None,
        devices={
            None: SensorDeviceInfo(
                name="Pro Plus F509",
                model="M1015",
                manufacturer="Mopeka IOT",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="battery_voltage", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery_voltage", device_id=None),
                device_class=SensorDeviceClass.VOLTAGE,
                native_unit_of_measurement=Units.ELECTRIC_POTENTIAL_VOLT,
            ),
            DeviceKey(key="tank_level", device_id=None): SensorDescription(
                device_key=DeviceKey(key="tank_level", device_id=None),
                device_class=SensorDeviceClass.DISTANCE,
                native_unit_of_measurement=Units.LENGTH_MILLIMETERS,
            ),
            DeviceKey(key="temperature", device_id=None): SensorDescription(
                device_key=DeviceKey(key="temperature", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="battery", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(key="reading_quality", device_id=None): SensorDescription(
                device_key=DeviceKey(key="reading_quality", device_id=None),
                device_class=None,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="reading_quality_raw", device_id=None): SensorDescription(
                device_key=DeviceKey(key="reading_quality_raw", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="accelerometer_y", device_id=None): SensorDescription(
                device_key=DeviceKey(key="accelerometer_y", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="accelerometer_x", device_id=None): SensorDescription(
                device_key=DeviceKey(key="accelerometer_x", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
        },
        entity_values={
            DeviceKey(key="battery_voltage", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery_voltage", device_id=None),
                name="Battery Voltage",
                native_value=3.5625,
            ),
            DeviceKey(key="tank_level", device_id=None): SensorValue(
                device_key=DeviceKey(key="tank_level", device_id=None),
                name="Tank Level",
                native_value=0,
            ),
            DeviceKey(key="temperature", device_id=None): SensorValue(
                device_key=DeviceKey(key="temperature", device_id=None),
                name="Temperature",
                native_value=30,
            ),
            DeviceKey(key="battery", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery", device_id=None),
                name="Battery",
                native_value=100,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-63,
            ),
            DeviceKey(key="reading_quality", device_id=None): SensorValue(
                device_key=DeviceKey(key="reading_quality", device_id=None),
                name="Reading quality",
                native_value=33,
            ),
            DeviceKey(key="reading_quality_raw", device_id=None): SensorValue(
                device_key=DeviceKey(key="reading_quality_raw", device_id=None),
                name="Reading quality raw",
                native_value=1,
            ),
            DeviceKey(key="accelerometer_y", device_id=None): SensorValue(
                device_key=DeviceKey(key="accelerometer_y", device_id=None),
                name="Position Y",
                native_value=216,
            ),
            DeviceKey(key="accelerometer_x", device_id=None): SensorValue(
                device_key=DeviceKey(key="accelerometer_x", device_id=None),
                name="Position X",
                native_value=240,
            ),
        },
        binary_entity_descriptions={
            DeviceKey(key="button_pressed", device_id=None): BinarySensorDescription(
                device_key=DeviceKey(key="button_pressed", device_id=None),
                device_class=BinarySensorDeviceClass.OCCUPANCY,
            )
        },
        binary_entity_values={
            DeviceKey(key="button_pressed", device_id=None): BinarySensorValue(
                device_key=DeviceKey(key="button_pressed", device_id=None),
                name="Button pressed",
                native_value=False,
            )
        },
        events={},
    )


def test_pro_good_quality():
    parser = MopekaIOTBluetoothDeviceData()
    service_info = PRO_SERVICE_GOOD_QUALITY_INFO
    result = parser.update(service_info)
    assert result == SensorUpdate(
        title=None,
        devices={
            None: SensorDeviceInfo(
                name="Pro Plus F509",
                model="M1015",
                manufacturer="Mopeka IOT",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="battery_voltage", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery_voltage", device_id=None),
                device_class=SensorDeviceClass.VOLTAGE,
                native_unit_of_measurement=Units.ELECTRIC_POTENTIAL_VOLT,
            ),
            DeviceKey(key="tank_level", device_id=None): SensorDescription(
                device_key=DeviceKey(key="tank_level", device_id=None),
                device_class=SensorDeviceClass.DISTANCE,
                native_unit_of_measurement=Units.LENGTH_MILLIMETERS,
            ),
            DeviceKey(key="temperature", device_id=None): SensorDescription(
                device_key=DeviceKey(key="temperature", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="battery", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(key="reading_quality", device_id=None): SensorDescription(
                device_key=DeviceKey(key="reading_quality", device_id=None),
                device_class=None,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="reading_quality_raw", device_id=None): SensorDescription(
                device_key=DeviceKey(key="reading_quality_raw", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="accelerometer_y", device_id=None): SensorDescription(
                device_key=DeviceKey(key="accelerometer_y", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="accelerometer_x", device_id=None): SensorDescription(
                device_key=DeviceKey(key="accelerometer_x", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
        },
        entity_values={
            DeviceKey(key="battery_voltage", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery_voltage", device_id=None),
                name="Battery Voltage",
                native_value=3.5625,
            ),
            DeviceKey(key="tank_level", device_id=None): SensorValue(
                device_key=DeviceKey(key="tank_level", device_id=None),
                name="Tank Level",
                native_value=0,
            ),
            DeviceKey(key="temperature", device_id=None): SensorValue(
                device_key=DeviceKey(key="temperature", device_id=None),
                name="Temperature",
                native_value=30,
            ),
            DeviceKey(key="battery", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery", device_id=None),
                name="Battery",
                native_value=100,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-63,
            ),
            DeviceKey(key="reading_quality", device_id=None): SensorValue(
                device_key=DeviceKey(key="reading_quality", device_id=None),
                name="Reading quality",
                native_value=100,
            ),
            DeviceKey(key="reading_quality_raw", device_id=None): SensorValue(
                device_key=DeviceKey(key="reading_quality_raw", device_id=None),
                name="Reading quality raw",
                native_value=3,
            ),
            DeviceKey(key="accelerometer_y", device_id=None): SensorValue(
                device_key=DeviceKey(key="accelerometer_y", device_id=None),
                name="Position Y",
                native_value=216,
            ),
            DeviceKey(key="accelerometer_x", device_id=None): SensorValue(
                device_key=DeviceKey(key="accelerometer_x", device_id=None),
                name="Position X",
                native_value=240,
            ),
        },
        binary_entity_descriptions={
            DeviceKey(key="button_pressed", device_id=None): BinarySensorDescription(
                device_key=DeviceKey(key="button_pressed", device_id=None),
                device_class=BinarySensorDeviceClass.OCCUPANCY,
            )
        },
        binary_entity_values={
            DeviceKey(key="button_pressed", device_id=None): BinarySensorValue(
                device_key=DeviceKey(key="button_pressed", device_id=None),
                name="Button pressed",
                native_value=False,
            )
        },
        events={},
    )


def test_pro_installed():
    parser = MopekaIOTBluetoothDeviceData()
    service_info = PRO_INSTALLED_SERVICE_INFO
    result = parser.update(service_info)
    assert result == SensorUpdate(
        title=None,
        devices={
            None: SensorDeviceInfo(
                name="Pro Plus F509",
                model="M1015",
                manufacturer="Mopeka IOT",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="battery_voltage", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery_voltage", device_id=None),
                device_class=SensorDeviceClass.VOLTAGE,
                native_unit_of_measurement=Units.ELECTRIC_POTENTIAL_VOLT,
            ),
            DeviceKey(key="tank_level", device_id=None): SensorDescription(
                device_key=DeviceKey(key="tank_level", device_id=None),
                device_class=SensorDeviceClass.DISTANCE,
                native_unit_of_measurement=Units.LENGTH_MILLIMETERS,
            ),
            DeviceKey(key="temperature", device_id=None): SensorDescription(
                device_key=DeviceKey(key="temperature", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="battery", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(key="reading_quality", device_id=None): SensorDescription(
                device_key=DeviceKey(key="reading_quality", device_id=None),
                device_class=None,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="reading_quality_raw", device_id=None): SensorDescription(
                device_key=DeviceKey(key="reading_quality_raw", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="accelerometer_y", device_id=None): SensorDescription(
                device_key=DeviceKey(key="accelerometer_y", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="accelerometer_x", device_id=None): SensorDescription(
                device_key=DeviceKey(key="accelerometer_x", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
        },
        entity_values={
            DeviceKey(key="battery_voltage", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery_voltage", device_id=None),
                name="Battery Voltage",
                native_value=3.5,
            ),
            DeviceKey(key="tank_level", device_id=None): SensorValue(
                device_key=DeviceKey(key="tank_level", device_id=None),
                name="Tank Level",
                native_value=341,
            ),
            DeviceKey(key="temperature", device_id=None): SensorValue(
                device_key=DeviceKey(key="temperature", device_id=None),
                name="Temperature",
                native_value=27,
            ),
            DeviceKey(key="battery", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery", device_id=None),
                name="Battery",
                native_value=100,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-63,
            ),
            DeviceKey(key="reading_quality", device_id=None): SensorValue(
                device_key=DeviceKey(key="reading_quality", device_id=None),
                name="Reading quality",
                native_value=100,
            ),
            DeviceKey(key="reading_quality_raw", device_id=None): SensorValue(
                device_key=DeviceKey(key="reading_quality_raw", device_id=None),
                name="Reading quality raw",
                native_value=3,
            ),
            DeviceKey(key="accelerometer_y", device_id=None): SensorValue(
                device_key=DeviceKey(key="accelerometer_y", device_id=None),
                name="Position Y",
                native_value=227,
            ),
            DeviceKey(key="accelerometer_x", device_id=None): SensorValue(
                device_key=DeviceKey(key="accelerometer_x", device_id=None),
                name="Position X",
                native_value=250,
            ),
        },
        binary_entity_descriptions={
            DeviceKey(key="button_pressed", device_id=None): BinarySensorDescription(
                device_key=DeviceKey(key="button_pressed", device_id=None),
                device_class=BinarySensorDeviceClass.OCCUPANCY,
            )
        },
        binary_entity_values={
            DeviceKey(key="button_pressed", device_id=None): BinarySensorValue(
                device_key=DeviceKey(key="button_pressed", device_id=None),
                name="Button pressed",
                native_value=False,
            )
        },
        events={},
    )


def test_check_universal_installed():
    parser = MopekaIOTBluetoothDeviceData()
    service_info = CHECK_UNIVERSAL_INSTALLED_SERVICE_INFO
    result = parser.update(service_info)
    assert result == SensorUpdate(
        title=None,
        devices={
            None: SensorDeviceInfo(
                name="Pro Check Universal F509",
                model="M1017",
                manufacturer="Mopeka IOT",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="battery_voltage", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery_voltage", device_id=None),
                device_class=SensorDeviceClass.VOLTAGE,
                native_unit_of_measurement=Units.ELECTRIC_POTENTIAL_VOLT,
            ),
            DeviceKey(key="tank_level", device_id=None): SensorDescription(
                device_key=DeviceKey(key="tank_level", device_id=None),
                device_class=SensorDeviceClass.DISTANCE,
                native_unit_of_measurement=Units.LENGTH_MILLIMETERS,
            ),
            DeviceKey(key="temperature", device_id=None): SensorDescription(
                device_key=DeviceKey(key="temperature", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="battery", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(key="reading_quality", device_id=None): SensorDescription(
                device_key=DeviceKey(key="reading_quality", device_id=None),
                device_class=None,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="reading_quality_raw", device_id=None): SensorDescription(
                device_key=DeviceKey(key="reading_quality_raw", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="accelerometer_y", device_id=None): SensorDescription(
                device_key=DeviceKey(key="accelerometer_y", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="accelerometer_x", device_id=None): SensorDescription(
                device_key=DeviceKey(key="accelerometer_x", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
        },
        entity_values={
            DeviceKey(key="battery_voltage", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery_voltage", device_id=None),
                name="Battery Voltage",
                native_value=3.5,
            ),
            DeviceKey(key="tank_level", device_id=None): SensorValue(
                device_key=DeviceKey(key="tank_level", device_id=None),
                name="Tank Level",
                native_value=341,
            ),
            DeviceKey(key="temperature", device_id=None): SensorValue(
                device_key=DeviceKey(key="temperature", device_id=None),
                name="Temperature",
                native_value=27,
            ),
            DeviceKey(key="battery", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery", device_id=None),
                name="Battery",
                native_value=100,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-63,
            ),
            DeviceKey(key="reading_quality", device_id=None): SensorValue(
                device_key=DeviceKey(key="reading_quality", device_id=None),
                name="Reading quality",
                native_value=100,
            ),
            DeviceKey(key="reading_quality_raw", device_id=None): SensorValue(
                device_key=DeviceKey(key="reading_quality_raw", device_id=None),
                name="Reading quality raw",
                native_value=3,
            ),
            DeviceKey(key="accelerometer_y", device_id=None): SensorValue(
                device_key=DeviceKey(key="accelerometer_y", device_id=None),
                name="Position Y",
                native_value=227,
            ),
            DeviceKey(key="accelerometer_x", device_id=None): SensorValue(
                device_key=DeviceKey(key="accelerometer_x", device_id=None),
                name="Position X",
                native_value=250,
            ),
        },
        binary_entity_descriptions={
            DeviceKey(key="button_pressed", device_id=None): BinarySensorDescription(
                device_key=DeviceKey(key="button_pressed", device_id=None),
                device_class=BinarySensorDeviceClass.OCCUPANCY,
            )
        },
        binary_entity_values={
            DeviceKey(key="button_pressed", device_id=None): BinarySensorValue(
                device_key=DeviceKey(key="button_pressed", device_id=None),
                name="Button pressed",
                native_value=False,
            )
        },
        events={},
    )


def test_check_installed():
    parser = MopekaIOTBluetoothDeviceData()
    service_info = CHECK_INSTALLED_SERVICE_INFO
    result = parser.update(service_info)
    assert result == SensorUpdate(
        title=None,
        devices={
            None: SensorDeviceInfo(
                name="Pro Check F509",
                model="M1017",
                manufacturer="Mopeka IOT",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="battery_voltage", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery_voltage", device_id=None),
                device_class=SensorDeviceClass.VOLTAGE,
                native_unit_of_measurement=Units.ELECTRIC_POTENTIAL_VOLT,
            ),
            DeviceKey(key="tank_level", device_id=None): SensorDescription(
                device_key=DeviceKey(key="tank_level", device_id=None),
                device_class=SensorDeviceClass.DISTANCE,
                native_unit_of_measurement=Units.LENGTH_MILLIMETERS,
            ),
            DeviceKey(key="temperature", device_id=None): SensorDescription(
                device_key=DeviceKey(key="temperature", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="battery", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(key="reading_quality", device_id=None): SensorDescription(
                device_key=DeviceKey(key="reading_quality", device_id=None),
                device_class=None,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="reading_quality_raw", device_id=None): SensorDescription(
                device_key=DeviceKey(key="reading_quality_raw", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="accelerometer_y", device_id=None): SensorDescription(
                device_key=DeviceKey(key="accelerometer_y", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="accelerometer_x", device_id=None): SensorDescription(
                device_key=DeviceKey(key="accelerometer_x", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
        },
        entity_values={
            DeviceKey(key="battery_voltage", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery_voltage", device_id=None),
                name="Battery Voltage",
                native_value=3.5,
            ),
            DeviceKey(key="tank_level", device_id=None): SensorValue(
                device_key=DeviceKey(key="tank_level", device_id=None),
                name="Tank Level",
                native_value=341,
            ),
            DeviceKey(key="temperature", device_id=None): SensorValue(
                device_key=DeviceKey(key="temperature", device_id=None),
                name="Temperature",
                native_value=27,
            ),
            DeviceKey(key="battery", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery", device_id=None),
                name="Battery",
                native_value=100,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-63,
            ),
            DeviceKey(key="reading_quality", device_id=None): SensorValue(
                device_key=DeviceKey(key="reading_quality", device_id=None),
                name="Reading quality",
                native_value=100,
            ),
            DeviceKey(key="reading_quality_raw", device_id=None): SensorValue(
                device_key=DeviceKey(key="reading_quality_raw", device_id=None),
                name="Reading quality raw",
                native_value=3,
            ),
            DeviceKey(key="accelerometer_y", device_id=None): SensorValue(
                device_key=DeviceKey(key="accelerometer_y", device_id=None),
                name="Position Y",
                native_value=227,
            ),
            DeviceKey(key="accelerometer_x", device_id=None): SensorValue(
                device_key=DeviceKey(key="accelerometer_x", device_id=None),
                name="Position X",
                native_value=250,
            ),
        },
        binary_entity_descriptions={
            DeviceKey(key="button_pressed", device_id=None): BinarySensorDescription(
                device_key=DeviceKey(key="button_pressed", device_id=None),
                device_class=BinarySensorDeviceClass.OCCUPANCY,
            )
        },
        binary_entity_values={
            DeviceKey(key="button_pressed", device_id=None): BinarySensorValue(
                device_key=DeviceKey(key="button_pressed", device_id=None),
                name="Button pressed",
                native_value=False,
            )
        },
        events={},
    )


def test_lippert():
    parser = MopekaIOTBluetoothDeviceData()
    service_info = LIPPERT_SERVICE_INFO
    result = parser.update(service_info)
    assert result == SensorUpdate(
        title=None,
        devices={
            None: SensorDeviceInfo(
                name="Lippert BottleCheck F509",
                model="M1017",
                manufacturer="Mopeka IOT",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="battery_voltage", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery_voltage", device_id=None),
                device_class=SensorDeviceClass.VOLTAGE,
                native_unit_of_measurement=Units.ELECTRIC_POTENTIAL_VOLT,
            ),
            DeviceKey(key="tank_level", device_id=None): SensorDescription(
                device_key=DeviceKey(key="tank_level", device_id=None),
                device_class=SensorDeviceClass.DISTANCE,
                native_unit_of_measurement=Units.LENGTH_MILLIMETERS,
            ),
            DeviceKey(key="temperature", device_id=None): SensorDescription(
                device_key=DeviceKey(key="temperature", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="battery", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(key="reading_quality", device_id=None): SensorDescription(
                device_key=DeviceKey(key="reading_quality", device_id=None),
                device_class=None,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="reading_quality_raw", device_id=None): SensorDescription(
                device_key=DeviceKey(key="reading_quality_raw", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="accelerometer_y", device_id=None): SensorDescription(
                device_key=DeviceKey(key="accelerometer_y", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="accelerometer_x", device_id=None): SensorDescription(
                device_key=DeviceKey(key="accelerometer_x", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
        },
        entity_values={
            DeviceKey(key="battery_voltage", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery_voltage", device_id=None),
                name="Battery Voltage",
                native_value=3.5,
            ),
            DeviceKey(key="tank_level", device_id=None): SensorValue(
                device_key=DeviceKey(key="tank_level", device_id=None),
                name="Tank Level",
                native_value=341,
            ),
            DeviceKey(key="temperature", device_id=None): SensorValue(
                device_key=DeviceKey(key="temperature", device_id=None),
                name="Temperature",
                native_value=27,
            ),
            DeviceKey(key="battery", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery", device_id=None),
                name="Battery",
                native_value=100,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-63,
            ),
            DeviceKey(key="reading_quality", device_id=None): SensorValue(
                device_key=DeviceKey(key="reading_quality", device_id=None),
                name="Reading quality",
                native_value=100,
            ),
            DeviceKey(key="reading_quality_raw", device_id=None): SensorValue(
                device_key=DeviceKey(key="reading_quality_raw", device_id=None),
                name="Reading quality raw",
                native_value=3,
            ),
            DeviceKey(key="accelerometer_y", device_id=None): SensorValue(
                device_key=DeviceKey(key="accelerometer_y", device_id=None),
                name="Position Y",
                native_value=227,
            ),
            DeviceKey(key="accelerometer_x", device_id=None): SensorValue(
                device_key=DeviceKey(key="accelerometer_x", device_id=None),
                name="Position X",
                native_value=250,
            ),
        },
        binary_entity_descriptions={
            DeviceKey(key="button_pressed", device_id=None): BinarySensorDescription(
                device_key=DeviceKey(key="button_pressed", device_id=None),
                device_class=BinarySensorDeviceClass.OCCUPANCY,
            )
        },
        binary_entity_values={
            DeviceKey(key="button_pressed", device_id=None): BinarySensorValue(
                device_key=DeviceKey(key="button_pressed", device_id=None),
                name="Button pressed",
                native_value=False,
            )
        },
        events={},
    )


def test_pro_200b():
    parser = MopekaIOTBluetoothDeviceData()
    service_info = PRO_200B_SERVICE_INFO
    result = parser.update(service_info)
    assert result == SensorUpdate(
        title=None,
        devices={
            None: SensorDeviceInfo(
                name="Pro-200B E52B",
                model="Pro-200",
                manufacturer="Mopeka IOT",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="battery_voltage", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery_voltage", device_id=None),
                device_class=SensorDeviceClass.VOLTAGE,
                native_unit_of_measurement=Units.ELECTRIC_POTENTIAL_VOLT,
            ),
            DeviceKey(key="tank_level", device_id=None): SensorDescription(
                device_key=DeviceKey(key="tank_level", device_id=None),
                device_class=SensorDeviceClass.DISTANCE,
                native_unit_of_measurement=Units.LENGTH_MILLIMETERS,
            ),
            DeviceKey(key="temperature", device_id=None): SensorDescription(
                device_key=DeviceKey(key="temperature", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="battery", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(key="reading_quality", device_id=None): SensorDescription(
                device_key=DeviceKey(key="reading_quality", device_id=None),
                device_class=None,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="reading_quality_raw", device_id=None): SensorDescription(
                device_key=DeviceKey(key="reading_quality_raw", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="accelerometer_y", device_id=None): SensorDescription(
                device_key=DeviceKey(key="accelerometer_y", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="accelerometer_x", device_id=None): SensorDescription(
                device_key=DeviceKey(key="accelerometer_x", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
        },
        entity_values={
            DeviceKey(key="battery_voltage", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery_voltage", device_id=None),
                name="Battery Voltage",
                native_value=2.96875,
            ),
            DeviceKey(key="tank_level", device_id=None): SensorValue(
                device_key=DeviceKey(key="tank_level", device_id=None),
                name="Tank Level",
                native_value=806,
            ),
            DeviceKey(key="temperature", device_id=None): SensorValue(
                device_key=DeviceKey(key="temperature", device_id=None),
                name="Temperature",
                native_value=9,
            ),
            DeviceKey(key="battery", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery", device_id=None),
                name="Battery",
                native_value=100,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-63,
            ),
            DeviceKey(key="reading_quality", device_id=None): SensorValue(
                device_key=DeviceKey(key="reading_quality", device_id=None),
                name="Reading quality",
                native_value=100,
            ),
            DeviceKey(key="reading_quality_raw", device_id=None): SensorValue(
                device_key=DeviceKey(key="reading_quality_raw", device_id=None),
                name="Reading quality raw",
                native_value=3,
            ),
            DeviceKey(key="accelerometer_y", device_id=None): SensorValue(
                device_key=DeviceKey(key="accelerometer_y", device_id=None),
                name="Position Y",
                native_value=63,
            ),
            DeviceKey(key="accelerometer_x", device_id=None): SensorValue(
                device_key=DeviceKey(key="accelerometer_x", device_id=None),
                name="Position X",
                native_value=168,
            ),
        },
        binary_entity_descriptions={
            DeviceKey(key="button_pressed", device_id=None): BinarySensorDescription(
                device_key=DeviceKey(key="button_pressed", device_id=None),
                device_class=BinarySensorDeviceClass.OCCUPANCY,
            )
        },
        binary_entity_values={
            DeviceKey(key="button_pressed", device_id=None): BinarySensorValue(
                device_key=DeviceKey(key="button_pressed", device_id=None),
                name="Button pressed",
                native_value=False,
            )
        },
        events={},
    )


@pytest.mark.parametrize(
    "battery_raw, expected_voltage",
    [
        (89, 2.78125),
        (90, 2.8125),
        (91, 2.84375),
        (92, 2.875),
        (93, 2.90625),
        (94, 2.9375),
        (95, 2.96875),
        (96, 3.0),
        (97, 3.03125),
        (98, 3.0625),
        (99, 3.09375),
        (100, 3.125),
    ],
)
def test_battery_to_voltage(battery_raw: int, expected_voltage: float) -> None:
    voltage = battery_to_voltage(battery_raw)
    assert voltage == expected_voltage


def test_battery_to_percentage():
    battery_raw = 89  # example battery raw value
    percentage = battery_to_percentage(battery_raw)
    assert percentage == 89.4


def test_temp_to_celsius():
    temperature_raw = 77  # example temperature raw value

    celsius = temp_to_celsius(temperature_raw)
    assert celsius == 37


def test_tank_level_to_mm():
    tank_level_raw = 3145  # example tank level raw value
    mm = tank_level_to_mm(tank_level_raw)
    assert mm == 31450  # tank_level_raw * 10


def test_tank_level_and_temp_to_mm():
    temperature_raw = 77  # example temperature raw value
    tank_level_raw = 3145  # example tank level raw value

    tank_level_mm = tank_level_and_temp_to_mm(
        tank_level_raw, temperature_raw, MediumType.AIR
    )
    expected_mm = int(
        tank_level_raw
        * (
            0.153096  # coefs[0] for MediumType.AIR
            + (0.000327 * temperature_raw)  # coefs[1] * temp
            + (-0.000000294 * (temperature_raw**2))  # coefs[2] * (temp ** 2)
        )
    )
    assert tank_level_mm == expected_mm


def test_parser_with_sample_data():
    medium_type = MediumType.AIR
    battery_raw = 89  # example battery raw value
    tank_level_raw = 3145  # example tank level raw value
    temperature_raw = 77  # example temperature raw value
    assert MopekaIOTBluetoothDeviceData(medium_type)
    assert battery_to_voltage(battery_raw) == 2.78125
    assert battery_to_percentage(battery_raw) == 89.4
    assert temp_to_celsius(temperature_raw) == 37
    assert tank_level_and_temp_to_mm(
        tank_level_raw, temperature_raw, medium_type
    ) == int(
        tank_level_raw
        * (
            0.153096  # coefs[0] for MediumType.AIR
            + (0.000327 * temperature_raw)  # coefs[1] * temp
            + (-0.000000294 * (temperature_raw**2))  # coefs[2] * (temp ** 2)
        )
    )


# Test entire parser chain
def test_tdr40_air_bad_quality():
    parser = MopekaIOTBluetoothDeviceData(MediumType.AIR)
    service_info = TDR40_AIR_BAD_QUALITY_INFO
    result = parser.update(service_info)

    assert result == SensorUpdate(
        title=None,
        devices={
            None: SensorDeviceInfo(
                name="TD40/TD200 7510",  # Corrected name
                model="TD40/TD200",  # Corrected model
                manufacturer="Mopeka IOT",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="battery_voltage", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery_voltage", device_id=None),
                device_class=SensorDeviceClass.VOLTAGE,
                native_unit_of_measurement=Units.ELECTRIC_POTENTIAL_VOLT,
            ),
            DeviceKey(key="tank_level", device_id=None): SensorDescription(
                device_key=DeviceKey(key="tank_level", device_id=None),
                device_class=SensorDeviceClass.DISTANCE,
                native_unit_of_measurement=Units.LENGTH_MILLIMETERS,
            ),
            DeviceKey(key="temperature", device_id=None): SensorDescription(
                device_key=DeviceKey(key="temperature", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="battery", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(key="reading_quality", device_id=None): SensorDescription(
                device_key=DeviceKey(key="reading_quality", device_id=None),
                device_class=None,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="reading_quality_raw", device_id=None): SensorDescription(
                device_key=DeviceKey(key="reading_quality_raw", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="accelerometer_y", device_id=None): SensorDescription(
                device_key=DeviceKey(key="accelerometer_y", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="accelerometer_x", device_id=None): SensorDescription(
                device_key=DeviceKey(key="accelerometer_x", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
        },
        entity_values={
            DeviceKey(key="battery_voltage", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery_voltage", device_id=None),
                name="Battery Voltage",
                native_value=3.59375,
            ),
            DeviceKey(key="tank_level", device_id=None): SensorValue(
                device_key=DeviceKey(key="tank_level", device_id=None),
                name="Tank Level",
                native_value=588,
            ),
            DeviceKey(key="temperature", device_id=None): SensorValue(
                device_key=DeviceKey(key="temperature", device_id=None),
                name="Temperature",
                native_value=24,
            ),
            DeviceKey(key="battery", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery", device_id=None),
                name="Battery",
                native_value=100,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-60,
            ),
            DeviceKey(key="reading_quality", device_id=None): SensorValue(
                device_key=DeviceKey(key="reading_quality", device_id=None),
                name="Reading quality",
                native_value=33,
            ),
            DeviceKey(key="reading_quality_raw", device_id=None): SensorValue(
                device_key=DeviceKey(key="reading_quality_raw", device_id=None),
                name="Reading quality raw",
                native_value=1,
            ),
            DeviceKey(key="accelerometer_y", device_id=None): SensorValue(
                device_key=DeviceKey(key="accelerometer_y", device_id=None),
                name="Position Y",
                native_value=128,
            ),
            DeviceKey(key="accelerometer_x", device_id=None): SensorValue(
                device_key=DeviceKey(key="accelerometer_x", device_id=None),
                name="Position X",
                native_value=127,
            ),
        },
        binary_entity_descriptions={
            DeviceKey(key="button_pressed", device_id=None): BinarySensorDescription(
                device_key=DeviceKey(key="button_pressed", device_id=None),
                device_class=BinarySensorDeviceClass.OCCUPANCY,
            )
        },
        binary_entity_values={
            DeviceKey(key="button_pressed", device_id=None): BinarySensorValue(
                device_key=DeviceKey(key="button_pressed", device_id=None),
                name="Button pressed",
                native_value=False,
            )
        },
        events={},
    )


def test_tdr40_air_low_quality():
    parser = MopekaIOTBluetoothDeviceData(MediumType.AIR)

    result = parser.update(TDR40_AIR_LOW_QUALITY_INFO_2)

    assert result == SensorUpdate(
        title=None,
        devices={
            None: SensorDeviceInfo(
                name="Pro Check Universal 7510",  # Updated name
                model="M1017",  # Updated model
                manufacturer="Mopeka IOT",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="battery_voltage", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery_voltage", device_id=None),
                device_class=SensorDeviceClass.VOLTAGE,
                native_unit_of_measurement=Units.ELECTRIC_POTENTIAL_VOLT,
            ),
            DeviceKey(key="tank_level", device_id=None): SensorDescription(
                device_key=DeviceKey(key="tank_level", device_id=None),
                device_class=SensorDeviceClass.DISTANCE,
                native_unit_of_measurement=Units.LENGTH_MILLIMETERS,
            ),
            DeviceKey(key="temperature", device_id=None): SensorDescription(
                device_key=DeviceKey(key="temperature", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="battery", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(key="reading_quality", device_id=None): SensorDescription(
                device_key=DeviceKey(key="reading_quality", device_id=None),
                device_class=None,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="reading_quality_raw", device_id=None): SensorDescription(
                device_key=DeviceKey(key="reading_quality_raw", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="accelerometer_y", device_id=None): SensorDescription(
                device_key=DeviceKey(key="accelerometer_y", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="accelerometer_x", device_id=None): SensorDescription(
                device_key=DeviceKey(key="accelerometer_x", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
        },
        entity_values={
            DeviceKey(key="battery_voltage", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery_voltage", device_id=None),
                name="Battery Voltage",
                native_value=3.0,
            ),
            DeviceKey(key="tank_level", device_id=None): SensorValue(
                device_key=DeviceKey(key="tank_level", device_id=None),
                name="Tank Level",
                native_value=141,
            ),
            DeviceKey(key="temperature", device_id=None): SensorValue(
                device_key=DeviceKey(key="temperature", device_id=None),
                name="Temperature",
                native_value=16,
            ),
            DeviceKey(key="battery", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery", device_id=None),
                name="Battery",
                native_value=100,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-49,
            ),
            DeviceKey(key="reading_quality", device_id=None): SensorValue(
                device_key=DeviceKey(key="reading_quality", device_id=None),
                name="Reading quality",
                native_value=67,
            ),
            DeviceKey(key="reading_quality_raw", device_id=None): SensorValue(
                device_key=DeviceKey(key="reading_quality_raw", device_id=None),
                name="Reading quality raw",
                native_value=2,
            ),
            DeviceKey(key="accelerometer_y", device_id=None): SensorValue(
                device_key=DeviceKey(key="accelerometer_y", device_id=None),
                name="Position Y",
                native_value=248,
            ),
            DeviceKey(key="accelerometer_x", device_id=None): SensorValue(
                device_key=DeviceKey(key="accelerometer_x", device_id=None),
                name="Position X",
                native_value=49,
            ),
        },
        binary_entity_descriptions={
            DeviceKey(key="button_pressed", device_id=None): BinarySensorDescription(
                device_key=DeviceKey(key="button_pressed", device_id=None),
                device_class=BinarySensorDeviceClass.OCCUPANCY,
            )
        },
        binary_entity_values={
            DeviceKey(key="button_pressed", device_id=None): BinarySensorValue(
                device_key=DeviceKey(key="button_pressed", device_id=None),
                name="Button pressed",
                native_value=False,
            )
        },
        events={},
    )


def test_tdr40_air_good_quality():
    parser = MopekaIOTBluetoothDeviceData(MediumType.AIR)
    service_info = TDR40_AIR_GOOD_QUALITY_INFO
    result = parser.update(service_info)

    assert result == SensorUpdate(
        title=None,
        devices={
            None: SensorDeviceInfo(
                name="TD40/TD200 7510",
                model="TD40/TD200",
                manufacturer="Mopeka IOT",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="battery_voltage", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery_voltage", device_id=None),
                device_class=SensorDeviceClass.VOLTAGE,
                native_unit_of_measurement=Units.ELECTRIC_POTENTIAL_VOLT,
            ),
            DeviceKey(key="tank_level", device_id=None): SensorDescription(
                device_key=DeviceKey(key="tank_level", device_id=None),
                device_class=SensorDeviceClass.DISTANCE,
                native_unit_of_measurement=Units.LENGTH_MILLIMETERS,
            ),
            DeviceKey(key="temperature", device_id=None): SensorDescription(
                device_key=DeviceKey(key="temperature", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="battery", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(key="reading_quality", device_id=None): SensorDescription(
                device_key=DeviceKey(key="reading_quality", device_id=None),
                device_class=None,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="reading_quality_raw", device_id=None): SensorDescription(
                device_key=DeviceKey(key="reading_quality_raw", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="accelerometer_y", device_id=None): SensorDescription(
                device_key=DeviceKey(key="accelerometer_y", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="accelerometer_x", device_id=None): SensorDescription(
                device_key=DeviceKey(key="accelerometer_x", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
        },
        entity_values={
            DeviceKey(key="battery_voltage", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery_voltage", device_id=None),
                name="Battery Voltage",
                native_value=3.53125,
            ),
            DeviceKey(key="tank_level", device_id=None): SensorValue(
                device_key=DeviceKey(key="tank_level", device_id=None),
                name="Tank Level",
                native_value=729,
            ),
            DeviceKey(key="temperature", device_id=None): SensorValue(
                device_key=DeviceKey(key="temperature", device_id=None),
                name="Temperature",
                native_value=24,
            ),
            DeviceKey(key="battery", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery", device_id=None),
                name="Battery",
                native_value=100,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-50,
            ),
            DeviceKey(key="reading_quality", device_id=None): SensorValue(
                device_key=DeviceKey(key="reading_quality", device_id=None),
                name="Reading quality",
                native_value=100,
            ),
            DeviceKey(key="reading_quality_raw", device_id=None): SensorValue(
                device_key=DeviceKey(key="reading_quality_raw", device_id=None),
                name="Reading quality raw",
                native_value=3,
            ),
            DeviceKey(key="accelerometer_y", device_id=None): SensorValue(
                device_key=DeviceKey(key="accelerometer_y", device_id=None),
                name="Position Y",
                native_value=32,
            ),
            DeviceKey(key="accelerometer_x", device_id=None): SensorValue(
                device_key=DeviceKey(key="accelerometer_x", device_id=None),
                name="Position X",
                native_value=128,
            ),
        },
        binary_entity_descriptions={
            DeviceKey(key="button_pressed", device_id=None): BinarySensorDescription(
                device_key=DeviceKey(key="button_pressed", device_id=None),
                device_class=BinarySensorDeviceClass.OCCUPANCY,
            )
        },
        binary_entity_values={
            DeviceKey(key="button_pressed", device_id=None): BinarySensorValue(
                device_key=DeviceKey(key="button_pressed", device_id=None),
                name="Button pressed",
                native_value=False,
            )
        },
        events={},
    )


STD_CHECK_OFF_TANK_INFO = BluetoothServiceInfo(
    name="",
    address="34:08:E1:29:4D:0A",
    rssi=-70,
    manufacturer_data={
        13: bytes.fromhex("00029d270c148081021d08b08104074c40c002a9294d0a")
    },
    service_uuids=["0000ada0-0000-1000-8000-00805f9b34fb"],
    service_data={},
    source="local",
)

STD_CHECK_ON_TANK_INFO = BluetoothServiceInfo(
    name="",
    address="34:08:E1:29:4D:0A",
    rssi=-78,
    manufacturer_data={
        13: bytes.fromhex("00028c212854f701103e1c3001011330d08106b8294d0a")
    },
    service_uuids=["0000ada0-0000-1000-8000-00805f9b34fb"],
    service_data={},
    source="local",
)


def _values(update: SensorUpdate) -> dict[str, object]:
    return {key.key: value.native_value for key, value in update.entity_values.items()}


def test_std_check_identifies_device() -> None:
    parser = MopekaIOTBluetoothDeviceData()
    update = parser.update(STD_CHECK_OFF_TANK_INFO)
    info = update.devices[None]
    assert info.manufacturer == "Mopeka IOT"
    assert info.model == "M1001"
    assert info.name == "Standard Check 4D0A"


def test_std_check_decodes_battery_and_temperature() -> None:
    parser = MopekaIOTBluetoothDeviceData()
    values = _values(parser.update(STD_CHECK_OFF_TANK_INFO))
    assert values["battery_voltage"] == 2.73
    assert values["temperature"] == 24.9


def test_std_check_temperature_is_stable_off_tank() -> None:
    """Off-tank captures months apart must report the same temperature."""
    september = BluetoothServiceInfo(
        name="",
        address="34:08:E1:29:4D:0A",
        rssi=-70,
        manufacturer_data={
            13: bytes.fromhex("0002a5271e28d080051c64904106111cb08003a9294d0a")
        },
        service_uuids=["0000ada0-0000-1000-8000-00805f9b34fb"],
        service_data={},
        source="local",
    )
    a = _values(MopekaIOTBluetoothDeviceData().update(september))
    b = _values(MopekaIOTBluetoothDeviceData().update(STD_CHECK_OFF_TANK_INFO))
    assert a["temperature"] == b["temperature"] == 24.9


def test_std_check_on_tank_reads_tank_temperature() -> None:
    parser = MopekaIOTBluetoothDeviceData()
    values = _values(parser.update(STD_CHECK_ON_TANK_INFO))
    assert values["battery_voltage"] == 2.59
    assert values["temperature"] == 14.2


def test_std_check_reports_distance_on_tank() -> None:
    """The strongest echo yields a reading distance to the fluid surface."""
    values = _values(MopekaIOTBluetoothDeviceData().update(STD_CHECK_ON_TANK_INFO))
    assert values["tank_level"] == 177


def test_std_check_reports_no_distance_off_tank() -> None:
    """A silent sweep is a failed read, not a zero-distance reading."""
    values = _values(MopekaIOTBluetoothDeviceData().update(STD_CHECK_OFF_TANK_INFO))
    assert values["tank_level"] is None


def test_std_check_sensor_type_ignores_reserved_bits() -> None:
    """Bits 4 and 5 of the type byte are not part of the hardware id."""
    info = BluetoothServiceInfo(
        name="",
        address="34:08:E1:29:4D:0A",
        rssi=-70,
        manufacturer_data={
            13: bytes.fromhex("00329d270c148081021d08b08104074c40c002a9294d0a")
        },
        service_uuids=["0000ada0-0000-1000-8000-00805f9b34fb"],
        service_data={},
        source="local",
    )
    assert MopekaIOTBluetoothDeviceData().update(info).devices[None].model == "M1001"


def test_std_check_echo_strength_is_zero_off_tank() -> None:
    """Every echo entry is silent when the sensor is not mounted on a tank."""
    values = _values(MopekaIOTBluetoothDeviceData().update(STD_CHECK_OFF_TANK_INFO))
    assert values["echo_strength"] == 0


def test_std_check_echo_strength_is_set_on_tank() -> None:
    """A mounted sensor returns at least one strong echo."""
    values = _values(MopekaIOTBluetoothDeviceData().update(STD_CHECK_ON_TANK_INFO))
    assert values["echo_strength"] == 14


def test_std_check_button_not_pressed() -> None:
    update = MopekaIOTBluetoothDeviceData().update(STD_CHECK_OFF_TANK_INFO)
    assert not update.binary_entity_values[
        DeviceKey(key="button_pressed", device_id=None)
    ].native_value


def test_std_check_wrong_length_is_ignored() -> None:
    info = BluetoothServiceInfo(
        name="",
        address="34:08:E1:29:4D:0A",
        rssi=-70,
        manufacturer_data={13: bytes.fromhex("00029d27")},
        service_uuids=["0000ada0-0000-1000-8000-00805f9b34fb"],
        service_data={},
        source="local",
    )
    assert not _values(MopekaIOTBluetoothDeviceData().update(info))


def test_std_check_unknown_sensor_type_is_ignored() -> None:
    payload = bytearray(bytes.fromhex("00029d270c148081021d08b08104074c40c002a9294d0a"))
    payload[1] = 0x77
    info = BluetoothServiceInfo(
        name="",
        address="34:08:E1:29:4D:0A",
        rssi=-70,
        manufacturer_data={13: bytes(payload)},
        service_uuids=["0000ada0-0000-1000-8000-00805f9b34fb"],
        service_data={},
        source="local",
    )
    assert not _values(MopekaIOTBluetoothDeviceData().update(info))


def test_std_check_requires_service_uuid() -> None:
    """Manufacturer ID 13 is Texas Instruments -- the UUID must gate it."""
    info = BluetoothServiceInfo(
        name="",
        address="34:08:E1:29:4D:0A",
        rssi=-70,
        manufacturer_data={
            13: bytes.fromhex("00029d270c148081021d08b08104074c40c002a9294d0a")
        },
        service_uuids=["0000180f-0000-1000-8000-00805f9b34fb"],
        service_data={},
        source="local",
    )
    assert not _values(MopekaIOTBluetoothDeviceData().update(info))
