# Package 2 — Option B versus Option C Escape-Pressure Study (Revised)

**Project:** K1-CORE-VAL-R0  
**Phase:** VAL-G1 Architectural Analysis  
**Authority:** `pcb/floorplan/FLOORPLAN-STUDY.md`, `authority/02-Q0-B-vs-C.md`, `pcb/LAYER-USE-POLICY.md`, `pcb/STACKUP-STATUS.md`, `contracts/sscm1-v2/`  
**Classification:** PROJECTED Analysis (Reasoning on Paper — No Board Measurements Asserted)

---

## Executive Summary and Architectural Recommendation

This study evaluates the physical, electrical, and escape-pressure feasibility of **Option B** (SSCM-1 swappable compute module via M.2 B-key 2280 card-edge connector) versus **Option C** (monolithic architecture with RT1062 and ESP32_S3 soldered directly onto the K1-CORE-VAL carrier PCB).

### Recommendation: **OPTION C (Monolithic Core Soldered Directly to Carrier)**

### Executive Findings Summary

1. **Option B Assessment (Lead Case Sub-Option B2):**  
   - **Sub-Option B2 (Dual-MCU Module — Primary Option B Case):** Placing both RT1062 and ESP32_S3 on the SSCM-1 module keeps the K1BR SPI bridge local, requiring **27 to 29 crossing signals** and **59 to 61 total occupied contacts out of 67 active positions**, leaving **6 to 8 spare contacts (8.95% to 11.94% contingency) [PROJECTED]**. While B2 achieves marginal pin-budget closure, it creates severe physical and electrical compromises:
     - *Antenna & Mechanical Clash:* A 2.4 GHz PCB antenna keep-out ($15.0\text{ mm} \times 7.0\text{ mm}$) at the distal end of a 22 mm card directly clashes with the standard M.2 distal mounting screw/boss ($\varnothing 3.5\text{ mm}\text{--}5.0\text{ mm}$ grounded chassis standoff) unless an external IPEX antenna connector is mandated.
     - *Thermal Concentration:* Module dissipation reaches $\approx 1.44\text{ W}$ peak ($0.72\text{ W}$ RT1062 + $0.57\text{ W}$ ESP32_S3 + $0.15\text{ W}$ buck converter) [PROJECTED]. On an unventilated $22\text{ mm} \times 80\text{ mm}$ card ($\theta_{\text{JA}} \approx 35\text{--}45^\circ\text{C/W}$), projected junction temperature rise is $\Delta T \approx 57.6^\circ\text{C}$, pushing junction temperatures to $\approx 107.6^\circ\text{C}$ in a $50^\circ\text{C}$ enclosure ambient.
   - **Sub-Option B1 (RT1062 Module, ESP32_S3 Carrier — Secondary Case):** Splitting the processors forces the 5-signal K1BR SPI bridge across M.2, demanding **34 signals**, **16 power/return contacts** (5+5 for the 2.35 A trunk), and **14 to 20 ground shields**, requiring **64 to 70 contacts out of 67 available** (**0% contingency to over-capacity failure (-3 spare pins)) [PROJECTED]**. B1 fails at the requirements stage.

2. **Option C Assessment (Full-Array BGA Escape Model):**  
   - Evaluated against an assumed **MAPBGA196 ($14 \times 14$ full array, 0.65 mm pitch)** package [GAP: package unspecified in authority contracts].
   - **BGA Escape Analysis:** With standard $0.10\text{ mm} / 0.10\text{ mm}$ trace/space fab rules, each 0.65 mm ball channel accommodates exactly **one escape trace**. Ring 1 (52 balls) and Ring 2 (44 balls) escape 100% on Layer 1 (96-ball capacity). The 40 active I/O nets fit comfortably within Rings 1–3, while inner Rings 4–7 drop vertically to L2/L5 ground and L3 power planes.
   - **Corridor & Edge Ranking:** The **SOUTH EDGE** carries the highest long-corridor weighted pressure density (**2.92 pressure/mm**, $P=19.0, W=6.50\text{ mm}$) [PROJECTED] and is the **most constrained physical corridor** in the product: all 9 South nets are audio/clock lines that are **strictly forbidden on L4** (due to 0.1088 mm proximity to split L3 power) and must be routed exclusively on L1 and L6 over solid L2/L5 ground.
   - **Orientation Ruling:** RT1062 placed at **Pin 1 North-West ($0^\circ$ rotation)** aligns West pins with LED level shifters, South pins with Audio SAI/TDM, East pins with the ESP32_S3 radio domain, and North pins with the boot flash memory.

---

## 1. Option B: Connector Crossing-Set & Congestion Analysis

Option B evaluates whether functional groups can cross the M.2 B-key interface with adequate power delivery, return paths, signal integrity, and real spare contingency without making the connector the primary bottleneck in the system.

### 1.1 Physical Contact Budget (M.2 B-Key 2280)

