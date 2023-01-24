from bluetooth_sensor_state_data import BluetoothServiceInfo, SensorUpdate
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

from mopeka_iot_ble.parser import MopekaIOTBluetoothDeviceData

PRO_SERVICE_INFO = BluetoothServiceInfo(
    name="",
    address="C9:F3:32:E0:F5:09",
    rssi=-63,
    manufacturer_data={89: b"\x08rF\x00@\xe0\xf5\t\xf0\xd8"},
    service_uuids=["0000fee5-0000-1000-8000-00805f9b34fb"],
    service_data={},
    source="local",
)


def test_can_create():
    MopekaIOTBluetoothDeviceData()


def test_pro():
    parser = MopekaIOTBluetoothDeviceData()
    service_info = PRO_SERVICE_INFO
    result = parser.update(service_info)
    assert result == SensorUpdate(
        title=None,
        devices={
            None: SensorDeviceInfo(
                name="Pro+ F509",
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
                native_unit_of_measurement=None,
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
                name="Battery " "Voltage",
                native_value=3.5625,
            ),
            DeviceKey(key="tank_level", device_id=None): SensorValue(
                device_key=DeviceKey(key="tank_level", device_id=None),
                name="Tank " "Level",
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
                name="Signal " "Strength",
                native_value=-63,
            ),
            DeviceKey(key="reading_quality", device_id=None): SensorValue(
                device_key=DeviceKey(key="reading_quality", device_id=None),
                name="Reading " "quality",
                native_value="low",
            ),
            DeviceKey(key="reading_quality_raw", device_id=None): SensorValue(
                device_key=DeviceKey(key="reading_quality_raw", device_id=None),
                name="Reading " "quality " "raw",
                native_value=1,
            ),
            DeviceKey(key="accelerometer_y", device_id=None): SensorValue(
                device_key=DeviceKey(key="accelerometer_y", device_id=None),
                name="Position " "Y",
                native_value=216,
            ),
            DeviceKey(key="accelerometer_x", device_id=None): SensorValue(
                device_key=DeviceKey(key="accelerometer_x", device_id=None),
                name="Position " "X",
                native_value=240,
            ),
        },
        binary_entity_descriptions={
            DeviceKey(key="occupancy", device_id=None): BinarySensorDescription(
                device_key=DeviceKey(key="occupancy", device_id=None),
                device_class=BinarySensorDeviceClass.OCCUPANCY,
            )
        },
        binary_entity_values={
            DeviceKey(key="occupancy", device_id=None): BinarySensorValue(
                device_key=DeviceKey(key="occupancy", device_id=None),
                name="Occupancy",
                native_value=False,
            )
        },
        events={},
    )
