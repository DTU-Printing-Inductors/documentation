# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml", "matplotlib", "plotly"]
# ///
"""
AM feedstock resistivity map: an overview figure and a state-of-the-art ladder of the near-metal window.

Reads the entries listed by the first view of notes/hardware/AM feedstock map/AM feedstock map.base.
Each entry picks its figure(s) with the `Plots` property (Overview / Zoom). Link-only entries
(`Source note: "[[...]]"`) take their values from the linked material note.

State of the art: one row per `Plot category` (how the conducting path forms). Filled = `Printed`,
hollow = not printed yet, grey = `Context only`, bar = a range given by the source.

Run from anywhere:   uv run scripts/plot_am_feedstock_map.py
Writes images/plots/am_feedstock_overview.(png|html) and am_feedstock_state_of_the_art.(png|html).
"""
from __future__ import annotations

import math
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import plot_soft_magnetic as psm  # noqa: E402  (shared base-filter and value-parsing helpers)
from plot_soft_magnetic import compile_filter, frontmatter, parse_upper, parse_value, replace_file  # noqa: E402

# ---------- settings (the only things meant to be edited) ----------
VAULT = Path(__file__).resolve().parent.parent
BASE_FILE = VAULT / "notes" / "hardware" / "AM feedstock map" / "AM feedstock map.base"
OUT_DIR = VAULT / "images" / "plots"
OVERVIEW_NAME = "am_feedstock_overview"
AVAIL_NAME = "am_feedstock_state_of_the_art"     # state of the art, rows = availability
ZOOM_NAME = "am_feedstock_categories"            # state of the art, rows = category (ladder)
OVERVIEW_TITLE = "Overview of Commercial Material Extrusion feedstocks"
AVAIL_TITLE = "Conductor options for 3D-printed windings by availability"
ZOOM_TITLE = "Conductor options for 3D-printed windings by category and availability"

# State of the art by availability: rows from `Commercial status`, colour repeats the row,
# shape = feedstock format, hollow = requires sintering
AVAIL_ROWS = {
    "Commercial AM feedstock": "Commercially available",
    "Commercial molding-only": "Commercially available",
    "Research": "Research (papers)",
    "Patent": "Patents",
}
AVAIL_ROW_ORDER = ["Commercially available", "Research (papers)", "Patents"]
AVAIL_ROW_COLOURS = {"Commercially available": "#2a78d6", "Research (papers)": "#1baf7a", "Patents": "#eb6834"}
MARKERS = {"filament": ("o", "circle"), "pellet": ("s", "square"), "ink": ("^", "triangle-up"),
           "other": ("D", "diamond")}
FORMAT_LABEL = {"filament": "Filament", "pellet": "Pellets", "ink": "Ink / paste", "other": "Molded / other"}

VOL_KEY = "Volume resistivity (Ω·m)"
SURF_KEY = "Surface resistance (Ω)"

ZOOM_WINDOW = (1e-8, 1e-3)   # Ω·m, the near-metal window

ROW_ORDER = [
    "Unfilled thermoplastics (reference)",
    "Antistatic",
    "ESD / static dissipative",
    "Carbon fibre-filled",
    "Carbon black",
    "Graphene / CNT",
    "Metal-polymer",
    "Low-melt alloy hybrids (research)",
    "Silver-filled (research)",
    "Bound metal / MIM (sintered)",
    "Bulk metals (reference)",
]
BAND_CATEGORY = "Bands"

# Overview: colour = row (fixed per row, never by rank). Dataviz reference palette in its validated order.
PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#e87ba4", "#4a3aa7", "#e34948"]
ROW_COLOURS = {
    "ESD / static dissipative": PALETTE[3],
    "Carbon fibre-filled": PALETTE[4],
    "Carbon black": PALETTE[1],
    "Graphene / CNT": PALETTE[2],
    "Metal-polymer": PALETTE[0],
    "Bound metal / MIM (sintered)": PALETTE[5],
    "Antistatic": PALETTE[3],  # same hue as ESD (static control), drawn lighter via ROW_ALPHA
}
ROW_ALPHA = {"Antistatic": 0.45}  # bar opacity per row; default 0.9
GREY = "#a8a69e"
INK = "#52514e"
BAND_FILL = ["#ecebe7", "#dedcd6"]  # alternating band tints

# Overview: the state-of-the-art categories fold into the overview's coarser rows
OVERVIEW_ROW_OF = {
    "Metal-filled polymers": "Metal-polymer",
    "Low-melt alloy hybrids": "Metal-polymer",
    "Sintered metals": "Bound metal / MIM (sintered)",
}

# State of the art: rows = `Plot category` (how the conducting path forms), top to bottom
ZOOM_ROW_ORDER = ["Metal-filled polymers", "Cured inks and pastes", "Low-melt alloy hybrids",
                  "Low-melt alloy filaments", "Liquid metals", "Sintered metals"]
# Reference categorical palette, slots 1-6 in their validated order. Rows are labelled as well,
# so colour never carries the category alone.
ZOOM_ROW_COLOURS = {
    "Metal-filled polymers": "#2a78d6",
    "Cured inks and pastes": "#eb6834",
    "Low-melt alloy hybrids": "#1baf7a",
    "Low-melt alloy filaments": "#eda100",
    "Liquid metals": "#e87ba4",
    "Sintered metals": "#008300",
}
CONTEXT_INK = "#898781"     # labels of `Context only` entries (their marks use GREY)
LEADER = "#c3c2b7"          # leader lines from labels two or more slots away
RANGE_LW = 2.0              # range whisker line width, pt (dashed when not printed yet)
RANGE_DASH = (0, (2.4, 1.6))
SPAN_W = 20.0               # faint band behind each row spanning its candidates, pt
SPAN_PAD_DEC = 0.12         # the band reaches this many decades past the row's outermost entries
RHO_CU = 1.7241e-8          # Ω·m, 100 % IACS; the state-of-the-art top axis is ρ / RHO_CU
REF_EMPHASIS = {"copper"}   # reference lines drawn darker (others lighter)
TITLE_SIZE = 15    # figure title font size, pt (HTML uses TITLE_SIZE + 5 px)
POINT_D = 7.0      # marker diameter, pt
OVERVIEW_BAR_H = 1.0   # overview bar height in row units (1.0 = bars fill the row up to the dividers)
ROW_LABEL_CHAR_PT = 4.7  # approx. width of one 8.5 pt character, for fitting row names beside bars
ROW_LABEL_PAD_DEC = 0.25  # gap between a bar and its row name, decades
SINGLE_HALF_DEC = 0.15  # overview: a row with one value gets a bar of ±this many decades
POINT_PX = 10
BAR_PX = 10

warnings = psm.warnings  # compile_filter reports into the shared list


