# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml", "matplotlib", "plotly"]
# ///
"""
AM feedstock resistivity map: an overview figure and a zoom on the near-metal window.

Reads the entries listed by the first view of notes/hardware/AM feedstock map/AM feedstock map.base.
Each entry picks its figure(s) with the `Plots` property (Overview / Zoom). Link-only entries
(`Source note: "[[...]]"`) take their values from the linked material note.

Run from anywhere:   uv run scripts/plot_am_feedstock_map.py
Writes images/plots/am_feedstock_overview.(png|html) and am_feedstock_zoom_metals.(png|html).
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
ZOOM_NAME = "am_feedstock_state_of_the_art"
OVERVIEW_TITLE = "Commercial AM feedstocks: volume resistivity overview"
ZOOM_TITLE = "State of the art: near-metal window"

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

# State of the art: rows = availability (from `Commercial status`), colour = material family (`Plot category`)
ZOOM_ROWS = {
    "Commercial AM feedstock": "Commercially available",
    "Commercial molding-only": "Commercially available",
    "Research": "Research (papers)",
    "Patent": "Patents",
    "Reference": "Bulk metals",
}
ZOOM_ROW_ORDER = ["Commercially available", "Research (papers)", "Patents", "Bulk metals"]
ZOOM_ROW_COLOURS = {  # colour repeats the row, so availability reads at a glance
    "Commercially available": PALETTE[0],
    "Research (papers)": PALETTE[2],
    "Patents": PALETTE[1],
    "Bulk metals": INK,
}

MARKERS = {"filament": ("o", "circle"), "pellet": ("s", "square"), "ink": ("^", "triangle-up"),
           "other": ("D", "diamond")}
FORMAT_LABEL = {"filament": "Filament", "pellet": "Pellets", "ink": "Ink / paste", "other": "Molded / other"}
POINT_D = 7.0      # marker diameter, pt
BAR_W = 9.0        # range bar width in the state-of-the-art plot, pt
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


def place_labels(entries, y_of, xmin, xmax, prefer_below_ranges=False):
    """Greedy label slots per row: a label takes the first slot (above, below, higher, lower, ...) where it
    doesn't overlap a label already placed in that slot. Overlap is judged in log-x using an estimated text width."""
    per_decade_pt = AXES_PT / (math.log10(xmax) - math.log10(xmin))
    per_row = defaultdict(list)
    for e in entries:
        per_row[y_of(e)].append(e)
    for group in per_row.values():
        taken = defaultdict(list)  # slot -> [(x0, x1)]
        for e in sorted(group, key=lambda e: -label_x(e)):
            cx = math.log10(label_x(e))
            half = len(e["label"]) * CHAR_PT / 2 / per_decade_pt + 0.05
            slots = ([-1, 1, -2, 2, -3] if (prefer_below_ranges and e["hi"]) else LABEL_SLOTS)
            for s in slots:
                if all(cx + half < a or cx - half > b for a, b in taken[s]):
                    break
            else:
                s = slots[-1]
            taken[s].append((cx - half, cx + half))
            e["label_dy"] = s


# ---------- matplotlib ----------
def setup_axes(ax, xmin, xmax, order, n_lanes, title):
    ax.set_xscale("log")
    ax.set_xlim(xmax, xmin)  # reversed: insulators left, metals right
    ax.set_ylim(len(order) - 0.4, -n_lanes - 0.6)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels(order, fontsize=8.5)
    ax.set_xlabel("Volume resistivity ρ (Ω·m)")
    ax.grid(True, axis="x", which="major", alpha=0.25)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    import numpy as np

    def inv(x):
        x = np.asarray(x, dtype=float)
        with np.errstate(divide="ignore"):
            return np.where(x > 0, 1.0 / np.where(x > 0, x, 1.0), np.inf)

    top = ax.secondary_xaxis("top", functions=(inv, inv))
    top.set_xlabel("Conductivity σ (S/m)", fontsize=9)
    ax.set_title(title, fontsize=11, loc="center", pad=28)


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


