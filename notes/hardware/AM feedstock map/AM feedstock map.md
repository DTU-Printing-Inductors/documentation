# AM feedstock map

Two figures of volume resistivity (Ω·m) for the review, generated from the entries in [[AM feedstock map.base]]:

1. **Overview**: commercial AM feedstocks from insulators to metals, kept general. One thick bar per category over the ESD / conductive / EMI / metal bands, plus a box marking the state-of-the-art window. No format or product detail: a row that has no `Area` entry gets one bar spanning its products.
2. **State of the art**: the near-metal window (1e-8 to 1e-3 Ω·m). This is where the detail goes.
   - **rows** = availability, from `Commercial status`: Commercially available (AM feedstock and molding-only; molding-only ones say so in their label), Research (papers), Patents, Bulk metals
   - **colour** repeats the row: commercial (blue), research (green), patents (orange), bulk metals (dark grey)
   - **shape** = filament ● / pellet ■ / molded or other ◆
   - **hollow** = requires sintering

**Gap claim (to re-check: Kupros Cu29 at ~1.2e-7 Ω·m and the Heraeus silver ink at 7e-7 Ω·m are commercial and sit inside this range; the gap strip was removed from the plot):** no commercial feedstock that works as printed, without sintering, sits between about 1e-7 and 1e-5 Ω·m. Only injection-molded research and molding compounds reach that range (Siemens/JST alloy hybrids, TinCo 50, silver-flake filaments). Sintered copper bound-metal/MIM gets below it, but only after ~1000 °C sintering, which a co-printed PA12-FeSiAl core can't survive.

![[am_feedstock_overview.png]]

![[am_feedstock_state_of_the_art.png]]

Run from the vault root:
```bash
uv run scripts/plot_am_feedstock_map.py
```
Output: `images/plots/am_feedstock_overview.png/.html` and `images/plots/am_feedstock_state_of_the_art.png/.html`.

## Rows (`Plot category`)
Order is set in the script. New categories are appended at the bottom.
1. Unfilled thermoplastics (reference)
2. Antistatic (between insulating and ESD-safe; thin evidence, see its area note)
3. ESD / static dissipative
3. Carbon fibre-filled
4. Carbon black
5. Graphene / CNT
6. Metal-polymer: includes molding-only compounds (TinCo 50, RTP EMI 161) and the research/patent low-melt alloy and silver-filled composites. In the overview the commercial span is solid and the extension from research and patents is drawn lighter.
7. Bound metal / MIM (sintered)
8. Bulk metals (reference)

Bands use `Plot category: Bands`.

## How to add an entry
Put the note in `entries/` with a prefix so it never shares a name with a material note.

| Prefix | Entry type | Properties | Body |
|---|---|---|---|
| `Product - ` | `Product` | Material template + plot properties. One value in `Volume resistivity (Ω·m)` | Source with the original unit |
| `Area - ` | `Range` | `Volume resistivity (Ω·m): "lo-hi"`, e.g. `"6.5e-2-4.8e-1"`. Areas known only as surface resistance go in `Surface resistance (Ω)` and are drawn hatched | **`## Sources`** listing every paper/datasheet and the value it supports, plus a `## To validate` checklist |
| `Link - ` | `Product` | Only plot properties + `Source note: "[[material note]]"`. The value, manufacturer and format are read from the material note (`Feedstock format` here is used only if the material note has none) | |
| `Lit - ` | `Literature` | `Commercial status: Research`, `Plots: [Zoom]`. Zoom only | |
| `Band - ` | `Band` | Background band; range in `Volume resistivity (Ω·m)` | Source of the definition |
| `Ref - ` | `Reference` | Bulk metals | |

- **`Plots`:** `Overview`, `Zoom`, both, or empty (kept as a record, not drawn).
- **`Commercial status`:** `Commercial AM feedstock`, `Commercial molding-only`, `Research` (papers), `Patent`, `Reference` (bulk metals). It sets the row in the state-of-the-art plot.
- **`Requires sintering: true`:** drawn hollow.
- **Units:** convert everything to Ω·m (1 Ω·cm = 0.01 Ω·m; %IACS → 1.7241e-8 / fraction) and keep the original value and unit in the body.

## Sources to validate
- Areas:
  - [[Area - Unfilled thermoplastics]]: PLA value in Dichtl et al. 2017 still to read; needs a textbook/peer-reviewed source
  - [[Area - ESD static dissipative filaments]]: now plotted from vendor **volume** resistivity (1e4-1e9 Ω·cm); peer-reviewed leads (Mahmoodi 2012, Dorigato 2017) still to read
  - [[Area - Antistatic filaments]]: one vendor grade plus the EIA-541 limit; needs a peer-reviewed source
  - [[Area - Carbon fibre-filled]]: mixed molded/printed basis; confirm the J. Mater. Eng. Perform. 2021 details
  - [[Area - Carbon black filaments]]: Nowka et al. 2024 (filament values); decide filament vs printed basis
  - [[Area - Graphene and CNT filaments]]: Nowka et al. 2024
  - [[Area - Sintered copper bound metal and MIM]]: Sakib-Uz-Zaman & Khondoker 2023 review
- [[Product - Amolen Conductive PLA]]: the quoted 1.5 Ω·cm vs the measured 22.33 Ω·cm don't agree
- [[Lit - Pellet-printed sintered Cu]]: confirm which paper reports ~15 % IACS
- [[Lit - Ag flake polyester PVB filament]]: confirm the full citation
- Every band and bulk-metal note: cite the primary standard / handbook

## To collect
- 3-5 ESD filament TDS with test method
- carbon black / graphene **pellets** with stated resistivity
- copper MIM pellet datasheets (sintered %IACS)
- the injection-molding compounds you want shown (link-only entries)