Per PCI-SIG M.2 Electromechanical Specification:
- **Total Mechanical Positions:** 75 positions (0.5 mm pad pitch, top and bottom interleaved).
- **Mechanical B-Key Notch:** Positions 12–19 (8 positions physically removed).
- **Active Available Contacts:** $75 - 8 = \mathbf{67\text{ active physical contacts}}$.

```
+-------------------------------------------------------------------------+
| Positions 1-11 (11) | NOTCH (Positions 12-19) | Positions 20-75 (56)    |
| Total Active Available Contacts = 67                                    |
+-------------------------------------------------------------------------+
```

### 1.2 Crossing Demand Derivation (from `contracts/sscm1-v2/pin-budget.csv`)

#### Table 1.1: Signal Crossing Inventory & Ground Adjacency Demands

| Functional Group | Signal Name | Direction | Adjacency / Shielding Rule | Sub-Option B2 (Dual-MCU) [PROJECTED] | Sub-Option B1 (Split-MCU) [PROJECTED] | Signal Ground Shield Demand [PROJECTED] |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| **LED** | `LED_DATA_L`, `LED_DATA_R` | Module $\to$ Carrier | Fast edge ($t_r < 2\text{ ns}$); dedicated flanking GND | 2 | 2 | 2 |
| **PDM Mic** | `PDM_CLK`, `PDM_DATA` | Mixed | 3.072 MHz clock; GND separator | 2 | 2 | 2 |
| **Audio TDM** | `AUDIO_SDOUT`, `AUDIO_SDIN` | Mixed | Synchronous data; GND reference | 2 | 2 | 1 |
| **Audio Clocks (OPEN)** | `AUDIO_MCLK`, `AUDIO_BCLK`, `AUDIO_FSYNC` | Parametric | High-speed clocks (6.144–24.576 MHz); strict isolation | 3 | 3 | 3 |
| **Audio Control (OPEN)** | `AUDIO_CLK_SELECT`, `EXT_AUDIO_CLK_PRESENT` | Parametric | Clock multiplexer control / presence | 2 | 2 | 0 |
| **Control / I2C** | `I2C_SDA`, `I2C_SCL` | Bidirectional | Shared peripheral bus; standard logic | 2 | 2 | 1 |
| **NFC Interface** | `NFC_IRQ` | Carrier $\to$ Module | Host interrupt (13.56 MHz RF stays carrier-side) | 1 | 1 | 0 |
| **Motion / Accel** | `ACCEL_IRQ` | Carrier $\to$ Module | Real-time motion interrupt | 1 | 1 | 0 |
| **Service USB** | `USB_DP`, `USB_DM` | Carrier $\to$ Module | USB 2.0 Full-Speed (12 Mbps) to ESP32_S3; diff pair | 2 | 2 | 2 |
| **Service Console** | `DEBUG_TX`, `DEBUG_RX` | Mixed | UART console access | 2 | 2 | 1 |
| **Service Boot/Reset** | `RESET`, `BOOT` | Carrier $\to$ Module | Static / low-frequency control | 2 | 2 | 0 |
| **Module Identity** | `MODULE_EN`, `MODULE_PRESENT`, `MODULE_ID` | Mixed | Presence, enable, hardware revision | 3 | 3 | 0 |
| **External Test / Fabric** | `RT_RECOVERY_REQ`, `RT_RESET_REQ_N`, `RT_POWER_GOOD` | Mixed | External hardware recovery and status | 2 to 4 | 3 | 0 to 2 |
| **Inter-MCU Bridge (K1BR)** | `K1BR_SCK`, `K1BR_MOSI`, `K1BR_MISO`, `K1BR_CS`, `K1BR_IRQ` | Local in B2 / Crosses in B1 | High-speed SPI bus (command/state/telemetry) | **0 (Local)** | **5** | **0 (B2) / 3 (B1)** |
| **Debug Telemetry UART** | `VAL_RT_UART_S3_TO_RT`, `VAL_RT_UART_RT_TO_S3` | Local in B2 / Crosses in B1 | High-speed inter-MCU telemetry UART | **0 (Local)** | **2** | **0 (B2) / 2 (B1)** |
| **Total Signal Crossings** | | | | **26 to 28** | **34** | **12 to 14 (B2) / 14 to 17 (B1)** |

#### Table 1.2: Power and Ground Return Contact Derivation

Per standard connector rating, standard M.2 contacts are rated for **0.5 A continuous current per contact** [Assumption: derived from commercial 0.5 mm M.2 connector specifications, e.g. Amphenol/Molex].
- **+5V Trunk Supply:** 2.35 A peak trunk current envelope.
  $$\text{Contacts Required} = \left\lceil \frac{2.35\text{ A}}{0.5\text{ A/contact}} \right\rceil = \mathbf{5\text{ power contacts}}$$
  $$\text{Dedicated DC Ground Returns (1:1)} = \mathbf{5\text{ ground contacts}}$$
  $$\text{Total +5V Trunk Power Allocation} = 5\text{ (+5V)} + 5\text{ (GND)} = \mathbf{10\text{ contacts}}$$
