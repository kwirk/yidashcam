"""YI Dashcam config options"""

import enum


@enum.unique
class Option(enum.IntEnum):
    """Dashcam config options"""
    adas = 2031
    audio = 2007
    exposure = 2005
    firmware_version = 3012
    gsensor = 2011
    language = 3008
    model = 3035
    photo_resolution = 1002
    serial_number = 3037
    standby_clock = 2050
    video_auto_start = 2012
    video_length = 2003
    video_logo = 2040
    video_resolution = 2002
    video_timestamp = 2008

    # TODO = 2020
    # TODO = 2030
    # TODO = 2051
    # TODO = 3007
    # TODO = 3009
    # TODO = 3032
    # TODO = 3033
    # TODO = 3041


@enum.unique
class Exposure(enum.IntEnum):
    """Dashcam exposure values"""
    pos2 = 0
    pos5_3 = 1
    pos4_3 = 2
    pos1 = 3
    pos2_3 = 4
    pos1_3 = 5
    zero = 6  # Default
    neg_one_third = 7
    neg_two_thrid = 8
    neg_one = 9
    neg_four_thrid = 10
    neg_five_thrid = 11
    neg_two = 12


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


@enum.unique
class PhotoResolution(enum.IntEnum):
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
class VideoLength(enum.IntEnum):
    """Dashcam video length"""
    #  no_limit = 0
    three_minutes = 1
    five_minutes = 2
    ten_minutes = 3


@enum.unique
class VideoResolution(enum.IntEnum):
    """Dashcam video resolutions"""
    r1920x1080p_30fps = 0
    r1920x1080p_60fps = 1
    r2304x1296p_30fps = 2


option_map = {
    Option.adas: bool,
    Option.audio: bool,
    Option.exposure: Exposure,
    Option.firmware_version: str,
    Option.gsensor: GSensor,
    Option.language: Language,
    Option.model: str,
    Option.photo_resolution: PhotoResolution,
    Option.serial_number: str,
    Option.standby_clock: bool,
    Option.video_auto_start: bool,
    Option.video_length: VideoLength,
    Option.video_logo: bool,
    Option.video_resolution: VideoResolution,
    Option.video_timestamp: bool,
}

assert set(Option) == set(option_map)
