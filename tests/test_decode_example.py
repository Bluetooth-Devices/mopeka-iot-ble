"""Tests for the standalone ``examples/decode_advertisement.py`` helper."""

import importlib.util
from pathlib import Path

import pytest

_EXAMPLE_PATH = (
    Path(__file__).resolve().parent.parent / "examples" / "decode_advertisement.py"
)
_spec = importlib.util.spec_from_file_location("decode_advertisement", _EXAMPLE_PATH)
assert _spec is not None and _spec.loader is not None
decode_example = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(decode_example)


# A real Pro Plus "good quality" advertisement payload (see tests/test_parser.py).
GOOD_PAYLOAD = b"\x08rF\x00\xc0\xe0\xf5\t\xf0\xd8"
GOOD_ADDRESS = "C9:F3:32:E0:F5:09"


@pytest.mark.parametrize(
    "raw",
    [
        "08724600c0e0f509f0d8",
        "08 72 46 00 c0 e0 f5 09 f0 d8",
        "08:72:46:00:c0:e0:f5:09:f0:d8",
        "08-72-46-00-c0-e0-f5-09-f0-d8",
        "0x08 0x72 0x46 0x00 0xc0 0xe0 0xf5 0x09 0xf0 0xd8",
        r"\x08\x72\x46\x00\xc0\xe0\xf5\x09\xf0\xd8",
    ],
)
def test_parse_hex_payload_accepts_common_separators(raw):
    assert decode_example.parse_hex_payload(raw) == GOOD_PAYLOAD


@pytest.mark.parametrize("raw", ["", "   ", "zz", "08x"])
def test_parse_hex_payload_rejects_garbage(raw):
    with pytest.raises(ValueError):
        decode_example.parse_hex_payload(raw)


def test_decode_returns_named_sensors():
    update = decode_example.decode(
        GOOD_ADDRESS, GOOD_PAYLOAD, decode_example.MediumType.PROPANE
    )
    names = {v.name for v in update.entity_values.values()}
    assert "Temperature" in names
    assert "Battery Voltage" in names
    assert "Tank Level" in names
    # device was recognised as a Pro Plus (model byte 0x08)
    assert any(d.model == "M1015" for d in update.devices.values())


def test_format_update_is_human_readable():
    update = decode_example.decode(
        GOOD_ADDRESS, GOOD_PAYLOAD, decode_example.MediumType.PROPANE
    )
    text = decode_example.format_update(update)
    assert "Pro Plus" in text
    assert "Temperature" in text
    assert "Button pressed" in text  # binary sensor is rendered too


def test_main_prints_report(capsys):
    rc = decode_example.main([GOOD_ADDRESS, "08724600c0e0f509f0d8"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Sensors:" in out
    assert "Temperature" in out


def test_main_rejects_unknown_model_byte(capsys):
    # model byte 0xff is not in DEVICE_TYPES -> parser returns no device
    rc = decode_example.main([GOOD_ADDRESS, "ff724600c0e0f509f0d8"])
    err = capsys.readouterr().err
    assert rc == 1
    assert "not recognised" in err


def test_main_rejects_bad_hex(capsys):
    rc = decode_example.main([GOOD_ADDRESS, "nothex"])
    err = capsys.readouterr().err
    assert rc == 2
    assert "valid hex" in err
