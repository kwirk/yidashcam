"""YI Dashcam config options"""

import enum
from types import DynamicClassAttribute


class _ExposureEnumMeta(enum.EnumMeta):
    def __getitem__(self, name):
        name = name.replace("+", "pos_").replace("-", "neg_").replace("/", "_")
        return super().__getitem__(name)


class _ResolutionEnumMeta(enum.EnumMeta):
    def __getitem__(self, name):
        if not name.startswith("r"):
            name = "r{}".format(name)
        return super().__getitem__(name)


class _ResolutionEnum(enum.IntEnum, metaclass=_ResolutionEnumMeta):
    @DynamicClassAttribute
    def name(self):
        return super().name.lstrip("r")


@enum.unique
class Option(enum.IntEnum):
    """Dashcam config options"""
    adas = 2031
    audio = 2007
    button_sound = 3041
    exposure = 2005
    firmware_version = 3012
    gsensor = 2011
    language = 3008
    model = 3035
    photo_resolution = 1002
    power_on_off_sound = 2051
    serial_number = 3037
    standby_clock = 2050
    standby_timeout = 3033
    video_auto_start = 2012
    video_length = 2003
    video_logo = 2040
    video_resolution = 2002
    video_timestamp = 2008

    # TODO = 2020
    # TODO = 2030
    # TODO = 3032


class Exposure(enum.IntEnum, metaclass=_ExposureEnumMeta):
    """Dashcam exposure values"""
    neg_2 = 12
    neg_5_3 = 11
    neg_4_3 = 10
    neg_1 = 9
    neg_2_3 = 8
    neg_1_3 = 7
    pos_0 = 6  # Default and auto
    auto = 6
    pos_1_3 = 5
    pos_2_3 = 4
    pos_1 = 3
    pos_4_3 = 2
    pos_5_3 = 1
    pos_2 = 0

    @DynamicClassAttribute
    def name(self):
        name = super().name
        return name.replace("pos_", "+").replace("neg_", "-").replace("_", "/")


@enum.unique
class GSensor(enum.IntEnum):
    """Dashcam G Sensor sensitivity"""
    low = 0
    medium = 1
    high = 2


@enum.unique
class Language(enum.IntEnum):
    """Dashcam UI language"""
    chinese_simplified = 6
    chinese_traditional = 7
    english = 0
    french = 1
    german = 4
    italian = 5
    japanese = 9
    portuguese = 3
    russian = 8
    spanish = 2


class PhotoResolution(_ResolutionEnum):
    """Dashcam photo Resolutions"""
    r640x480 = 5
    r1280x960 = 6
    r1920x1080 = 7
    r2048x1536 = 4
    r2592x1944 = 3
    r3264x2448 = 2
    r3648x2736 = 1
    r4032x3024 = 0


@enum.unique
class StandbyTimeout(enum.IntEnum):
    """Timout for screen to turn off or to clock"""
    always_on = 0
    one_minute = 1
    five_minutes = 2
    ten_minutes = 3


@enum.unique
class VideoLength(enum.IntEnum):
    """Dashcam video length"""
    #  no_limit = 0
    three_minutes = 1
    five_minutes = 2
    ten_minutes = 3


class VideoResolution(_ResolutionEnum):
    """Dashcam video resolutions"""
    r1920x1080p_30fps = 0
    r1920x1080p_60fps = 1
    r2304x1296p_30fps = 2


option_map = {
    Option.adas: bool,
    Option.audio: bool,
    Option.button_sound: bool,
    Option.exposure: Exposure,
    Option.firmware_version: str,
    Option.gsensor: GSensor,
    Option.language: Language,
    Option.model: str,
    Option.photo_resolution: PhotoResolution,
    Option.power_on_off_sound: bool,
    Option.serial_number: str,
    Option.standby_clock: bool,
    Option.standby_timeout: StandbyTimeout,
    Option.video_auto_start: bool,
    Option.video_length: VideoLength,
    Option.video_logo: bool,
    Option.video_resolution: VideoResolution,
    Option.video_timestamp: bool,
}

assert set(Option) == set(option_map)
