"""Figure 2 (method) built in place on the user's PPTX draft, slide 1.  Slide 2 keeps the earlier edits.

Print size: the slide is 14.22 in wide and is placed at \\textwidth = 6.30 in, so 1 pt on the slide
prints at 0.443 pt.  Font roles: TITLE 19 pt (8.4 pt printed), MAIN 16 pt (7.1), NOTE 15 pt (6.6),
nothing below 15 pt except sub/superscripts.
"""
import sys
from copy import deepcopy

sys.path.insert(0, '/home/claude/pptfig')
from pptlib import *  # noqa

SRC, DST = sys.argv[1], sys.argv[2]
prs = Presentation(SRC)

TITLE, MAIN, NOTE, EQ = 19, 16, 15, 18
BLUE, BLUE_D, NAVY = '347ED0', '1F5FAF', '255AAA'
FK = '148CE4'          # f_k (prediction)
PURP = '7A55C2'        # verified values / replay
RED = 'C62828'
ORNG, ORNG_D = 'E27B2B', 'B5541C'
INK, INK2 = '000000', '4A4F55'
B = 5.01               # common bottom of the four panels
DX = -0.55             # response band shifted left so that s_5 sits above panel (2)
DY23 = 0.15            # panels (2) and (3) start lower, leaving room for the s_5 arrow

s1 = Ctx(prs.slides[0])
for g in (155, 204, 228, 283):
    ungroup(s1, g)

# ------------------------------------------------------------------ panels: frame, header, title
s1.delete(2)  # slide title -> caption
PAN = {1: (3, 4, 5, 6), 2: (7, 8, 9, 10), 3: (11, 12, 13, 14), 4: (15, 16, 17, 18)}
TITLES = {1: '(1) Hindsight predictor', 2: '(2) Randomized forks', 3: '(3) Rectified credit', 4: '(4) Policy update'}
for k, (cont, head, outl, ttl) in PAN.items():
    x, y, w, h = get_box(s1.el(cont))
    for i in (cont, outl):
        set_box(s1.el(i), h=(B - DY23 if k in (2, 3) else B) - y)
        gd = s1.el(i).find('.//a:prstGeom/a:avLst/a:gd', NS)
        if gd is not None: gd.set('fmla', 'val %d' % int(0.07 / min(w, (B - DY23 if k in (2, 3) else B) - y) * 100000))
    set_text(s1.el(ttl), [TITLES[k]], size=TITLE)
    tw, th = measure([TITLES[k]], TITLE, bold=True)
    set_box(s1.el(ttl), x=x + w / 2 - (tw + 0.1) / 2, y=y + 0.185 - th / 2 + 0.005, w=tw + 0.1, h=th)
    hd = s1.el(head)
    hx, hy, hw, hh = get_box(hd)
    set_box(hd, h=0.37)

# ------------------------------------------------------------------ top band: the original response
set_text(s1.el(19), ['Original response from the old policy //π//_{old} (no reference)'], size=MAIN)
tw, th = measure(['Original response from the old policy //π//_{old} (no reference)'], MAIN)
set_box(s1.el(19), x=7.255 - (tw + 0.1) / 2, y=0.46, w=tw + 0.1, h=th)
set_text(s1.el(20), ['prompt //x//'], size=NOTE)
tw, th = measure(['prompt //x//'], NOTE)
set_box(s1.el(20), x=5.115 - tw / 2 - 0.05, y=0.98, w=tw + 0.1, h=th)
set_box(s1.el(21), y=1.21, h=0.29)
for gid, lab in ((27, 'a_{1}'), (32, 'a_{2}'), (37, 'a_{3}'), (42, 'a_{4}'), (47, 'a_{5}'), (52, 'a_{6}'), (57, 'a_{7}')):
    g = s1.el(gid)
    t = [c for c in g if etree.QName(c).localname == 'sp' and c.find('p:txBody', NS) is not None
         and ''.join(c.itertext()).strip()][0]
    set_text(t, [lab], size=MAIN + 1, align='ctr')
    face = [c for c in g if c.find('.//p:cNvPr', NS) is not None and 'token top' in c.find('.//p:cNvPr', NS).get('name')][0]
    fx, fy, fw, fh = get_box(face)
    set_box(t, x=fx, y=fy + 0.015, w=fw, h=fh - 0.03)   # centred on the top face of the token
    bp = t.find('p:txBody/a:bodyPr', NS); bp.set('anchor', 'ctr')
    for ch in list(bp): bp.remove(ch)
    etree.SubElement(bp, '{%s}noAutofit' % A)
