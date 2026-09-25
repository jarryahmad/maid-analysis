"""
Minimal inline-SVG chart kit.

Charts are generated at build time as inline SVG so the published page has no
runtime dependencies, no CDN, and renders identically everywhere. Colours are
emitted as CSS custom properties (var(--...)), so light/dark theming is handled
by the stylesheet rather than by two sets of SVG.

Palette: the dataviz reference palette. Validated with
  node scripts/validate_palette.js "#2a78d6,#eb6834" --mode light|dark
  node scripts/validate_palette.js "<5-step blue>" --mode light|dark --ordinal
All checks PASS in both modes.
"""
from html import escape

# Ordered prognosis ramp (single hue, light -> dark), 5 steps.
ORDINAL = [f"var(--ord-{i})" for i in range(1, 6)]
S1, S2 = "var(--series-1)", "var(--series-2)"
INK, INK2, MUTED = "var(--ink)", "var(--ink-2)", "var(--muted)"
GRID, AXIS, SURFACE = "var(--grid)", "var(--axis)", "var(--surface)"


def _t(s):
    return escape(str(s), quote=True)


def fmt(v, dp=0, pct=False, thousands=True):
    if v is None:
        return "-"
    s = f"{v:,.{dp}f}" if thousands else f"{v:.{dp}f}"
    return s + ("%" if pct else "")


class Chart:
    """An SVG canvas with a linear y scale and a banded x scale."""

    def __init__(self, width=720, height=360, pad=(16, 16, 42, 52), title=None):
        self.w, self.h = width, height
        self.pt, self.pr, self.pb, self.pl = pad
        self.parts = []
        self.title = title
        self.legend = []

    # -- geometry -------------------------------------------------------
    @property
    def x0(self): return self.pl
    @property
    def x1(self): return self.w - self.pr
    @property
    def y0(self): return self.pt
    @property
    def y1(self): return self.h - self.pb
    @property
    def iw(self): return self.x1 - self.x0
    @property
    def ih(self): return self.y1 - self.y0

    def y(self, v, vmax, vmin=0):
        return self.y1 - (v - vmin) / (vmax - vmin) * self.ih

    def band(self, i, n, pad_frac=0.28):
        step = self.iw / n
        bw = step * (1 - pad_frac)
        return self.x0 + i * step + (step - bw) / 2, bw

    # -- primitives -----------------------------------------------------
    def add(self, s):
        self.parts.append(s)

    def grid_y(self, ticks, vmax, vmin=0, fmt_fn=None, label=None):
        for t in ticks:
            yy = self.y(t, vmax, vmin)
            self.add(f'<line x1="{self.x0}" x2="{self.x1}" y1="{yy:.1f}" y2="{yy:.1f}" '
                     f'stroke="{GRID}" stroke-width="1"/>')
            txt = fmt_fn(t) if fmt_fn else fmt(t)
            self.add(f'<text x="{self.x0 - 8}" y="{yy + 4:.1f}" text-anchor="end" '
                     f'class="tick">{_t(txt)}</text>')
        self.add(f'<line x1="{self.x0}" x2="{self.x1}" y1="{self.y1}" y2="{self.y1}" '
                 f'stroke="{AXIS}" stroke-width="1"/>')
        if label:
            self.add(f'<text x="{self.x0}" y="{self.y0 - 6}" class="axis-label">{_t(label)}</text>')

    def x_labels(self, labels, rotate=0):
        n = len(labels)
        for i, lab in enumerate(labels):
            cx = self.x0 + (i + 0.5) * self.iw / n
            if rotate:
                self.add(f'<text x="{cx:.1f}" y="{self.y1 + 16}" text-anchor="end" '
                         f'transform="rotate({-rotate} {cx:.1f} {self.y1 + 16})" '
                         f'class="tick">{_t(lab)}</text>')
            else:
                self.add(f'<text x="{cx:.1f}" y="{self.y1 + 18}" text-anchor="middle" '
                         f'class="tick">{_t(lab)}</text>')

    def rect(self, x, y, w, h, fill, tip=None, r=4, flat_bottom=True):
        """Bar with 4px rounded data-end, square against the baseline."""
        h = max(h, 0.6)
        r = min(r, w / 2, h)
        if flat_bottom and h > r:
            d = (f"M{x:.2f},{y + h:.2f} V{y + r:.2f} Q{x:.2f},{y:.2f} {x + r:.2f},{y:.2f} "
                 f"H{x + w - r:.2f} Q{x + w:.2f},{y:.2f} {x + w:.2f},{y + r:.2f} "
                 f"V{y + h:.2f} Z")
            el = f'<path d="{d}" fill="{fill}"'
        else:
            el = f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}"'
        if tip:
            el += f' class="mark" data-tip="{_t(tip)}"'
        el += "/>"
        if tip:
            el = el[:-2] + f'><title>{_t(tip)}</title></' + ("path" if flat_bottom and h > r else "rect") + ">"
        self.add(el)

    def seg(self, x, y, w, h, fill, tip=None):
        """Stacked segment: plain rect, 2px surface gap handled by caller."""
        h = max(h, 0.5)
        el = (f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" '
              f'fill="{fill}" class="mark" data-tip="{_t(tip or "")}">')
        el += f"<title>{_t(tip or '')}</title></rect>"
        self.add(el)

    def line(self, pts, stroke, width=2, dash=None):
        d = "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{width}" '
                 f'stroke-linejoin="round" stroke-linecap="round"{da}/>')

    def dot(self, x, y, fill, tip=None, r=4.5):
        el = (f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="{fill}" '
              f'stroke="{SURFACE}" stroke-width="2" class="mark" data-tip="{_t(tip or "")}">')
        el += f"<title>{_t(tip or '')}</title></circle>"
        self.add(el)

    def label(self, x, y, text, cls="datalabel", anchor="middle"):
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
                 f'class="{cls}">{_t(text)}</text>')

    def rule(self, y, text=None, dash=None):
        self.add(f'<line x1="{self.x0}" x2="{self.x1}" y1="{y:.1f}" y2="{y:.1f}" '
                 f'stroke="{INK2}" stroke-width="1"/>')
        if text:
            self.add(f'<text x="{self.x1}" y="{y - 6:.1f}" text-anchor="end" '
                     f'class="rule-label">{_t(text)}</text>')

    def render(self, desc=""):
        legend = ""
        if self.legend:
            items = "".join(
                f'<span class="lg"><i style="background:{c}"></i>{_t(l)}</span>'
                for l, c in self.legend)
            legend = f'<div class="legend">{items}</div>'
        role = f' aria-label="{_t(desc)}"' if desc else ""
        return (f'{legend}<svg viewBox="0 0 {self.w} {self.h}" class="chart" '
                f'role="img"{role} preserveAspectRatio="xMidYMid meet">'
                + "".join(self.parts) + "</svg>")


def table(headers, rows, caption=None):
    """The table view that must exist alongside every chart."""
    th = "".join(f"<th>{_t(h)}</th>" for h in headers)
    tr = "".join("<tr>" + "".join(f"<td>{_t(c)}</td>" for c in r) + "</tr>" for r in rows)
    cap = f"<caption>{_t(caption)}</caption>" if caption else ""
    return (f'<details class="tableview"><summary>Show the numbers</summary>'
            f'<div class="tw"><table>{cap}<thead><tr>{th}</tr></thead>'
            f'<tbody>{tr}</tbody></table></div></details>')