# ---------- loading ----------
def load_base_filter():
    base = yaml.safe_load(BASE_FILE.read_text(encoding="utf-8")) or {}
    view = (base.get("views") or [{}])[0]
    top, view_f = compile_filter(base.get("filters")), compile_filter(view.get("filters"))
    return (lambda n, p: top(n, p) and view_f(n, p)), view.get("name")


def as_list(v):
    if v is None or v == "n/a":
        return []
    return [str(x).strip() for x in v] if isinstance(v, list) else [s.strip() for s in str(v).split(",") if s.strip()]


def clean(v, default="n/a"):
    if v is None or (isinstance(v, str) and not v.strip()):
        return default
    s = ", ".join(map(str, v)) if isinstance(v, list) else str(v)
    return s.replace("[[", "").replace("]]", "")


def fmt_kind(v) -> str:
    s = str(v or "").lower()
    if "pellet" in s:
        return "pellet"
    if "filament" in s:
        return "filament"
    if "ink" in s or "paste" in s:
        return "ink"
    return "other"


def build_index():
    """All vault notes by relative path (no .md) and by basename, for wikilink resolution."""
    by_path, by_name = {}, defaultdict(list)
    for path in VAULT.rglob("*.md"):
        rel = path.relative_to(VAULT).as_posix()
        if rel.startswith(".") or "/." in rel:
            continue
        by_path[rel[:-3]] = path
        by_name[path.stem].append(path)
    return by_path, by_name


def resolve(link, by_path, by_name, owner):
    m = re.search(r"\[\[([^\]|#]+)", str(link))
    if not m:
        warnings.append(f"{owner}: Source note is not a wikilink: {link}")
        return None
    target = m.group(1).strip().removesuffix(".md")
    if target in by_path:
        return by_path[target]
    hits = by_name.get(target.split("/")[-1], [])
    if len(hits) == 1:
        return hits[0]
    warnings.append(f"{owner}: Source note [[{target}]] " + ("is ambiguous" if hits else "not found"))
    return None


def collect():
    keep, view_name = load_base_filter()
    by_path, by_name = build_index()
    rows, skipped, unresolved = [], [], []
    for rel_noext, path in by_path.items():
        rel = rel_noext + ".md"
        n_warn = len(warnings)
        fm = frontmatter(path)
        if not fm or not keep(fm, rel):
            del warnings[n_warn:]  # frontmatter problems in notes outside the base aren't ours to report
            continue
        values = fm
        src_name = "n/a"
        if fm.get("Source note") not in (None, "", "n/a"):
            src = resolve(fm["Source note"], by_path, by_name, path.stem)
            if src is None:
                unresolved.append(path.stem)
                continue
            values, src_name = frontmatter(src), src.stem
        vol_raw, surf_raw = values.get(VOL_KEY), values.get(SURF_KEY)
        lo, hi, basis = parse_value(vol_raw), parse_upper(vol_raw), "volume"
        if lo is None and parse_value(surf_raw) is not None:
            lo, hi, basis = parse_value(surf_raw), parse_upper(surf_raw), "surface"
        if lo is None:
            skipped.append(path.stem)
            continue
        fmt = values.get("Feedstock format")
        if fmt in (None, "", "n/a"):
            fmt = fm.get("Feedstock format")
        rows.append({
            "note": path.stem,
            "type": str(fm.get("Entry type") or "Product"),
            "plots": as_list(fm.get("Plots")),
            "category": str(fm.get("Plot category") or "Uncategorised"),
            "status": str(fm.get("Commercial status") or "n/a"),
            "label": str(fm.get("Plot label") or path.stem),
            "manufacturer": clean(values.get("Manufacturer")),
            "format": fmt_kind(fmt),
            "format_raw": clean(fmt),
            "lo": lo, "hi": hi, "basis": basis,
            "raw": clean(vol_raw if basis == "volume" else surf_raw),
            "sinter": bool(fm.get("Requires sintering")),
            "printed": bool(fm.get("Printed")),
            "printed_missing": "Printed" not in fm,
            "context": bool(fm.get("Context only")),
            "value_basis": clean(fm.get("Value basis")),
            "source": src_name,
            "refs": as_list(fm.get("References")),
            "to_validate": str(fm.get("Status") or "").lower().startswith("to validate"),
        })
    return rows, skipped, unresolved, view_name


# ---------- layout helpers ----------
def rows_for(entries, row_order=ROW_ORDER):
    present = {e["category"] for e in entries if e["type"] != "Band"}
    order = [r for r in row_order if r in present] + sorted(present - set(row_order))
    return {r: i for i, r in enumerate(order)}, order


def band_lanes(bands):
    """Greedy lanes so overlapping bands (e.g. EMI inside Conductive) sit on separate strips."""
    lanes = []
    for b in sorted(bands, key=lambda b: -(b["hi"] or b["lo"])):
        for k, lane in enumerate(lanes):
            if all(b["lo"] >= o["hi"] or (b["hi"] or b["lo"]) <= o["lo"] for o in lane):
                lane.append(b); b["lane"] = k
                break
        else:
            lanes.append([b]); b["lane"] = len(lanes) - 1
    return len(lanes)


def x_limits(entries):
    xs = [v for e in entries for v in (e["lo"], e["hi"]) if v]
    lo, hi = min(xs), max(xs)
    return 10 ** (math.floor(math.log10(lo)) - 0.3), 10 ** (math.ceil(math.log10(hi)) + 0.3)


def gmean(a, b):
    return math.sqrt(a * b)


LABEL_SLOTS = [1, -1, 2, -2, 3]   # label offset in units of LABEL_STEP pt (+ = above the mark)
LABEL_STEP = 9
CHAR_PT = 3.9                     # approx. width of one 7 pt character
AXES_PT = 9.0 * 72                # approx. axes width in points


def label_x(e):
    return gmean(e["lo"], e["hi"]) if e["hi"] else e["lo"]


