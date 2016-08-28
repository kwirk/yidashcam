"""Unofficial module for interacting with Xiaomi YI Dashcam"""

__author__ = "Steven Hiscocks"
__version__ = "0.1"

import datetime
import enum
import logging
import ntpath
import socket
import threading
import weakref
from collections import namedtuple, OrderedDict
from xml.etree import ElementTree as ET

import requests

_LOG = logging.getLogger(__name__)


class YIDashcamException(Exception):
    """Exception for dashcam specific errors"""


class YIDashcamConnectionException(YIDashcamException):
    """Exception for loss of connection with camera"""


class YIDashcamFileException(YIDashcamException):
    """Exception for file errors with dashcam"""


@enum.unique
class Command(enum.IntEnum):
    """Dashcam commands"""
    card_info = 3039
    clock = 3034
    config = 3014
    connect = 8001
    disconnect = 8002
    file_delete = 4003
    file_get = -1  # Not really a command...
    file_list = 3015
    file_thumbnail = 4001
    mode = 3001

    def __str__(self):
        """Return value string for URL parameters"""
        return str(self.value)


@enum.unique
class Mode(enum.IntEnum):
    """Dashcam modes"""
    stream = 1
    file = 2

    def __str__(self):
        """Return value string for URL parameters"""
        return str(self.value)


@enum.unique
class Config(enum.IntEnum):
    """Dashcam config options"""
    firmware_version = 3012
    model = 3035
    serial_number = 3037
    # TODO = 1002
    # TODO = 2002
    # TODO = 2003
    # TODO = 2004
    # TODO = 2005
    # TODO = 2006
    # TODO = 2007
    # TODO = 2008
    # TODO = 2011
    # TODO = 2012
    # TODO = 2016
    # TODO = 2020
    # TODO = 2030
    # TODO = 2031
    # TODO = 2040
    # TODO = 2050
    # TODO = 2051
    # TODO = 3007
    # TODO = 3008
    # TODO = 3009
    # TODO = 3032
    # TODO = 3033
    # TODO = 3041


class YIDashcamFile(
        namedtuple('YIDashcamFile',
                   ['name', 'path', 'size', 'time', 'read_only'])):
    """Dashcam File properties"""

    @property
    def url_path(self):
        """URL path for file"""
        return self._url_path(self.path)

    @staticmethod
    def _url_path(path):
        """Convert file path for using in URLs"""
        return ntpath.splitdrive(path)[1].replace("\\", "/")


