# Laser Startup Procedure
tags:: #lab #hardware #laser
created:: 2025-07-09

## Metadata
```dataview
table status, warmup_time
from "laser"
where file.name = this.file.name
```

---

## Prechecks
1. Ensure **top box switch** is **ON**.

---

## Monaco GUI
- Always open
- Do **not** change any laser settings
- **System status** should read `ready` with all green lights (except `pulsing`)
- If **laser switch is OFF**: pulsing = black  
  If **laser switch is ON**: pulsing = green
- Press `START`
- Wait 5–10 minutes  
  → Status should now read `ON`

---

## `run.batch`
- Wait for GUI to open
- Check **thermometer** — should read approximately `25°C`

---

## `Pump` Application
- Opens with subicons → select **Reference**
- May say: `State: undef`

---

## Reference Setup
1. Press `Reference`
   - If stuck at `Ref_waitref_AUX`, close window and re-open `Reference`

2. Choose: `960`, `5MHz`  
   → Should read: `State 960 Closed Saved`

3. Press `Open`  
   → You should hear the shutter click

---

## Starlab Application
- Open the Starlab application
- Confirm power reads approximately `2.5W`
- Allow system to warm up for about 1 hour  
  → Target temperature: approximately `27°C`

---

## Warm-up Status
```dataview
table temperature, power
from "laser"
where file.name = this.file.name
```