TICKS = {59: 5.115, 61: 5.29 + 0.39, 63: 6.255, 65: 6.83, 67: 7.405, 69: 7.98, 71: 8.56, 73: 9.115}
SX = {59: 5.115, 61: 5.672, 63: 6.244, 65: 6.818, 67: 7.398, 69: 7.976, 71: 8.556, 73: 9.112}
for i, lab in zip((59, 61, 63, 65, 67, 69, 71, 73), ['s_{%d}' % k for k in range(8)]):
    set_text(s1.el(i), [lab], size=NOTE)
    tw, th = measure(['//s//_{0}'], NOTE)
    set_box(s1.el(i), x=SX[i] - 0.17, y=1.70, w=0.34, h=th)
set_text(s1.el(78), ['wrong turn'], size=MAIN, color=RED)
tw, th = measure(['wrong turn'], MAIN, bold=True)
set_box(s1.el(78), x=7.736 - (tw + 0.1) / 2, y=0.80, w=tw + 0.1, h=th)
s1.delete(79, 80)   # old bent arrow; a straight one is drawn after the band is placed
s1.delete(81)  # "terminal reward" -> caption
s1.delete(82)       # R = 0 becomes a badge at the end of the response (drawn below)

# ------------------------------------------------------------------ ribbons (the vivid arrows of the draft)
s1.delete(83, 84, 85, 86)
RB_BLUE, RB_BLUE_L = '255AAA', 'C5E3FC'
RB_OR, RB_OR_L = 'C55B20', 'FFDEB7'
ribbon(s1, 'ribbon: prefixes to predictor', [(4.47, 1.62), (4.17, 1.84), (3.95, 1.36), (3.63, 1.30)],
       0.07, 0.15, 0.30, 0.22, fill_xml(RB_BLUE_L), RB_BLUE)
ribbon(s1, 'ribbon: reward to rectifier', [(9.00, 1.60), (9.10, 1.98), (9.95, 1.86), (10.28, 2.22)],
       0.06, 0.11, 0.24, 0.17, fill_xml(RB_OR_L), RB_OR)
ribbon(s1, 'ribbon: tokens to update', [(8.36, 1.20), (8.75, 0.98), (10.20, 1.08), (10.96, 1.22)],
       0.07, 0.15, 0.30, 0.22, fill_xml(RB_OR_L), RB_OR)
tb(s1, 'label prefixes', ['prefixes //s//_{k}'], NOTE, cx=4.09, y=0.94, color=RB_BLUE)
tb(s1, 'label tokens', ['tokens //a//_{k}'], NOTE, cx=9.95, y=0.74, color=RB_OR)

# ================================================================== panel (1) hindsight predictor
s1.delete(87, 92, *range(99, 128), 128, 129, 130, 131, 132, 133)
XL = 0.74  # left column centre
place(s1, [88, 89, 90, 91], XL - 0.31, 1.40, s=1.1)
tb(s1, 'Reference c', ['Reference //c//'], NOTE, cx=XL, y=1.74)
# prefix: three small response tokens
PX = [XL - 0.42, XL - 0.16, XL + 0.10]
for gid, px in zip((27, 32, 37), PX):
    c = clone(s1, gid)
    for t in [ch for ch in c if etree.QName(ch).localname == 'sp' and ''.join(ch.itertext()).strip()]:
        c.remove(t)
    xf = c.find('p:grpSpPr/a:xfrm', NS)
    xf.find('a:off', NS).set('x', str(e(px))); xf.find('a:off', NS).set('y', str(e(2.17)))
    xf.find('a:ext', NS).set('cx', str(e(0.625 * 0.46))); xf.find('a:ext', NS).set('cy', str(e(0.458 * 0.46)))