class YIDashcam():
    """Class to interact with Xiaomi YI Dashcam"""
    HOST = "192.168.1.254"

    def __init__(self, connect=True, mode=Mode.stream):
        self._config = None
        self._file_list = None
        self._mode = None
        self._heartbeat_timer = None
        if connect:
            self.connect(mode)

    def __del__(self):
        self.disconnect()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

    def _send_cmd(self, cmd, path="/", stream=False, **kwargs):
        """Send a command to the dashcam"""
        if not self.connected and cmd not in (Command.connect, Command.mode):
            raise YIDashcamException("Dashcam not connected")

        params = OrderedDict()  # Order of parameters is important
        if cmd >= 0:
            params['custom'] = 1  # Must be first!
            params['cmd'] = cmd
        params.update(kwargs)
        url = "http://{}/{}".format(self.HOST, path.lstrip("/"))
        try:
            res = requests.get(url, params=params, stream=stream, timeout=5)
            _LOG.debug("Sent dashcam command URL: %s", res.url)
            res.raise_for_status()
        except requests.exceptions.HTTPError:
            raise YIDashcamException("Bad response to command")
        except requests.exceptions.RequestException:
            raise YIDashcamException("Failed to send command")

        if stream:
            return res.iter_content(1024)  # Return iterator for data

        if res.headers.get('content-type') == "text/xml":
            res_xml = ET.fromstring(res.text)
            res_cmd = res_xml.find("Cmd")
            res_status = res_xml.find("Status")
            if res_cmd is not None and int(res_cmd.text) == cmd and \
                    res_status is not None:
                status = int(res_status.text)
                if status == -256:
                    self._heartbeat_timer.cancel()
                    self._heartbeat_timer = None
                    self._mode = None
                    raise YIDashcamConnectionException("Lost connection")
                elif status < 0:
                    raise YIDashcamException("Bad status returned: {}".format(
                        status))
                res_str = res_xml.find("String")
                return res_str.text if res_str is not None else res_status.text
        elif res.headers.get('content-type') == "text/html":
            res_html = ET.fromstring(res.text)
            res_title = res_html.find("head/title")
            if res_title is not None \
                    and res_title.text.lower() == "page not found":
                # Doesn't raise expected 404 in HTTP code
                raise YIDashcamFileException("File not found {}".format(path))
        return res.text

    def __send_heartbeat(self):
        """Send periodic heartbeat to dashcam"""
        try:
            self._heartbeat_sock.sendall(b"02:001:0")
        except socket.timeout:
            _LOG.debug("Heartbeat failed", exc_info=True)
            self._heartbeat_timer = None
            self._mode = None
        else:
            self._heartbeat_timer = threading.Timer(
                10, YIDashcam.__send_heartbeat, args=(self, ))
            self._heartbeat_timer.start()

    @property
    def connected(self):
        """Status of connection to dashcam"""
        return self._mode is not None

    @property
    def mode(self):
        """Current mode dashcam is in"""
        return self._mode

    def set_mode(self, mode):
        """Enter dashcam mode"""
        if mode not in Mode:
            raise ValueError("Invalid mode")
        try:
            self._send_cmd(Command.mode, par=mode)
        except YIDashcamException as err:
            raise YIDashcamException("Error entering mode {}".format(err))
        self._mode = mode
        if self._mode == Mode.file:
            self._file_list = None  # Cache now potentially wrong

    def connect(self, mode=Mode.stream):
        """Connect to dashcam"""
        if self.connected:
            raise YIDashcamException("Already connected")
        if mode not in Mode:
            raise ValueError("Invalid mode")

        try:
            self._send_cmd(Command.connect)
        except YIDashcamException:
            raise YIDashcamConnectionException("Failed to connect")

        self._heartbeat_sock = socket.socket(socket.AF_INET,
                                             socket.SOCK_STREAM)
        self._heartbeat_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY,
                                        1)
        self._heartbeat_sock.settimeout(10)
        self._heartbeat_sock.connect((self.HOST, 3333))
        YIDashcam.__send_heartbeat(weakref.proxy(self))

        self._config = None
        self._file_list = None
        self.set_mode(mode)
        _LOG.debug("Connected to dashcam")

    def disconnect(self):
        """Disconnect from dashcam"""
        if self.connected:
            self._heartbeat_timer.cancel()
            try:
                self._heartbeat_sock.shutdown(socket.SHUT_RDWR)
                self._heartbeat_sock.close()
                # Doesn't matter if we fail here, as dash cam will disconnect
                # itself without a heartbeat.
                self._send_cmd(Command.disconnect)
            except (OSError, YIDashcamException):
                _LOG.debug("Error disconnecting", exc_info=True)
            finally:
                self._mode = None

    @property
    def card_info(self):
        """Information of SD Card in dashcam"""
        info_et = ET.fromstring(self._send_cmd(Command.card_info))
        return {
            'type': info_et.find('CARDTYPE').text,
            'write_rate': int(info_et.find('CARDWRITERATE').text),
            'capacity': int(info_et.find('CARDCAPACITY').text),
            'vendor': int(info_et.find('CARDVENDOR').text),
            'slow_card': bool(int(info_et.find('CTNSLOWCARD').text)),
            'average_use_duration': int(info_et.find('AVGUSEDUR').text),
            'total_use': int(info_et.find('CTNTOTALUSE').text),
            # 'LDW': int(info_et.find('CTNLDW').string),
            # 'FCW': int(info_et.find('CTNFCW').string),
        }

    @property
    def config(self):
        """Config from dashcam"""
        if self._config is None:
            self._config = {}
            config_et = ET.fromstring(self._send_cmd(Command.config))
            for cmd_et, status_et in zip(
                    config_et.iter('Cmd'), config_et.iter('Status')):
                try:
                    cmd = Config(int(cmd_et.text))
                except ValueError:
                    _LOG.debug("Config option %s not recognised", cmd_et.text)
                else:
                    try:
                        status = int(status_et.text)
                    except ValueError:
                        status = status_et.text
                    self._config[cmd] = status
        return self._config.copy()

    @property
    def firmware_version(self):
        """Firmware version on dash cam"""
        return self.config[Config.firmware_version]

    @property
    def model(self):
        """Model name of dashcam"""
        return self.config[Config.model]

    @property
    def serial_number(self):
        """Serial number of dash cam"""
        return self.config[Config.serial_number]

    def set_clock(self, date_time=None):
        """Set clock on dashcam to specified time (default: 'now')"""
        if date_time is None:
            date_time = datetime.datetime.now()
        self._send_cmd(
            Command.clock, str=date_time.strftime("%Y-%m-%d_%H:%M:%S"))

    @property
    def file_list(self):
        """List of files on dashcam SD Card"""
        if not self._file_list:
            if self.mode != Mode.file:
                self.set_mode(Mode.file)
            _LOG.debug("Fetching file list from dash cam")
            files_et = ET.fromstring(self._send_cmd(Command.file_list))
            self._file_list = [
                YIDashcamFile(
                    file_.find("NAME").text, file_.find("FPATH").text,
                    int(file_.find("SIZE").text), datetime.datetime.strptime(
                        file_.find("TIME").text, "%Y/%m/%d %H:%M:%S"),
                    bool(int(file_.find("ATTR").text) & 1))
                for file_ in files_et.iter("File")
            ]
        return self._file_list.copy()

    @property
    def roadmap_list(self):
        """List of files from "roadmap" folder on dashcam SD Card"""
        return [file_ for file_ in self.file_list
                if "movie" in file_.path.lower()]

    @property
    def emergency_list(self):
        """List of files from "emergency" folder on dashcam SD Card"""
        return [file_ for file_ in self.file_list
                if "emr" in file_.path.lower()]

    def get_thumbnail(self, path):
        """Get a thumbnail for specified file on dashcam SD Card

        Returns iterator for data"""
        try:
            path = path.url_path
        except AttributeError:
            path = YIDashcamFile._url_path(path)
        yield from self._send_cmd(Command.file_thumbnail, path, stream=True)

    def get_file(self, path):
        """Get the specified file from the dashcam SD Card

        Returns iterator for data"""
        try:
            path = path.url_path
        except AttributeError:
            path = YIDashcamFile._url_path(path)
        yield from self._send_cmd(Command.file_get, path, stream=True)

    def delete_file(self, path):
        """Delete specified file from the dashcam SD Card"""
        try:
            path = path.path
        except AttributeError:
            pass
        self._send_cmd(Command.file_delete, str=path)
        self._file_list = None  # Cache now potentially wrong