def draw_point_png(ax, x, y, colour, kind, hollow, z=10):
    ax.scatter([x], [y], s=POINT_D ** 2, marker=MARKERS[kind][0], facecolors="white" if hollow else colour,
               edgecolors=colour if hollow else "white", linewidths=1.4 if hollow else 0.8, zorder=z)


def label_png(ax, e, x, y, colour="#333333"):
    s = e.get("label_dy", 1)
    # y axis is inverted (row 0 at top), so "above" on screen is a positive offset in points
    ax.annotate(e["label"], (x, y), xytext=(0, LABEL_STEP * s + (-3 if s < 0 else 0)), textcoords="offset points",
                ha="center", va="bottom" if s > 0 else "top", fontsize=7, color=colour, zorder=30)


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
        ranges = [e for e in group if e["hi"]]
        if ranges:
            areas += [dict(e) for e in ranges]
            continue
        commercial = [e for e in group if e["status"].startswith("Commercial") or e["status"] == "Reference"]
        others = [e for e in group if e not in commercial]
        # full span (incl. research / patents) drawn light underneath, commercial span drawn solid on top
        for members, light in ((group, True), (commercial, False)) if others and commercial else ((group, False),):
            vals = [e["lo"] for e in members]
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
    setup_axes(ax, xmin, xmax, order, n_lanes, OVERVIEW_TITLE)
    draw_bands_png(ax, bands, xmin, xmax, len(order))

    # zoom window
    zlo, zhi = ZOOM_WINDOW
    ax.add_patch(Rectangle((zlo, -0.5), zhi - zlo, len(order), fill=False, linestyle="--", edgecolor=INK,
                           linewidth=1.0, zorder=3))
    ax.text(gmean(zlo, zhi), len(order) - 0.5, "state of the art", ha="center", va="bottom", fontsize=7.5, color=INK)

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


def plot_zoom_png(entries, bands):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    y_of, order = rows_for(entries, ZOOM_ROW_ORDER)
    xmin, xmax = 10 ** (math.log10(ZOOM_WINDOW[0]) - 0.3), 10 ** (math.log10(ZOOM_WINDOW[1]) + 0.3)
    n_lanes = band_lanes(bands)
    fig, ax = plt.subplots(figsize=(11, 1.0 * (len(order) + n_lanes) + 2.6), dpi=200)
    setup_axes(ax, xmin, xmax, order, n_lanes, ZOOM_TITLE)
    draw_bands_png(ax, bands, xmin, xmax, len(order))

    colour = lambda e: ZOOM_ROW_COLOURS.get(e["category"], GREY)
    place_labels(entries, lambda e: y_of[e["category"]], xmin, xmax)
    for e in entries:
        y, c = y_of[e["category"]], colour(e)
        if e["hi"]:
            ax.plot([e["lo"], e["hi"]], [y, y], color=c, linewidth=BAR_W, solid_capstyle="round", alpha=0.6, zorder=5)
            label_png(ax, e, gmean(e["lo"], e["hi"]), y)
        else:
            draw_point_png(ax, e["lo"], y, c, e["format"], e["sinter"], z=20)
            label_png(ax, e, e["lo"], y)

    handles = [Line2D([], [], marker="o", linestyle="", markersize=POINT_D, markerfacecolor=c, markeredgecolor="white",
                      label=r) for r, c in ZOOM_ROW_COLOURS.items() if r in order]
    handles += [Line2D([], [], marker=MARKERS[k][0], linestyle="", markersize=POINT_D, markerfacecolor=GREY,
                       markeredgecolor="white", label=FORMAT_LABEL[k]) for k in FORMAT_LABEL
                if any(e["format"] == k for e in entries)]
    if any(e["sinter"] for e in entries):
        handles.append(Line2D([], [], marker="o", linestyle="", markersize=POINT_D, markerfacecolor="white",
                              markeredgecolor=INK, markeredgewidth=1.4, label="Hollow = requires sintering"))
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.09), ncol=4, fontsize=7.5, frameon=False,
              title="Colour = availability (row)   ·   shape = feedstock format", title_fontsize=7.5)
    fig.tight_layout()
    out = save_png(fig, ZOOM_NAME)
    plt.close(fig)
    return out


