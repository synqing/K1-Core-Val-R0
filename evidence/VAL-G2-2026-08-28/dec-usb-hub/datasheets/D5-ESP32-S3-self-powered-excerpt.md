# D5 — Espressif ESP32-S3 USB Device snapshot (2026-08-29)

Source HTML saved as `D5-ESP32-S3-usb_device.html` from:

https://docs.espressif.com/projects/esp-usb/en/latest/esp32s3/usb_device.html

## Native PHY pins

> The ESP32-S3 routes the **USB 1.1 peripheral** D+ and D- signals to GPIOs 20 and 19 respectively.

## One PHY

> The ESP32-S3 contains two USB controllers: USB-OTG and USB-Serial-JTAG. However, both controllers share a **single PHY**, which means only one can operate at a time.

## Self-Powered Device (quoted)

> USB specification mandates self-powered devices to monitor voltage levels on USB’s VBUS signal. As opposed to bus-powered devices, a self-powered device can be fully functional even without a USB connection. The self-powered device detects connection and disconnection events by monitoring the VBUS voltage level. VBUS is considered valid if it rises above 4.75 V and invalid if it falls below 4.35 V.

Options listed on that page:

- Connect VBUS to a voltage comparator that detects 4.35 V and 4.75 V, and outputs a 3.3 V logic level.
- Use a resistor voltage divider that outputs (0.75 × Vdd) if VBUS is 4.4 V.

> In either case, the voltage on the sensing pin must be logic low within 3 ms after the device is unplugged from the USB host.

TinyUSB: `tinyusb_phy_config_t::self_powered` and `tinyusb_phy_config_t::vbus_monitor_io`.
