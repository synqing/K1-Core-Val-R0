# USB2422 Errata Hold — DS00001576A

Source: `datasheets/D3-USB2422-Errata-DS00001576A.pdf`  
Captured: 2026-08-29

---

## Anomaly 1 — Low-Speed Keep-Alive Traffic is not Resumed in 3ms

In Full-Speed mode the hub does not produce a keep-alive strobe within 3 ms of a SOF, potentially allowing a Low-Speed device to enter suspend. No known real-world implications; will not be addressed.

## Anomaly 2 — Disconnect Event Occurs when Hub is Operating at Full-Speed

When an adjacent downstream port disconnects during a simultaneous data transfer, packet corruption on the other port can infrequently cause a full hub disconnect. Work-around: 100 pF caps on downstream DP/DM. Will not be addressed.

## Anomaly 3 — High-Speed Split Transaction to Full-Speed ← HOLD

> **Description:** If a High-Speed (HS) split transaction exceeds 288 bytes per microframe to a single downstream port, the Transaction Translator of the USB2422 could be corrupted if another HS data packet is sent before the Full-Speed packets downstream have completed.
>
> **End User Implications:** The corrupted data would be caught by the USB error checks in most applications, causing the host to resend the data to the device with no visibility to the end user. However, if the data is not checked by the device and streamed to a speaker for example, the corrupted data can negatively impact the performance of the device.
>
> **Work around:** There is no known work around at this time.
>
> **Plan:** This will not be addressed in a future revision of the device.

**Design note:** This anomaly is relevant to the K1 audio path. If RT1062 issues HS bulk or isochronous split transactions >288 bytes/µframe to the ESP32-S3 downstream port, TT corruption is possible with no recovery path. Document as a design constraint; limit bulk transfer sizes or use HS-only topology if feasible.

---

*Text quoted verbatim from DS00001576A page 1–2.*
