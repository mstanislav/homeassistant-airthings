# homeassistant-airthings (Airthings Wave)

## Supplemental README from mstanislav
This is a fork of https://github.com/gkreitz/homeassistant-airthings that changes a few things. Notably, I am using the Wave -- not Wave Plus -- so I stripped out the extra bits not relevant to my unit's feature set. I've also adjusted the Radon readings to be in pCi/L insead of Bq/m3, because that's what the app uses in the U.S. and my previous monitor used, too. I've changed the class name to relect that it is for the Wave, not WavePlus as before. Lastly, I've also poached some small bits of code from https://github.com/Airthings/wave-reader/blob/master/read_wave2.py to save some confusion.

Thanks to Gunnar Kreitz for publishing the initial repository!

## Modified Original README from gkreitz

1. Find out the MAC address of your Airthings Wave. See https://airthings.com/us/raspberry-pi/ for how to find MAC address.
1. Put `__init__.py`, `sensor.py`, `manifest.json` into `<config>/custom_components/airthings/` on your home assistant installation (where `<config>` is the directory where your config file resides).
1. Add the following to your `configuration.yaml` (or modify your `sensor` heading, if you already have one):
```yaml
sensor:
  - platform: airthings
    mac: 00:11:22:AA:BB:CC # replace with MAC of your Airthings Wave
```

Then restart home assistant and if everything works, you'll have some new sensors named `sensor.airthings_{humidity,long_radon,pressure,short_radon,temperature}`
