---
tags:
  - contact
Affiliation: IMDEA Materials (Madrid), MIT alumnus
Position: Research Associate, MSCA Postdoctoral Fellow
Email: jorge.canada@imdeamaterials.org
Status: Draft ready, not sent
---
> [!info] Compiled with Claude on 06/11/2026 from Jorge's papers, PhD thesis, the MATE and Neosid datasheets in this vault, and web sources (listed at the bottom). Values marked ≈ were read off plots.

Related: [[MIT, Luis Fernando Velásquez-García]] · [[canada3DPrintedSoftMagnetic2024]] · [[canadaMagneticFluxGuides2026]] · [[MATE Co]] · [[MATE Co TS-2S50C]] · [[Neosid PFS9]] · [[Mahor]] · [[Print parameter varying multi-permeability]] · [[Functionally gradient material]]

## Communication
| Timestamp  | Status | Who? | Type          | Summary                                                                                   | Email link |
| ---------- | ------ | ---- | ------------- | ----------------------------------------------------------------------------------------- | ---------- |
| 06/11/2026 | Draft  | Me   | Initial email | Draft ready (see below), not sent. Do the "Before sending" checklist first.               | —          |

## Who
- **Dr. Jorge Cañada Pérez-Sala** (publishes as Jorge Cañada).
- **PhD:** MIT EECS, May 2025. Thesis: *Additive Manufacturing of Electrical Machines and Electronic Devices*, advisor Luis F. Velásquez-García. Funded by a "la Caixa" Foundation fellowship and Empiriko Corporation. Earlier co-authors at the University of Barcelona: Neus Vidal and José M. López-Villegas.
- **Now:** Research Associate at IMDEA Materials, Madrid. MSCA Postdoctoral Fellow on the project MORPHOGENESIS (self-assembling, self-monitoring, multi-stimuli-responsive implants for critical-size defects), 1 Apr 2026 – 31 Mar 2028, supervisor Dr. Andrés Díaz.
- IMDEA lists Jorge's research as additive manufacturing of electromagnetic components for medical devices. So it's still printed electromagnetics, now applied to medical devices.
- **Still linked to MIT:** co-mentors the visiting-student project "Multi-material 3D printing for electromagnetic devices" (4–5 months from Sept 2026, posted by UPM).
- **Contact:** jorge.canada@imdeamaterials.org (IMDEA staff page). Fallbacks: LinkedIn, or contact.materials@imdea.org.

## The MIT group now
- **Group:** Micro- and Nano-enabled Multiplexed Scaled-down Systems Group, MIT Microsystems Technology Laboratories. Velásquez-García is a principal research scientist (lfvelasq@mit.edu). The group website is partly outdated.
- **People on the electromagnetics line:**
	- Zoey Bigelow: EECS grad student, motor paper co-author. Works on hard magnets, magnetizing ferrite–PA12 during printing with a magnet under the bed.
	- Hector Jesus Grijalva Pazos: visiting PhD student from Tec de Monterrey. Multi-material AM and tool changing.
	- A UPM visiting student, from Sept 2026.
- **Their stated next steps:** magnetizing hard magnets during printing, rotary machines (the Fig. 23 concept in the motor paper), single-step printing on one machine, and printed robots.
- **The gap for us:** nobody visibly works on soft-magnetic inductor cores. Multi-permeability cores are proposed in the PowerMEMS paper and the thesis, but never demonstrated.
- **Visitors:** the lab hosts visiting students for 4–5 months (the UPM project, Grijalva), so an external stay is plausible later. The UPM listing asks for electrical engineering (circuits, electromagnetism, characterization), mechanical engineering (mechanisms, CAD, simulation) and extrusion printing experience.

## Key papers and what's in them

### Solenoids: Virtual and Physical Prototyping 2024 (Cañada, Kim, Velásquez-García)
- PLA dielectric, copper-PLA (Electrifi) coils, and cores in iron-PLA versus FeSiAl–PA12 pellets.
- Cites MATE's μ = 44 for unoriented particles and assumes printing doesn't orient them.
- Thanks MATE for providing pellets, and Tumaker (Spain) for printing C-cores.
- **Monolithic cored solenoids:** the nylon core's layers cooled between tool changes and didn't fuse. Printing the core separately (two-step) worked better. Their suggested fix is a temperature-controlled enclosure.

