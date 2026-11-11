# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml", "matplotlib", "plotly"]
# ///
"""
Saturation vs permeability plot for the soft magnetic materials.

Reads the filters from notes/hardware/Soft magnetic materials.base, collects the
matching notes, and writes a static PNG and an interactive Plotly HTML to images/plots/.

Run from anywhere:   uv run scripts/plot_soft_magnetic.py

Nothing here depends on the current data: axis padding and the nudge between overlapping
ranges scale with the data range, the top matrices are recomputed every run, and new
matrices / companies / folders are picked up automatically.
"""
from __future__ import annotations

import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

# ---------- settings (the only things meant to be edited) ----------
VAULT = Path(__file__).resolve().parent.parent
BASE_FILE = VAULT / "notes" / "hardware" / "Soft magnetic materials.base"
OUT_DIR = VAULT / "images" / "plots"
OUT_NAME = "soft_magnetic_saturation_vs_permeability"

MU_KEY = "Permeability"
JS_KEY = "Magnetic saturation (T)"
MATRIX_KEY = "Matrix"
STATUS_KEY = "Status"
ORDERED_STATUS = "ordered"  # notes whose Status starts with this (any case) are drawn as an x
TOP_N = 3  # matrices that get their own colour; the rest are "Other matrices"

# Colour = polymer matrix. Dataviz reference-palette slots in their validated order; the first
# three are documented as distinguishable in scatter plots (all pairs, incl. colour-blindness).
# If TOP_N is raised above 3 the extra slots are used, but they are less distinct.
PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#e87ba4", "#4a3aa7", "#e34948"]
OTHER_COLOR = "#a8a69e"

POINT_D = 5.0        # point diameter, pt (PNG)
LINE_W = POINT_D     # range line width = point diameter, so a range reads as one shape
POINT_PX = 7         # point diameter, px (HTML)
LINE_PX = POINT_PX   # same rule for the HTML
DODGE_FRAC = 0.006   # nudge between ranges at the same saturation, as a fraction of the x-span
SAME_X_FRAC = 0.004  # ranges closer than this fraction of the x-span count as "same saturation"
PAD_FRAC = 0.03      # axis padding, as a fraction of the data span

warnings: list[str] = []


# ---------- base filters ----------
def compile_filter(node):
    """Turn a base filter tree into a predicate(note_dict, rel_path) -> bool."""
    if node is None:
        return lambda n, p: True
    if isinstance(node, dict):
        if "and" in node:
            parts = [compile_filter(x) for x in node["and"]]
            return lambda n, p: all(f(n, p) for f in parts)
        if "or" in node:
            parts = [compile_filter(x) for x in node["or"]]
            return lambda n, p: any(f(n, p) for f in parts)
        if "not" in node:
            parts = [compile_filter(x) for x in node["not"]]
            return lambda n, p: not any(f(n, p) for f in parts)
        warnings.append(f"unsupported filter group: {node}")
        return lambda n, p: True

    s = str(node).strip()
    m = re.fullmatch(r'(!)?\s*file\.inFolder\(\s*"(.+?)"\s*\)', s)
    if m:
        neg, folder = bool(m.group(1)), m.group(2).strip("/")
        def in_folder(n, p, folder=folder, neg=neg):
            hit = p == folder or p.startswith(folder + "/")
            return not hit if neg else hit
        return in_folder
    m = re.fullmatch(r'(!)?\s*file\.hasTag\(\s*"(.+?)"\s*\)', s)
    if m:
        neg, tag = bool(m.group(1)), m.group(2)
        def has_tag(n, p, tag=tag, neg=neg):
            tags = n.get("tags") or []
            tags = [tags] if isinstance(tags, str) else tags
            hit = tag in [str(t).lstrip("#") for t in tags]
            return not hit if neg else hit
        return has_tag
    m = re.fullmatch(r'(?:note\[\s*"(.+?)"\s*\]|note\.(\S+)|([^=!]+?))\s*(==|!=)\s*"(.*)"', s)
    if m:
        prop = (m.group(1) or m.group(2) or m.group(3)).strip()
        op, val = m.group(4), m.group(5)
        def compare(n, p, prop=prop, op=op, val=val):
            v = n.get(prop)
            vals = [str(x).strip() for x in v] if isinstance(v, list) else [str(v if v is not None else "").strip()]
            hit = val in vals
            return hit if op == "==" else not hit
        return compare
    warnings.append(f"unsupported filter (ignored): {s}")
    return lambda n, p: True


