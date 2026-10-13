"""Edit the user's PPTX figure draft in place (slide 1 = method figure, slide 2 = motivation figure)."""
import re
import sys
from copy import deepcopy

from lxml import etree
from pptx import Presentation

A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
NS = {'a': A, 'p': P}
EMU = 914400
e = lambda inch: int(round(inch * EMU))



# ------------------------------------------------------------------ helpers
class Ctx:
    def __init__(self, slide):
        self.slide = slide
        self.tree = slide.shapes._spTree
        ids = [int(x) for x in etree.XPath('.//p:cNvPr/@id', namespaces=NS)(self.tree)]
        self.next_id = max(ids) + 1

    def el(self, i):
        c = etree.XPath('.//p:cNvPr[@id="%d"]' % i, namespaces=NS)(self.tree)
        assert c, i
        return c[0].getparent().getparent()

    def delete(self, *ids):
        for i in ids:
            el = self.el(i)
            el.getparent().remove(el)

    def nid(self):
        self.next_id += 1
        return self.next_id

    def add(self, xml):
        el = etree.fromstring(xml)
        self.tree.append(el)
        return el


def xfrm_of(el):
    tag = etree.QName(el).localname
    if tag == 'grpSp':
        return el.find('p:grpSpPr/a:xfrm', NS)
    return el.find('p:spPr/a:xfrm', NS)


def set_box(el, x=None, y=None, w=None, h=None):
    xf = xfrm_of(el)
    off, ext = xf.find('a:off', NS), xf.find('a:ext', NS)
    if x is not None: off.set('x', str(e(x)))
    if y is not None: off.set('y', str(e(y)))
    if w is not None: ext.set('cx', str(e(w)))
    if h is not None: ext.set('cy', str(e(h)))


def get_box(el):
    xf = xfrm_of(el)
    off, ext = xf.find('a:off', NS), xf.find('a:ext', NS)
    return (int(off.get('x')) / EMU, int(off.get('y')) / EMU, int(ext.get('cx')) / EMU, int(ext.get('cy')) / EMU)


def move(el, dx=0.0, dy=0.0):
    x, y, w, h = get_box(el)
    set_box(el, x + dx, y + dy)


TOK = re.compile(r'(_\{[^}]*\}|\^\{[^}]*\})')


def set_text(el, paras, size=None, bold=None, italic=None, color=None, align=None):
    """paras: list of strings; _{..} subscript, ^{..} superscript; '**' toggles bold, '//' toggles italic."""
    txBody = el.find('p:txBody', NS)
    ps = txBody.findall('a:p', NS)
    base_p = ps[0]
    base_r = base_p.find('a:r', NS)
    base_rPr = deepcopy(base_r.find('a:rPr', NS))
    for k in ('baseline',):
        if k in base_rPr.attrib: del base_rPr.attrib[k]
    if size: base_rPr.set('sz', str(int(round(size * 100))))
    if color:
        for f in base_rPr.findall('a:solidFill', NS): base_rPr.remove(f)
        sf = etree.Element('{%s}solidFill' % A); etree.SubElement(sf, '{%s}srgbClr' % A, val=color)
        base_rPr.insert(0, sf)
    math = any('//' in p for p in paras)
    if italic is None and math: italic = False
    it0 = (base_rPr.get('i') == '1') if italic is None else italic
    pPr = deepcopy(base_p.find('a:pPr', NS))
    if pPr is not None and align: pPr.set('algn', align)
    for p in ps: txBody.remove(p)
    sz = int(base_rPr.get('sz', '1200'))
    for line in paras:
        p = etree.SubElement(txBody, '{%s}p' % A)
        if pPr is not None: p.append(deepcopy(pPr))
        b_on = bool(bold) if bold is not None else (base_rPr.get('b') == '1')
        i_on = it0
        for chunk in re.split(r'(\*\*|//)', line):
            if chunk == '**':
                b_on = not b_on; continue
            if chunk == '//':
                i_on = not i_on; continue
            for part in TOK.split(chunk):
                if not part: continue
                r = etree.SubElement(p, '{%s}r' % A)
                rPr = deepcopy(base_rPr)
                rPr.set('b', '1' if b_on else '0')
                rPr.set('i', '1' if i_on else '0')
                if part.startswith('_{') or part.startswith('^{'):
                    rPr.set('baseline', '-20000' if part[0] == '_' else '30000')
                    rPr.set('sz', str(int(round(sz * 0.78))))
                    part = part[2:-1]
                    if math and part not in ('old', 'min') and not part.isdigit():
                        rPr.set('i', '1')
                r.append(rPr)
                t = etree.SubElement(r, '{%s}t' % A)
                t.text = part
                if part != part.strip(): t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')