def place_labels(entries, y_of, xmin, xmax, slots_of=None):
    """Greedy label slots per row: a label takes the first slot (by default above, below, higher, lower, ...) where
    it overlaps no label already in that slot. A label two or more slots out gets a leader line, so it must not sit
    across a longer leader, and its own leader must not cross the labels it passes. Overlap is judged in log-x
    using an estimated text width."""
    per_decade_pt = AXES_PT / (math.log10(xmax) - math.log10(xmin))
    per_row = defaultdict(list)
    for e in entries:
        per_row[y_of(e)].append(e)
    for group in per_row.values():
        taken = defaultdict(list)  # slot -> [(x0, x1)]
        leaders = []               # (x, slot) of labels drawn with a leader
        for e in sorted(group, key=lambda e: -label_x(e)):
            cx = math.log10(label_x(e))
            half = len(e["label"]) * CHAR_PT / 2 / per_decade_pt + 0.05
            slots = slots_of(e) if slots_of else LABEL_SLOTS

            def clear_text(s):
                return all(cx + half < a or cx - half > b for a, b in taken[s])

            def fits(s):
                if not clear_text(s):
                    return False
                if any(ls * s > 0 and abs(ls) > abs(s) and cx - half <= lx <= cx + half for lx, ls in leaders):
                    return False
                sign = 1 if s > 0 else -1
                return not any(a - 0.02 <= cx <= b + 0.02 for t in range(1, abs(s)) for a, b in taken[sign * t])

            s, nx = next((s for s in slots if fits(s)), None), cx
            if s is None:  # no clean slot: shift a leader label sideways, past the labels its leader would cross
                for s2 in (t for t in slots if abs(t) >= 2):
                    sign = 1 if s2 > 0 else -1
                    block = [(a, b) for t in range(1, abs(s2)) for a, b in taken[sign * t] if a - 0.02 <= cx <= b + 0.02]
                    if not block:
                        continue
                    # higher ρ (left on screen) first: the right side holds the bulk-metal lines
                    for cand in (max(b for _, b in block) + half + 0.03, min(a for a, _ in block) - half - 0.03):
                        if all(cand + half < a or cand - half > b for a, b in taken[s2]):
                            s, nx = s2, cand
                            break
                    if s is not None:
                        break
            if s is None:  # still nothing: the first slot without overlapping text
                s = next((s for s in slots if clear_text(s)), slots[-1])
            taken[s].append((nx - half, nx + half))
            if abs(s) >= 2:
                leaders.append((cx, s))
            e["label_dy"], e["label_dx"] = s, nx - cx  # label_dx: sideways shift in decades of ρ


def group_labels(entries):
    """One label per product family: entries in the same row from the same manufacturer share a label
    ('Electrifi (3 grades)', 'RTP EMI 161/162'), placed at their geometric centre. Others keep their own label."""
    groups = defaultdict(list)
    for e in entries:
        # printed and not-printed grades of one manufacturer keep separate labels (e.g. TE AM / TE IM)
        key = ((e["category"], e["manufacturer"], e.get("printed")) if e["manufacturer"] != "n/a"
               else (e["category"], e["note"]))
        groups[key].append(e)
    items = []
    for members in groups.values():
        if len(members) == 1:
            items.append(dict(members[0]))
            continue
        words = [m["label"].split() for m in members]
        common = []
        for parts in zip(*words):
            if len(set(parts)) != 1:
                break
            common.append(parts[0])
        rest = [" ".join(w[len(common):]) for w in words]
        base = " ".join(common) or members[0]["manufacturer"]
        label = f"{base} {'/'.join(rest)}" if all(rest) and len(set(rest)) == len(rest) else f"{base} ({len(members)} grades)"
        xs = [label_x(m) for m in members]
        items.append({**members[0], "label": label, "lo": 10 ** (sum(map(math.log10, xs)) / len(xs)), "hi": None})
    return items


# ---------- matplotlib ----------
def setup_axes(ax, xmin, xmax, order, n_lanes, title, top_axis="conductivity", xlabel="Volume resistivity ρ (Ω·m)"):
    ax.set_xscale("log")
    ax.set_xlim(xmax, xmin)  # reversed: insulators left, metals right
    ax.set_ylim(len(order) - 0.4, -n_lanes - 0.6)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels(order, fontsize=8.5)
    ax.set_xlabel(xlabel)
    ax.grid(True, axis="x", which="major", alpha=0.25)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    import numpy as np

    def inv(x):
        x = np.asarray(x, dtype=float)
        with np.errstate(divide="ignore"):
            return np.where(x > 0, 1.0 / np.where(x > 0, x, 1.0), np.inf)

    if top_axis == "resistivity":
        # Bottom axis shows conductivity σ = 1/ρ, top axis shows the stored volume resistivity ρ (the ESD/insulative
        # band limits are defined in resistivity).
        from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter
        ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"$10^{{{round(-math.log10(v))}}}$" if v > 0 else ""))
        ax.xaxis.set_minor_formatter(NullFormatter())
        top = ax.secondary_xaxis("top", functions=(lambda x: np.asarray(x), lambda x: np.asarray(x)))
        top.set_xlabel("Volume resistivity ρ (Ω·m)", fontsize=9)
        top.xaxis.set_major_locator(FixedLocator(ax.get_xticks()))  # same decades as the bottom axis
        top.xaxis.set_minor_formatter(NullFormatter())
    elif top_axis == "iacs":
        # Bottom axis shows conductivity σ = 1/ρ (the data stay in ρ; the reversed ρ axis already runs low σ -> high σ),
        # top axis shows conductivity relative to annealed copper (% IACS).
        from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter
        ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"$10^{{{round(-math.log10(v))}}}$" if v > 0 else ""))
        ax.xaxis.set_minor_formatter(NullFormatter())
        top = ax.secondary_xaxis("top", functions=(lambda x: inv(x) * RHO_CU * 100, lambda p: inv(p) * RHO_CU * 100))
        top.set_xlabel("Conductivity relative to copper (% IACS)", fontsize=9)
        top.xaxis.set_major_locator(LogLocator(base=10))
        top.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g} %"))
    else:
        top = ax.secondary_xaxis("top", functions=(inv, inv))
        top.set_xlabel("Conductivity σ (S/m)", fontsize=9)
    ax.set_title(title, fontsize=TITLE_SIZE, loc="center", pad=30, fontweight="bold")


def draw_bands_png(ax, bands, xmin, xmax, n_rows):
    from matplotlib.patches import Rectangle
    for i, b in enumerate(sorted(bands, key=lambda b: -b["lo"])):
        lo, hi = max(b["lo"], xmin), min(b["hi"] or b["lo"], xmax)
        if hi <= lo:
            continue
        y = -1 - b["lane"]
        ax.add_patch(Rectangle((lo, y - 0.32), hi - lo, 0.64, facecolor=BAND_FILL[i % 2], edgecolor="white",
                               linewidth=1.5, zorder=1))
        ax.text(gmean(lo, hi), y, b["label"], ha="center", va="center", fontsize=7.5, color=INK, zorder=2)
        for edge in (lo, hi):
            if xmin < edge < xmax:
                ax.plot([edge, edge], [y + 0.32, n_rows - 0.4], color=INK, alpha=0.12, linewidth=0.8, zorder=0)


# Category plot: marker shape = availability (from `Commercial status`), fill = printed
AVAIL_SHAPES = {"Commercially available": ("o", "circle"), "Research (papers)": ("s", "square"),
                "Patents": ("D", "diamond")}


def avail_shape(e, plotly=False):
    return AVAIL_SHAPES.get(AVAIL_ROWS.get(e["status"]), ("o", "circle"))[1 if plotly else 0]


