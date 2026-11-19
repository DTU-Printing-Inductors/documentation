---
W Compatibility with PA: 1
W Cost: 1
W Process simplicity: 1
W Adaption maturity: 1
W Availability: 1
W Implementation simplicity: 1
W Conductivity: 1
---
## Matrix
![[State-of-the-art category evaluation matrix.base]]

# State-of-the-art evaluation criteria

The weights are the `W …` properties above. [[State-of-the-art category evaluation matrix.base]] reads them from this note, so change a weight here and every total updates.

**Scoring:** each category note in `Categories/` gets a score from **1 to 5** per criterion, using a property with the criterion's exact name (e.g. `Cost: 3`). **5 is always best**, so for cost, 5 means cheapest.

**Total** = Σ(weight × score) / Σ(weight), counting only criteria that have a score. It's a weighted average on the same 1–5 scale.
## Compatibility with PA
Can it be co-processed with the polyamide (PA12) soft-magnetic core material?
- **5:** Directly bonds to PA.
- **3:** Intermediate material is needed.
- **1:** Incompatible bonding, and there's no intermediate material.

## Process simplicity
How many steps after printing before the part is usable?
- **5:** usable as printed
- **3:** Needs curing
- **1:** needs sintering

## Adaption maturity (availability)
How established is the approach?
- **5:** Commercial products
- **3:** Commercial as the company will develop the material, large MOQ or long lead time
- **1:** Research level or a patent, needs to be made in-house

## Implementation simplicity
Effort to run it on our setup (Mahor V5 pellet extruder).
- **5:** runs on the in-house available FDM
- **3:** runs on the in-house available FGF
- **1:** needs a different extruder
## Conductivity
Ranked by in order of their relative positions on the conductivity scale.
- **6:** The best
- **5:** 
- **4:** 
- **3:** 
- **2:** 
- **1:** The worst