tb(s1, 'Prefix s_k', ['Prefix //s//_{k}'], NOTE, cx=XL, y=2.42)

BX0, BX1 = 1.47, 3.28
for box, txt, y0, lines in ((93, 94, 1.36, ['Privileged pass', '//π//_{old}(· | //x//, //c//)']),
                            (95, 96, 1.99, ['Plain pass', '//π//_{old}(· | //x//)'])):
    set_box(s1.el(box), x=BX0, y=y0, w=BX1 - BX0, h=0.52)
    s1.delete(txt)
    tb(s1, lines[0], lines[:1], MAIN, cx=(BX0 + BX1) / 2, y=y0 + 0.03)
    tb(s1, lines[0] + ' policy', lines[1:], NOTE, cx=(BX0 + BX1) / 2, y=y0 + 0.28)
# wiring: c -> privileged; prefix -> both; both -> features
arrow(s1, 'c to privileged', [(1.13, 1.52), (BX0 - 0.01, 1.52)], BLUE_D)
arrow(s1, 'prefix to plain', [(1.18, 2.25), (BX0 - 0.01, 2.25)], BLUE_D)
arrow(s1, 'prefix to privileged', [(1.30, 2.25), (1.30, 1.74), (BX0 - 0.01, 1.74)], BLUE_D)
dot(s1, 1.30, 2.25, BLUE_D)
arrow(s1, 'passes to features', [(BX1, 1.62), (3.44, 1.62), (3.44, 2.95), (BX1 + 0.01, 2.95)], BLUE_D)
arrow(s1, 'plain to bus', [(BX1, 2.25), (3.44, 2.25)], BLUE_D, head=False)
dot(s1, 3.44, 2.25, BLUE_D)

set_box(s1.el(97), x=0.30, y=2.68, w=BX1 - 0.30, h=0.54)
s1.delete(98)
tb(s1, 'features', ['Prefix features //z//_{k}: evidence //L//_{k},'], NOTE, cx=(0.30 + BX1) / 2, y=2.70)
tb(s1, 'features 2', ['entropies, log length'], NOTE, cx=(0.30 + BX1) / 2, y=2.93)
# logistic calibrator
CX, CY, R = 1.79, 3.53, 0.19
arrow(s1, 'features to calibrator', [(CX, 3.22), (CX, CY - R - 0.005)], BLUE_D)
prst(s1, 'logistic calibrator icon frame', 'roundRect', CX - R, CY - R, 2 * R, 2 * R,
     fill=fill_xml('FFFFFF'), ln=ln_xml('2F5F9E', 1.0), adj=18000)
path_shape(s1, 'logistic calibrator axis', [('M', CX - R + 0.06, CY + R - 0.07), ('L', CX + R - 0.05, CY + R - 0.07)], ln=ln_xml('A9BCD6', 0.75))
path_shape(s1, 'logistic calibrator sigmoid',
           [('M', CX - R + 0.06, CY + R - 0.09), ('C', CX - 0.02, CY + R - 0.09, CX + 0.02, CY - R + 0.08, CX + R - 0.06, CY - R + 0.08)],
           ln=ln_xml('2F5F9E', 1.75))
tb(s1, 'calibrator', ['Logistic', 'calibrator'], NOTE, rx=CX - R - 0.09, cy=CY)
tb(s1, 'g_phi', ['//g//_{ϕ}'], MAIN + 2, x=CX + R + 0.08, cy=CY - 0.02)
arrow(s1, 'calibrator to f', [(CX, CY + R), (CX, 3.95)], BLUE_D)
tb(s1, 'f_k label', ['//f//_{k}'], MAIN + 1, x=CX + 0.07, cy=3.83, color=FK)
# bar chart of f_1..f_6
AX = 4.43
for i in (134,): set_box(s1.el(i), y=AX)
for i in (153, 154):
    x, y, w, h = get_box(s1.el(i)); set_box(s1.el(i), y=AX - h / 2)