### Soft magnetic cores: PowerMEMS 2024, [[canada3DPrintedSoftMagnetic2024]]
- **Setup:** E3D ToolChanger with a Mahor v4. 0.8 mm nozzle, 0.2 mm layers, 270 °C nozzle, 90 °C bed, 1000 mm/min.
- **Permeability:** μr ≈ 31 at 1 MHz (Keysight 16454A fixture) for EM ≥ 1. Wound-core LCR data read 5–10 higher.
- **EM sweep (0.5–1.5):** μ ≈ 11.5 at 0.5, ≈ 19 at 0.75, ≈ 30 at 1.0, then flat above 1.
- **What's missing:** they call the drop below EM 1 linear and say parts reach full density at EM = 1. But no density data, no toolpath, and nothing on print quality at low EM is reported.
- **B–H at 100 Hz:** coercive field below 200 A/m, remanence below 10 mT, slow saturation above 0.15 T.
- Proposes multi-permeability inductors, citing Wang 2013 and Liu 2017.

### Flux guides: Advanced Science 2026, [[canadaMagneticFluxGuides2026]]
- **Permeability:** μr ≈ 42 by B–H (300 Hz–1 kHz) and 44 by impedance (1 kHz–1 MHz).
- **Dense parts:** extrusion width 0.75 mm on a 0.8 mm nozzle, a deliberate overlap for full density. Designs were shrunk 1 mm horizontally to compensate.
- **Flakes:** FeSiAl flakes up to 150 µm give rough surfaces, a minimum feature of about 0.8 mm and a minimum layer of 0.2 mm.
- PLA was used only as removable support.
- **Comparison and contact:** the moulded comparison material came from Max Baermann GmbH (μr ≈ 32). The corresponding author is Kiziroglou (Imperial).

### Motor: Virtual and Physical Prototyping 2026 (Cañada, Bigelow, Velásquez-García)
- **Materials:**
	- Dielectric: 3D-Fuel Pro PLA+.
	- Conductive: PriElex AG-1074 silver ink, cured at 80 °C.
	- Soft magnetic: MATE FeSiAl–PA12, 50 vol% / 86 wt%.
	- Hard magnetic: MATE strontium-ferrite–PA12, 69 vol%.
	- Flexible: FiberFlex 40D, used for the spring and as rafts so PA12 parts stick.
- Five materials on a four-tool printer, so parts were printed separately and assembled.
- **Discussion section:**
	- Sec. 5 lists the next steps.
	- Sec. 5.1 says printing in a magnetic field could orient anisotropic soft magnetic filler like their FeSiAl.
	- Sec. 5.2 covers printed bearings.
	- Fig. 23 is a rotary motor concept that could be printed in one go.
	- Sec. 5.3: PLA–nylon interfaces have low affinity and can delaminate. A single base polymer with different fillers avoids this. Interlayers or gradient-material transitions are proposed as fixes.
- **Results:** solenoids up to 2.03 mT, magnets up to 71 mT, 318 µm displacement at 41.6 Hz. About 3 hours to print and about 50 cents of material.

### Planar spiral inductors: Scientific Reports 2025 (Cañada, López-Villegas, Vidal, Nagle, Velásquez-García)
- Broadband planar inductors optimized by modulating trace width. Not read yet. It's the inductor connection.

### PhD thesis (MIT, May 2025)
- **§9.1.2:** nylon adheres poorly to PLA. FeSiAl–nylon parts are brittle and shed powder under light friction. Rough finish, no sub-millimetre features.
- **§8.2:** μr 30–40. Core loss ≈ 13 kW/m³ from a 100 Hz B–H loop, the only loss figure anywhere. Multi-permeability is stated as possible.
- **Appendix II:** the full Mahor v4 (70 W, 0.8 mm nozzle) extruder build for the E3D ToolChanger, with technical drawings.

## Answers to my original questions
1. **Why MATE, and why not PFS9?** Not answered.
	- They only justify pellets (higher filler loading) and FeSiAl–nylon over iron-PLA (μ ≈ 2).
	- MATE provided pellets, so supply was probably part of it.
	- The PFS9 datasheet is preliminary and dated 31 July 2023, around or after their choice. It's unclear whether Neosid even sells it as granulate.
2. **Problems bonding PLA and PA12?** Answered: yes, they know. The thesis (§9.1.2) and the motor paper (Sec. 5.3) both describe poor PLA–nylon adhesion and delamination. Their workarounds:
	- FiberFlex 40D rafts.
	- Separately printed parts.
	- Proposed future fixes: interlayers or gradient transitions.
3. **Did low-EM cores print well?** Not answered anywhere: no toolpath, density data or failed prints reported.