# ---------- plotly ----------
HOVER = ("<b>%{customdata[0]}</b><br>%{customdata[1]}<br>Manufacturer: %{customdata[2]}<br>ρ: %{customdata[3]}"
         "<br>Basis: %{customdata[4]}<br>Status: %{customdata[5]}<br>Format: %{customdata[6]}"
         "<br>Source note: %{customdata[7]}<br>Refs: %{customdata[8]}<extra></extra>")


def custom(e):
    unit = "Ω (surface resistance)" if e["basis"] == "surface" else "Ω·m"
    return [e["label"], e["note"], e["manufacturer"], f"{e['raw']} {unit}", e["value_basis"], e["status"],
            e["format_raw"], e["source"], "<br>".join(e["refs"][:4]) or "n/a"]


def plotly_fig(entries, bands, order, y_of, xmin, xmax, n_lanes, title, colour_of, mode):
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
    if mode == "overview":
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
    for e in entries:
        y, c = y_of[e["category"]], colour_of(e)
        if mode == "overview" and e["hi"]:
            alpha = ROW_ALPHA.get(e["category"], 0.9) / (3 if e.get("light") else 1)
            surface = e["basis"] == "surface"
            shapes.append(dict(type="rect", x0=e["lo"], x1=e["hi"], y0=y - OVERVIEW_BAR_H / 2, y1=y + OVERVIEW_BAR_H / 2,
                               fillcolor="rgba(0,0,0,0)" if surface else c, opacity=1 if surface else alpha,
                               line=dict(color=c, width=1.5 if surface else 0, dash="dot")))
            fig.add_trace(go.Scatter(x=[gmean(e["lo"], e["hi"])], y=[y], mode="markers",
                                     marker=dict(size=24, color="rgba(0,0,0,0)"), customdata=[custom(e)],
                                     hovertemplate=HOVER, showlegend=False))
            continue
        if e["hi"]:
            width = BAR_PX
            fig.add_trace(go.Scatter(x=[e["lo"], e["hi"]], y=[y, y], mode="lines", showlegend=False,
                                     line=dict(color=c, width=width, dash="dot" if e["basis"] == "surface" else "solid"),
                                     opacity=0.3 if e.get("light") else 0.9, hoverinfo="skip"))
            fig.add_trace(go.Scatter(x=[gmean(e["lo"], e["hi"])], y=[y], mode="markers+text",
                                     text=[e["label"] if mode != "overview" else ""],
                                     textposition="top center", marker=dict(size=BAR_PX + 4, color="rgba(0,0,0,0)"),
                                     customdata=[custom(e)], hovertemplate=HOVER, showlegend=False,
                                     textfont=dict(size=10)))
        else:
            sym = MARKERS[e["format"]][1] + ("-open" if e["sinter"] else "")
            fig.add_trace(go.Scatter(x=[e["lo"]], y=[y], mode="markers+text", text=[e["label"]],
                                     textposition="top center" if e.get("label_dy", 1) > 0 else "bottom center",
                                     marker=dict(size=POINT_PX, color=c, symbol=sym, line=dict(width=2 if e["sinter"] else 0, color=c)),
                                     customdata=[custom(e)], hovertemplate=HOVER, showlegend=False, textfont=dict(size=10)))
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor="center"), template="plotly_white", shapes=shapes, annotations=annotations,
        height=60 * (len(order) + n_lanes) + 200,
        xaxis=dict(type="log", range=[math.log10(xmax), math.log10(xmin)], title="Volume resistivity ρ (Ω·m)",
                   exponentformat="power"),
        yaxis=dict(tickvals=[] if mode == "overview" else list(range(len(order))),
                   ticktext=[] if mode == "overview" else order, range=[len(order) - 0.5, -n_lanes - 0.6],
                   showgrid=False),
        margin=dict(l=40 if mode == "overview" else 260, r=40, t=70, b=60),
    )
    return fig