def draw_dot_png(ax, x, y, colour, hollow, z=10, marker="o"):
    ax.scatter([x], [y], s=POINT_D ** 2, marker=marker, facecolors="white" if hollow else colour,
               edgecolors=colour if hollow else "white", linewidths=1.4 if hollow else 0.8, zorder=z)


def leader_target(e, x_text):
    """Where a label's leader ends: the mark, or for a range the point of the whisker nearest the label."""
    return min(max(x_text, e["lo"]), e["hi"]) if e.get("hi") else e["lo"]


def label_png(ax, e, x, y, colour="#333333"):
    s = e.get("label_dy", 1)
    x_text = x * 10 ** e.get("label_dx", 0.0)
    # y axis is inverted (row 0 at top), so "above" on screen is a positive offset in points
    leader = dict(arrowstyle="-", color=LEADER, lw=0.6, shrinkA=0, shrinkB=4) if abs(s) >= 2 else None
    ax.annotate(e["label"], (leader_target(e, x_text) if leader else x, y),
                xytext=(x_text, LABEL_STEP * s + (-3 if s < 0 else 0)), textcoords=("data", "offset points"),
                ha="center", va="bottom" if s > 0 else "top", fontsize=7, color=colour, zorder=30, arrowprops=leader)


def save_png(fig, name):
    out, tmp = OUT_DIR / f"{name}.png", OUT_DIR / f"{name}.tmp.png"
    fig.savefig(tmp, bbox_inches="tight")
    replace_file(tmp, out)
    return out


def overview_areas(entries):
    """One general bar per row. A row with Range entries shows those ranges; a row with only products gets
    one bar spanning its products (a single value gets ±SINGLE_HALF_DEC decades). No format or product detail."""
    by_row = defaultdict(list)
    for e in entries:
        by_row[e["category"]].append(e)
    areas = []
    for cat, group in by_row.items():
        ranges = [e for e in group if e["type"] == "Range"]
        if ranges:
            areas += [dict(e) for e in ranges]
            continue
        commercial = [e for e in group if e["status"].startswith("Commercial") or e["status"] == "Reference"]
        others = [e for e in group if e not in commercial]
        # full span (incl. research / patents) drawn light underneath, commercial span drawn solid on top
        # rows with only research/patent entries are drawn light too, so solid always means "commercial"
        for members, light in ((group, True), (commercial, False)) if others and commercial else ((group, not commercial),):
            vals = [v for e in members for v in (e["lo"], e["hi"]) if v]
            lo, hi = min(vals), max(vals)
            if hi / lo < 10 ** (2 * SINGLE_HALF_DEC):
                mid = gmean(lo, hi)
                lo, hi = mid / 10 ** SINGLE_HALF_DEC, mid * 10 ** SINGLE_HALF_DEC
            kind = "incl. research and patents" if light else ("commercial" if others else "all")
            areas.append({**members[0], "note": f"{cat} ({kind}, {len(members)} entries)", "lo": lo, "hi": hi,
                          "label": cat, "basis": "volume", "raw": f"{min(vals):.3g}-{max(vals):.3g}", "light": light,
                          "value_basis": f"Span of the row's entries ({kind})",
                          "source": ", ".join(e["note"] for e in members), "refs": []})
    return areas


def plot_overview_png(entries, bands):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch, Rectangle

    y_of, order = rows_for(entries)
    xmin, xmax = x_limits(entries + bands)
    n_lanes = band_lanes(bands)
    fig, ax = plt.subplots(figsize=(11, 0.55 * (len(order) + n_lanes) + 2.4), dpi=200)
    setup_axes(ax, xmin, xmax, order, n_lanes, OVERVIEW_TITLE, top_axis="resistivity",
               xlabel="Electrical conductivity σ (S/m)")
    draw_bands_png(ax, bands, xmin, xmax, len(order))

    # zoom window
    zlo, zhi = ZOOM_WINDOW
    ax.add_patch(Rectangle((zlo, -0.5), zhi - zlo, len(order), fill=False, linestyle="--", edgecolor=INK,
                           linewidth=1.0, zorder=3))
    ax.text(gmean(zlo, zhi), len(order) - 0.5, "state-of-the-art", ha="center", va="bottom", fontsize=7.5, color=INK)

    colour = lambda e: ROW_COLOURS.get(e["category"], GREY)
    h = OVERVIEW_BAR_H
    for e in entries:
        y, c = y_of[e["category"]], colour(e)
        if e["basis"] == "surface":
            ax.add_patch(Rectangle((e["lo"], y - h / 2), e["hi"] - e["lo"], h, facecolor="none", hatch="////",
                                   edgecolor=c, linewidth=1.2, zorder=5))
        else:
            base = ROW_ALPHA.get(e["category"], 0.9)
            light = e.get("light", False)
            ax.add_patch(Rectangle((e["lo"], y - h / 2), e["hi"] - e["lo"], h, facecolor=c, edgecolor="none",
                                   alpha=base / 3 if light else base, zorder=4 if light else 5))

    # dashed dividers between rows, and each row's name written beside its bar
    for i in range(len(order) - 1):
        ax.axhline(i + 0.5, color=INK, linestyle="--", linewidth=0.7, alpha=0.35, zorder=2)
    ax.set_yticks([])
    per_decade_pt = AXES_PT / (math.log10(xmax) - math.log10(xmin))
    for row, y in y_of.items():
        members = [e for e in entries if e["category"] == row]
        lo, hi = min(e["lo"] for e in members), max(e["hi"] or e["lo"] for e in members)
        need = len(row) * ROW_LABEL_CHAR_PT / per_decade_pt + 2 * ROW_LABEL_PAD_DEC
        room_left = math.log10(xmax) - math.log10(hi)  # reversed axis: higher ρ is to the left
        if room_left >= need:
            ax.text(hi * 10 ** ROW_LABEL_PAD_DEC, y, row, ha="right", va="center", fontsize=8.5, color="#333333", zorder=30)
        else:
            ax.text(lo / 10 ** ROW_LABEL_PAD_DEC, y, row, ha="left", va="center", fontsize=8.5, color="#333333", zorder=30)

    handles = [Patch(facecolor=INK, alpha=0.9, label="Commercial range")]
    if any(e.get("light") for e in entries):
        handles.append(Patch(facecolor=INK, alpha=0.3, label="Extended by research and patents"))
    if any(e["basis"] == "surface" for e in entries):
        handles.append(Patch(facecolor="none", edgecolor=INK, hatch="////", label="Surface resistance (Ω), position indicative"))
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.09), ncol=3, fontsize=7.5,
              frameon=False)
    fig.tight_layout()
    out = save_png(fig, OVERVIEW_NAME)
    plt.close(fig)
    return out


