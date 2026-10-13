# =================================================================== SLIDE 2: motivation
s2 = Ctx(prs.slides[1])
s2.delete(2, 3, 183)              # title, "conceptual illustration", tagline -> caption
s2.delete(67, 79, 91, 103)        # hand-and-document clip art
s2.delete(*range(107, 183))       # old credit strips, rebuilt below

B = [1.97, 2.87, 3.77, 4.67, 5.58, 6.48, 7.38, 8.28, 9.19, 10.09, 10.99, 11.90, 12.80, 13.67]
V = [0.12, 0.22, 0.33, 0.42, 0.50, 0.60, 0.70, 0.24, 0.20, 0.18, 0.16, 0.14, 0.12, 0.0]
F = [0.14, 0.25, 0.36, 0.45, 0.53, 0.63, 0.73, 0.72, 0.71, 0.71, 0.70, 0.70, 0.69, 0.0]
YT, YB = 0.77, 3.17
yv = lambda v: YB - v * (YB - YT)
XL, XR = B[0], B[-1]

# gridlines and axes
for k, i in enumerate(range(4, 18)):
    el = s2.el(i); x, y, w, h = get_box(el); set_box(el, x=B[k])
s2.delete(18)
for i, v in ((19, 1.0), (20, 0.75), (21, 0.5), (22, 0.0)):
    el = s2.el(i); set_box(el, x=XL, y=yv(v), w=XR - XL)
g25 = deepcopy(s2.el(21)); s2.el(21).addnext(g25)
g25.find('p:nvSpPr/p:cNvPr', NS).set('id', str(s2.nid())); set_box(g25, y=yv(0.25))
set_box(s2.el(24), x=XL, w=XR - XL)
set_box(s2.el(23), x=XL)
for i, v in ((25, 1.0), (26, 0.0)):
    el = s2.el(i); x, y, w, h = get_box(el); set_box(el, x=XL - 0.43, y=yv(v) - h / 2)
t05 = deepcopy(s2.el(26)); s2.el(26).addnext(t05)
t05.find('p:nvSpPr/p:cNvPr', NS).set('id', str(s2.nid()))
x, y, w, h = get_box(t05); set_box(t05, y=yv(0.5) - h / 2); set_text(t05, ['0.5'])
x, y, w, h = get_box(s2.el(28)); set_box(s2.el(28), x=1.22 - w / 2)
x, y, w, h = get_box(s2.el(27)); set_box(s2.el(27), x=XL - w / 2)
x, y, w, h = get_box(s2.el(29)); set_box(s2.el(29), x=(XL + XR) / 2 - w / 2)
x, y, w, h = get_box(s2.el(31)); set_box(s2.el(31), x=XR - w / 2)
set_box(s2.el(30), x=XL + 0.08, y=yv(V[0]) - 0.02)
for i, (xx, vv) in ((41, (XL, V[0])), (42, (B[6], V[6])), (43, (XR, 0.0))):
    el = s2.el(i); x, y, w, h = get_box(el); set_box(el, x=xx - w / 2, y=yv(vv) - h / 2)

# legend: move right of the y axis, rename to the paper's terms
for i in (44, 45, 46, 47, 48): move(s2.el(i), dx=XL + 0.10 - 1.08)
set_text(s2.el(46), ['Hindsight prediction f_{k}'])
set_text(s2.el(48), ['Oracle value V(s_{k})'])


# curves: monotone cubic for V (no overshoot at the peak), polyline for f
def monotone(xs, ys):
    n = len(xs); d = [(ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]) for i in range(n - 1)]
    m = [d[0]] + [0.0 if d[i - 1] * d[i] <= 0 else (d[i - 1] + d[i]) / 2 for i in range(1, n - 1)] + [d[-1]]
    for i in range(n - 1):
        if d[i] == 0: m[i] = m[i + 1] = 0; continue
        a, b = m[i] / d[i], m[i + 1] / d[i]
        s = a * a + b * b
        if s > 9:
            t = 3 / s ** 0.5; m[i] = t * a * d[i]; m[i + 1] = t * b * d[i]
    cmds = [('M', xs[0], ys[0])]
    for i in range(n - 1):
        h = xs[i + 1] - xs[i]
        cmds.append(('C', xs[i] + h / 3, ys[i] + m[i] * h / 3, xs[i + 1] - h / 3, ys[i + 1] - m[i + 1] * h / 3, xs[i + 1], ys[i + 1]))
    return cmds


vy = [yv(v) for v in V]; fy = [yv(f) for f in F]
vcmd = monotone(B, vy)
fcmd = [('M', B[0], fy[0])] + [('L', B[k], fy[k]) for k in range(1, len(B))]
pbox = (XL, YT - 0.05, XR, YB + 0.02)
for i in (33, 34, 35, 36, 40): set_path(s2.el(i), vcmd, pbox)
for i in (37, 38, 39): set_path(s2.el(i), fcmd, pbox)


def sample(cmds, n=12):
    out = [(cmds[0][1], cmds[0][2])]
    for c in cmds[1:]:
        x0, y0 = out[-1]
        for t in [j / n for j in range(1, n + 1)]:
            u = 1 - t
            out.append((u ** 3 * x0 + 3 * u * u * t * c[1] + 3 * u * t * t * c[3] + t ** 3 * c[5],
                        u ** 3 * y0 + 3 * u * u * t * c[2] + 3 * u * t * t * c[4] + t ** 3 * c[6]))
        out[-1] = (c[5], c[6])
    return out


