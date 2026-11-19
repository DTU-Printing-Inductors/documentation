---
Grade: n/a
Manufacturer: n/a
Supplier: n/a
Type: n/a
Functionality: n/a
Matrix: "PETG, PA, ..."
Filler: "Low CNT loading / inherently dissipative polymers (IDP)"
Filler loading: n/a
Size: n/a
Feedstock format: "Filament"
Permeability: n/a
Surface resistivity (Ω/sq): n/a
Surface resistance (Ω): n/a
Surface resistance standard: n/a
Volume resistivity (Ω·m): "1e6-1e9"
Volume resistivity standard: n/a
Dielectric properties: n/a
Thermal conductivity integral (W/m·K): n/a
Thermal conductivity integral standard: n/a
Thermal conductivity in-plane (W/m·K): n/a
Thermal conductivity through-plane (W/m·K): n/a
Thermal conductivity directional standard: n/a
MOQ: n/a
Price: n/a
Lead time: n/a
Status: "To validate"
Datasheet: n/a
Processing instructions: n/a
Plot category: "Antistatic"
Entry type: "Range"
Plots:
  - "Overview"
Commercial status: "Commercial AM feedstock"
Plot label: "Antistatic filaments"
Source note: n/a
Requires sintering: false
Value basis: "Vendor datasheet + papers (volume resistivity)"
References:
  - "https://abc3d.ca/product/conductive-petg-carbon-nanotube-filament/"
  - "https://utw10945.utweb.utexas.edu/sites/default/files/2019/088%20Electrical%20and%20Mechancial%20Properties%20of%20Fused%20Fila.pdf"
  - "https://www.sciencedirect.com/science/article/abs/pii/S0008622311008906"
---
The step between unfilled (insulating) thermoplastics and ESD-safe grades: antistatic feedstocks that stop charge build-up but dissipate slowly. Range 1e8-1e11 Ω·cm (1e6-1e9 Ω·m): the lower end from a vendor antistatic grade, the upper end at the EIA-541 insulative limit (1e11 Ω·cm). Evidence is thin; treat as indicative.

## Sources
- ABC3D PETG/CNT filament: antistatic grade 1e8-1e10 Ω·cm volume resistivity (no test method given). [product page](https://abc3d.ca/product/conductive-petg-carbon-nanotube-filament/)
- UT Austin SFF Symposium (2019), electrical and mechanical properties of fused-filament PA composites, [PDF](https://utw10945.utweb.utexas.edu/sites/default/files/2019/088%20Electrical%20and%20Mechancial%20Properties%20of%20Fused%20Fila.pdf): places electrostatic dissipation at about 1e10-1e11 Ω·cm volume resistivity.
- Mahmoodi, Arjmand, Sundararaj & Park, *Carbon* 50 (2012), [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0008622311008906): likely source of the antistatic / ESD / EMI resistivity ranges (confirm).
- Standards: EIA-541 / ANSI/ESD S541, insulative ≥1e11 Ω·cm, dissipative 1e4-1e11 Ω·cm. Note that "antistatic" is defined inconsistently (older DoD definition: 1e9-1e14 Ω/sq surface resistivity).
- Background: inherently dissipative polymers (e.g. polyether block amides, ether-based TPU) give permanent antistatic behaviour without carbon; neat PEBA is reported above 1e6 Ω/sq surface resistivity (surface, not volume).

## To validate
- [ ] Find a peer-reviewed volume resistivity range for antistatic AM feedstocks (IDP blends or low-CNT filaments)
- [ ] Decide whether this area should overlap the ESD area (definitions overlap between 1e8 and 1e11 Ω·cm)
- [ ] Find commercial antistatic filament/pellet datasheets with volume resistivity