def zoom_layout(entries):
    """Split off the bulk-metal references and lay out the state-of-the-art rows and window."""
    refs = [e for e in entries if e["status"] == "Reference"]  # bulk metals -> vertical reference lines
    items = [e for e in entries if e["status"] != "Reference"]
    y_of, order = rows_for(items, ZOOM_ROW_ORDER)
    xmin, xmax = 10 ** (math.log10(ZOOM_WINDOW[0]) - 0.3), 10 ** (math.log10(ZOOM_WINDOW[1]) + 0.3)
    return refs, items, y_of, order, xmin, xmax


def row_spans(items, order):
    """Each row's span over its candidates (`Context only` entries left out), both ends of ranges included."""
    spans = {}
    for row in order:
        xs = [v for e in items if e["category"] == row and not e["context"] for v in (e["lo"], e["hi"]) if v]
        if xs:
            spans[row] = (min(xs), max(xs))
    return spans


def zoom_colour(e):
    return GREY if e["context"] else ZOOM_ROW_COLOURS.get(e["category"], GREY)


def zoom_slots(e):
    """Point labels go above first, range labels below, so a row's two kinds of label stay apart."""
    return [-1, -2, 1, 2] if e["hi"] else [1, -1, 2, -2, 3]


def draw_range_png(ax, lo, hi, y, colour, printed, z=10):
    """A range as a thin whisker with end caps: solid if printed, dashed if not printed yet."""
    ax.plot([lo, hi], [y, y], color=colour, linewidth=RANGE_LW, linestyle="-" if printed else RANGE_DASH,
            solid_capstyle="butt", dash_capstyle="butt", zorder=z)
    ax.plot([lo, hi], [y, y], linestyle="", marker="|", markersize=8, markeredgewidth=RANGE_LW, color=colour, zorder=z)


def plot_zoom_png(entries):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    refs, items, y_of, order, xmin, xmax = zoom_layout(entries)
    fig, ax = plt.subplots(figsize=(11, 1.05 * len(order) + 2.6), dpi=200)
    setup_axes(ax, xmin, xmax, order, 0, ZOOM_TITLE, top_axis="iacs", xlabel="Electrical conductivity σ (S/m)")

    ax.tick_params(axis="y", labelsize=9, length=0)

    # a faint band per row, spanning its candidates
    for row, (lo, hi) in row_spans(items, order).items():
        ax.plot([lo / 10 ** SPAN_PAD_DEC, hi * 10 ** SPAN_PAD_DEC], [y_of[row]] * 2, color=ZOOM_ROW_COLOURS.get(row, GREY),
                alpha=0.14, linewidth=SPAN_W, solid_capstyle="round", zorder=2)

    # reference lines, labelled along the top edge (empty there); neighbours alternate sides of their line
    for k, r in enumerate(sorted(refs, key=lambda r: -r["lo"])):
        main = r["label"].lower() in REF_EMPHASIS
        ax.axvline(r["lo"], color=INK, linestyle="--", linewidth=1.1 if main else 0.7, alpha=0.8 if main else 0.4, zorder=1)
        ax.text(r["lo"], -0.5, f" {r['label']} ", rotation=90, ha="right" if k % 2 == 0 else "left",
                va="top", fontsize=7, color=INK, alpha=1 if main else 0.65)

    # entries: filled = printed, hollow = not printed yet; a whisker where the source gives a range
    for e in items:
        y, c = y_of[e["category"]], zoom_colour(e)
        if e["hi"]:
            draw_range_png(ax, e["lo"], e["hi"], y, c, e["printed"], z=10)
        else:
            draw_dot_png(ax, e["lo"], y, c, hollow=not e["printed"], z=20, marker=avail_shape(e))
    labels = group_labels(items)
    place_labels(labels, lambda e: y_of[e["category"]], xmin, xmax, slots_of=zoom_slots)
    for it in labels:
        label_png(ax, it, label_x(it), y_of[it["category"]], colour=CONTEXT_INK if it["context"] else "#333333")

    from matplotlib.legend_handler import HandlerLine2D
    dot = lambda face, edge, label, m="o", **kw: Line2D([], [], marker=m, linestyle="", markersize=POINT_D,
                                                        markerfacecolor=face, markeredgecolor=edge, label=label, **kw)
    whisker = lambda ls, label: Line2D([0, 1], [0, 0], color=INK, linewidth=RANGE_LW, linestyle=ls, marker="|",
                                       markersize=8, markeredgewidth=RANGE_LW, label=label)
    shown = {AVAIL_ROWS.get(e["status"]) for e in items if not e["hi"]}
    handles = [dot(GREY, "white", name, m) for name, (m, _) in AVAIL_SHAPES.items() if name in shown]
    handles += [dot(INK, "white", "Filled = printed (paper or product)"),
                dot("white", INK, "Hollow = not printed yet (molded or patent only)", markeredgewidth=1.4)]
    whiskers = []
    if any(e["hi"] and e["printed"] for e in items):
        whiskers.append(whisker("-", "Range given by the source"))
    if any(e["hi"] and not e["printed"] for e in items):
        whiskers.append(whisker(RANGE_DASH, "Range, not printed yet"))
    handles += whiskers
    if any(e["context"] for e in items):
        handles.append(dot(GREY, "white", "Ink or liquid metal (context, not pellet/filament)"))
    if refs:
        handles.append(Line2D([0, 1], [0, 0], color=INK, linestyle="--", linewidth=1.1, label="Bulk metal"))
    ax.legend(handles=handles, handler_map={w: HandlerLine2D(numpoints=2) for w in whiskers}, loc="upper center",
              bbox_to_anchor=(0.5, -0.13), ncol=3, fontsize=7.5, frameon=False)
    fig.tight_layout()
    out = save_png(fig, ZOOM_NAME)
    plt.close(fig)
    return out


# ---------- plotly ----------
HOVER = ("<b>%{customdata[0]}</b><br>%{customdata[1]}<br>Manufacturer: %{customdata[2]}<br>ρ: %{customdata[3]}"
         "<br>Basis: %{customdata[4]}<br>Status: %{customdata[5]}<br>Format: %{customdata[6]}"
         "<br>Source note: %{customdata[7]}<br>Refs: %{customdata[8]}<extra></extra>")


def avail_layout(entries):
    """The state of the art regrouped by availability: copies with `category` = availability row."""
    refs = [e for e in entries if e["status"] == "Reference"]
    items = [{**e, "category": AVAIL_ROWS.get(e["status"], e["status"])} for e in entries if e["status"] != "Reference"]
    y_of, order = rows_for(items, AVAIL_ROW_ORDER)
    xmin, xmax = 10 ** (math.log10(ZOOM_WINDOW[0]) - 0.3), 10 ** (math.log10(ZOOM_WINDOW[1]) + 0.3)
    return refs, items, y_of, order, xmin, xmax