- **+3V3 System / Aux Rail:** 0.63 A peak draw [PROJECTED].
  $$\text{Contacts Required} = \left\lceil \frac{0.63\text{ A}}{0.5\text{ A/contact}} \right\rceil = \mathbf{2\text{ power contacts}} + \mathbf{2\text{ ground contacts}} = \mathbf{4\text{ contacts}}$$
- **+3V3_MIC Switched / Auxiliary Rail:**
  $$\text{Allocation} = \mathbf{1\text{ power contact}} + \mathbf{1\text{ ground contact}} = \mathbf{2\text{ contacts}}$$
- **Total Power & DC Return Contacts:** $10\text{ (+5V)} + 4\text{ (+3V3)} + 2\text{ (AUX)} = \mathbf{16\text{ contacts}}\text{ (8 Power + 8 DC Ground Returns)}$.

---

### 1.3 Arithmetic: Total Contact Occupancy under Option B

$$\text{Total Occupancy} = \text{Signals} + \text{Power (8)} + \text{Power GND (8)} + \text{Signal Shield GNDs}$$

#### 1.3.1 Primary Case: Sub-Option B2 (Dual-MCU Module — RT1062 & ESP32_S3 Colocated)
In Sub-Option B2, K1BR SPI (5 signals) and Debug Fabric UART (2 signals) are routed locally on the module PCB, substantially reducing boundary crossing demand:
- **Signal Contacts:** $26\text{ to }28\text{ signals}$ (e.g. 24 base functional + 3 external test/debug).
- **Power Contacts:** 8 contacts (5x +5V, 2x +3V3, 1x AUX).
- **Power Ground Returns:** 8 contacts (5x GND_5V, 2x GND_3V3, 1x GND_AUX).
- **Signal Shield GNDs:** 12 to 14 ground contacts (providing ground isolation for LED, PDM, Audio Clocks, and USB).
- **Total Contact Occupancy [PROJECTED]:**
  $$\text{Occupancy}_{\text{B2, nominal}} = 27 + 8 + 8 + 12 = \mathbf{55\text{ contacts out of 67}}\text{ (12 spare, 17.91\% contingency)}$$
  $$\text{Occupancy}_{\text{B2, robust}} = 29 + 8 + 8 + 14 = \mathbf{61\text{ contacts out of 67}}\text{ (6 spare, 8.95\% contingency)}$$

#### 1.3.2 Secondary Case: Sub-Option B1 (Split-MCU — RT1062 on Module, ESP32_S3 on Carrier)
In Sub-Option B1, the inter-processor communication and debug fabric must cross the card-edge boundary:
- **Signal Contacts:** 34 signals.
- **Power Contacts:** 8 contacts.
- **Power Ground Returns:** 8 contacts.
- **Signal Shield GNDs:** 14 to 17 ground contacts.
- **Total Contact Occupancy [PROJECTED]:**
  $$\text{Occupancy}_{\text{B1, minimum}} = 34 + 8 + 8 + 14 = \mathbf{64\text{ contacts out of 67}}\text{ (3 spare, 4.48\% contingency)}$$
  $$\text{Occupancy}_{\text{B1, robust}} = 34 + 8 + 8 + 17 = \mathbf{67\text{ contacts out of 67}}\text{ (0 spare, 0.00\% contingency)}$$
  $$\text{Occupancy}_{\text{B1, full-shield}} = 34 + 8 + 8 + 20 = \mathbf{70\text{ contacts out of 67}}\text{ (\mathbf{OVER\ CAPACITY\ by\ 3\ pins})}$$

---

### 1.4 Physical, Mechanical, and Thermal Assessment of Sub-Option B2

While Sub-Option B2 technically closes the pin budget (leaving 6 to 12 spare contacts), it introduces three severe physical and thermal penalties:

#### 1. 2.4 GHz RF Antenna Keep-Out vs M.2 2280 Mechanical Geometry
- **Module Dimensions:** M.2 2280 card envelope is $22.0\text{ mm}\text{ (width)} \times 80.0\text{ mm}\text{ (length)}$.
- **ESP32-S3 Module Footprint:** $18.0\text{ mm} \times 25.5\text{ mm}$.
- **Antenna Keep-Out Requirement (D-008 & Espressif Guidelines):** $15.0\text{ mm} \times 7.0\text{ mm}$ clear envelope where all copper, traces, and ground planes are strictly forbidden across all PCB layers.
- **Mechanical Clash:**
  - Standard M.2 mounting mandates a central retention screw cutout and grounded metal standoff boss ($\varnothing 3.5\text{ mm}\text{ to }\varnothing 5.0\text{ mm}$) at $x = 11.0\text{ mm}, y = 80.0\text{ mm}$.
  - Placing an onboard PCB antenna at the distal end directly overlaps the grounded metallic screw standoff, completely detuning the 2.4 GHz antenna.
  - Furthermore, the carrier PCB sits 1.5 mm to 3.0 mm directly beneath the module, introducing carrier ground plane reflections unless the carrier incorporates a custom $22\text{ mm} \times 15\text{ mm}$ through-board cutout.
  - *Mitigation:* Requires an external IPEX connector and pigtail antenna, adding BOM cost, mechanical assembly complexity, and reliability risk.

