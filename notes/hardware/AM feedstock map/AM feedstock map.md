# AM feedstock map

Two figures of volume resistivity (Ω·m) for the review, generated from the entries in [[AM feedstock map.base]]:

1. **Overview**: commercial AM feedstocks from insulators to metals, kept general. One thick bar per category over the ESD / conductive / EMI / metal bands, plus a box marking the state-of-the-art window. No format or product detail: a row that has no `Area` entry gets one bar spanning its products.
2. **State of the art by availability** (`am_feedstock_state_of_the_art`): the near-metal window, rows from `Commercial status` (Commercially available, Research, Patents); colour repeats the row, shape = feedstock format (filament ● / pellet ■ / ink ▲ / molded ◆), hollow = requires sintering, bars = ranges.
3. **State of the art by category** (`am_feedstock_categories`): the same window (1e-8 to 1e-3 Ω·m) drawn as a ladder. This is where the detail goes.
   - **rows** = `Plot category`, i.e. how the conducting path forms. The mechanism order is also the conductivity order:
     1. Metal-filled polymers: thermoplastic with solid metal filler; the particles only touch, so contact resistance caps conductivity
     2. Cured inks and pastes: metal flakes in a binder that is only cured or dried (≤150 °C), no sintering. Same mechanism as row 1, printed as an ink. An ink that needs sintering goes in row 6
     3. Low-melt alloy hybrids: a low-melt alloy melts during compounding and welds the Cu/Ni filler into a metal network (review: Amoabeng & Velankar 2018, [10.1002/pen.24774](https://doi.org/10.1002/pen.24774))
     4. Low-melt alloy filaments: dense Sn/Bi-based alloy, solid at room temperature; capped by the alloy itself (bulk tin is 8.7e6 S/m)
     5. Liquid metals: Ga alloys, liquid at room temperature; need a sealed channel (e.g. Lazarus 2019 filled printed channels with Galinstan)
     6. Sintered metals: particles fused at 250–1000 °C after printing (nanosilver paste, bound-metal Cu), too hot for a co-printed PA12 core (melts at ~178 °C). The plot shows only the row names; these descriptions live here
   - **filled / hollow** = `Printed`: printed by material extrusion in a paper or product, or not yet (molded or patent only). It says whether the material has been printed, not where the plotted value was measured
   - **grey** = `Context only`: shown for comparison only (no entry uses it at the moment)
   - **whisker** = the source gives a range (`"lo-hi"`); dashed when not printed yet
   - **faint band** = the row's span over its candidates (grey entries left out)
   - **colour** repeats the row (reference palette, slots 1-6). Bulk metals (`Reference`) are dashed vertical lines, copper darkest
   - **top axis** = conductivity relative to copper (% IACS)
   - **labels**: entries in the same row from the same manufacturer share one label (e.g. "Electrifi (3 grades)", "Siemens PA6/PPS"); a label pushed two slots out gets a leader line. Names, values and printed status for each entry are in the HTML hover

**Gap claim (to re-check: Kupros Cu29 at ~1.2e-7 Ω·m and the Heraeus silver ink at 7e-7 Ω·m are commercial and sit inside this range; the gap strip was removed from the plot):** no commercial feedstock that works as printed, without sintering, sits between about 1e-7 and 1e-5 Ω·m. Only injection-molded research and molding compounds reach that range (Siemens/JST alloy hybrids, TinCo 50, silver-flake filaments). Sintered copper bound-metal/MIM gets below it, but only after ~1000 °C sintering, which a co-printed PA12-FeSiAl core can't survive.

![[am_feedstock_overview.png]]

![[am_feedstock_state_of_the_art.png]]

![[am_feedstock_categories.png]]

Run from the vault root:
```bash
uv run scripts/plot_am_feedstock_map.py
```
Output: `images/plots/am_feedstock_overview.png/.html`, `images/plots/am_feedstock_state_of_the_art.png/.html` and `images/plots/am_feedstock_categories.png/.html`.

## Rows (`Plot category`)
Order is set in the script (`ROW_ORDER`, `ZOOM_ROW_ORDER`). New categories are appended at the bottom.

Overview:
1. Unfilled thermoplastics (reference)
2. Antistatic (between insulating and ESD-safe; thin evidence, see its area note)
3. ESD / static dissipative
4. Carbon fibre-filled
5. Carbon black
6. Graphene / CNT
7. Metal-polymer: built from the *Metal-filled polymers* and *Low-melt alloy hybrids* entries, which the script folds into this row (`OVERVIEW_ROW_OF`). Includes molding-only compounds (TinCo 50, RTP EMI 161). The commercial span is solid and the extension from research and patents is drawn lighter.
8. Bound metal / MIM (sintered): also takes the *Sintered metals* entries, but only its area entry is drawn
9. Bulk metals (reference)

State of the art: the six categories listed under figure 3. A state-of-the-art entry with any other category gets its own row and a warning.

Bands use `Plot category: Bands`.

## How to add an entry
Give the note a prefix so it never shares a name with a material note, and put it in the folder for that prefix:
- `Overview/`: `Area/`, `Band/`, `Product/` (products that only feed the overview, e.g. the carbon filaments)
- `State of the art/`: `Lit/`, `Product/`, `Link/`, `Ref/`

The folder is only for keeping things tidy: the base reads both folders, and `Plots` decides which figures draw an entry (Markforged Cu and bulk copper sit in *State of the art* but are drawn in the overview too).

| Prefix | Entry type | Properties | Body |
|---|---|---|---|
| `Product - ` | `Product` | Material template + plot properties. One value in `Volume resistivity (Ω·m)`, or `"lo-hi"` when the source gives a range | Source with the original unit |
| `Area - ` | `Range` | `Volume resistivity (Ω·m): "lo-hi"`, e.g. `"6.5e-2-4.8e-1"`. Areas known only as surface resistance go in `Surface resistance (Ω)` and are drawn hatched | **`## Sources`** listing every paper/datasheet and the value it supports, plus a `## To validate` checklist |
| `Link - ` | `Product` | Only plot properties + `Source note: "[[material note]]"`. The value, manufacturer and format are read from the material note (`Feedstock format` here is used only if the material note has none) | |
| `Lit - ` | `Literature` | `Commercial status: Research`, `Plots: [Zoom]`. Zoom only | |
| `Band - ` | `Band` | Background band; range in `Volume resistivity (Ω·m)` | Source of the definition |
| `Ref - ` | `Reference` | Bulk metals | |

- **`Plots`:** `Overview`, `Zoom`, both, or empty (kept as a record, not drawn).
- **`Commercial status`:** `Commercial AM feedstock`, `Commercial molding-only`, `Research` (papers), `Patent`, `Reference` (bulk metals). Shown in the hover; `Reference` entries become the bulk-metal lines.
- **`Printed: true/false`** (state-of-the-art entries): filled if the material has been printed by material extrusion in a paper or product, hollow if not yet. The script warns about state-of-the-art entries without it and draws them as not printed.
- **`Context only: true`:** drawn grey in the state-of-the-art plot and left out of the row's band. For inks and liquid metals that aren't pellet or filament candidates.
- **`Requires sintering: true`:** recorded; in the state-of-the-art plot sintering shows as the *Sintered metals* row.
- **Ranges:** any entry can hold `"lo-hi"` in `Volume resistivity (Ω·m)`; the state-of-the-art plot draws it as a whisker. Say in the body what each end is.
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
- Every band and bulk-metal note: cite the primary standard / handbook