def ln_xml(color, w_pt, dash=None, tail=False, head=False, alpha=None, cap='rnd'):
    a = f'<a:alpha val="{int(alpha*1000)}"/>' if alpha is not None else ''
    d = f'<a:prstDash val="{dash}"/>' if dash else ''
    h = '<a:headEnd type="triangle" w="med" len="med"/>' if head else ''
    t = '<a:tailEnd type="triangle" w="med" len="med"/>' if tail else ''
    return f'<a:ln w="{int(w_pt*12700)}" cap="{cap}"><a:solidFill><a:srgbClr val="{color}">{a}</a:srgbClr></a:solidFill>{d}<a:round/>{h}{t}</a:ln>'


def fill_xml(color, alpha=None):
    if color is None: return '<a:noFill/>'
    a = f'<a:alpha val="{int(alpha*1000)}"/>' if alpha is not None else ''
    return f'<a:solidFill><a:srgbClr val="{color}">{a}</a:srgbClr></a:solidFill>'


def path_shape(ctx, name, cmds, ln='', fill='<a:noFill/>', closed=False, box=None):
    """cmds in inches: ('M',x,y) ('L',x,y) ('C',x1,y1,x2,y2,x,y) ('Z',)."""
    pts = [(c[i], c[i + 1]) for c in cmds if c[0] != 'Z' for i in range(1, len(c), 2)]
    if box is None:
        x0 = min(p[0] for p in pts); y0 = min(p[1] for p in pts)
        x1 = max(p[0] for p in pts); y1 = max(p[1] for p in pts)
    else:
        x0, y0, x1, y1 = box
    W = max(e(x1 - x0), 1); H = max(e(y1 - y0), 1)
    q = lambda x, y: f'<a:pt x="{e(x - x0)}" y="{e(y - y0)}"/>'
    body = ''
    for c in cmds:
        if c[0] == 'M': body += f'<a:moveTo>{q(c[1], c[2])}</a:moveTo>'
        elif c[0] == 'L': body += f'<a:lnTo>{q(c[1], c[2])}</a:lnTo>'
        elif c[0] == 'C': body += f'<a:cubicBezTo>{q(c[1], c[2])}{q(c[3], c[4])}{q(c[5], c[6])}</a:cubicBezTo>'
        elif c[0] == 'Z': body += '<a:close/>'
    fl = 'norm' if closed else 'none'
    xml = (f'<p:sp xmlns:p="{P}" xmlns:a="{A}"><p:nvSpPr><p:cNvPr id="{ctx.nid()}" name="{name}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
           f'<p:spPr><a:xfrm><a:off x="{e(x0)}" y="{e(y0)}"/><a:ext cx="{W}" cy="{H}"/></a:xfrm>'
           f'<a:custGeom><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/><a:rect l="l" t="t" r="r" b="b"/>'
           f'<a:pathLst><a:path w="{W}" h="{H}" fill="{fl}">{body}</a:path></a:pathLst></a:custGeom>'
           f'{fill}{ln if ln else "<a:ln><a:noFill/></a:ln>"}</p:spPr></p:sp>')
    return ctx.add(xml)


def set_path(el, cmds, box, closed=None):
    """Rewrite an existing custGeom shape's geometry, keeping its style."""
    x0, y0, x1, y1 = box
    W = max(e(x1 - x0), 1); H = max(e(y1 - y0), 1)
    set_box(el, x0, y0, x1 - x0, y1 - y0)
    path = el.find('p:spPr/a:custGeom/a:pathLst/a:path', NS)
    for ch in list(path): path.remove(ch)
    path.set('w', str(W)); path.set('h', str(H))
    def pt(parent, x, y):
        etree.SubElement(parent, '{%s}pt' % A, x=str(e(x - x0)), y=str(e(y - y0)))
    for c in cmds:
        if c[0] == 'M': pt(etree.SubElement(path, '{%s}moveTo' % A), c[1], c[2])
        elif c[0] == 'L': pt(etree.SubElement(path, '{%s}lnTo' % A), c[1], c[2])
        elif c[0] == 'C':
            cb = etree.SubElement(path, '{%s}cubicBezTo' % A)
            pt(cb, c[1], c[2]); pt(cb, c[3], c[4]); pt(cb, c[5], c[6])
        elif c[0] == 'Z': etree.SubElement(path, '{%s}close' % A)