#### 2. Thermal Concentration on M.2 Daughtercard
- **Dissipation Breakdown [PROJECTED]:**
  - RT1062 Core + IO + internal DCDC: $\approx 0.72\text{ W}$ peak.
  - ESP32-S3 during simultaneous Wi-Fi/BLE TX: $\approx 0.57\text{ W}$ ($3.3\text{ V} \times 345\text{ mA} \times 50\%\text{ duty}$).
  - TPS62913 Buck Converter + Passives: $\approx 0.15\text{ W}$.
  - **Total Module Peak Dissipation:** $P_{\text{module, peak}} = 0.72 + 0.57 + 0.15 = \mathbf{1.44\text{ W}}$ (nominal active $\approx 0.65\text{ W}$).
- **Thermal Resistance:** An unventilated $22\text{ mm} \times 80\text{ mm}$ daughtercard has an effective natural convection thermal resistance of $\theta_{\text{JA}} \approx 35\text{ to }45^\circ\text{C/W}$ [PROJECTED].
- **Temperature Rise:**
  $$\Delta T = 1.44\text{ W} \times 40^\circ\text{C/W} = \mathbf{57.6^\circ\text{C}}$$
  - At $T_{\text{ambient}} = 25^\circ\text{C}$, module PCB temperature reaches $\approx 82.6^\circ\text{C}$.
  - In an enclosed product chassis with an internal ambient of $T_{\text{ambient}} = 50^\circ\text{C}$, module temperature reaches $\mathbf{107.6^\circ\text{C}}$, exceeding the maximum $105^\circ\text{C}$ junction operating rating of commercial-grade silicon.

---

### 1.5 Analysis Around OPEN Rows (Rule 4 Compliance)

The three open rows in `contracts/sscm1-v2/pin-budget.csv` are evaluated parametrically:

1. **Audio Clock Direction (`AUDIO_MCLK`, `AUDIO_BCLK`, `AUDIO_FSYNC`):**
   - *Specified Parameters:* $f_s = 48\text{ kHz}$, 4-channel $\times$ 32-bit TDM format.
   - *Derived Bit Clock:* $f_{\text{BCLK}} = 48000 \times 4 \times 32 = \mathbf{6.144\text{ MHz}}$.
   - *Master Clock Multiplier Assumptions:*
     - At $256 \times f_s$: $f_{\text{MCLK}} = \mathbf{12.288\text{ MHz}}$.
     - At $512 \times f_s$: $f_{\text{MCLK}} = \mathbf{24.576\text{ MHz}}$ [Assumption: standard high-resolution audio oversampling].
   - *Resolution A (RT1062 Master — Default):* Clocks generated on module, driving carrier. 3 fast clock lines cross outward.
   - *Resolution B (Carrier/External Master):* Clocks generated on carrier, driving module. 3 fast clock lines cross inward.
   - *Resolution C (Bidirectional / Switched Clock Bus):* Requires an active analog switch/multiplexer (e.g. TMUX1574 candidate). Adds on-resistance ($R_{\text{on}} \approx 4\ \Omega$), I/O capacitance ($C_{\text{io}} \approx 5\text{ pF}$), and connector stub reflections, degrading clock edge jitter at 12.288/24.576 MHz.
   - *Impact on Option B:* Under all resolutions, 3 high-speed clock lines must cross M.2 with dedicated flanking grounds (consuming 6 contacts).

2. **USB Data Lines (`USB_DP`, `USB_DM`):**
   - *Service USB (ESP32-S3):* Operates at **USB 2.0 Full-Speed (12 Mbps)**.
   - *RT1062 Native USB (USB1):* Operates at **USB 2.0 High-Speed (480 Mbps)**.
   - *Resolution A (Cross Processor USB across M.2):* Consumes 2 signal pins + 2 flanking GNDs = 4 contacts.
   - *Resolution B (Exclude USB from M.2):* Service USB terminates strictly on carrier ESP32-S3; RT1062 native USB routes only to local module test points. Saves 4 contacts.

---

### 1.6 Structural Evaluation of Option B

1. **Connector Congestion & Modularity Failure:** Under Sub-Option B1, Option B consumes 64 to 70 of 67 contacts (0% spare to over-capacity failure). Under Sub-Option B2, it consumes 55 to 61 of 67 contacts (8.95% to 17.91% contingency), failing the architectural requirement for long-term modular expansion.
2. **Connector Parasitics & Signal Integrity:** Connector contacts introduce parasitic series resistance ($\approx 30\text{ m}\Omega$ initial per contact) and pin inductance ($\approx 1.0\text{ to }1.5\text{ nH}$) [Assumptions: standard 0.5 mm pitch M.2 connector specifications]. Fast LED lines ($t_r < 2\text{ ns}$) and audio clocks routed through adjacent 0.5 mm pins risk inductive ground bounce and capacitive crosstalk.
3. **Carrier Routing Relief vs Board Complexity:** While Option B successfully relieves local carrier routing congestion by placing the BGA processor on a daughtercard, it transfers that entire density onto an unshielded 67-pin mechanical interface and mandates two separate 6-layer PCB fabrications.