def save_html(fig, name):
    out, tmp = OUT_DIR / f"{name}.html", OUT_DIR / f"{name}.tmp.html"
    fig.write_html(tmp, include_plotlyjs=True, full_html=True)
    replace_file(tmp, out)
    return out


def plot_html(entries, bands, mode):
    y_of, order = rows_for(entries, ROW_ORDER if mode == "overview" else ZOOM_ROW_ORDER)
    n_lanes = band_lanes(bands)
    if mode == "overview":
        xmin, xmax = x_limits(entries + bands)
        colour_of = lambda e: ROW_COLOURS.get(e["category"], GREY)
        title, name = OVERVIEW_TITLE, OVERVIEW_NAME
    else:
        xmin, xmax = 10 ** (math.log10(ZOOM_WINDOW[0]) - 0.3), 10 ** (math.log10(ZOOM_WINDOW[1]) + 0.3)
        colour_of = lambda e: ZOOM_ROW_COLOURS.get(e["category"], GREY)
        title, name = ZOOM_TITLE, ZOOM_NAME
    place_labels(entries, lambda e: y_of[e["category"]], xmin, xmax, prefer_below_ranges=(mode == "overview"))
    return save_html(plotly_fig(entries, bands, order, y_of, xmin, xmax, n_lanes, title, colour_of, mode), name)


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
    # Literature entries in the overview only extend their row's span (drawn lighter), never drawn on their own
    ov = overview_areas([r for r in ov_all if r["type"] != "Band"])
    ov_bands = [dict(r) for r in ov_all if r["type"] == "Band"]
    zm = [r for r in zm_all if r["type"] != "Band"
          and (r["hi"] or r["lo"]) >= ZOOM_WINDOW[0] * 0.5 and r["lo"] <= ZOOM_WINDOW[1] * 2]
    outside = sorted(r["note"] for r in zm_all if r["type"] != "Band" and r not in zm)
    zm_bands = [dict(r) for r in zm_all if r["type"] == "Band"]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outs = []
    if ov:
        outs += [plot_overview_png(ov, ov_bands), plot_html(ov, ov_bands, "overview")]
    def zoom_rows():
        """Copies regrouped for the state-of-the-art plot: row = availability, family = the original category."""
        return [{**r, "family": r["category"], "category": ZOOM_ROWS.get(r["status"], r["status"])} for r in zm]

    no_row = sorted(f"{r['note']} ('{r['status']}')" for r in zm if r["status"] not in ZOOM_ROWS)
    if zm:
        outs += [plot_zoom_png(zoom_rows(), zm_bands), plot_html(zoom_rows(), zm_bands, "zoom")]
    if no_row:
        print(f"WARNING: Commercial status without a state-of-the-art row (drawn in its own row): {', '.join(no_row)}")

    print(f"Overview: {len(ov)} entries + {len(ov_bands)} bands.  Zoom: {len(zm)} entries + {len(zm_bands)} bands.")
    print(f"Skipped (no value): {len(skipped)}  {', '.join(sorted(skipped))}")
    if unresolved:
        print(f"Unresolved Source note links: {', '.join(sorted(unresolved))}")
    if outside:
        print(f"Zoom entries outside the window (not drawn): {', '.join(outside)}")
    print(f"Still 'To validate': {sum(r['to_validate'] for r in rows)} of {len(rows)} plotted-capable entries")
    print("Wrote: " + "\n       ".join(o.relative_to(VAULT).as_posix() for o in outs))


if __name__ == "__main__":
    main()
