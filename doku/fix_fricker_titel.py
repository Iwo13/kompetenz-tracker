import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document
from docx.oxml.ns import qn

SRC = r'C:\Projekte\IT-Lehre Handlungskompetenzen\doku\HKTracker_CAS_Abschlussarbeit_Entwurf_v01.docx'
doc = Document(SRC)

def fix_para_text(para, old_fragment, new_fragment):
    t_elems = list(para._p.iter(qn('w:t')))
    combined = ''.join((t.text or '') for t in t_elems)
    if old_fragment not in combined:
        return False
    t_elems[0].text = combined.replace(old_fragment, new_fragment, 1)
    for t in t_elems[1:]:
        t.text = ''
    return True

def find_para(doc, fragment):
    for p in doc.paragraphs:
        if fragment in p.text:
            return p
    return None

ref = find_para(doc, 'Samuel Fricker (Prof. Dr.) ist Leiter des CAS AI-SE')
assert ref, 'Ref not found'
ok = fix_para_text(ref, 'Leiter des CAS AI-SE', 'Studiengangsleiter CAS AI-SE')
print('Korrektur Studiengangsleiter:', 'OK' if ok else 'FEHLER')

doc.save(SRC)
print('Gespeichert.')