vpts = [p for p in sample(vcmd) if p[0] >= B[6] - 1e-6]
shade = [('M', B[6], fy[6])] + [('L', B[k], fy[k]) for k in range(7, len(B))] + [('L', x, y) for x, y in reversed(vpts)] + [('Z',)]
set_path(s2.el(32), shade, pbox)

# annotations follow the new geometry
for i in (49, 50, 51): move(s2.el(i), dx=B[6] - 7.76, dy=yv(V[6]) - 1.57)
set_text(s2.el(52), ['Prefix still matches reference c:', 'high f_{k}, low V(s_{k})'])
x, y, w, h = get_box(s2.el(52)); set_box(s2.el(52), x=(B[7] + B[12]) / 2 - w / 2, y=1.72)

# credit strips: one stem per segment at its centre, height proportional to the change
ROWS = [
    ('Oracle credit', '(ΔV)', [V[k] - V[k - 1] for k in range(1, len(B))], 'E5483F', 'FFDCDC'),
    ('Hindsight credit', '(Δf)', [F[k] - F[k - 1] for k in range(1, len(B))], '6A55E8', 'E7E2FF'),
    ('ForkOPD credit', '(E[Â] = ΔV)', [V[k] - V[k - 1] for k in range(1, len(B))], 'E06A1F', 'FFE6D3'),
]
Y0, RH, GAP = 3.62, 0.52, 0.06
dmax = 0.69; Lmax = 0.22
label_fill = None
for r, (title, sub, d, col, tint) in enumerate(ROWS):
    y0 = Y0 + r * (RH + GAP); yc = y0 + RH / 2
    prst(s2, f'{title} strip', 'roundRect', 0.18, y0, 13.85, RH, fill=fill_xml('FFFFFF'), ln=ln_xml('C9C9C9', 0.75), adj=11000)
    path_shape(s2, f'{title} label fill',
               [('M', 1.83, y0), ('L', 0.24, y0), ('C', 0.21, y0, 0.18, y0 + 0.03, 0.18, y0 + 0.06), ('L', 0.18, y0 + RH - 0.06),
                ('C', 0.18, y0 + RH - 0.03, 0.21, y0 + RH, 0.24, y0 + RH), ('L', 1.83, y0 + RH), ('Z',)],
               fill=fill_xml(tint), closed=True)
    textbox(s2, f'{title} label', 0.18, y0 + 0.02, 1.65, RH - 0.04, ['**' + title + '**', sub], size=13.5)
    for xb in B[1:-1]:
        path_shape(s2, 'segment boundary', [('M', xb, y0 + 0.04), ('L', xb, y0 + RH - 0.04)], ln=ln_xml('DEDEDE', 0.5, dash='dash'))
    path_shape(s2, 'zero line', [('M', XL, yc), ('L', XR, yc)], ln=ln_xml('C4C4C4', 0.9))
    for k, dv in enumerate(d):
        c = (B[k] + B[k + 1]) / 2
        L = abs(dv) / dmax * Lmax
        if L < 0.012:
            prst(s2, 'zero credit', 'ellipse', c - 0.03, yc - 0.03, 0.06, 0.06, fill=fill_xml('C9C9C9'))
            continue
        ye = yc - L if dv > 0 else yc + L
        alpha = 55 if dv > 0 else None
        path_shape(s2, 'credit stem', [('M', c, yc), ('L', c, ye)], ln=ln_xml(col, 2.5, alpha=alpha, cap='flat'))
        prst(s2, 'credit tip', 'ellipse', c - 0.04, ye - 0.04, 0.08, 0.08, fill=fill_xml(col, alpha))
    if title.startswith('ForkOPD'):
        # fork glyph: the verified continuations from s_7 both fail
        fx, fy0 = B[7], y0 + 0.095
        prst(s2, 'fork node', 'ellipse', fx - 0.035, fy0 - 0.035, 0.07, 0.07, fill=fill_xml('2F6DB5'))
        for dy in (-0.045, 0.045):
            path_shape(s2, 'fork branch', [('M', fx, fy0), ('C', fx + 0.10, fy0, fx + 0.10, fy0 + dy, fx + 0.24, fy0 + dy)], ln=ln_xml('2F6DB5', 1.25))
            xc_, yc_ = fx + 0.30, fy0 + dy
            prst(s2, 'fork fail', 'ellipse', xc_ - 0.042, yc_ - 0.042, 0.084, 0.084, fill=fill_xml('E5483F'))
            for a, b2 in (((-0.025, -0.025), (0.025, 0.025)), ((-0.025, 0.025), (0.025, -0.025))):
                path_shape(s2, 'fork fail x', [('M', xc_ + a[0], yc_ + a[1]), ('L', xc_ + b2[0], yc_ + b2[1])], ln=ln_xml('FFFFFF', 1.0))
        textbox(s2, 'fork label', fx + 0.42, y0 + 0.0, 2.4, 0.2, ['fork at s_{7}: both verified continuations fail'],
                size=11.5, color='2F6DB5', align='l', italic=True)

