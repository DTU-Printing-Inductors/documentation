---
Grade: n/a
Manufacturer: n/a
Supplier: n/a
Type: n/a
Functionality: n/a
Matrix: "PLA, ABS, PA12, PEEK, ..."
Filler: "none"
Filler loading: n/a
Size: n/a
Feedstock format: "Filament, pellets"
Permeability: n/a
Surface resistivity (Ω/sq): n/a
Surface resistance (Ω): n/a
Surface resistance standard: n/a
Volume resistivity (Ω·m): "1e14-1e16"
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
Plot category: "Unfilled thermoplastics (reference)"
Entry type: "Range"
Plots:
  - "Overview"
Commercial status: "Commercial AM feedstock"
Plot label: "Unfilled polymers"
Source note: n/a
Requires sintering: false
Value basis: "Reference tables (molded)"
References:
  - "https://www.specialchem.com/plastics/guide/volume-resistivity"
  - "https://doi.org/10.1155/2017/6913835"
---
Reference area for unfilled thermoplastic feedstocks. 1e14-1e16 Ω·m = 1e16-1e18 Ω·cm.

## Sources
- SpecialChem volume resistivity guide (vendor reference table): unfilled ABS about 1.4-1.6e16 Ω·cm, PEEK about 1.6-1.7e16 Ω·cm (molded). [link](https://www.specialchem.com/plastics/guide/volume-resistivity)
- Dichtl, Sippel & Krohns, *Advances in Materials Science and Engineering* (2017) 6913835, [10.1155/2017/6913835](https://doi.org/10.1155/2017/6913835): dielectric properties of as-printed PLA (value not yet read).

## To validate
- [ ] Read the PLA DC conductivity / resistivity from Dichtl et al. 2017
- [ ] Add a peer-reviewed or textbook source for the 1e16-1e18 Ω·cm span (e.g. Blythe & Bloor, *Electrical Properties of Polymers*)
- [ ] Check whether the lower end should include PA (moisture lowers ρ)