def load_base_filter():
    base = yaml.safe_load(BASE_FILE.read_text(encoding="utf-8")) or {}
    view = (base.get("views") or [{}])[0]
    top, view_f = compile_filter(base.get("filters")), compile_filter(view.get("filters"))
    desc = {"base filters": base.get("filters"), "view filters": view.get("filters"), "view": view.get("name")}
    return (lambda n, p: top(n, p) and view_f(n, p)), desc


# ---------- notes ----------
def frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.S)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        warnings.append(f"bad frontmatter in {path.name}: {e}")
        return {}


NUM = r"\d+(?:[.,]\d+)?(?:[eE][+-]?\d+)?"


def _num(s: str) -> float:
    return float(s.replace(",", "."))


def parse_value(v):
    """'< 5'->5, '≤ 0.30'->0.30, '~47'->47, '44-94'->44 (lower), '17 (at 1 MHz)'->17, n/a/empty->None."""
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().strip('"').strip()
    if not s or s.lower() in {"n/a", "na", "-", "none", "?"}:
        return None
    m = re.search(NUM, s)  # first number = the bound for '<'/'≤', the lower end of a range
    return _num(m.group(0)) if m else None


def parse_upper(v):
    """Upper end of a range ('44-94' -> 94, '30 – 45*' -> 45); None if the value isn't a range."""
    if v is None or isinstance(v, (bool, int, float)):
        return None
    m = re.search(rf"({NUM})\s*(?:-|–|—|to)\s*({NUM})", str(v))
    if not m:
        return None
    lo, hi = _num(m.group(1)), _num(m.group(2))
    return hi if hi > lo else None


def normalise_matrix(v) -> str:
    """One label per polymer, however it's written: 'PA 12'/'PA12*' -> PA12, 'PA6.6' -> PA66,
    'PPA (PA9T)' -> PPA, lists like 'PP, PBT, PA12' -> Multiple, empty/n/a -> Unknown."""
    if v is None:
        return "Unknown"
    if isinstance(v, list):
        return "Multiple" if len(v) > 1 else normalise_matrix(v[0] if v else None)
    s = str(v).strip()
    if not s or s.lower() in {"n/a", "na", "-", "unknown"}:
        return "Unknown"
    s = re.sub(r"\(.*?\)", "", s).replace("*", "")
    if re.search(r"[,;+&]|\band\b|/", s):
        return "Multiple"
    s = re.sub(r"\s+", "", s).upper()
    s = re.sub(r"^PA(\d)\.(\d)$", r"PA\1\2", s)  # PA6.6 -> PA66
    return s or "Unknown"


def collect():
    keep, desc = load_base_filter()
    rows, skipped = [], []
    for path in VAULT.rglob("*.md"):
        rel = path.relative_to(VAULT).as_posix()
        if rel.startswith(".") or "/." in rel:
            continue
        fm = frontmatter(path)
        if not fm or not keep(fm, rel):
            continue
        mu_raw, js_raw = fm.get(MU_KEY), fm.get(JS_KEY)
        mu, js = parse_value(mu_raw), parse_value(js_raw)
        if mu is None and js is None:
            skipped.append(path.stem)
            continue
        rows.append({
            "note": path.stem,
            "manufacturer": str(fm.get("Manufacturer") or "n/a").replace("[[", "").replace("]]", ""),
            "matrix_raw": str(fm.get(MATRIX_KEY) or "n/a"),
            "filler": str(fm.get("Filler") or "n/a"),
            "matrix": normalise_matrix(fm.get(MATRIX_KEY)),
            "mu_raw": "n/a" if mu_raw in (None, "") else str(mu_raw),
            "js_raw": "n/a" if js_raw in (None, "") else str(js_raw),
            "mu": mu if mu is not None else 0.0,
            "js": js if js is not None else 0.0,
            "mu_hi": parse_upper(mu_raw) if mu is not None else None,
            "js_hi": parse_upper(js_raw) if js is not None else None,
            "filled": mu is None or js is None,
            "ordered": str(fm.get(STATUS_KEY) or "").strip().lower().startswith(ORDERED_STATUS),
        })
    return rows, skipped, desc