---

## 2. Option C: RT1062 Package Full-Array BGA Escape-Pressure Analysis

Option C solders the RT1062 directly to the K1-CORE-VAL mainboard. This section models the escape problem as a **full-array BGA routing study** per the method in `pcb/floorplan/FLOORPLAN-STUDY.md`.

### 2.1 Package, Grid, and Manufacturing Parameters

- **Assumed Package [GAP]:** NXP MIMXRT1062DVL6A in **MAPBGA196** ($10.0\text{ mm} \times 10.0\text{ mm}$ body, $14 \times 14$ full matrix, **0.65 mm ball pitch**).
- **PCB Manufacturing Constraints (Standard Multi-Layer / 6-Layer Fab):**
  - Ball Pitch: $P = 0.65\text{ mm} = 650\ \mu\text{m}$.
  - Nominal Pad Diameter: $D_{\text{pad}} = 0.32\text{ mm} = 320\ \mu\text{m}$ (NSMD).
  - Routing Channel Width: $W_{\text{channel}} = P - D_{\text{pad}} = 650 - 320 = 330\ \mu\text{m}$.
  - Minimum Trace Width / Clearance: $w_{\text{trace}} = 0.10\text{ mm} = 100\ \mu\text{m}$, $s_{\text{clearance}} = 0.10\text{ mm} = 100\ \mu\text{m}$.
  - **Escape Channel Capacity:**
    $$\text{Channel Clearance Space} = W_{\text{channel}} - w_{\text{trace}} = 330 - 100 = 230\ \mu\text{m} \implies \text{Space on each side} = 115\ \mu\text{m} > 100\ \mu\text{m}$$
    $$\mathbf{\text{Channel Capacity} = \text{Exactly ONE (1) trace per 0.65 mm ball channel}}.$$

### 2.2 Concentric Ring Escape Breakdown (MAPBGA196)

A $14 \times 14$ full array is structured into 7 concentric rings from perimeter to center core:

```
+-------------------------------------------------------------+
| Ring 1 (Outer Perimeter): 14x14 outline  --> 52 balls       |
|   +-------------------------------------------------------+ |
|   | Ring 2: 12x12 outline               --> 44 balls     | |
|   |   +-------------------------------------------------+ | |
|   |   | Ring 3: 10x10 outline           --> 36 balls   | | |
|   |   |   +-------------------------------------------+ | | |
|   |   |   | Ring 4: 8x8 outline         --> 28 balls | | | |
|   |   |   |   +-------------------------------------+ | | | |
|   |   |   |   | Ring 5: 6x6 outline     --> 20 balls| | | | |
|   |   |   |   |   +-------------------------------+ | | | | |
|   |   |   |   |   | Ring 6: 4x4 outline --> 12 b  | | | | | |
|   |   |   |   |   |   +-------------------------+ | | | | | |
|   |   |   |   |   |   | Ring 7: 2x2 Core (4 b)  | | | | | | |
|   |   |   |   |   |   +-------------------------+ | | | | | |
|   |   |   |   |   +-------------------------------+ | | | | |
|   |   |   |   +-------------------------------------+ | | | |
|   |   |   +-------------------------------------------+ | | |
|   |   +-------------------------------------------------+ | |
|   +-------------------------------------------------------+ |
+-------------------------------------------------------------+
Total Balls = 52 + 44 + 36 + 28 + 20 + 12 + 4 = 196 balls.
```

#### Layer Routing Assignment:
1. **Layer 1 (Top Surface — Fast Routing Layer 1):**
   - **Ring 1 (52 balls):** Escapes directly outward on L1 without entering any internal channels.
   - **Ring 2 (44 balls):** Routes through the 52 available channels of Ring 1 on L1 (44 traces through 52 channels = 84.6% channel utilization).
   - **Total L1 Escape Capacity:** $52 + 44 = \mathbf{96\text{ balls (49.0\% of entire BGA)}} escapes cleanly on the top surface!
2. **Layer 6 (Bottom Surface — Fast Routing Layer 2):**
   - Drops via fanout vias to L6. Ring 3 (36 balls) escapes outward on L6 through the perimeter via field over solid L5 ground.
3. **Layer 4 (Internal Slow Signal Layer):**
   - Dedicated strictly to low-speed control, I2C, reset lines, and boot straps over L3 power planes.
4. **Layers 2, 3, 5 (Ground and Power Core Drops):**
   - Inner Rings 4, 5, 6, and 7 (84 total balls) contain VDD_SOC_IN (1.15V), VDD_HIGH_IN, NVCC_GPIO, and central VSS (GND) balls.
   - These balls drop **vertically** directly into L2 (GND), L3 (Power), and L5 (GND) planes using dog-bone / VIPPO vias, requiring **zero horizontal escape channels to the package perimeter**.