def plot_avail_png(entries):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    refs, items, y_of, order, xmin, xmax = avail_layout(entries)
    fig, ax = plt.subplots(figsize=(11, 1.0 * len(order) + 2.6), dpi=200)
    setup_axes(ax, xmin, xmax, order, 0, AVAIL_TITLE, top_axis="iacs", xlabel="Electrical conductivity σ (S/m)")
    for k, r in enumerate(sorted(refs, key=lambda r: -r["lo"])):
        main = r["label"].lower() in REF_EMPHASIS
        ax.axvline(r["lo"], color=INK, linestyle="--", linewidth=1.1 if main else 0.7, alpha=0.8 if main else 0.4, zorder=1)
        ax.text(r["lo"], len(order) - 0.45, f" {r['label']} ", rotation=90, ha="right" if k % 2 == 0 else "left",
                va="bottom", fontsize=7, color=INK, alpha=1 if main else 0.65)
    colour = lambda e: AVAIL_ROW_COLOURS.get(e["category"], GREY)
    for e in items:
        y, c = y_of[e["category"]], colour(e)
        if e["hi"]:
            ax.plot([e["lo"], e["hi"]], [y, y], color=c, linewidth=9.0, solid_capstyle="round", alpha=0.6, zorder=5)
        else:
            ax.scatter([e["lo"]], [y], s=POINT_D ** 2, marker=MARKERS[e["format"]][0],
                       facecolors="white" if e["sinter"] else c, edgecolors=c if e["sinter"] else "white",
                       linewidths=1.4 if e["sinter"] else 0.8, zorder=20)
    labels = group_labels(items)
    place_labels(labels, lambda e: y_of[e["category"]], xmin, xmax)
    for it in labels:
        label_png(ax, it, label_x(it), y_of[it["category"]])

    handles = [Line2D([], [], marker="o", linestyle="", markersize=POINT_D, markerfacecolor=c, markeredgecolor="white",
                      label=r) for r, c in AVAIL_ROW_COLOURS.items() if r in order]
    handles += [Line2D([], [], marker=MARKERS[k][0], linestyle="", markersize=POINT_D, markerfacecolor=GREY,
                       markeredgecolor="white", label=FORMAT_LABEL[k]) for k in FORMAT_LABEL
                if any(e["format"] == k for e in items)]
    if any(e["sinter"] for e in items):
        handles.append(Line2D([], [], marker="o", linestyle="", markersize=POINT_D, markerfacecolor="white",
                              markeredgecolor=INK, markeredgewidth=1.4, label="Hollow = requires sintering"))
    if refs:
        handles.append(Line2D([0, 1], [0, 0], color=INK, linestyle="--", linewidth=1.1, label="Bulk metal reference"))
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=4, fontsize=7.5, frameon=False,
              title="Colour = availability (row)   ·   shape = feedstock format", title_fontsize=7.5)
    fig.tight_layout()
    out = save_png(fig, AVAIL_NAME)
    plt.close(fig)
    return out


def plot_avail_html(entries):
    import plotly.graph_objects as go
    refs, items, y_of, order, xmin, xmax = avail_layout(entries)
    fig = go.Figure()
    annotations, shapes = [], []
    for e in items:
        y, c, cd = y_of[e["category"]], AVAIL_ROW_COLOURS.get(e["category"], GREY), [custom(e)]
        if e["hi"]:
            fig.add_trace(go.Scatter(x=[e["lo"], e["hi"]], y=[y, y], mode="lines", line=dict(color=c, width=BAR_PX),
                                     opacity=0.6, hoverinfo="skip", showlegend=False))
            fig.add_trace(go.Scatter(x=[gmean(e["lo"], e["hi"])], y=[y], mode="markers", customdata=cd,
                                     marker=dict(size=BAR_PX + 12, color="rgba(0,0,0,0)"), hovertemplate=HOVER,
                                     showlegend=False))
        else:
            sym = MARKERS[e["format"]][1] + ("-open" if e["sinter"] else "")
            fig.add_trace(go.Scatter(x=[e["lo"]], y=[y], mode="markers", customdata=cd, hovertemplate=HOVER,
                                     marker=dict(size=POINT_PX, color=c, symbol=sym,
                                                 line=dict(width=2 if e["sinter"] else 0, color=c)), showlegend=False))
    labels = group_labels(items)
    place_labels(labels, lambda e: y_of[e["category"]], xmin, xmax)
    for it in labels:
        annotations.append(dict(x=math.log10(label_x(it)), y=y_of[it["category"]], text=it["label"], showarrow=False,
                                yshift=14 * it.get("label_dy", 1), font=dict(size=10, color="#333333")))
    for k, r in enumerate(sorted(refs, key=lambda r: -r["lo"])):
        main = r["label"].lower() in REF_EMPHASIS
        shapes.append(dict(type="line", x0=r["lo"], x1=r["lo"], yref="paper", y0=0, y1=1, opacity=0.8 if main else 0.4,
                           line=dict(color=INK, dash="dash", width=1.5 if main else 1)))
        annotations.append(dict(x=math.log10(r["lo"]), yref="paper", y=1, yanchor="top", textangle=-90,
                                xanchor="right" if k % 2 == 0 else "left", text=r["label"], showarrow=False,
                                font=dict(size=10, color=INK)))
    decades = range(math.ceil(math.log10(xmin)), math.floor(math.log10(xmax)) + 1)
    fig.update_layout(
        title=dict(text=AVAIL_TITLE, x=0.5, xanchor="center", font=dict(size=TITLE_SIZE + 5)), template="plotly_white",
        shapes=shapes, annotations=annotations, height=60 * len(order) + 260,
        xaxis=dict(type="log", range=[math.log10(xmax), math.log10(xmin)], title="Electrical conductivity σ (S/m)",
                   tickvals=[10 ** d for d in decades], ticktext=[f"10<sup>{-d}</sup>" for d in decades]),
        yaxis=dict(tickvals=list(range(len(order))), ticktext=order, range=[len(order) - 0.5, -0.6], showgrid=False),
        margin=dict(l=200, r=40, t=80, b=60),
    )
    return save_html(fig, AVAIL_NAME)


def custom(e):
    unit = "Ω (surface resistance)" if e["basis"] == "surface" else "Ω·m"
    return [e["label"], e["note"], e["manufacturer"], f"{e['raw']} {unit}", e["value_basis"], e["status"],
            e["format_raw"], e["source"], "<br>".join(e["refs"][:4]) or "n/a"]


