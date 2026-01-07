---
title: Laser Startup
tags:
  - laser
  - lbm
  - calcium-imaging
  - lab
  - hardware
  - protocol
category: SOP
created: 2025-07-09
---
## Prechecks

1. Make sure you have laser-safety training
1. Never put eyes at light level, IR light can't see
1. Don't hold card too long in front of laser, especially if power is high
1. Ensure **top box switch** is **ON**.

---

## Monaco GUI

* Always open
* Do **not** change any laser settings
* **System status** should read `ready` with all green lights (except `pulsing`)
* If **laser switch is OFF**: pulsing = black  
  If **laser switch is ON**: pulsing = green
* Press `START`
* Wait 5–10 minutes  
  → Status should now read `ON`

---

## `run.batch`

* Wait for GUI to open
* Check **thermometer** — should read approximately `25°C`

---

## `Pump` Application

* Opens with subicons → select **Reference**
* May say: `State: undef`

---

## Reference Setup

1. Press `Reference`
   
   * If stuck at `Ref_waitref_AUX`, close window and re-open `Reference`
1. Choose: `960`, `5MHz`  
   → Should read: `State 960 Closed Saved`

1. Press `Open`  
   → You should hear the shutter click

---

## Starlab Application

* Open the Starlab application
* Confirm power reads approximately `2.5W`
* Allow system to warm up for about 1 hour  
  → Target temperature: approximately `27°C`

Laser Warmup Time: ~3 hours

---

\_After Laser Warmup

## Pockle Cell Calibration

* Remove power meter from laser (align dot)
* Make sure power meter is removed from laser
* Turn on pockle cell
* Place the laser mirror thing, align 180degrees
  * beam sampler
* make sure the shutter is closed via buttons
* turn on photodiode next to pockle cell
* **Make sure its plugged in**
* MATLAB -> `scanimage`
* right side: "pockle cell"
* "calibrate"
* Look for 100 or more extinction (sigmoid)
* DONE
  * Take out beam sampler
  * turn off photodiode

## Controllers

* Once photodiode is OFF
* Turn on Galvo (bottom box, switch on back)
* Turn on resonant galvo (middle)
* Get stage, place at 3mm working distance
* Get green fluoresence slide

![300](literature/lemon_keller_2015/images/IMG_2999.jpg)

* adjust the dichroic (right, move to the right)
* Turn PMT On, PMT Green On
  * PMT Gain Knob: 0.8 sweet spot, 0.9 maximum
  * Balance PMT gain and laser power
  * Used 0.8 with ~12% pockle cell laser power
* Adjust slide to working distance
* add tap water as medium, ensure no bubbles
* **Signal _ Controller** (Scanimage) GUI
* Make sure `Captive length = 4000`
* Start Continuous
  * Make sure PMT is on and cover is removed
* Actually, not sure if you need the PMT on here. Might need to turn on in next step after pockle cell calibration

## Calibrate Signal

*LBM: 224px / line, Uniform Sampling ON*

1. **Apply clock settings**
   1. If red, you lost your clock
   1. Advanced Timing Control
      1. Don't touch fill fractions

* Press "Focus" to hear galvo scream

1. Beam Controls
   1. 12%pockle cell
   1. frame rolling avg factor (attempt 10, not sure where we started)

![300](literature/lemon_keller_2015/images/IMG_3001.jpg)
![300](literature/lemon_keller_2015/images/IMG_3003.jpg)
![300](literature/lemon_keller_2015/images/IMG_3004.jpg)
![300](literature/lemon_keller_2015/images/IMG_3005.jpg)

## Cleanup

* From top to bottom: off
* For top box, first turn off red/green PMT channel, then back of box, then middle box, then bottom box
  ![300](literature/lemon_keller_2015/images/IMG_2998.jpg)
* Put power meter back in front of laser
