# ESP32-S3 USB Self-Powered VBUS Detection Extract

Source: `datasheets/D5-ESP32-S3-usb_device.html`  
URL: https://docs.espressif.com/projects/esp-usb/en/latest/esp32s3/usb_device.html  
Captured: 2026-08-28 (SHA256 in download receipt)

---

## Extracted Verbatim Text

> "VBUS is considered valid if it rises above **4.75 V** and invalid if it falls below **4.35 V**."

> "Use a resistor voltage divider that outputs **(0.75 × Vdd) if VBUS is 4.4 V** (see figure below)."

> "In either case, the voltage on the sensing pin must be logic low within **3 ms** after the device is unplugged from the USB host."

---

## Interpretation for K1

| Parameter | Value | Direction |
|-----------|-------|-----------|
| VBUS valid threshold | > 4.75 V | rising |
| VBUS invalid threshold | < 4.35 V | falling |
| Divider design point | (0.75 × Vdd) at VBUS = 4.4 V | R1/R2 ratio |
| Sense pin response time | ≤ 3 ms after unplug | falling edge |

**Implementation options (from source):**
1. A voltage comparator circuit detecting 4.35 V and 4.75 V, outputting 3.3 V logic.
2. A resistor voltage divider producing (0.75 × Vdd) when VBUS = 4.4 V — this node can be read by a GPIO.

The ESP32-S3's own I/O tolerates up to VDD (≈3.3 V), so a raw VBUS (5 V) must never be connected directly to a GPIO. The divider ratio is R2/(R1+R2) = (0.75 × 3.3) / 4.4 ≈ 0.5625, i.e. roughly a 9:7 divider.

---

## Relation to Hub Design

VBUS_DET on the USB2422 also monitors VBUS validity. The ESP32-S3 downstream port requires a separate VBUS sense path because its USB device attach/detach is signalled through this mechanism. These are two independent monitoring requirements on the same VBUS rail.