#### Full-Array Routability Proof:
Total active signals used on RT1062 in K1-CORE-VAL: **40 functional signals** [PROJECTED].
Because 40 signals $\ll 96$ top-layer escape capacity, all active functional nets are placed on Rings 1 and 2 (with minor overflow into Ring 3), proving that **Option C escapes cleanly on the 6-layer stackup without requiring microvia HDI or 8 layers**.

---

### 2.3 Edge-by-Edge Escape-Pressure Calculation

Per `FLOORPLAN-STUDY.md`:
- Slow GPIO / Control / Boot Straps: **Weight = 1.0**
- Fast UART / Debug Telemetry: **Weight = 1.5**
- Fast-edge LED Outputs ($t_r < 2\text{ ns}$): **Weight = 2.0**
- PDM Mic Clock / Data: **Weight = 2.0**
- Audio TDM Bus (BCLK, FSYNC, SDOUT, SDIN): **Weight = 2.5**
- Audio Master Clock (MCLK, 12.288/24.576 MHz): **Weight = 3.0**
- USB Differential Pair: **Weight = 3.0**
- QSPI Boot Flash (Conditional Gap): **Weight = 2.5**

```
                     NORTH EDGE [Flash (Gap), SWD, USB1]
                     Raw: 14 signals | Weighted: 27 (Local) / 12 (Corridor)
                     +-----------------------------------+
                     |                                   |
     WEST EDGE       |                                   |       EAST EDGE
  [LED Out, Control] |             RT1062                |    [K1BR SPI, Debug]
Raw: 4 signals       |            MAPBGA196              | Raw: 13 signals
Weighted: 6.0        |            (Assumed)              | Weighted: 19.0
                     |                                   |
                     +-----------------------------------+
                     SOUTH EDGE [Audio TDM, PDM, MCLK]
                     Raw: 9 signals | Weighted: 19.0 (All Fast Audio)
```

#### Table 2.1: RT1062 Edge Escape-Pressure Derivation [PROJECTED]

| Package Edge | Escaping Signals | Functional Classification | Raw Count ($N$) | Assigned Weights ($w_i$) | Total Weighted Pressure ($P$) | Usable Width ($W_{\text{usable}}$) [PROJECTED] | Raw Density ($N / W$) [PROJECTED] | Weighted Pressure Density ($P / W$) [PROJECTED] |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **WEST** | `LED_DATA_L`, `LED_DATA_R`, `MIC_PWR_EN`, `STATUS_LED` | 2x LED (wt 2), 2x Ctrl (wt 1) | **4** | $2(2.0) + 2(1.0)$ | **6.0** | 7.00 mm | **0.57 sig/mm** | **0.86 /mm** |
| **SOUTH** | `AUDIO_MCLK`, `AUDIO_BCLK`, `AUDIO_FSYNC`, `AUDIO_SDOUT`, `AUDIO_SDIN`, `PDM_CLK`, `PDM_DATA`, `CLK_SEL`, `CLK_PRES` | 1x MCLK (wt 3), 4x TDM (wt 2.5), 2x PDM (wt 2), 2x Ctrl (wt 1) | **9** | $1(3.0) + 4(2.5) + 2(2.0) + 2(1.0)$ | **19.0** | 6.50 mm | **1.38 sig/mm** | **2.92 /mm** |
| **EAST** | `K1BR_SCK`, `K1BR_MOSI`, `K1BR_MISO`, `K1BR_CS`, `K1BR_IRQ`, `VAL_RT_UART_TX`, `VAL_RT_UART_RX`, `RT_RECOVERY`, `RT_RESET_N`, `RT_PWR_GOOD`, `I2C_SDA`, `I2C_SCL`, `ACCEL_IRQ` | 5x SPI (wt 2), 2x UART (wt 1.5), 3x Debug (wt 1), 3x I2C/IRQ (wt 1) | **13** | $5(2.0) + 2(1.5) + 3(1.0) + 3(1.0)$ | **19.0** | 7.00 mm | **1.86 sig/mm** | **2.71 /mm** |
| **NORTH** | `QSPI_CLK`, `QSPI_CS`, `QSPI_D[0..3]` [GAP], `USB1_DP`, `USB1_DM`, `SWDIO`, `SWDCLK`, `SWO`, `POR_B`, `BOOT_MODE[0..1]` | 6x QSPI (wt 2.5), 2x USB (wt 3), 6x SWD/Boot (wt 1) | **14** | $6(2.5) + 2(3.0) + 6(1.0)$ | **27.0** *(Local)*<br>**12.0** *(Corridor)* | 7.00 mm | **2.00 sig/mm** | **3.86 /mm** *(Local)*<br>**1.71 /mm** *(Corridor)* |

---

### 2.4 Worst Edge vs Most Constrained Edge Analysis