def prst(ctx, name, geom, x, y, w, h, fill='<a:noFill/>', ln='<a:ln><a:noFill/></a:ln>', adj=None):
    av = f'<a:gd name="adj" fmla="val {adj}"/>' if adj is not None else ''
    xml = (f'<p:sp xmlns:p="{P}" xmlns:a="{A}"><p:nvSpPr><p:cNvPr id="{ctx.nid()}" name="{name}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
           f'<p:spPr><a:xfrm><a:off x="{e(x)}" y="{e(y)}"/><a:ext cx="{e(w)}" cy="{e(h)}"/></a:xfrm>'
           f'<a:prstGeom prst="{geom}"><a:avLst>{av}</a:avLst></a:prstGeom>{fill}{ln}</p:spPr></p:sp>')
    return ctx.add(xml)


def textbox(ctx, name, x, y, w, h, paras, size=12, color='000000', align='ctr', anchor='ctr', bold=False, italic=False):
    xml = (f'<p:sp xmlns:p="{P}" xmlns:a="{A}"><p:nvSpPr><p:cNvPr id="{ctx.nid()}" name="{name}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
           f'<p:spPr><a:xfrm><a:off x="{e(x)}" y="{e(y)}"/><a:ext cx="{e(w)}" cy="{e(h)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>'
           f'<p:txBody><a:bodyPr wrap="none" lIns="0" rIns="0" tIns="0" bIns="0" anchor="{anchor}"><a:noAutofit/></a:bodyPr><a:lstStyle/>'
           f'<a:p><a:pPr algn="{align}"><a:lnSpc><a:spcPct val="100000"/></a:lnSpc><a:spcBef><a:spcPts val="0"/></a:spcBef><a:spcAft><a:spcPts val="0"/></a:spcAft></a:pPr>'
           f'<a:r><a:rPr lang="en-US" sz="{int(size*100)}" b="{1 if bold else 0}" i="{1 if italic else 0}"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
           f'<a:latin typeface="Times New Roman"/><a:cs typeface="Times New Roman"/></a:rPr><a:t>x</a:t></a:r></a:p></p:txBody></p:sp>')
    el = ctx.add(xml)
    set_text(el, paras, bold=bold, italic=italic)
    return el


def shift_all(ctx, dy):
    for el in ctx.tree:
        tag = etree.QName(el).localname
        if tag in ('sp', 'grpSp', 'cxnSp', 'pic', 'graphicFrame'):
            if tag == 'graphicFrame':
                off = el.find('p:xfrm/a:off', NS)
            else:
                xf = xfrm_of(el); off = xf.find('a:off', NS) if xf is not None else None
            if off is not None: off.set('y', str(int(off.get('y')) + e(dy)))


def extent(ctx):
    y0, y1 = 1e9, -1e9
    for sh in ctx.slide.shapes:
        y0 = min(y0, sh.top / EMU); y1 = max(y1, (sh.top + sh.height) / EMU)
    return y0, y1



# ------------------------------------------------------------------ text metrics (Liberation Serif = Times New Roman metrics)
from PIL import ImageFont
_FD = '/usr/share/fonts/truetype/liberation/LiberationSerif-%s.ttf'
_fonts = {}
def _font(b, i):
    k = (b, i)
    if k not in _fonts:
        nm = {(0, 0): 'Regular', (1, 0): 'Bold', (0, 1): 'Italic', (1, 1): 'BoldItalic'}[k]
        _fonts[k] = ImageFont.truetype(_FD % nm, 1000)
    return _fonts[k]


def measure(paras, size, bold=False, italic=False, lead=1.17):
    """width/height in inches of a text block."""
    W = 0.0
    for line in paras:
        b_on, i_on, w = bool(bold), bool(italic), 0.0
        for chunk in re.split(r'(\*\*|//)', line):
            if chunk == '**': b_on = not b_on; continue
            if chunk == '//': i_on = not i_on; continue
            for part in TOK.split(chunk):
                if not part: continue
                f = 1.0
                if part.startswith('_{') or part.startswith('^{'):
                    f = 0.78; part = part[2:-1]
                part = part.replace('\u0303', '')
                w += _font(int(b_on), int(i_on)).getlength(part) / 1000 * size * f
        W = max(W, w)
    return W / 72, len(paras) * size * lead / 72


def tb(ctx, name, paras, size, x=None, y=None, cx=None, cy=None, rx=None, color='000000', align=None,
       bold=False, italic=False, pad=0.02):
    """Text box sized to its content. Give x (left), cx (centre) or rx (right); y (top) or cy (centre)."""
    w, h = measure(paras, size, bold, italic)
    w += pad
    if cx is not None: x = cx - w / 2; align = align or 'ctr'
    elif rx is not None: x = rx - w; align = align or 'r'
    else: align = align or 'l'
    if cy is not None: y = cy - h / 2
    el = textbox(ctx, name, x, y, w, h, paras, size=size, color=color, align=align, anchor='ctr', bold=bold, italic=italic)
    return el


