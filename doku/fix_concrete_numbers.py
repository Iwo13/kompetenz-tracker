"""
1. Replaces [X Lernende] with 10 Lernende in para 243 (Zeitersparnis-Hochrechnung)
2. Adds specific Ist-Aufwand question to Berufsbildner interview section (after para 822)
"""
import sys
from xml.sax.saxutils import escape as xml_escape
from docx import Document
from docx.oxml.ns import qn
from lxml import etree

DOCX_PATH = r'doku\HKTracker_CAS_Abschlussarbeit_Entwurf_v01.docx'

NRM = 'Standard'
LB  = 'Aufzhlungszeichen'
LB2 = 'Aufzhlungszeichen2'


def make_para(text, style_id, bold=False, italic=False):
    b = '<w:b/>' if bold else ''
    i = '<w:i/>' if italic else ''
    rpr = f'<w:rPr>{b}{i}</w:rPr>' if (bold or italic) else ''
    return etree.fromstring(
        f'<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f'<w:pPr><w:pStyle w:val="{style_id}"/></w:pPr>'
        f'<w:r>{rpr}<w:t xml:space="preserve">{xml_escape(text)}</w:t></w:r>'
        f'</w:p>'
    )


def fix_text(para, old, new):
    t_elems = list(para._p.iter(qn('w:t')))
    combined = ''.join((t.text or '') for t in t_elems)
    if old not in combined:
        return False
    t_elems[0].text = combined.replace(old, new, 1)
    for t in t_elems[1:]:
        t.text = ''
    return True


def main():
    doc = Document(DOCX_PATH)
    paras = doc.paragraphs

    # -------------------------------------------------------------------------
    # 1. Replace [X Lernende] → 10 Lernende (Zeitersparnis-Hochrechnung)
    # -------------------------------------------------------------------------
    hochrechnung_para = None
    for p in paras:
        if '[X Lernende]' in p.text and 'Hochrechnung' in p.text:
            hochrechnung_para = p
            break

    if hochrechnung_para:
        ok = fix_text(hochrechnung_para, '[X Lernende]', '10 Lernende')
        print(f"[X Lernende] → 10 Lernende: {ok}")
        print(f"  Result: {hochrechnung_para.text.strip()[:100]}")
    else:
        print("WARNING: Hochrechnung para not found")

    # -------------------------------------------------------------------------
    # 2. Add specific Minuten-Frage to Berufsbildner interview section
    #    Insert after "Was kostet dich am meisten Zeit..." question
    # -------------------------------------------------------------------------
    zeitfrage_para = None
    for p in paras:
        if 'Was kostet dich am meisten Zeit bei der ganzen Berufsbildungsarbeit' in p.text:
            zeitfrage_para = p
            break

    if zeitfrage_para:
        new_q = (
            'Wenn du heute eine Bloom-Bewertung für einen Kompetenznachweis machst — '
            'wie viele Minuten dauert das typischerweise, '
            'vom Dokument lesen bis zum fertigen Eintrag? '
            '(Ziel: Ist-Aufwand in Minuten für Kap. 2.3 Benefit 6)'
        )
        zeitfrage_para._p.addnext(make_para(new_q, LB))
        print(f"Added Minuten-Frage after: {zeitfrage_para.text.strip()[:80]}")
    else:
        print("WARNING: Zeitfrage anchor para not found")

    # -------------------------------------------------------------------------
    # Save
    # -------------------------------------------------------------------------
    doc.save(DOCX_PATH)
    print(f"\nSaved: {DOCX_PATH}")


if __name__ == '__main__':
    main()
