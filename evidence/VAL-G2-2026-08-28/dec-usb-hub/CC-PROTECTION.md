# CC-PROTECTION letter

```text
LETTER = IEC_ESD_ONLY_FOR_VAL_R0
STATUS = CLOSED_FOR_VAL
BIND_PROTECTOR = no
cc_protection on usb-interface = still OPEN until D-050 binds
```

CC1/CC2 are externally accessible **and** measured for source-current
advertisement (Rd 5.1 kΩ + sense taps on J1).

## Options evaluated

| Option | What it does | Why it is or is not VAL-R0 |
| --- | --- | --- |
| Connector IEC ESD only (no CC OVP IC) | Relies on receptacle/ESD environment | **Selected for VAL-R0.** Short-to-VBUS on CC is a named VAL bench risk, not a consumer-cable claim. |
| TPD2S300 / TPD4S201 class | CC/SBU OVP, short-to-VBUS | Evaluation pack on disk (`D5f-TI-SLVAF82B.pdf`, `D5f-TI-TPD2S300.pdf`, `D5f-TI-TPD4S201.pdf`). **Not bound.** Series R and leakage vs Rp/Rd sense are **not proven**. A lying throttle on a Default-current host is worse than no OVP IC on a mule. |

TI SLVAF82 is the application note, not a part.

## Proof required before a protector may bind

1. Series resistance in the CC path does not move the ADC tap across a
   Default / 1.5 A / 3 A decision boundary at the worst Rd tolerance.
2. Protector leakage with S3/RT unpowered does not fake a source advertisement.
3. Dead-hub / unpowered-board leakage is written.

Until those three exist, do not fit TPD2S300/TPD4S201.

## Letter

**VAL-R0: IEC connector ESD only on CC.** J1 keeps Rd + sense. No CC-protector
IC in the hub mutation list (T23a skipped). Short-to-VBUS on CC remains a
named hold. Captain may later bind a characterised protector without reopening
D-049 topology.

This closes H0c as a VAL letter. It does **not** close D-050 bind.