def mu_max(r):
    return r["mu_hi"] if r["mu_hi"] is not None else r["mu"]


def pick_top(rows):
    """Matrices that appear most often in the top third by permeability (upper end of ranges);
    ties go to the higher best value. 'Unknown' never counts as a material."""
    ranked = sorted(rows, key=mu_max, reverse=True)
    top_third = ranked[: max(1, math.ceil(len(ranked) / 3))]
    best = {}
    for r in ranked:
        best.setdefault(r["matrix"], mu_max(r))
    counts = Counter(r["matrix"] for r in top_third if r["matrix"] != "Unknown")
    order = sorted(counts, key=lambda m: (-counts[m], -best[m]))
    rest = sorted((m for m in best if m not in order and m != "Unknown"), key=lambda m: -best[m])
    return (order + rest)[:TOP_N], counts, len(top_third)


# ---------- geometry (all relative to the data, nothing absolute) ----------
def data_span(values):
    lo, hi = min(values), max(values)
    return lo, hi, (hi - lo) or abs(hi) or 1.0


def assign_dodge(rows):
    """Spread vertical range lines that sit at (nearly) the same saturation so they don't hide each other."""
    xs = [r["js"] for r in rows] + [r["js_hi"] for r in rows if r["js_hi"] is not None]
    _, _, span = data_span(xs)
    tol, step = SAME_X_FRAC * span, DODGE_FRAC * span
    vertical = sorted((r for r in rows if r["mu_hi"] is not None and r["js_hi"] is None), key=lambda r: r["js"])
    for r in rows:
        r["dx"] = 0.0
    clusters, current = [], []
    for r in vertical:
        if current and r["js"] - current[-1]["js"] > tol:
            clusters.append(current)
            current = []
        current.append(r)
    if current:
        clusters.append(current)
    for group in clusters:
        if len(group) > 1:
            group.sort(key=lambda r: (r["mu"], mu_max(r)))
            for k, r in enumerate(group):
                r["dx"] = (k - (len(group) - 1) / 2) * step


def ends(r):
    """Points to draw: one point, or both ends of a measured range."""
    x_lo, x_hi = r["js"] + r["dx"], (r["js_hi"] if r["js_hi"] is not None else r["js"]) + r["dx"]
    y_lo, y_hi = r["mu"], mu_max(r)
    return [(x_lo, y_lo)] if (x_lo, y_lo) == (x_hi, y_hi) else [(x_lo, y_lo), (x_hi, y_hi)]


def axis_limits(rows):
    pts = [p for r in rows for p in ends(r)]
    x0, x1, xs = data_span([p[0] for p in pts] + [0.0])
    y0, y1, ys = data_span([p[1] for p in pts] + [0.0])
    return (x0 - PAD_FRAC * xs, x1 + PAD_FRAC * xs), (y0 - PAD_FRAC * ys, y1 + PAD_FRAC * ys)


def emptiest_corner(rows):
    """Plot corner whose region holds the fewest points, so an in-plot legend covers as little data as possible."""
    (xl, xr), (yb, yt) = axis_limits(rows)
    pts = [p for r in rows for p in ends(r)]
    def count(right, top):
        x_cut = xl + (0.6 if right else 0.4) * (xr - xl)
        y_cut = yb + (0.55 if top else 0.45) * (yt - yb)
        return sum((x >= x_cut if right else x <= x_cut) and (y >= y_cut if top else y <= y_cut) for x, y in pts)
    return min([(True, True), (False, True), (True, False), (False, False)], key=lambda c: count(*c))


def encodings(rows, top):
    """Colour per top matrix; everything else is grey 'Other matrices'."""
    def group(r):
        return r["matrix"] if r["matrix"] in top else "Other matrices"
    order = list(top) + (["Other matrices"] if any(r["matrix"] not in top for r in rows) else [])
    colour = {m: PALETTE[i % len(PALETTE)] for i, m in enumerate(top)}
    colour["Other matrices"] = OTHER_COLOR
    return order, colour, group


# ---------- output ----------
def replace_file(tmp: Path, out: Path):
    """Swap a freshly written file into place; retry briefly if OneDrive or a viewer holds the old one."""
    import time
    for _ in range(10):
        try:
            tmp.replace(out)
            return
        except OSError:
            time.sleep(0.5)
    sys.exit(f"Could not overwrite {out.name} (is it open somewhere?). New version left at {tmp.name}.")