def ungroup(ctx, gid):
    g = ctx.el(gid)
    xf = g.find('p:grpSpPr/a:xfrm', NS)
    off, ext, cho, che = (xf.find('a:' + k, NS) for k in ('off', 'ext', 'chOff', 'chExt'))
    assert ext.get('cx') == che.get('cx') and ext.get('cy') == che.get('cy'), 'scaled group'
    dx = (int(off.get('x')) - int(cho.get('x'))) / EMU
    dy = (int(off.get('y')) - int(cho.get('y'))) / EMU
    for ch in list(g):
        tag = etree.QName(ch).localname
        if tag in ('sp', 'grpSp', 'cxnSp', 'pic'):
            move(ch, dx, dy)
            g.addprevious(ch)
    g.getparent().remove(g)


def clone(ctx, i):
    el = deepcopy(ctx.el(i))
    for c in etree.XPath('.//p:cNvPr', namespaces=NS)(el):
        c.set('id', str(ctx.nid()))
    ctx.tree.append(el)
    return el


def place(ctx, ids, x, y, s=1.0):
    """Move (and scale by s) a set of top-level shapes so that their joint bbox starts at (x, y)."""
    els = [ctx.el(i) for i in ids]
    bs = [get_box(el) for el in els]
    x0 = min(b[0] for b in bs); y0 = min(b[1] for b in bs)
    for el, (bx, by, bw, bh) in zip(els, bs):
        set_box(el, x + (bx - x0) * s, y + (by - y0) * s, bw * s, bh * s)


def bbox(ctx, ids):
    bs = [get_box(ctx.el(i)) for i in ids]
    return (min(b[0] for b in bs), min(b[1] for b in bs), max(b[0] + b[2] for b in bs), max(b[1] + b[3] for b in bs))


def arrow(ctx, name, pts, color, w=1.25, head=True, dash=None, curve=False):
    if curve:
        cmds = [('M',) + pts[0], ('C',) + pts[1] + pts[2] + pts[3]]
    else:
        cmds = [('M',) + pts[0]] + [('L',) + p for p in pts[1:]]
    return path_shape(ctx, name, cmds, ln=ln_xml(color, w, dash=dash, tail=head))


def dot(ctx, x, y, color, r=0.028):
    return prst(ctx, 'junction', 'ellipse', x - r, y - r, 2 * r, 2 * r, fill=fill_xml(color))


def _bez(P, t):
    u = 1 - t
    return (u**3 * P[0][0] + 3*u*u*t * P[1][0] + 3*u*t*t * P[2][0] + t**3 * P[3][0],
            u**3 * P[0][1] + 3*u*u*t * P[1][1] + 3*u*t*t * P[2][1] + t**3 * P[3][1])


def ribbon(ctx, name, P, w0, w1, hw, hl, fill, line, lw=0.75, n=60):
    """Tapered curved ribbon arrow along cubic Bezier P=[p0,p1,p2,p3] (inches)."""
    import math
    pts = [_bez(P, i / n) for i in range(n + 1)]
    L = [0.0]
    for i in range(1, n + 1):
        L.append(L[-1] + math.dist(pts[i], pts[i - 1]))
    tot = L[-1]
    base = next(i for i in range(n + 1) if L[i] >= tot - hl)
    def nrm(i):
        a = pts[max(i - 1, 0)]; b = pts[min(i + 1, n)]
        dx, dy = b[0] - a[0], b[1] - a[1]; d = math.hypot(dx, dy)
        return (-dy / d, dx / d)
    left, right = [], []
    for i in range(base + 1):
        w = w0 + (w1 - w0) * (L[i] / L[base]) if L[base] > 0 else w1
        nx, ny = nrm(i)
        left.append((pts[i][0] + nx * w / 2, pts[i][1] + ny * w / 2))
        right.append((pts[i][0] - nx * w / 2, pts[i][1] - ny * w / 2))
    nx, ny = nrm(base)
    hb = pts[base]
    poly = left + [(hb[0] + nx * hw / 2, hb[1] + ny * hw / 2), pts[-1], (hb[0] - nx * hw / 2, hb[1] - ny * hw / 2)] + right[::-1]
    cmds = [('M',) + poly[0]] + [('L',) + p for p in poly[1:]] + [('Z',)]
    return path_shape(ctx, name, cmds, ln=ln_xml(line, lw, cap='rnd'), fill=fill, closed=True)
