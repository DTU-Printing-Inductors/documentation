---
Grade: n/a
Manufacturer: n/a
Supplier: n/a
Type: n/a
Functionality: n/a
Matrix: "ABS, PETG, PEKK, PA612, ..."
Filler: "CNT / carbon black"
Filler loading: n/a
Size: n/a
Feedstock format: "Filament"
Permeability: n/a
Surface resistivity (Ω/sq): n/a
Surface resistance (Ω): "1e4-1e9"
Surface resistance standard: "Vendor: ASTM D257 / ESD STM11.11 / ASTM D4496"
Volume resistivity (Ω·m): "1e2-1e7"
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
Plot category: "ESD / static dissipative"
Entry type: "Range"
Plots:
  - "Overview"
Commercial status: "Commercial AM feedstock"
Plot label: "ESD filaments"
Source note: n/a
Requires sintering: false
Value basis: "Vendor datasheets (volume resistivity)"
References:
  - "https://abc3d.ca/product/conductive-petg-carbon-nanotube-filament/"
  - "https://www.matter3d.com/products/conductive-petg-electrostatic-discharge"
  - "https://www.sciencedirect.com/science/article/abs/pii/S0008622311008906"
  - "https://doi.org/10.1016/j.synthmet.2017.01.009"
  - "https://doi.org/10.3390/nano8010049"
---
Commercial ESD-safe filaments. The plotted range is now **volume resistivity** 1e4-1e9 Ω·cm (1e2-1e7 Ω·m), taken from vendors that quote volume resistivity for their ESD grades. The surface resistance most vendors quote (1e4-1e9 Ω) stays in `Surface resistance (Ω)` and in the sources below.

## Sources
Volume resistivity (plotted):
- ABC3D PETG/CNT filament: ESD grade 1e4-1e6 Ω·cm, antistatic grade 1e8-1e10 Ω·cm, EMI grade 1e0-1e2 Ω·cm (no test method given). [product page](https://abc3d.ca/product/conductive-petg-carbon-nanotube-filament/)
- Matter3D Conductive PETG (ESD): typical 1e6-1e9 Ω·cm. [product page](https://www.matter3d.com/products/conductive-petg-electrostatic-discharge)
- Prusament PETG ESD (CNT): reported 2.2e4 Ω·m volume resistivity and 6e7 Ω/sq surface resistivity on printed samples (secondary source). Official TDS also gives volume resistance 7.7e6 Ω. [news](https://3dprinting.com/news/prusa-launches-prusament-petg-esd-a-carbon-filled-3d-printing-filament-for-electronics/)

Peer-reviewed (ranges by application and printed CNT composites):
- Mahmoodi, Arjmand, Sundararaj & Park, *Carbon* 50 (2012), MWCNT/polystyrene, [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0008622311008906). ABC3D cites it for its grade ranges; it likely contains the resistivity-vs-application ranges (antistatic / ESD / EMI). **Confirm the figure and values.**
- Dorigato et al., *Synthetic Metals* (2017), ABS/CNT for FDM, [10.1016/j.synthmet.2017.01.009](https://doi.org/10.1016/j.synthmet.2017.01.009): CNT lowers ABS volume resistivity by about nine orders of magnitude from ~1e12 Ω·cm, and printing raises it again depending on orientation. **Read which loadings fall in 1e4-1e11 Ω·cm.**
- ABS/CNT filaments and FDM, *Nanomaterials* 8 (2018) 49, [10.3390/nano8010049](https://doi.org/10.3390/nano8010049): printed parts less conductive than filament, resistivity rises with build angle.

Surface resistance (kept for reference):
- Stratasys ABS-ESD7: 1e4-1e9 Ω (other versions 1e6-1e9 Ω), ASTM D257. [datasheet](https://cdn.goengineer.com/stratasys_fdm_abs-esd7_material_data_sheet.pdf)
- Stratasys Antero 840CN03: 1e3-1e9 Ω. [white paper](https://www.stratasys.com/contentassets/1ae695e2da8947e1ad150aa8f80ddbb5/antero-840cn03-electrical-properties---fr-fdm-white-paper.pdf)
- Polymaker Fiberon PETG-ESD / PA612-ESD: about 1e4-1e7 Ω/sq. [wiki](https://wiki.polymaker.com/the-basics/fun-3d-printing-facts/esd-safe-3d-printing-materials-and-how-they-work)
- 3DXTech 3DXNano ESD: 1e7-1e9 Ω/sq. [article](https://3dprintingindustry.com/news/3dxtech-releases-carbon-nanotube-esd-filaments-35027/)
- Standards: EIA-541 / ANSI/ESD S541 dissipative 1e4-1e11 Ω·cm volume; ANSI/ESD S20.20.

## To validate
- [ ] Confirm the Mahmoodi et al. 2012 ranges and get the full citation
- [ ] Read the Dorigato 2017 volume resistivity per CNT loading (filament and printed)
- [ ] Get the official Prusament PETG ESD TDS (2.2e4 Ω·m comes from a secondary source)
- [ ] Vendor volume values have no stated test method