NOTE_TEXT = "'< x' plotted at x. Ranges at the same saturation are nudged apart slightly."


def plot_png(rows, top):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    order, colour, group = encodings(rows, top)
    fig, ax = plt.subplots(figsize=(9, 6), dpi=200)
    layer = {g: i for i, g in enumerate(reversed(order))}  # "Other matrices" lowest, top matrix highest

    # Pass 1: every range line. Pass 2: every point. Points always sit on top of lines,
    # whatever the data, because all lines get a lower z-order than any point.
    for r in rows:
        pts = ends(r)
        if len(pts) == 2:
            g = group(r)
            ax.plot([p[0] for p in pts], [p[1] for p in pts], color=colour[g], linewidth=LINE_W,
                    alpha=0.5 if r["filled"] else 1.0, solid_capstyle="round", zorder=1 + layer[g] * 0.01)
    for r in rows:
        g, c = group(r), colour[group(r)]
        pts = ends(r)
        if r["ordered"]:  # ordered materials: an x in the matrix colour, slightly larger so it reads at a glance
            ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=(POINT_D * 1.6) ** 2, marker="X",
                       facecolors=c, edgecolors="white", linewidths=0.6, zorder=20 + layer[g])
            continue
        ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=POINT_D ** 2, marker="o",
                   facecolors="none" if r["filled"] else c, edgecolors=c, linewidths=1.2 if r["filled"] else 0,
                   zorder=10 + layer[g])

    ax.set_xlabel("Magnetic saturation (T)")
    ax.set_ylabel("Relative permeability $\\mu_r$")
    ax.set_title("Soft magnetic materials: saturation vs permeability")
    ax.grid(True, alpha=0.3)
    ax.set_axisbelow(True)
    (xl, xr), (yb, yt) = axis_limits(rows)
    ax.set_xlim(xl, xr)
    ax.set_ylim(yb, yt)

    handles = [Line2D([], [], marker="o", linestyle="", markersize=POINT_D + 2, markerfacecolor=colour[g],
                      markeredgewidth=0, label=f"{g} ({sum(group(r) == g for r in rows)})") for g in order]
    if any(len(ends(r)) == 2 for r in rows):
        handles.append(Line2D([0, 1], [0, 0], linestyle="-", linewidth=LINE_W, solid_capstyle="round",
                              color="#52514e", label="Range: lower to upper value"))
    if any(r["ordered"] for r in rows):
        handles.append(Line2D([], [], marker="X", linestyle="", markersize=POINT_D * 1.6 + 1, markerfacecolor="#52514e",
                              markeredgecolor="white", label="x = ordered (Status)"))
    if any(r["filled"] for r in rows):
        handles.append(Line2D([], [], marker="o", linestyle="", markersize=POINT_D + 2, markerfacecolor="none",
                              markeredgecolor="#52514e", label="Hollow = one value missing, plotted at 0"))
    # Inside the axes; matplotlib picks the position that covers the fewest data points.
    ax.legend(handles=handles, title="Matrix", loc="best", fontsize=8, title_fontsize=9,
              frameon=True, framealpha=0.85, edgecolor="#dddddd")
    fig.text(0.01, 0.01, f"Top {len(top)} matrices by permeability coloured. {NOTE_TEXT}", fontsize=8, color="#666666")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    out, tmp = OUT_DIR / f"{OUT_NAME}.png", OUT_DIR / f"{OUT_NAME}.tmp.png"
    fig.savefig(tmp, bbox_inches="tight")
    plt.close(fig)
    replace_file(tmp, out)
    return out


