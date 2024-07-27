"""Types for Mopeka IOT BLE advertisements.


Thanks to https://github.com/spbrogan/mopeka_pro_check for
help decoding the advertisements.

MIT License applies.
"""

from enum import Enum


class MediumType(Enum):
    """Enumeration of medium types for tank level measurements."""

    PROPANE = "propane"
    AIR = "air"
    FRESH_WATER = "fresh_water"
    WASTE_WATER = "waste_water"
    LIVE_WELL = "live_well"
    BLACK_WATER = "black_water"
    RAW_WATER = "raw_water"
    GASOLINE = "gasoline"
    DIESEL = "diesel"
    LNG = "lng"
    OIL = "oil"
    HYDRAULIC_OIL = "hydraulic_oil"