## The MATE grade question
| Grade    | Resin             | μ' at 1 MHz (5 mm / 0.6 mm ring) | Melt flow test |
| -------- | ----------------- | -------------------------------- | -------------- |
| TS-2S50C | PA12              | 44 / 94                          | 280 °C         |
| TS-3S50  | Heat-resistant PA | 39 / 74                          | 330 °C         |
| TS-1S50  | PA6               | 30 / 60                          | 280 °C         |

- **Conclusion:** Jorge's material is most likely **TS-2S50C**. It's PA12, its μ' of 44 is the value Jorge cites, and a 280 °C melt-flow test fits printing at 270 °C. HAWA's "TS-3S50" is probably a mix-up. Confirm with HAWA.
- **Vault note conflict:** [[MATE Co TS-3S50]] lists PA12 and 78% loading, which conflicts with the catalogue.
- **Loading:** all MATE FeSiAl grades are 3.9 g/cm³, which works out to ≈ 86 wt% / ~50 vol%.
- **Export:** MATE treats soft magnetic compounds as dual-use goods, which is why HAWA asks for end-user information.

## My own reasoning to keep

### Extrusion multiplier and toolpath
- **What EM does:** in Simplify3D, EM scales the flow but keeps the line spacing and layer height. Below 1 you get thinner beads, gaps between lines and less contact with the layer below, which means weaker, porous parts.
- **Mixing models**, assuming solid fraction = EM and μ = 30 when fully dense:

| Void structure                       | EM 0.75 | EM 0.5 |
| ------------------------------------ | ------- | ------ |
| Channels along the flux              | ~23     | ~15.5  |
| Randomly scattered pores             | ~20     | ~13    |
| Channels across the flux             | ~19     | ~11    |
| Sheets cutting the whole flux path   | ~3.6    | ~2     |
| **Measured (PowerMEMS)**             | **~19** | **~11.5** |

- **Takeaway:** the data can't identify the toolpath, so don't claim one. What is certain is that EM-tuned permeability depends on the mesostructure: the toolpath relative to the flux. The same EM can give different μ in different core shapes.

### Flake orientation
- **The evidence:** MATE's TS-2S50C reaches μ' 44 in a 5 mm ring and 94 in a 0.6 mm ring. PFS9 shows 50 at 4.8 mm and 80 at 1.1 mm. That points to flake alignment in thin parts.
- **What's missing:** Jorge's papers assume printing doesn't orient the flakes, and nobody has measured printed parts by direction. The motor paper (Sec. 5.1) suggests field-assisted printing to orient them.
- **For us:** a possible research angle, especially for cores where the flux crosses layers.

### Other points
- The permeability baseline is uncertain: 31 (PowerMEMS), 42–44 (Advanced Science), 44 (MATE catalogue).
- Brittle cores that shed powder need care when winding; maybe a coating.
- PA12 sticks poorly to beds and other polymers. The motor paper supports a PA12-only approach (one base polymer, different fillers).

## Final draft email
```text
Subject: Building on your FeSiAl–PA12 pellet work – a few questions from DTU

Dear Dr. Cañada,

I'm a research assistant at DTU Electro (Technical University of Denmark), where we're starting work on 3D-printed soft magnetic cores for power inductors. Your work has been crucial in choosing our starting point. In particular, your papers made a compelling case that pellet extrusion can reach much higher permeability than filament-based approaches while avoiding sintering. We now have a Mahor V5 pellet extruder and are ordering the same MATE FeSiAl–PA12 compound.

I saw that you've moved to IMDEA Materials (congratulations on the MSCA fellowship!), so I hope it's alright to ask a few things about your MIT work that I couldn't find in the papers or your thesis:

1. Were MATE's pellets a deliberate choice over other compounds (we're also looking at Neosid's PFS9), or mainly what was available?

2. You note that nylon bonds poorly to PLA. Did you ever try a compliant interlayer, like the FiberFlex 40D you used under the magnets, or neat PA12 around a core? Or did PLA win on printability?

3. Your PowerMEMS paper suggests EM-tuned multi-permeability inductors, which is close to what we'd like to explore. With EM below 1, the nozzle follows the same paths but deposits less material, so the lines come out thinner and I'd worry about weak bonding between neighbouring lines and layers. Did the low-EM cores print reliably and hold together? We'd also expect the toolpath relative to the flux to affect how much the permeability drops, so which toolpath did you use, and did you ever vary EM within a single part?

4. In your 3D-printed motor paper, you propose a rotary motor that could be printed in one go with your current setup (Fig. 23). Is anyone at MIT taking that forward, and are there other groups working toward fully printed rotary machines you'd recommend following?

Thank you for your time, and once our first results are out, I'd be happy to share them if you're interested.

Sincerely,
Artis Fils
Research Assistant, DTU Electro
Technical University of Denmark
```

