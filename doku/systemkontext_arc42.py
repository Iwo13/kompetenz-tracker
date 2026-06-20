"""
Generates an arc42 System Context Diagram (Kapitel 3 - Kontextabgrenzung)
for the HK-Tracker and inserts it into the thesis DOCX at two TODO paragraphs:
  - para in 1.4: [TODO: Systemkontextdiagramm erstellen (arc42 Kapitel 3)...]
  - para in 3.2: [TODO: arc42-Architekturdiagramm (C4 oder UML)...]

Arc42 Systemkontext shows the system as a BLACK BOX surrounded by:
  - Human actors (Lernende, Berufsbildner, Admin)
  - External systems (Azure OpenAI, Azure AD, FHNW IT/Azure)
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from matplotlib.lines import Line2D
from xml.sax.saxutils import escape as xml_escape
from docx import Document
from docx.shared import Inches
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from lxml import etree

DOCX_PATH = r'doku\HKTracker_CAS_Abschlussarbeit_Entwurf_v01.docx'
IMG_PATH  = r'doku\systemkontext_arc42.png'

# FHNW color palette
NAVY    = '#002B5C'
YELLOW  = '#FFD700'
WHITE   = '#FFFFFF'
GREEN   = '#15803d'
BLUE    = '#2563eb'
GRAY_BG = '#f8fafc'
GRAY_LT = '#e2e8f0'
GRAY_MD = '#94a3b8'
GRAY_DK = '#475569'
PLANNED_BG = '#eff6ff'
PLANNED_BD = '#93c5fd'
ORANGE  = '#c2410c'

# -------------------------------------------------------------------------
# Draw diagram
# -------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(14, 8.5))
fig.patch.set_facecolor(WHITE)
ax.set_facecolor(WHITE)
ax.set_xlim(0, 14)
ax.set_ylim(0, 8.5)
ax.axis('off')


def rbox(x, y, w, h, fc, ec, lw=1.0, ls='-', radius=0.15, alpha=1.0, zorder=3):
    """Rounded rectangle."""
    patch = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle=f'round,pad={radius}',
        facecolor=fc, edgecolor=ec, linewidth=lw,
        linestyle=ls, alpha=alpha, zorder=zorder
    )
    ax.add_patch(patch)


def label(x, y, text, fs=9, fw='normal', color=NAVY, ha='center', va='center', zorder=5):
    ax.text(x, y, text, fontsize=fs, fontweight=fw, color=color,
            ha=ha, va=va, zorder=zorder, linespacing=1.4)


def sublabel(x, y, text, fs=7.5, color=GRAY_DK):
    ax.text(x, y, text, fontsize=fs, color=color, ha='center', va='center',
            zorder=5, style='italic', linespacing=1.3)


def person(x, y, name, role_line='', color=GREEN):
    """Simple person icon: circle head + trapezoid body as box."""
    # Head
    head = plt.Circle((x, y + 0.38), 0.22, facecolor=color, edgecolor=WHITE,
                       linewidth=1.5, zorder=5)
    ax.add_patch(head)
    # Body
    rbox(x, y - 0.22, 0.72, 0.56, fc=color, ec=WHITE, lw=1.5, radius=0.08, zorder=4)
    # Name
    ax.text(x, y - 0.78, name, fontsize=8.5, fontweight='bold', color=NAVY,
            ha='center', va='top', zorder=6)
    if role_line:
        ax.text(x, y - 1.1, role_line, fontsize=7, color=GRAY_DK,
                ha='center', va='top', zorder=6, style='italic')


def arr(x1, y1, x2, y2, lbl='', lside='above', color=GRAY_DK, lw=1.4,
        style='->', lbl_fs=6.8):
    """One-way arrow with optional label."""
    ax.annotate('',
                xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color,
                                lw=lw, connectionstyle='arc3,rad=0.0'),
                zorder=6)
    if lbl:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dy = 0.17 if lside == 'above' else -0.17
        ax.text(mx, my + dy, lbl, fontsize=lbl_fs, color=color,
                ha='center', va='center', zorder=7,
                style='italic',
                bbox=dict(facecolor=WHITE, edgecolor='none', pad=1, alpha=0.7))


def darr(x1, y1, x2, y2, lbl='', lside='above', color=GRAY_DK):
    """Double-headed arrow."""
    arr(x1, y1, x2, y2, lbl=lbl, lside=lside, color=color, style='<->')


# =========================================================================
# LAYOUT
#   Actors left (x ≈ 1.4)
#   HK-Tracker center (x = 5 .. 9.5, y = 1.4 .. 7.6)
#   External systems right (x ≈ 12.3)
#   Azure Tenant boundary: dashed rect
# =========================================================================

# ---- Azure FHNW Tenant boundary ----
tenant = FancyBboxPatch(
    (4.4, 1.0), 9.3, 6.6,
    boxstyle='round,pad=0.2',
    facecolor='#f0f9ff', edgecolor='#60a5fa',
    linewidth=2, linestyle='--', alpha=0.6, zorder=1
)
ax.add_patch(tenant)
ax.text(4.6, 7.55, 'FHNW Azure Tenant  (Systemgrenze / Deployment-Kontext)',
        fontsize=7.5, color='#2563eb', va='center', zorder=2, style='italic')

# ---- HK-Tracker system box (center) ----
HK_X, HK_Y = 6.95, 4.3
HK_W, HK_H = 3.8, 4.8
rbox(HK_X, HK_Y, HK_W, HK_H, fc=NAVY, ec=NAVY, lw=0, radius=0.2, zorder=3)

label(HK_X, HK_Y + 1.6, 'HK-Tracker', fs=13, fw='bold', color=WHITE)
label(HK_X, HK_Y + 1.0, 'Handlungskompetenz-Tracker', fs=8, color=YELLOW)

# Internal component pills (informational — still a black-box context view)
for ix, iy, itxt, icolor in [
    (HK_X - 0.7, HK_Y + 0.25, 'React SPA\n(Frontend)',   '#1e40af'),
    (HK_X + 0.7, HK_Y + 0.25, 'ASP.NET Core 8\n(API)',   '#1e3a8a'),
    (HK_X,       HK_Y - 0.75, 'SQL Server\n(Datenbank)', '#1e3a8a'),
]:
    rbox(ix, iy, 1.1, 0.72, fc=icolor, ec=WHITE, lw=1, radius=0.1, alpha=0.9, zorder=4)
    ax.text(ix, iy, itxt, fontsize=6.5, color=WHITE, ha='center', va='center',
            zorder=5, linespacing=1.3)

sublabel(HK_X, HK_Y - 1.65,
         'React 19 + TypeScript + Vite\nASP.NET Core 8 + EF Core 8 + SQL Server',
         fs=6.5, color=GRAY_LT)

# ---- Human Actors (left column) ----
ACTOR_X = 1.55
person(ACTOR_X, 6.6,  'Lernende',       'Dokumenten-Upload\nFortschritts-Einsicht', color='#16a34a')
person(ACTOR_X, 3.95, 'Berufsbildner',  'Bewertungen, Planung\nFreigabe KI-Vorschläge', color='#0f766e')
person(ACTOR_X, 1.45, 'Admin\n(Chapter Lead)', 'Konfig., Ausb.-Plätze\nSysem-Pflege', color='#0369a1')

# ---- External Systems (right column) ----
EXT_X = 12.2
EXT_W, EXT_H = 2.55, 1.25

# Azure OpenAI
rbox(EXT_X, 6.55, EXT_W, EXT_H, fc='#dbeafe', ec=BLUE, lw=1.5, radius=0.12, zorder=3)
label(EXT_X, 6.7,  'Azure OpenAI Service', fs=8.5, fw='bold', color=BLUE)
sublabel(EXT_X, 6.4, 'GPT-4o · Bloom-Erkennung\nFHNW-Tenant (EU Data Boundary)', fs=6.8, color=BLUE)

# Azure AD
rbox(EXT_X, 4.3, EXT_W, EXT_H, fc=PLANNED_BG, ec=PLANNED_BD, lw=1.5,
     ls='--', radius=0.12, zorder=3)
label(EXT_X, 4.46, 'Azure AD / Entra ID', fs=8.5, fw='bold', color='#1d4ed8')
sublabel(EXT_X, 4.16, 'MSAL-Authentifizierung\n[geplant – IT-Freigabe ausstehend]',
         fs=6.8, color='#1d4ed8')

# Azure App Service
rbox(EXT_X, 2.1, EXT_W, EXT_H, fc=PLANNED_BG, ec=PLANNED_BD, lw=1.5,
     ls='--', radius=0.12, zorder=3)
label(EXT_X, 2.27, 'Azure App Service', fs=8.5, fw='bold', color='#1d4ed8')
sublabel(EXT_X, 1.96, 'Hosting / Deployment\n[geplant – Produktion]',
         fs=6.8, color='#1d4ed8')

# =========================================================================
# ARROWS
# =========================================================================
# LEFT: Actors → HK-Tracker left edge (x = 5.05)
HK_LEFT = HK_X - HK_W / 2 - 0.1

# Lernende ↔ HK-Tracker
darr(ACTOR_X + 0.75, 6.6, HK_LEFT, 6.0,
     lbl='Dokument-Upload / Fortschritt', lside='above', color='#16a34a')

# Berufsbildner ↔ HK-Tracker
darr(ACTOR_X + 0.75, 3.95, HK_LEFT, 4.3,
     lbl='Bloom-Bewertung / Rotationsplanung', lside='above', color='#0f766e')

# Admin ↔ HK-Tracker
darr(ACTOR_X + 0.75, 1.5, HK_LEFT, 2.6,
     lbl='Konfig / AP-Verwaltung', lside='below', color='#0369a1')

# RIGHT: HK-Tracker right edge → External systems
HK_RIGHT = HK_X + HK_W / 2 + 0.1
EXT_LEFT = EXT_X - EXT_W / 2 - 0.1

# HK ↔ Azure OpenAI
darr(HK_RIGHT, 5.9, EXT_LEFT, 6.55,
     lbl='anon. Dokumenttext + Leistungsziele\n← Bloom-Stufe K1-K6 + Begründung',
     lside='above', color=BLUE)

# HK ↔ Azure AD
arr(HK_RIGHT, 4.3, EXT_LEFT, 4.3,
    lbl='JWT-Token-Validierung [geplant]',
    lside='above', color='#6b7280', style='<->', lbl_fs=6.5)

# HK ↔ Azure App Service
arr(HK_RIGHT, 2.8, EXT_LEFT, 2.3,
    lbl='Deployment [geplant]',
    lside='below', color='#6b7280', lbl_fs=6.5)

# =========================================================================
# LEGEND
# =========================================================================
legend_y = 0.55
legend_items = [
    (mpatches.Patch(facecolor=NAVY, label='HK-Tracker (dieses System)'),),
    (mpatches.Patch(facecolor='#dbeafe', edgecolor=BLUE, lw=1.5,
                    label='Externe Systeme (bestehend)'),),
    (mpatches.Patch(facecolor=PLANNED_BG, edgecolor=PLANNED_BD, lw=1.5,
                    label='Externe Systeme [geplant]'),),
    (mpatches.Patch(facecolor=GREEN, label='Human Actors'),),
    (Line2D([0], [0], color=GRAY_DK, lw=1.4, marker='>', label='Kommunikationsbeziehung'),),
]
flat_legend = [item[0] for item in legend_items]
ax.legend(handles=flat_legend, loc='lower right', fontsize=7.5,
          framealpha=0.95, frameon=True, edgecolor=GRAY_LT,
          ncol=5, bbox_to_anchor=(0.99, 0.01))

# =========================================================================
# TITLE
# =========================================================================
ax.text(7, 8.2,
        'Abbildung: arc42 Systemkontextdiagramm – HK-Tracker (Kontextabgrenzung, Kapitel 3)',
        ha='center', va='center', fontsize=10, fontweight='bold', color=NAVY, zorder=10)

plt.tight_layout(pad=0.5)
plt.savefig(IMG_PATH, dpi=150, bbox_inches='tight', facecolor=WHITE)
plt.close()
print(f'PNG saved: {IMG_PATH}')


# =========================================================================
# Insert into DOCX at TWO TODO paragraphs
# =========================================================================
def make_caption(text):
    """Create a centred italic caption paragraph element."""
    return etree.fromstring(
        f'<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f'<w:pPr><w:jc w:val="center"/></w:pPr>'
        f'<w:r>'
        f'<w:rPr><w:i/><w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr>'
        f'<w:t xml:space="preserve">{xml_escape(text)}</w:t>'
        f'</w:r>'
        f'</w:p>'
    )


def insert_diagram(doc, todo_text_fragment, caption_text, width_inches=5.6):
    """Find TODO paragraph, insert image before it, replace TODO with caption."""
    todo_para = None
    for para in doc.paragraphs:
        if todo_text_fragment in para.text:
            todo_para = para
            break
    if todo_para is None:
        print(f"WARNING: TODO '{todo_text_fragment[:60]}' not found")
        return False

    print(f"Found TODO: {todo_para.text[:80]}")

    # 1. Add image paragraph at document end (python-docx limitation)
    img_para = doc.add_paragraph()
    img_para.alignment = 1  # CENTER
    run = img_para.add_run()
    run.add_picture(IMG_PATH, width=Inches(width_inches))

    # 2. Move image paragraph to BEFORE the TODO para
    todo_para._p.addprevious(img_para._p)

    # 3. Replace TODO paragraph content with caption
    # Remove all existing runs
    for r in todo_para._p.findall(qn('w:r')):
        todo_para._p.remove(r)
    # Ensure centre alignment
    pPr = todo_para._p.find(qn('w:pPr'))
    if pPr is None:
        pPr = OxmlElement('w:pPr')
        todo_para._p.insert(0, pPr)
    jc = pPr.find(qn('w:jc'))
    if jc is None:
        jc = OxmlElement('w:jc')
        pPr.append(jc)
    jc.set(qn('w:val'), 'center')
    # Add caption run
    r_elem = etree.fromstring(
        f'<w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f'<w:rPr><w:i/><w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr>'
        f'<w:t xml:space="preserve">{xml_escape(caption_text)}</w:t>'
        f'</w:r>'
    )
    todo_para._p.append(r_elem)
    print(f"OK: Image + caption inserted for '{todo_text_fragment[:50]}'")
    return True


doc = Document(DOCX_PATH)

CAPTION = ('Abbildung 4: arc42 Systemkontextdiagramm HK-Tracker – '
           'Akteure und externe Systeme (Kontextabgrenzung). '
           'Gestrichelt = geplant / ausstehende IT-Freigabe.')

# Insert at 1.4 TODO
insert_diagram(doc, '[TODO: Systemkontextdiagramm erstellen', CAPTION, width_inches=5.6)

# Insert at 3.2 TODO (same image, slightly narrower to fit the column)
insert_diagram(doc, '[TODO: arc42-Architekturdiagramm', CAPTION, width_inches=5.4)

doc.save(DOCX_PATH)
print(f'Saved: {DOCX_PATH}')
