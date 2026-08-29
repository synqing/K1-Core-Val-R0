# Disposable hub project identity

```text
FRIENDLY_NAME = K1-Core-Val-R0-G2.1-HUB-CANDIDATE
PROJECT_UUID  = 41c8e6523576456582ea35958b3684ed
TEAM_UUID     = 27700277ef7a49e48a0293bece6b2993
SCHEMATIC     = cffcdb562c1b48d1a5214cfc263b6c90
PAGE          = 1435cb46f39e48c8a8aadbb84ca81603
PCB           = 59bef7e87cff4cd580561703b62d8c19
NOT_LIVE      = 64325d0e55e0435abd018defb0089a9b
NOT_ORACLE    = dcd7e3cab2a24b9aa6e531d2b62e1b6f
SOURCE        = G2.1 archive 3db861a3.epro via New Project import
PRE_HASH      = 2352202:c5bf1157
PCB_COMPONENTS = 0
PCB_VIAS       = 0
SCH_COMPONENTS = 255
SCH_WIRES      = 773
```

Page and PCB UUIDs are inherited from the archive. They are the same
numbers as live and as `dcd7e3ca`. **Parent project UUID is the
discriminator.** Every write must first prove
`currentProject.uuid == 41c8e6523576456582ea35958b3684ed`.

Live product was focused when this project was created. No document-level
write was issued against live. Import used `saveTo.operation = New Project`.

**Source:** Captain, 2026-08-29 — “Create the new disposable EasyEDA hub
project… Never live 64325d0e… New disposable hub project from G2.1 archive.”

**Authority:** agent execution of Phase I under that order.
**Captain ratification: OPEN** on the imported UUID (host-assigned).
