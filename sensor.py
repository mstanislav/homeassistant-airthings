import logging
import struct
import datetime

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
from homeassistant.const import (TEMP_CELSIUS, DEVICE_CLASS_HUMIDITY, DEVICE_CLASS_TEMPERATURE, STATE_UNKNOWN)

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'airthings'
CONF_MAC = 'mac'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_MAC): cv.string,
})

MIN_TIME_BETWEEN_UPDATES = datetime.timedelta(minutes=15)
SENSOR_TYPES = [
    ['temperature', 'Temperature', TEMP_CELSIUS, None, DEVICE_CLASS_TEMPERATURE],
    ['humidity', 'Humidity', '%', None, DEVICE_CLASS_HUMIDITY],
    ['short_radon', 'Short-term Radon', 'pCi/L', 'mdi:cloud', None],
    ['long_radon', 'Long-term Radon', 'pCi/L', 'mdi:cloud', None],
]

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    _LOGGER.debug("Starting airthings")
    reader = AirthingsWaveDataReader(config.get(CONF_MAC))
    add_devices([ AirthingsSensorEntity(reader, key, name, unit, icon, device_class) for [key, name, unit, icon, device_class] in SENSOR_TYPES])

class AirthingsWaveDataReader:
    def __init__(self, mac):
        self._mac = mac
        self._state = { }

    def get_data(self, key):
        if key in self._state:
            return self._state[key]
        return STATE_UNKNOWN

    @property
    def mac(self):
        return self._mac

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        _LOGGER.debug("Airthings updating data")
        import pygatt
        from pygatt.backends import Characteristic
        adapter = pygatt.backends.GATTToolBackend()
        char = 'b42e2a68-ade7-11e4-89d3-123b93f75cba'

        try:
            adapter.start(reset_on_start=False)
            device = adapter.connect(self._mac)
            value = device.char_read_handle('0x000d',timeout=10)
            data = struct.unpack('<4B8H', value)
            self._state['humidity'] = data[1] / 2.0
            self._state['short_radon'] = round(data[4] / 37, 2)
            self._state['long_radon'] = round(data[5] / 37, 2)
            self._state['temperature'] = data[6] / 100.0
        finally:
            adapter.stop()

class AirthingsSensorEntity(Entity):
    """Representation of a Sensor."""

    def __init__(self, reader, key, name, unit, icon, device_class):
        """Initialize the sensor."""
        self._reader = reader
        self._key = key
        self._name = name
        self._unit = unit
        self._icon = icon
        self._device_class = device_class

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Airthings {}'.format(self._name)

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._icon

    @property
    def device_class(self):
        """Return the icon of the sensor."""
        return self._device_class

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._reader.get_data(self._key)

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def unique_id(self):
        return '{}-{}'.format(self._reader.mac, self._name)

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._reader.update()
