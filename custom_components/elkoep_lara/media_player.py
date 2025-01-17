"""Support for interface with an ElkoEP Lara devices."""
import asyncio
from datetime import timedelta
import logging
from urllib.parse import urlparse
from typing import Dict

import voluptuous as vol

from elkoep_lara import LaraClient
__version__ = '0.1.0'

from homeassistant import util
from homeassistant.components.media_player import (
    PLATFORM_SCHEMA as MEDIA_PLAYER_PLATFORM_SCHEMA,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
)
from homeassistant.components.media_player import MediaPlayerEntity, PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_CUSTOMIZE,
    CONF_FILENAME,
    CONF_HOST,
    CONF_NAME,
    CONF_TIMEOUT,
    STATE_OFF,
    STATE_PAUSED,
    STATE_PLAYING,
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.script import Script

_LOGGER = logging.getLogger(__name__)

CONF_SOURCES = "sources"

DEFAULT_NAME = "Lara Radio"

LARA_CONFIG_FILE = "elkoep_lara.conf"

CUSTOMIZE_SCHEMA = vol.Schema(
    {vol.Optional(CONF_SOURCES): vol.All(cv.ensure_list, [cv.string])}
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_CUSTOMIZE, default={}): CUSTOMIZE_SCHEMA,
        vol.Optional(CONF_FILENAME, default=LARA_CONFIG_FILE): cv.string,
        vol.Optional(CONF_HOST): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_TIMEOUT, default=8): cv.positive_int,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the ElkoEP Lara platform."""
    if discovery_info is not None:
        host = urlparse(discovery_info[1]).hostname
    else:
        host = config.get(CONF_HOST)

    if host is None:
        _LOGGER.error("No Lara found in configuration file or with discovery")
        return False

    name = config.get(CONF_NAME)
    customize = config.get(CONF_CUSTOMIZE)
    timeout = config.get(CONF_TIMEOUT)

    config = hass.config.path(config.get(CONF_FILENAME))

    add_entities(
        [LaraDevice(host, name, customize, config, timeout)],
        True,
    )
    return True



class LaraDevice(MediaPlayerEntity):
    """Representation of a ElkoEP Lara Device."""

    _attr_media_content_type = MediaType.CHANNEL
    _attr_supported_features = (
        MediaPlayerEntityFeature.NEXT_TRACK
        | MediaPlayerEntityFeature.PAUSE
        | MediaPlayerEntityFeature.PREVIOUS_TRACK
        | MediaPlayerEntityFeature.VOLUME_MUTE
        | MediaPlayerEntityFeature.VOLUME_SET
        | MediaPlayerEntityFeature.VOLUME_STEP
        | MediaPlayerEntityFeature.SELECT_SOURCE
        | MediaPlayerEntityFeature.PLAY
    )

    def __init__(self, host, name, customize, config, timeout):
        """Initialize the webos device."""

        self._lara = LaraClient(host)
        result = self._lara.init()
        _LOGGER.warning("Lara device initialization %s", result)
        self._customize = customize

        self._name = name
        current_input = self._lara.station
        if self._lara.playing:
          self._state = STATE_PLAYING
        else:
          self._state = STATE_PAUSED
        self._volume = self._lara.volume_level

    def update(self):
        if not self._lara.initialized:
            result = self._lara.init()
            if result == 0:
                return
        """Retrieve the latest data."""
        from websockets.exceptions import ConnectionClosed

        try:
            if self._lara.SendLoadStatusPacket() == 0:
              current_input = self._lara.station
              if self._lara.playing:
                self._state = STATE_PLAYING
              else:
                self._state = STATE_PAUSED
              self._volume = self._lara.volume_level
            else:
              current_input = ''
              self._state = STATE_PAUSED
              self._volume = 0
        except (OSError, ConnectionClosed, TypeError, asyncio.TimeoutError):
            self._state = STATE_OFF
            self._current_source = None
            self._current_source_id = None
            self._channel = None

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def is_volume_muted(self):
        #"""Boolean if volume is currently muted."""
        return False

    @property
    def volume_level(self):
        """Volume level of the media player (0..1)."""
        return self._volume

    @property
    def source(self):
        return self._lara.station

    @property
    def source_list(self):
        return self._lara.stations

    @property
    def media_title(self):
        return self._lara.station

    @property
    def media_image_url(self):
        """Image url of current playing media."""
        return None

    def volume_up(self):
        self._lara.volume_up()

    def volume_down(self):
        self._lara.volume_down()

    def set_volume_level(self, volume):
        self._volume = volume
        self._lara.volume_set(volume * 100)

    def mute_volume(self, mute):
        self._volume = 0
        self._lara.volume_mute()

    def media_play_pause(self):
        """Simulate play pause media player."""
        if self._state == STATE_PLAYING:
            self._state = STATE_PAUSED
            self._lara.pause()
        else:
            self._state = STATE_PLAYING
            self._lara.play()

    def select_source(self, source):
        """Select input source."""
        item_index = self._lara.stations.index(source)
        self._lara.select_station(item_index)

    def play_media(self, media_type, media_id, **kwargs):
        """Play a piece of media."""
        _LOGGER.debug("Call play media type <%s>, Id <%s>", media_type, media_id)

    def media_play(self):
        if self._state == STATE_PAUSED:
          self._state = STATE_PLAYING
          self._lara.play()

    def media_pause(self):
        if self._state == STATE_PLAYING:
            self._state = STATE_PAUSED
            self._lara.pause()

    def media_next_track(self):
        self._lara.next()

    def media_previous_track(self):
        self._lara.previous()