def plotly_overview_fig(entries, bands, order, y_of, xmin, xmax, n_lanes):
    import plotly.graph_objects as go
    fig = go.Figure()
    shapes, annotations = [], []
    for i, b in enumerate(sorted(bands, key=lambda b: -b["lo"])):
        lo, hi = max(b["lo"], xmin), min(b["hi"] or b["lo"], xmax)
        if hi <= lo:
            continue
        y = -1 - b["lane"]
        shapes.append(dict(type="rect", x0=lo, x1=hi, y0=y - 0.32, y1=y + 0.32, fillcolor=BAND_FILL[i % 2],
                           line=dict(color="white", width=1.5), layer="below"))
        annotations.append(dict(x=math.log10(gmean(lo, hi)), y=y, text=b["label"], showarrow=False,
                                font=dict(size=10, color=INK)))
    shapes.append(dict(type="rect", x0=ZOOM_WINDOW[0], x1=ZOOM_WINDOW[1], y0=-0.5, y1=len(order) - 0.5,
                       line=dict(color=INK, dash="dash", width=1)))
    for i in range(len(order) - 1):
        shapes.append(dict(type="line", xref="paper", x0=0, x1=1, y0=i + 0.5, y1=i + 0.5,
                           line=dict(color=INK, dash="dash", width=0.7), opacity=0.35))
    for row, y in y_of.items():
        members = [e for e in entries if e["category"] == row]
        hi = max(e["hi"] or e["lo"] for e in members)
        lo = min(e["lo"] for e in members)
        left = math.log10(xmax) - math.log10(hi) > 3  # rough room check, as in the PNG
        annotations.append(dict(x=math.log10(hi) + ROW_LABEL_PAD_DEC if left else math.log10(lo) - ROW_LABEL_PAD_DEC,
                                y=y, text=row, showarrow=False, xanchor="right" if left else "left",
                                font=dict(size=11, color="#333333")))
    for e in entries:  # every overview entry is a range: an area, or a row's span
        y, c = y_of[e["category"]], ROW_COLOURS.get(e["category"], GREY)
        lo, hi = (e["lo"], e["hi"]) if e["hi"] else (e["lo"] / 10 ** SINGLE_HALF_DEC, e["lo"] * 10 ** SINGLE_HALF_DEC)
        alpha = ROW_ALPHA.get(e["category"], 0.9) / (3 if e.get("light") else 1)
        surface = e["basis"] == "surface"
        shapes.append(dict(type="rect", x0=lo, x1=hi, y0=y - OVERVIEW_BAR_H / 2, y1=y + OVERVIEW_BAR_H / 2,
                           fillcolor="rgba(0,0,0,0)" if surface else c, opacity=1 if surface else alpha,
                           line=dict(color=c, width=1.5 if surface else 0, dash="dot")))
        fig.add_trace(go.Scatter(x=[gmean(lo, hi)], y=[y], mode="markers",
                                 marker=dict(size=24, color="rgba(0,0,0,0)"), customdata=[custom(e)],
                                 hovertemplate=HOVER, showlegend=False))
    decades = range(math.ceil(math.log10(xmin)), math.floor(math.log10(xmax)) + 1, 3)
    fig.update_layout(
        title=dict(text=OVERVIEW_TITLE, x=0.5, xanchor="center", font=dict(size=TITLE_SIZE + 5)),
        template="plotly_white", shapes=shapes, annotations=annotations, height=60 * (len(order) + n_lanes) + 200,
        xaxis=dict(type="log", range=[math.log10(xmax), math.log10(xmin)],
                   title="Electrical conductivity σ (S/m)   (resistivity ρ = 1/σ in the hover)",
                   tickvals=[10 ** d for d in decades], ticktext=[f"10<sup>{-d}</sup>" for d in decades]),
        yaxis=dict(tickvals=[], ticktext=[], range=[len(order) - 0.5, -n_lanes - 0.6], showgrid=False),
        margin=dict(l=40, r=40, t=70, b=60),
    )
    return fig


def save_html(fig, name):
    out, tmp = OUT_DIR / f"{name}.html", OUT_DIR / f"{name}.tmp.html"
    fig.write_html(tmp, include_plotlyjs=True, full_html=True)
    replace_file(tmp, out)
    return out


def plot_overview_html(entries, bands):
    y_of, order = rows_for(entries, ROW_ORDER)
    n_lanes = band_lanes(bands)
    xmin, xmax = x_limits(entries + bands)
    return save_html(plotly_overview_fig(entries, bands, order, y_of, xmin, xmax, n_lanes), OVERVIEW_NAME)


HOVER_ZOOM = ("<b>%{customdata[0]}</b><br>%{customdata[1]}<br>%{customdata[2]}<br>σ: %{customdata[3]} S/m"
              "   (ρ: %{customdata[4]} Ω·m)<br>Printed: %{customdata[5]}<br>Manufacturer: %{customdata[6]}"
              "<br>Status: %{customdata[7]}<br>Format: %{customdata[8]}<br>Basis: %{customdata[9]}"
              "<br>Source note: %{customdata[10]}<extra></extra>")


def zoom_custom(e):
    sigma = f"{1 / e['hi']:.2g} to {1 / e['lo']:.2g}" if e["hi"] else f"{1 / e['lo']:.3g}"
    printed = "yes" if e["printed"] else "not yet (molded or patent only)"
    if e["context"]:
        printed += "; shown for context (not a pellet/filament feedstock)"
    return [e["label"], e["note"], e["category"], sigma, e["raw"], printed, e["manufacturer"], e["status"],
            e["format_raw"], e["value_basis"], e["source"]]