for bar, tick, lab in zip((135, 138, 141, 144, 147, 150), (136, 139, 142, 145, 148, 151), (137, 140, 143, 146, 149, 152)):
    x, y, w, h = get_box(s1.el(bar)); h2 = h * 1.25
    set_box(s1.el(bar), y=AX - h2, h=h2)
    set_box(s1.el(tick), y=AX)
    set_text(s1.el(lab), ['//s//_{%d}' % ((lab - 137) // 3 + 1)], size=NOTE)
    lx = x + w / 2
    set_box(s1.el(lab), x=lx - 0.17, y=AX + 0.08, w=0.34, h=0.25)

# ================================================================== panel (2) randomized forks
s1.delete(156, 159, 160, 161, 201, 202, 203)
P2X0, P2X1 = 3.79, 7.47
set_box(s1.el(157), x=3.86, y=2.50, w=1.42, h=0.42)
s1.delete(158)
tb(s1, 'Z_k ~ Bern', ['//Z//_{k} ∼ Bern(//p//_{k})'], MAIN + 1, cx=3.86 + 0.71, cy=2.71)
tb(s1, 'p_k rule', ['//p//_{k} ∝ predicted residual'], NOTE, x=5.42, y=2.47)
tb(s1, 'Z_k = 0', ['//Z//_{k} = 0: keep anchor //m//_{k}'], NOTE, x=5.42, y=2.71)
# fork picture, moved left and enlarged
pic = [165, 166, 167, 168, 169, 170, 174, 178, 182, 183, 184, 188, 192, 196, 197, 198, 199, 200]
x0, y0, x1, y1 = bbox(s1, [165, 174, 178, 182, 188, 192, 196, 183, 197])
place(s1, [i for i in pic if i not in (166, 183, 184, 197, 198)], 3.98, 3.08, s=1.0)
for i, yy in ((183, 2.98), (197, 3.52)):
    set_text(s1.el(i), ['×'], size=20)
for i, yy in ((184, 3.0), (198, 3.53)):
    set_text(s1.el(i), ['//R// = 0'], size=NOTE)
tok = [get_box(s1.el(i)) for i in (182, 196)]
for (bx, by, bw, bh), xi, ri in zip(tok, (183, 197), (184, 198)):
    set_box(s1.el(xi), x=bx + bw + 0.05, y=by + bh / 2 - 0.20, w=0.24, h=0.34)
    set_box(s1.el(ri), x=bx + bw + 0.27, y=by + bh / 2 - 0.13, w=0.55, h=0.25)
sx, sy, sw, sh = get_box(s1.el(165))
set_text(s1.el(166), ['//s//_{5}'], size=NOTE)
set_box(s1.el(166), x=sx + sw / 2 - 0.17, y=sy + sh + 0.02, w=0.34, h=0.25)
tb(s1, 'M = 2', ['//M// = 2'], NOTE, cx=sx + sw / 2, y=sy + sh + 0.27)
# result: both continuations fail -> Y_hat_5 = 0
RX = 6.50
path_shape(s1, 'fork result brace', [('M', 6.25, 3.12), ('C', 6.35, 3.12, 6.31, 3.40, 6.40, 3.40), ('C', 6.31, 3.40, 6.35, 3.68, 6.25, 3.68)],
           ln=ln_xml('7F7F7F', 1.0))
tb(s1, 'both fail', ['both fail'], NOTE, x=RX, cy=3.13)
tb(s1, 'Y5', ['//Ŷ//_{5} = 0'], MAIN + 1, x=RX, cy=3.39, color=PURP)
tb(s1, 'continuations note', ['Forks sample from //π//_{old} without //c//;'], NOTE, cx=(P2X0 + P2X1) / 2, y=4.17)
tb(s1, 'no gradients', ['no gradients flow through them.'], NOTE, cx=(P2X0 + P2X1) / 2, y=4.42, color=RED)

# ================================================================== panel (3) rectified credit
s1.delete(205, 206, 207, 210, 211, 213, 214, 221, 224, 208)
P3X0, P3X1 = 7.75, 10.77
P3C = (7.65 + 10.87) / 2
tb(s1, 'anchor', ['anchor  //m//_{k} = //b// + //λ//(//f//_{k} − //b//)'], MAIN, cx=P3C, y=2.48)
EB = (8.34, 2.86, 10.70, 3.56)  # equation box
set_box(s1.el(215), x=EB[0], y=EB[1], w=EB[2] - EB[0], h=EB[3] - EB[1])
set_text(s1.el(209), ['//f//_{k}'], size=EQ, color=FK)
set_text(s1.el(212), ['//Ŷ//_{k}'], size=EQ, color=PURP)
set_box(s1.el(209), x=7.80, y=2.86, w=0.32, h=0.30)
set_box(s1.el(212), x=7.80, y=3.24, w=0.34, h=0.30)
arrow(s1, 'f to equation', [(8.13, 3.02), (EB[0] - 0.01, 3.02)], FK, w=1.5)
arrow(s1, 'Y to equation', [(8.15, 3.40), (EB[0] - 0.01, 3.40)], PURP, w=1.5)
# equation  V~_k = m_k + Z_k/p_k (Y^_k - m_k)
ecy = (EB[1] + EB[3]) / 2
lhs = ['//Ṽ//_{k} = //m//_{k} +']
rhs = ['(//Ŷ//_{k} − //m//_{k})']
wl, hl = measure(lhs, EQ); wr, hr = measure(rhs, EQ); wf = measure(['//Z//_{k}'], EQ - 2)[0]
tot = wl + 0.06 + wf + 0.06 + wr
ex = (EB[0] + EB[2]) / 2 - tot / 2
set_text(s1.el(216), lhs, size=EQ); set_box(s1.el(216), x=ex, y=ecy - hl / 2, w=wl + 0.04, h=hl)
fx = ex + wl + 0.06
set_text(s1.el(217), ['//Z//_{k}'], size=EQ - 2); set_box(s1.el(217), x=fx - 0.02, y=ecy - 0.29, w=wf + 0.06, h=0.27)
set_text(s1.el(219), ['//p//_{k}'], size=EQ - 2); set_box(s1.el(219), x=fx - 0.02, y=ecy + 0.02, w=wf + 0.06, h=0.27)
set_box(s1.el(218), x=fx - 0.01, y=ecy, w=wf + 0.04)
set_text(s1.el(220), rhs, size=EQ); set_box(s1.el(220), x=fx + wf + 0.08, y=ecy - hr / 2, w=wr + 0.04, h=hr)
s1.delete(222, 223, 225)
tb(s1, 'boundary values', ['//Ṽ//_{0} = //b//,   //Ṽ//_{K} = //R//'], MAIN, cx=P3C, y=3.64)
tb(s1, 'segment credit', ['//Â//_{k} = //Ṽ//_{k} − //Ṽ//_{k−1},   Σ_{k} //Â//_{k} = //R// − //b//'], MAIN, cx=P3C, y=3.92)
set_box(s1.el(226), x=7.80, y=4.24, w=3.02, h=0.52)
s1.delete(227)
tb(s1, 'unbiased 1', ['Unbiased for any predictor //f//_{k}:'], NOTE, cx=P3C, y=4.27)
tb(s1, 'unbiased 2', ['E[//Ṽ//_{k}] = //V//(//s//_{k}),  //k// = 1, …, //K// − 1'], NOTE, cx=P3C, y=4.50)

# ================================================================== panel (4) policy update
s1.delete(229, 245)
P4X0, P4X1 = 10.97, 14.16
P4C = (P4X0 + P4X1) / 2
TW = 0.40
TX = [P4C - 3.5 * TW + i * TW for i in range(7)]
set_text(s1.el(230), ['Original tokens'], size=NOTE)
tw, th = measure(['Original tokens'], NOTE)
set_box(s1.el(230), x=P4C - tw / 2 - 0.05, y=1.36, w=tw + 0.1, h=th)
for i, (bx, tx) in enumerate(zip(range(231, 245, 2), range(232, 246, 2))):
    set_box(s1.el(bx), x=TX[i], y=1.64, w=TW, h=0.32)
    set_text(s1.el(tx), ['a_{%d}' % (i + 1)], size=MAIN)
    set_box(s1.el(tx), x=TX[i], y=1.67, w=TW, h=0.27)
x5 = TX[4] + TW / 2
place(s1, [246, 247], x5 - 0.055, 1.98)
x, y, w, h = get_box(s1.el(246)); set_box(s1.el(246), h=0.46)
x, y, w, h = get_box(s1.el(247)); set_box(s1.el(247), y=1.98 + 0.46 - h + 0.02)
tb(s1, 'token credit 1', ['tokens of segment //k//'], NOTE, rx=x5 - 0.12, y=2.00)
tb(s1, 'token credit 2', ['share credit //Â//_{k}'], NOTE, rx=x5 - 0.12, y=2.23)
for i, (bx, br, bl) in enumerate(zip(range(248, 267, 3), range(249, 268, 3), range(250, 269, 3))):
    set_box(s1.el(bx), x=TX[i], y=2.52, w=TW, h=0.18)
    set_box(s1.el(br), x=TX[i] + 0.02, y=2.73, w=TW - 0.04, h=0.08)
    set_text(s1.el(bl), ['//Â//_{%d}' % (i + 1)], size=MAIN)
    set_box(s1.el(bl), x=TX[i] - 0.02, y=2.82, w=TW + 0.04, h=0.28)
place(s1, [269], P4C - 0.07, 3.14)
x, y, w, h = get_box(s1.el(269)); set_box(s1.el(269), w=0.14, h=0.30)
DB = (TX[0], 3.50, TX[-1] + TW, 4.14)
set_box(s1.el(270), x=DB[0], y=DB[1], w=DB[2] - DB[0], h=DB[3] - DB[1])
s1.delete(271)
tb(s1, 'DAPO 1', ['DAPO clipped'], MAIN, cx=DB[0] + 0.95, y=DB[1] + 0.07)
tb(s1, 'DAPO 2', ['surrogate'], MAIN, cx=DB[0] + 0.95, y=DB[1] + 0.33)
PLOT = [272, 273, 274, 275, 276, 278, 279]          # clip plot without its label, fitted inside the DAPO box
px0, py0, px1, py1 = bbox(s1, PLOT)
lx0, ly0, lx1, ly1 = bbox(s1, [277])
ps = (DB[3] - DB[1] - 0.31) / (py1 - py0)              # leave room for the 'clip' label above the curve
pw = (px1 - px0) * ps
place(s1, PLOT, DB[2] - 0.14 - pw, DB[3] - 0.07 - (py1 - py0) * ps, s=ps)
set_text(s1.el(277), ['clip'], size=NOTE)
set_box(s1.el(277), x=DB[2] - 0.14 - pw / 2 - 0.25, y=DB[1] + 0.03, w=0.5, h=0.22)
set_text(s1.el(277), ['clip'], size=NOTE, align='ctr')
place(s1, [280], P4C - 0.065, DB[3] + 0.02)
x, y, w, h = get_box(s1.el(280)); set_box(s1.el(280), w=0.14, h=0.20)
UB = (P4C - 1.0, DB[3] + 0.24, P4C + 1.0, DB[3] + 0.66)
set_box(s1.el(281), x=UB[0], y=UB[1], w=UB[2] - UB[0], h=UB[3] - UB[1])
s1.delete(282)
tb(s1, 'updated policy', ['**Updated policy //π//_{θ}**'], MAIN + 1, cx=P4C, cy=(UB[1] + UB[3]) / 2)
# credit from (3) into the update
s1.delete(284, 285)  # two-piece arrow -> one ribbon, drawn below
s1.delete(286)

# ================================================================== cross-fitting loop
s1.delete(*range(287, 295))
LY = B + 0.24
path_shape(s1, 'cross-fit loop', [('M', P4C, B), ('L', P4C, LY), ('L', 1.835, LY), ('L', 1.835, B + 0.01)],
           ln=ln_xml('8561C7', 1.25, dash='dash', tail=True))
msg = ['Other fold + replay: fit //g//_{ϕ}, //h//_{ψ}, //λ// and estimate //η//']
w, h = measure(msg, NOTE)
prst(s1, 'cross-fit box', 'roundRect', 7.26 - w / 2 - 0.14, LY - 0.17, w + 0.28, 0.34,
     fill=fill_xml('FBF8FF'), ln=ln_xml('896AC2', 1.0, dash='dash'), adj=30000)
tb(s1, 'cross-fit text', msg, NOTE, cx=7.26, cy=LY)

# Y_hat from (2) to (3), drawn last so it sits on top
arrow(s1, 'verified mean to rectifier', [(7.16, 3.39), (7.79, 3.39)], PURP, w=1.5)

# ------------------------------------------------------------------ final placement
TRAJ = [19, 20, 21, 22, 27, 32, 37, 42, 47, 52, 57, 77, 58, 60, 62, 64, 66, 68, 70, 72,
        59, 61, 63, 65, 67, 69, 71, 73, 78]
for i in TRAJ: move(s1.el(i), dx=DX)
x, y, w, h = get_box(s1.el(20)); set_box(s1.el(20), x=4.62)      # "prompt x", clear of the ribbon label
for el in list(s1.tree):
    if etree.QName(el).localname not in ('sp', 'grpSp', 'cxnSp', 'pic'): continue
    x, y, w, h = get_box(el)
    if x >= 3.64 and x + w <= 10.92 and y >= 1.99 and y + h <= B - DY23 + 0.02:
        move(el, dy=DY23)
# s_5 is forked: a down arrow in the style of panel (4) drops it into panel (2)

# boundary ticks and labels at the exact joints of the tokens
toks = [get_box(s1.el(g)) for g in (27, 32, 37, 42, 47, 52, 57)]
for g in (27, 32, 37, 42, 47, 52, 57):          # drop the per-token centre ticks
    for c in list(s1.el(g)):
        nm = c.find('.//p:cNvPr', NS)
        if nm is not None and nm.get('name').endswith(' path'): s1.el(g).remove(c)
s1.delete(77, 58)                                 # unexplained end token, stray tick
JX = [toks[0][0]] + [(toks[k][0] + toks[k][2] + toks[k + 1][0]) / 2 for k in range(6)] + [toks[6][0] + toks[6][2]]
for k, (tick, lab) in enumerate(zip((None, 60, 62, 64, 66, 68, 70, 72), (59, 61, 63, 65, 67, 69, 71, 73))):
    if tick is not None:
        el = s1.el(tick); x, y, w, h = get_box(el); set_box(el, x=JX[k], y=1.50, h=0.16)
    x, y, w, h = get_box(s1.el(lab)); set_box(s1.el(lab), x=JX[k] - w / 2)
x, y, w, h = get_box(s1.el(21)); set_box(s1.el(21), x=JX[0])
x, y, w, h = get_box(s1.el(22)); set_box(s1.el(22), x=JX[0] - w / 2)
# verifier outcome as a badge after s_7
bx0 = JX[7] + 0.08
prst(s1, 'reward badge', 'roundRect', bx0, 1.31, 0.56, 0.27, fill=fill_xml('FDECEA'), ln=ln_xml('E06C5F', 1.0), adj=30000)
tb(s1, 'reward', ['//R// = 0'], MAIN, cx=bx0 + 0.28, cy=1.445, color='D4544A', bold=True)
# 'wrong turn' points straight down at the top vertex of a_5
a5 = toks[4]; x5 = a5[0] + a5[2] / 2
x, y, w, h = get_box(s1.el(78)); set_box(s1.el(78), x=x5 - w / 2)
arrow(s1, 'wrong turn pointer', [(x5, y + h + 0.01), (x5, a5[1] - 0.025)], 'D4544A', w=1.25)
# s_5 is forked: a down arrow in the style of panel (4) drops it into panel (2)
dn = clone(s1, 269)
set_box(dn, x=JX[5] - 0.07, y=1.95, w=0.14, h=0.21)
# segment credit from (3) into the update, one ribbon
ribbon(s1, 'ribbon: credit to update', [(10.74, 3.82), (10.86, 3.82), (11.02, 3.82), (11.16, 3.82)],
       0.13, 0.13, 0.28, 0.16, fill_xml(RB_OR_L), RB_OR)

# ------------------------------------------------------------------ palette shared with Figure 1 (light fills, hairline frames)
REMAP = {'347ED0': '8FB6E8', 'C1DDF6': 'E3EEFC', 'C8E5F3': 'E9F2FD', 'F1FAFF': 'F8FBFF', 'ECF8FF': 'F4F8FE',
         'EE812F': 'EBB083', 'FFDEBA': 'FDEBDC', 'FFD7A7': 'FCE5D2', 'FFF6E5': 'FFFAF5', 'FFF9EE': 'FFFBF8',
         'DEEDFA': 'EDF4FD', 'F3F7F8': 'FAFCFF', 'D5EBFF': 'EDF4FD', 'F2F9FF': 'FAFCFF',
         'C7E6E8': 'EDF4FD', 'E2F4F2': 'F7FAFF', '08B5C4': '8FB6E8',
         'FDE9DC': 'FEF3EA', 'AF471F': 'E39A6A', 'FDEBDA': 'FEF3EA', 'B84921': 'E39A6A', '222222': '9AA4B5',
         '8561C7': '7B68D6', '896AC2': '7B68D6', 'FBF8FF': 'F7F5FE', '7A55C2': '7B68D6',
         '148CE4': '3D7FD9', '1F5FAF': '3D7FD9', 'C62828': 'D4544A', 'D00000': 'E06C5F', 'EA0000': 'E06C5F',
         '255AAA': '6F9BD8', 'C5E3FC': 'DCEAFB', 'C55B20': 'E39A6A', 'FFDEB7': 'FDE6D2',
         '869BCF': 'BCD6F5', '485C97': '6F9BD8', '000000': '263040',
         '77ABE6': 'A9C8EE', '97BFEA': 'D3E3F7', '3A5C88': '6F9BD8', '8AB9E8': 'BCD6F5', 'BCD6F1': 'DCEAFB',
         '283A46': '7A8597', 'B7A1D1': 'BCD6F5', '755198': '6F9BD8'}
for c in s1.tree.iter('{%s}srgbClr' % A):
    v = c.get('val').upper()
    if v in REMAP: c.set('val', REMAP[v])
for i in (3, 5, 7, 9, 11, 13, 15, 17):           # frames: lighter colour, slightly wider line
    ln = s1.el(i).find('p:spPr/a:ln', NS)
    if ln is not None: ln.set('w', str(int(1.5 * 12700)))

exec(open('/home/claude/pptfig/slide2_part.py').read())

# =================================================================== layout
y0a, y1a = extent(s2); shift_all(s2, 0.10 - y0a)
y0b, y1b = extent(s1)
H = (y1b - y0b) + 0.10
shift_all(s1, 0.05 - y0b)
y0a, y1a = extent(s2); shift_all(s2, (H - (y1a - y0a)) / 2 - y0a)
prs.slide_height = e(H)
prs.save(DST)
print('saved', DST, 'slide height', round(H, 3))