def plot_html(rows, top):
    import plotly.graph_objects as go

    order, colour, group = encodings(rows, top)
    hover = ("<b>%{customdata[0]}</b><br>Manufacturer: %{customdata[1]}<br>Matrix: %{customdata[2]}"
             "<br>Filler: %{customdata[3]}<br>Permeability: %{customdata[4]}"
             "<br>Saturation (T): %{customdata[5]}%{customdata[6]}<extra></extra>")
    line_traces, point_traces = [], []
    for g in reversed(order):  # later traces draw on top: "Other matrices" first, top matrix last
        c, members = colour[g], [r for r in rows if group(r) == g]
        xs, ys, data, open_flags, ordered_flags, lx, ly = [], [], [], [], [], [], []
        for r in members:
            pts = ends(r)
            missing = " (one value missing, plotted at 0)" if r["filled"] else ""
            for k, (x, y) in enumerate(pts):
                xs.append(x); ys.append(y); open_flags.append(r["filled"]); ordered_flags.append(r["ordered"])
                end = "" if len(pts) == 1 else (" (range, lower end)" if k == 0 else " (range, upper end)")
                data.append([r["note"], r["manufacturer"], r["matrix_raw"], r["filler"], r["mu_raw"], r["js_raw"],
                             missing + end])
            if len(pts) == 2:
                lx += [pts[0][0], pts[1][0], None]
                ly += [pts[0][1], pts[1][1], None]
        if lx:
            line_traces.append(go.Scatter(x=lx, y=ly, mode="lines", line=dict(color=c, width=LINE_PX),
                                          opacity=1.0, hoverinfo="skip", legendgroup=g, showlegend=False))
        point_traces.append(go.Scatter(
            x=xs, y=ys, mode="markers", name=f"{g} ({len(members)})", legendgroup=g,
            marker=dict(size=[POINT_PX * 1.6 if o else POINT_PX for o in ordered_flags], color=c,
                        symbol=["x" if o else ("circle-open" if f else "circle") for f, o in zip(open_flags, ordered_flags)],
                        line=dict(width=[1.5 if f else 0 for f in open_flags], color=c)),
            customdata=data, hovertemplate=hover,
        ))
    # All lines first, then all points, so points are always drawn on top of lines.
    fig = go.Figure(data=line_traces + point_traces)
    (xl, xr), (yb, yt) = axis_limits(rows)
    right, upper = emptiest_corner(rows)  # Plotly has no "best" legend position, so pick the emptiest corner
    fig.update_layout(
        title="Soft magnetic materials: saturation vs permeability",
        xaxis=dict(title="Magnetic saturation (T)", range=[xl, xr]),
        yaxis=dict(title="Relative permeability µr", range=[yb, yt]),
        template="plotly_white",
        legend=dict(title="Matrix", traceorder="reversed", x=0.99 if right else 0.01, y=0.99 if upper else 0.01,
                    xanchor="right" if right else "left", yanchor="top" if upper else "bottom",
                    bgcolor="rgba(255,255,255,0.85)", bordercolor="#dddddd", borderwidth=1),
        annotations=[dict(text=f"Joined points = range (lower and upper value). Open marker = one value missing, x = ordered, "
                               f"plotted at 0. {NOTE_TEXT}",
                          xref="paper", yref="paper", x=0, y=-0.13, showarrow=False, font=dict(size=11, color="#666"))],
        margin=dict(b=90),
    )
    out, tmp = OUT_DIR / f"{OUT_NAME}.html", OUT_DIR / f"{OUT_NAME}.tmp.html"
    fig.write_html(tmp, include_plotlyjs=True, full_html=True)
    replace_file(tmp, out)
    return out


def main():
    rows, skipped, desc = collect()
    print(f"Base: {BASE_FILE.relative_to(VAULT).as_posix()}  (view: {desc['view']})")
    print(f"  view filters: {desc['view filters']}")
    if desc["base filters"]:
        print(f"  base filters: {desc['base filters']}")
    for w in warnings:
        print(f"  WARNING: {w}")
    if not rows:
        sys.exit("No plottable notes found.")
    top, counts, n_top = pick_top(rows)
    assign_dodge(rows)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    png, html = plot_png(rows, top), plot_html(rows, top)
    print(f"Plotted: {len(rows)}  ({sum(r['filled'] for r in rows)} with one value missing -> 0, "
          f"{sum(len(ends(r)) == 2 for r in rows)} ranges)")
    print(f"Skipped (both values missing): {len(skipped)}  {', '.join(sorted(skipped))}")
    print(f"Matrices found: {', '.join(sorted({r['matrix'] for r in rows}))}")
    print(f"Top {len(top)} matrices (frequency in the top {n_top} by permeability): "
          + ", ".join(f"{m} ({counts.get(m, 0)})" for m in top))
    print(f"Wrote: {png.relative_to(VAULT).as_posix()}\n       {html.relative_to(VAULT).as_posix()}")


if __name__ == "__main__":
    main()