## Why it's written this way
- **Jorge first, not the PI.** Jorge did the hands-on work, still co-mentors in the lab, and is the natural bridge to Velásquez-García later.
- **From me, no cc,** but tell my supervisor first. It's the group's project.
- **Disclosure:** name graded/multi-permeability cores (their own published idea, never demonstrated). Keep the pellet-blending method and the DC-bias hypothesis for a call.
- **Follow-up questions only.** Nothing already answered in the papers or thesis. The PLA question builds on what they wrote.
- **"Building on", not "continuing" his work.** "Continuing" can sound like taking over their line.
- **No promises I can't back.** The core-loss/DC-bias offer was dropped; offering to share results is enough.
- **No PhD, stay or meeting ask** in a first email. Propose a call in the reply if Jorge answers in detail.
- **No unverified inferences.** The toolpath inference was dropped after checking the numbers.

## Before sending
- [ ] Skim thesis §9.1.2 and §8.2 (the email says I read the thesis).
- [ ] Heads-up to my supervisor, and agree what to disclose.
- [ ] Confirm with HAWA that TS-2S50C is the PA12 grade.
- [ ] Send to jorge.canada@imdeamaterials.org. Follow up once after about 10 days; LinkedIn as fallback.

## If Jorge replies
- Thank Jorge, react to one answer specifically, then: "Would you be open to a short call sometime in the next few weeks? I'd love to hear more about [topic]."
- Only bring up the PhD or a visit after I've talked to my supervisor about it.

## Meeting questions

