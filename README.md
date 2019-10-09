[![Version](https://img.shields.io/badge/version-0.1.0-green.svg?style=for-the-badge)](#)
[![mantained](https://img.shields.io/maintenance/yes/2019.svg?style=for-the-badge)](#)
[![maintainer](https://img.shields.io/badge/maintainer-%20%40exKAjFASH-blue.svg?style=for-the-badge)](#)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

# Custom component for ElkoEP Lara Devices
A platform which allows you to interact with the ElkoEP Lara Devices.

## ElkoEP Lara Devices support
This custom component supports next devices:
* Lara Radio
* Lara Intercom
* Lara 5 in 1

## Installation
You can use HACS or install the component manually:

To get started put the files from `/custom_components/elkoep_lara/` in your folder `<config directory>/custom_components/elkoep_lara/`

## Configuration
**Example configuration.yaml:**

```yaml
media_player:
  - platform: elkoep_lara
    host: 192.168.1.2
    name: kitchen_lara
```

***
ElkoEP Lara is always on device, so turn on or off is not supported.
This is initial version so configured password are not supported - only default.

***