def plot_zoom_html(entries):
    """The state-of-the-art ladder with hover details; same encodings as the PNG."""
    import plotly.graph_objects as go
    refs, items, y_of, order, xmin, xmax = zoom_layout(entries)
    fig = go.Figure()
    shapes, annotations = [], []  # on a log axis, shapes take data values and annotations take log10 values
    for row, (lo, hi) in row_spans(items, order).items():
        y = y_of[row]
        shapes.append(dict(type="rect", x0=lo / 10 ** SPAN_PAD_DEC, x1=hi * 10 ** SPAN_PAD_DEC, y0=y - 0.17, y1=y + 0.17,
                           fillcolor=ZOOM_ROW_COLOURS.get(row, GREY), opacity=0.14, line=dict(width=0), layer="below"))
    for k, r in enumerate(sorted(refs, key=lambda r: -r["lo"])):  # rotated labels along the top, sides alternating
        main = r["label"].lower() in REF_EMPHASIS
        shapes.append(dict(type="line", x0=r["lo"], x1=r["lo"], yref="paper", y0=0, y1=1, opacity=0.8 if main else 0.4,
                           line=dict(color=INK, dash="dash", width=1.5 if main else 1)))
        annotations.append(dict(x=math.log10(r["lo"]), yref="paper", y=1, yanchor="top", textangle=-90,
                                xanchor="right" if k % 2 == 0 else "left", text=r["label"], showarrow=False,
                                font=dict(size=10, color=INK)))
    for e in items:
        y, c, cd = y_of[e["category"]], zoom_colour(e), [zoom_custom(e)]
        if e["hi"]:
            fig.add_trace(go.Scatter(x=[e["lo"], e["hi"]], y=[y, y], mode="lines+markers", hoverinfo="skip",
                                     showlegend=False, line=dict(color=c, width=2.5, dash="solid" if e["printed"] else "dot"),
                                     marker=dict(symbol="line-ns-open", size=12, line=dict(width=2.5, color=c))))
            xs = [e["lo"], gmean(e["lo"], e["hi"]), e["hi"]]  # hover anywhere along the whisker
            fig.add_trace(go.Scatter(x=xs, y=[y] * 3, mode="markers", marker=dict(size=BAR_PX + 12, color="rgba(0,0,0,0)"),
                                     customdata=cd * 3, hovertemplate=HOVER_ZOOM, showlegend=False))
        else:
            hollow = not e["printed"]
            fig.add_trace(go.Scatter(x=[e["lo"]], y=[y], mode="markers", customdata=cd, hovertemplate=HOVER_ZOOM,
                                     marker=dict(size=POINT_PX + 2, color="white" if hollow else c,
                                                 symbol=avail_shape(e, plotly=True),
                                                 line=dict(width=2 if hollow else 1, color=c if hollow else "white")),
                                     showlegend=False))
    labels = group_labels(items)
    place_labels(labels, lambda e: y_of[e["category"]], xmin, xmax, slots_of=zoom_slots)
    for it in labels:
        s = it.get("label_dy", 1)
        a = dict(x=math.log10(label_x(it)), y=y_of[it["category"]], text=it["label"],
                 font=dict(size=10, color=CONTEXT_INK if it["context"] else "#333333"))
        if abs(s) >= 2:  # leader line, as in the PNG; a shifted label puts its tail at the shifted x
            x_text = label_x(it) * 10 ** it.get("label_dx", 0.0)
            a.update(x=math.log10(leader_target(it, x_text)), showarrow=True, arrowhead=0, arrowwidth=0.8,
                     arrowcolor=LEADER, ay=-14 * s, standoff=5, axref="x", ax=math.log10(x_text))
        else:
            a.update(showarrow=False, yshift=14 * s)
        annotations.append(a)
    shown = {AVAIL_ROWS.get(e["status"]) for e in items if not e["hi"]}
    legend = [(name, dict(color=GREY, symbol=sym, line=dict(width=1, color="white")))
              for name, (_, sym) in AVAIL_SHAPES.items() if name in shown]
    legend += [("Filled = printed (paper or product)", dict(color=INK, line=dict(width=1, color="white"))),
               ("Hollow = not printed yet (molded or patent only)", dict(color="white", line=dict(width=2, color=INK)))]
    if any(e["context"] for e in items):
        legend.append(("Ink or liquid metal (context, not pellet/filament)", dict(color=GREY, line=dict(width=1, color="white"))))
    for name, marker in legend:
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name=name, marker=dict(size=POINT_PX + 2, **marker)))
    for printed, dash, name in ((True, "solid", "Range given by the source"), (False, "dot", "Range, not printed yet")):
        if any(e["hi"] and e["printed"] == printed for e in items):
            fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name=name,
                                     line=dict(color=INK, width=2.5, dash=dash)))
    if refs:
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name="Bulk metal",
                                 line=dict(color=INK, dash="dash", width=1.5)))
    decades = range(math.ceil(math.log10(xmin)), math.floor(math.log10(xmax)) + 1)
    ticktext = list(order)
    fig.update_layout(
        title=dict(text=ZOOM_TITLE, x=0.5, xanchor="center", font=dict(size=TITLE_SIZE + 5)), template="plotly_white",
        shapes=shapes, annotations=annotations, height=120 * len(order) + 240,
        xaxis=dict(type="log", range=[math.log10(xmax), math.log10(xmin)], title="Electrical conductivity σ (S/m)",
                   tickvals=[10 ** d for d in decades], ticktext=[f"10<sup>{-d}</sup>" for d in decades]),
        yaxis=dict(tickvals=list(range(len(order))), ticktext=ticktext, range=[len(order) - 0.5, -0.5],
                   showgrid=False, zeroline=False),
        legend=dict(orientation="h", yanchor="top", y=-0.16, xanchor="center", x=0.5),
        margin=dict(l=300, r=40, t=90, b=120),
    )
    return save_html(fig, ZOOM_NAME)


# ---------- main ----------
def main():
    rows, skipped, unresolved, view = collect()
    print(f"Base: {BASE_FILE.relative_to(VAULT).as_posix()}  (view: {view})")
    for w in warnings:
        print(f"  WARNING: {w}")
    if not rows:
        sys.exit("No plottable entries found.")

    def pick(plot):
        return [r for r in rows if plot in r["plots"]]

    ov_all, zm_all = pick("Overview"), pick("Zoom")
    # the overview keeps its coarse rows: the state-of-the-art categories fold into them
    ov_all = [{**r, "category": OVERVIEW_ROW_OF.get(r["category"], r["category"])} for r in ov_all]
    # Literature entries in the overview only extend their row's span (drawn lighter), never drawn on their own
    ov = overview_areas([r for r in ov_all if r["type"] != "Band"])
    ov_bands = [dict(r) for r in ov_all if r["type"] == "Band"]
    zm = [r for r in zm_all if r["type"] != "Band"
          and (r["hi"] or r["lo"]) >= ZOOM_WINDOW[0] * 0.5 and r["lo"] <= ZOOM_WINDOW[1] * 2]
    outside = sorted(r["note"] for r in zm_all if r["type"] != "Band" and r not in zm)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outs = []
    if ov:
        outs += [plot_overview_png(ov, ov_bands), plot_overview_html(ov, ov_bands)]
    if zm:
        outs += [plot_avail_png(zm), plot_avail_html(zm), plot_zoom_png(zm), plot_zoom_html(zm)]
    candidates = [r for r in zm if r["status"] != "Reference"]
    no_row = sorted(f"{r['note']} ('{r['category']}')" for r in candidates if r["category"] not in ZOOM_ROW_ORDER)
    if no_row:
        print(f"WARNING: Plot category without a state-of-the-art row (drawn in its own row): {', '.join(no_row)}")
    no_flag = sorted(r["note"] for r in candidates if r["printed_missing"])
    if no_flag:
        print(f"WARNING: no `Printed` property (drawn as not printed): {', '.join(no_flag)}")

    print(f"Overview: {len(ov)} entries + {len(ov_bands)} bands.  State of the art: {len(zm)} entries.")
    print(f"Skipped (no value): {len(skipped)}  {', '.join(sorted(skipped))}")
    if unresolved:
        print(f"Unresolved Source note links: {', '.join(sorted(unresolved))}")
    if outside:
        print(f"Zoom entries outside the window (not drawn): {', '.join(outside)}")
    print(f"Still 'To validate': {sum(r['to_validate'] for r in rows)} of {len(rows)} plotted-capable entries")
    print("Wrote: " + "\n       ".join(o.relative_to(VAULT).as_posix() for o in outs))


if __name__ == "__main__":
    main()
