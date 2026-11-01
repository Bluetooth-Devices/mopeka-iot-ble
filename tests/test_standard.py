"""Tests for Mopeka Standard "Check" sensor decoding.

Constructed advertisements with hand-verified expected outputs. The decoder was
also validated against real hardware (readings matched the Mopeka Check phone
app). Algorithm ported from ESPHome's ``mopeka_std_check`` component.
"""

from bluetooth_sensor_state_data import BluetoothServiceInfo, SensorUpdate

from mopeka_iot_ble import MopekaIOTBluetoothDeviceData

STD_SERVICE_UUID = "0000ada0-0000-1000-8000-00805f9b34fb"
PRO_SERVICE_UUID = "0000fee5-0000-1000-8000-00805f9b34fb"


def _service_info(
    manufacturer_data: dict[int, bytes],
    service_uuid: str,
    address: str = "AA:BB:CC:DD:EE:F0",
    rssi: int = -55,
) -> BluetoothServiceInfo:
    return BluetoothServiceInfo(
        name="MOPEKA",
        address=address,
        rssi=rssi,
        manufacturer_data=manufacturer_data,
        service_data={},
        service_uuids=[service_uuid],
        source="test",
    )


def _values(update: SensorUpdate) -> dict[str, object]:
    return {key.key: value.native_value for key, value in update.entity_values.items()}


def test_standard_check_decodes() -> None:
    """A Standard advertisement with one strong echo decodes fully."""
    # data_1=0x02 (Standard), raw_voltage=0xE0, raw_temp=42, one strong echo
    # (time_0=4, value_0=15) in the first measurement block.
    data = bytes([0x00, 0x02, 0xE0, 0x2A, 0xE4, 0x03] + [0] * 13)
    device = MopekaIOTBluetoothDeviceData()
    service_info = _service_info({13: data}, STD_SERVICE_UUID)

    assert device.supported(service_info)
    values = _values(device.update(service_info))
    assert values["temperature"] == 30.2
    assert values["battery"] == 100.0
    assert values["battery_voltage"] == 3.25
    assert values["tank_level"] == 35
    assert values["reading_quality_raw"] == 31
    assert values["reading_quality"] == 100


def test_standard_check_no_usable_echo() -> None:
    """No usable echo -> tank level is None, temp/battery still report."""
    data = bytes([0x00, 0x02, 0xE0, 0x2A] + [0] * 15)
    device = MopekaIOTBluetoothDeviceData()
    values = _values(device.update(_service_info({13: data}, STD_SERVICE_UUID)))
    assert values["tank_level"] is None
    assert values["temperature"] == 30.2
    assert values["battery"] == 100.0


def test_standard_check_unsupported_hardware_id() -> None:
    """An unknown hardware id on the Standard service is ignored."""
    data = bytes([0x00, 0x11, 0xE0, 0x2A] + [0] * 15)
    device = MopekaIOTBluetoothDeviceData()
    assert not device.supported(_service_info({13: data}, STD_SERVICE_UUID))


def test_pro_still_supported() -> None:
    """The Pro path is unaffected by adding Standard support."""
    data = bytes([0x0C, 90, 60, 0x10, 0x40, 0, 0, 0, 7, 9])
    device = MopekaIOTBluetoothDeviceData()
    values = _values(
        device.update(
            _service_info({89: data}, PRO_SERVICE_UUID, address="AA:BB:CC:DD:EE:F1")
        )
    )
    assert values["temperature"] == 20
    assert values["tank_level"] == 6