### Must-ask (30-minute call)
1. If not answered by email: the exact MATE grade, and whether you saw differences between batches.
2. Which print settings mattered most with the Mahor extruder for FeSiAl–PA12 (temperature, screw speed and flow calibration, nozzle material, drying), and what failed first when things went wrong?
3. Which toolpath did you use for the toroids (perimeters vs infill, angles), and did you ever check how μ changes with toolpath direction? *This decides whether EM grading acts like dilution or like distributed gaps.*
4. How fragile were the low-EM cores? Do you have any cross-sections or density measurements?
5. Did you ever vary EM or blend materials within one print? How long was the transition when the flow changed? *Pellet extruders lag behind flow changes.*
6. Did you see direction-dependent μ from flake alignment? MATE shows 44 vs 94 for 5 mm vs 0.6 mm rings. Has anyone tried orienting flakes during printing (Sec. 5.1, or Zoey's under-bed magnet setup)?
7. Why 31 in PowerMEMS but 42–44 in Advanced Science: measurement method, batch or process?
8. If you started this again, what would you do differently? What's the biggest pitfall?

### Material and sourcing
- How did you find MATE, did they supply samples, and was the export paperwork a problem?
- Which other compounds did you try or rule out (Toda Kogyo, Neosid, a custom Max Baermann compound), and why?
- How did you dry and store the PA12 compound? Did moisture show up as bubbles or porosity?
- Any feeding problems with pellet size or shape in the Mahor hopper (bridging, stalls)?

### Printing with the Mahor extruder
- Nozzle and screw wear from 150 µm FeSiAl flakes: did you need a hardened nozzle, and after how many kg did wear show?
- What bed surface and first-layer settings did you use for cores? Was warping a problem?
- How stable was the flow at low screw speeds? Any oozing, stringing or start/stop artifacts?
- How did you settle on a 0.75 mm extrusion width and the 1 mm shrink? How accurate were fixture-sized toroids?
- When printing several materials, did an enclosure or a different print order fix layer fusion? What was a typical tool-change time?

### Magnetic characterization
- 16454A fixture or wound ring: which do you trust, and how did you prepare samples to fit the fixture?
- Any loss data above 100 Hz? How does μ'' trend with frequency? Do the large flakes cause eddy-current losses (did you measure resistivity)?
- How far along the B–H curve did you go? Did you see inductance drop with DC current?
- Does μ drift with temperature? Any PA12 creep or PLA softening near the coils, and what was the highest temperature you saw in operation?
- Did winding wire damage the cores or make them shed powder? Did you use any coating?

### Multi-permeability and grading (share only what my supervisor OK'd)
- What stopped you from making a multi-permeability core after the PowerMEMS paper?
- What do you think of diluting the compound with neat PA12? Mahor told us the screw mixes poorly and ground masterbatch works better. How important is matching viscosity at 270 °C?
- What did you have in mind with gradient-material transitions (motor paper Sec. 5.3)? Did you try any?
- Which inductor geometry would you try first?

### Interfaces and multi-material
- Does FiberFlex 40D bond well to both PA12 and PLA, and would it work inside a part?
- Would you go all-PA12 (one base polymer)? How bad is warping with neat PA12?

### Rotary motor and the group
- What's the status of the Fig. 23 concept, and who's working on it? Which soft magnetic parts does it need, and could graded cores help?
- Who in the lab is continuing the soft magnetic work, and whose work should I follow?
- At IMDEA, are you still printing with pellets or doing electromagnetics? Is there any overlap with medical devices?

### Collaboration and visiting (later, only after rapport and talking to my supervisor)
- How do visitors usually join Velásquez-García's lab: length, funding, expectations?
- Would you be open to introducing me to Luis once our project is further along?
- Would you be interested in sharing data, or a joint paper where we extend the work to inductors?
- What makes a good visiting student in the lab?

## Path to collaboration and an external stay
1. Build rapport with Jorge: email, then a call.
2. Talk with my supervisor about a PhD and an external stay. DTU advises planning early; 3–6 months is typical. Some DTU guidance says travel grants open up for stays of 3+ months.
3. With my supervisor's backing, ask Jorge for an intro to Velásquez-García, or email lfvelasq@mit.edu referencing the exchange.
4. **Funding later:** MIT MISTI Global Seed Funds, where an MIT PI applies (usually ≤ $30k) to collaborate with groups abroad.
5. **Alternatives:** IMDEA Materials (Madrid) through Jorge; Imperial (Kiziroglou, Wright).

## Other leads
- **Kiziroglou and Wright (Imperial):** flux guides. Their PowerMEMS 2024 paper is "Challenges in Printing and Shaping Soft Magnetic Flux Guides".
- **Vidal and López-Villegas (University of Barcelona):** inductor design, Jorge's co-authors.
- **Max Baermann GmbH:** moulded soft magnetic compound (μr ≈ 32). A possible EU supplier, not yet in my company list.
- **Tumaker (Spain):** printed FeSiAl–nylon C-cores for the solenoid paper.
- **Mettes et al.:** fully 3D-printed multilayer axial-flux stator, cited in the motor paper.
- **IMDEA Materials, AM2SoftMag project:** soft magnetic metallic glass by laser powder bed fusion.
- [[elsersawyDesignPerformanceAssessment2025]]: static mixers on a Mahor extruder, relevant to blending.

## Sources
- [PhD thesis (MIT DSpace)](https://dspace.mit.edu/handle/1721.1/164065)
- [Motor paper (MIT DSpace)](https://dspace.mit.edu/handle/1721.1/165206), DOI 10.1080/17452759.2026.2613185
- [Solenoid paper (MIT DSpace)](https://dspace.mit.edu/handle/1721.1/164333), DOI 10.1080/17452759.2024.2310046
- PowerMEMS 2024 paper, DOI 10.1109/PowerMEMS63147.2024.10814238 (in vault)
- Advanced Science 2026 paper, DOI 10.1002/advs.202517310 (in vault)
- [IMDEA staff page](https://materials.imdea.org/people/dr-jorge-canada/)
- [IMDEA people listing](https://materials.imdea.org/people/)
- [IMDEA MSCA projects](https://materials.imdea.org/scope/international/)
- [UPM visiting-student listing](https://www.upm.es/gsfs/SFS49213)
- [Group publications](https://multiplexed.mit.edu/publications/referred-journal-publications/refereed-journal-publications-by-year)
- [Group graduate students](https://multiplexed.mit.edu/about/graduate-students)
- [MTL 2025 research report](https://www.mtl.mit.edu/sites/default/files/media/documents/2025/section1.pdf)
- [MIT News 2026: motor](https://news.mit.edu/2026/3d-printing-platform-rapidly-produces-complex-electric-machines-0218)
- [MIT News 2024: solenoids](https://news.mit.edu/2024/mit-engineers-3d-print-electromagnets-solenoids-0223)
- [DTU: external research stays](https://www.inside.dtu.dk/phd/The-PhD-journey/PhD-plan/Participation-in-other-research-environments)
- [DTU Space: PhD education](https://space.dtu.dk/english/phd-education)
- [MISTI faculty partnerships](https://global.mit.edu/?p=4683)
- [IMDEA AM2SoftMag](https://materials.imdea.org/new-advanced-materials-could-give-electric-motors-an-efficiency-boost/)
- MATE catalogue and Neosid PFS9 datasheet in `notes/hardware/materials/datasheets/manual parsed/`