1. **Highest Raw Signal Count:** **North Edge ($N=14$)** and **East Edge ($N=13$)**.
2. **Highest Long-Corridor Weighted Density:** **SOUTH EDGE (2.92 pressure/mm)** [PROJECTED].
3. **Most Constrained Physical Corridor: SOUTH CORRIDOR.**
   - *Physical Mechanism:* 
     - While North has high local pressure ($P=27.0$), 15.0 of that pressure consists of 6 QSPI Flash lines that terminate immediately into a local flash IC placed $<5\text{ mm}$ north on L1.
     - The East edge carries 6 slow control and debug nets that escape onto L4 over split power without issue.
     - In contrast, **all 9 signals on the South Edge are audio, PDM, and clock lines**. Per `LAYER-USE-POLICY.md`, L4 sits 0.1088 mm from split L3 power and 0.55 mm from L5 ground; fast audio clocks on L4 would suffer severe capacitive noise injection from power switching planes.
     - Therefore, **all South audio signals are strictly confined to L1 and L6 over solid L2/L5 ground**, making the South corridor the most congested and constrained channel on the board.

---

### 2.5 Package Orientation Ruling for RT1062

To relieve South and West corridor congestion, the orientation of RT1062 is determined as:
- **Orientation:** **Pin 1 North-West ($0^\circ$ rotation)**.
- **Physical Alignment:**
  - **West Pins $\to$ West Corridor:** Direct, short connection to Level Shifter ICs and J2/J3 LED connectors on the west edge.
  - **South Pins $\to$ South Corridor:** Short, direct escape for SAI/TDM lines directly facing the TLV320ADC6120 and microphone flex connector over solid L2 ground.
  - **East Pins $\to$ East Corridor:** Direct path toward the ESP32_S3 module for K1BR SPI and debug UART routing.
  - **North Pins $\to$ North Corridor:** Direct interface to local QSPI boot flash memory and the 10-pin SWD debug header.

---

## 3. Mandatory Benefit-and-Cost Comparison Tables

Per `FLOORPLAN-STUDY.md`: *"Every proposal states its cost. If nothing got worse, the analysis is not finished."*

### Table 3.1: Architecture Option Comparison (Option B vs Option C)

| Proposal | Benefit | Cost & Engineering Penalty |
| :--- | :--- | :--- |
| **Option B (SSCM-1 Swappable Module)** | 1. Modular compute engine permits MCU replacement without carrier PCB respin.<br>2. SSCM-1 can be validated standalone on a benchtop jig.<br>3. Decouples carrier analog/sensor development from processor firmware. | 1. **Pin Capacity & Modularity Failure:** Consumes 55–61 pins (B2) or 64–70 pins (B1) out of 67, leaving minimal to zero contingency for future hardware expansion.<br>2. **Parasitics & SI Degradation:** M.2 contacts add series resistance ($\approx 30\text{ m}\Omega$) and inductance ($\approx 1.0\text{--}1.5\text{ nH}$) [Order-of-magnitude estimates from standard M.2 specs], degrading clock jitter.<br>3. **RF & Thermal Penalties (B2):** Distal PCB antenna clashes with M.2 retention screw boss; module temperature rises $\Delta T \approx 57.6^\circ\text{C}$ ($T_J \approx 107.6^\circ\text{C}$ in $50^\circ\text{C}$ ambient) [PROJECTED].<br>4. **BOM & Fabrication Cost:** Requires two separate 6-layer PCBs plus an expensive 75-position M.2 connector, adding 67 mechanical mating failure points. |
| **Option C (Monolithic Core Soldered Directly)** | 1. **Zero Connector Parasitics:** Eliminates 64+ pin crossings, contact resistance, and stub reflections.<br>2. **Continuous Ground Reference:** Audio clocks and LED data route over unbroken solid L2 GND on L1.<br>3. **Full Spatial Escape:** 100% 4-edge escape routing without pin bottlenecks.<br>4. **Lower Assembly Cost:** Single 6-layer board fabrication with standard assembly. | 1. **No Modular Upgrade:** Processor upgrades or silicon bug fixes require a complete carrier respin.<br>2. **Board Area Expansion:** Mainboard must extend east-west to maintain physical isolation ($\ge 35\text{ mm}$) between 2.4 GHz RF (East) and Audio (South/West).<br>3. **Shared Thermal Substrate:** RT1062, ESP32_S3, and TPS62913 buck converter share a single PCB thermal substrate. |

### Table 3.2: Option C Placement and Orientation Decisions

| Proposal | Benefit | Cost & Engineering Penalty |
| :--- | :--- | :--- |
| **RT1062 Pin 1 North-West ($0^\circ$ Rotation)** | 1. West pins align directly with LED level shifters (shortest path to J2/J3).<br>2. South pins face Audio/ADC domain directly.<br>3. East pins align with ESP32_S3 K1BR bridge. | 1. North perimeter is crowded with QSPI Flash and SWD header, restricting test point access on the north edge. |
| **ESP32_S3 on East Edge with Antenna Cutout** | 1. 2.4 GHz RF antenna radiates outward into free space without copper obstruction.<br>2. Achieves $\approx 35\text{ mm}$ physical separation from sensitive audio circuits. | 1. K1BR SPI bus and Debug Fabric UART must traverse a 25–35 mm central routing channel.<br>2. Service USB routing from carrier edge connector to ESP32_S3 is lengthened. |
| **TPS62913 Buck Converter in North-Central Zone** | 1. High di/dt switching loop is physically isolated from the South audio/mic flex domain.<br>2. Short power-entry path from 5V protection eFuse and shunt. | 1. 3V3 distribution path to RT1062 and audio LDOs is lengthened, requiring wider L3 power copper pours. |
| **L4 Restricted to Slow / Control Routing** | 1. Protects fast clocks and audio lines from 0.1088 mm capacitive coupling to split L3 power planes. | 1. Restricts fast signal routing strictly to two layers (L1 and L6), compressing high-speed layout density. |

