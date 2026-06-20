"""
1. Adds AI transparency declaration paragraph to Ehrenwörtliche Erklärung
   (after existing two standard paragraphs, before [TODO] signature line)
2. Adds R56 (Anthropic Claude Code) to Literaturverzeichnis after R55
"""
import sys
from xml.sax.saxutils import escape as xml_escape
from docx import Document
from docx.oxml.ns import qn
from lxml import etree

DOCX_PATH = r'doku\HKTracker_CAS_Abschlussarbeit_Entwurf_v01.docx'

NRM = 'Standard'
LP  = 'Listenabsatz'


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


AI_DECLARATION = (
    'Die vorliegende Arbeit entstand in strukturierter Zusammenarbeit mit '
    'Claude Code (Anthropic PBC, Modell: claude-sonnet-4-6, [R56]). '
    'KI wurde in zwei Rollen eingesetzt: '
    '(1) als alleiniges Entwicklungswerkzeug für den vollständigen Quellcode '
    'des HK-Trackers — sine qua non, da der Autor über keine aktiven '
    'Programmierkenntnisse verfügt; '
    '(2) zur Anreicherung und Ausformulierung von Textabschnitten auf Basis '
    'vom Autor definierter Inhalte, Struktur und inhaltlicher Entscheide '
    '(Specification-Driven Development, vgl. Kap. 2.4). '
    'Alle inhaltlichen Entscheide, Bewertungen, Konzepte und die '
    'Gesamtverantwortung lagen beim Autor. '
    'Diese Offenlegung erfolgt im Geiste verantwortungsvoller KI-Nutzung '
    '(EU AI Act Transparenzpflicht [R52]) und in Übereinstimmung mit dem '
    'Thema des CAS AI for Software Engineering.'
)

R56 = (
    '[R56] Anthropic PBC. (2025). Claude Code (Modell: claude-sonnet-4-6) '
    '[KI-Entwicklungs- und Texterstellungsassistent]. '
    'https://claude.ai/code '
    '(eingesetzt März–August 2026 für Codeentwicklung und Thesis-Anreicherung).'
)


def main():
    doc = Document(DOCX_PATH)
    paras = doc.paragraphs

    # -------------------------------------------------------------------------
    # 1. Find [TODO: Datum und Unterschrift] in Ehrenwörtliche Erklärung
    #    and insert AI declaration paragraph before it
    # -------------------------------------------------------------------------
    todo_sig_para = None
    for p in paras:
        if '[TODO: Datum und Unterschrift' in p.text:
            todo_sig_para = p
            break

    if not todo_sig_para:
        print("ERROR: Signature TODO not found"); sys.exit(1)

    print(f"Signature TODO found: {todo_sig_para.text.strip()[:60]}")
    todo_sig_para._p.addprevious(make_para(AI_DECLARATION, NRM))
    print("OK: AI declaration inserted before signature TODO")

    # -------------------------------------------------------------------------
    # 2. Add R56 to Literaturverzeichnis after R55
    # -------------------------------------------------------------------------
    r55_para = None
    for p in paras:
        if p.text.strip().startswith('[R55]'):
            r55_para = p
            break

    if not r55_para:
        print("ERROR: R55 not found"); sys.exit(1)

    print(f"R55 found: {r55_para.text.strip()[:80]}")
    r55_para._p.addnext(make_para(R56, LP))
    print("OK: R56 (Anthropic Claude Code) added after R55")

    # -------------------------------------------------------------------------
    # Save
    # -------------------------------------------------------------------------
    doc.save(DOCX_PATH)
    print(f"\nSaved: {DOCX_PATH}")


if __name__ == '__main__':
    main()