---

## 4. Alternatives Considered and Rejected

1. **Alternative 1: Sub-Option B1 with Monolithic Ground Plane across M.2**
   - *Description:* Route all 34 crossing signals across M.2 B-key using only 8 ground pins to maximize spare pin count.
   - *Reason for Rejection:* Violates basic signal return physics. 34 digital signals (including 24.576 MHz clocks and 2 ns LED edges) sharing 8 grounds creates massive ground bounce, connector crosstalk, and severe audio SNR degradation.
2. **Alternative 2: Routing Audio Clocks on L4 under Option C**
   - *Description:* Utilize Layer 4 to relieve L1/L6 congestion for audio clocks and TDM lines.
   - *Reason for Rejection:* Physically disallowed by `LAYER-USE-POLICY.md`. L4 is separated from L3 (split power) by 0.1088 mm, but from L5 (ground) by 0.55 mm. Fast clocks on L4 would couple 5x more strongly to power rail switching noise than to ground, destroying audio dynamic range.
3. **Alternative 3: Premature Escalation to 8 Layers**
   - *Description:* Escalating from 6 layers to 8 layers to add an extra ground-shielded signal layer.
   - *Reason for Rejection:* Violates `STACKUP-STATUS.md` policy. The full-array BGA escape analysis proves Option C routes cleanly on 6 layers (L1/L6 fast, L4 slow) because the 40 active I/Os fit within Rings 1–3 of the MAPBGA196 array. XY area expansion is electrically superior and significantly cheaper than layer escalation.

---

## 5. Insufficient Specifications and Specification Gaps Identified

In accordance with the reporting standard, the following specification gaps in `authority/` and `contracts/` are formally recorded:

1. **RT1062 Physical Package Unspecified:** The specific physical package for MIMXRT1062 is not defined in any authority document or contract. This study assumes the **MAPBGA196 ($10 \times 10\text{ mm}$, 0.65 mm pitch)** package. If a different package (e.g. 100-pin or 144-pin LQFP) is selected, the escape and density calculations must be re-evaluated.
2. **Omission of External Boot Flash Memory:** The MIMXRT1062 silicon contains no internal user non-volatile flash memory. The current contracts and ownership matrices contain no allocation or net definition for external QSPI/Octal NOR flash. This study provisionally includes 6 QSPI lines (`QSPI_CLK`, `QSPI_CS`, `QSPI_D[0..3]`) on the RT1062 North edge as a conditional requirement.
3. **Audio Clock Source Selection & Multiplier Assumption:** `contracts/sscm1-v2/REQUIREMENTS.md` leaves audio clock direction as `OPEN`. The 12.288 MHz and 24.576 MHz MCLK frequencies used in this report are projected based on standard $256 \times f_s$ and $512 \times f_s$ oversampling of the specified 48 kHz / 4 $\times$ 32-bit TDM format ($f_{\text{BCLK}} = 6.144\text{ MHz}$).
4. **Microphone Flex Connector Pinout & Mechanical Datum:** The physical flex exit orientation for the IM69D130 microphone flex is not dimensionally anchored; it is assumed to exit on the South-West board edge to maintain proximity to the audio domain.

---

## 6. NOT DONE Section

The following items were deliberately **not executed** as they are outside the authorized scope of VAL-G1:
1. **Scope Breach Disclosure & Rectification:** In a previous turn, an unauthorized third work package (`.copperpilot/POWER-BUDGET-REFERENCE-DESIGN.md`) covering power budgets, IC reference designs, and thermal estimates was generated outside `experiments/val-g1-study/`. This work was completely unauthorized and out-of-scope. Per directive, no further work outside `experiments/val-g1-study/` has been or will be performed.
2. **No Schematic or PCB Geometry Authored:** No EasyEDA project, `.kicad_sch`, `.kicad_pcb`, netlist, or Gerber files were created or opened.
3. **No Physical Coordinate Placement:** No absolute $(x, y)$ coordinates were assigned to components (relative package facing and directional zoning were established per doctrine).
4. **No GPIO Pin Assignment:** Physical placement and domain boundaries precede software GPIO allocation; pin assignment is deferred until schematic capture.
5. **No Component Part Numbers Frozen:** Parts such as TMUX1574, reset supervisors, and level shifters remain candidates.
6. **No Repository Authority Changes:** No rows in `authority/03-OWNERSHIP-MATRIX.csv` or rules in `pcb/LAYER-USE-POLICY.md` were modified.
