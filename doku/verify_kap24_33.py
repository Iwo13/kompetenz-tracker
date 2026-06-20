from docx import Document
doc = Document(r'doku\HKTracker_CAS_Abschlussarbeit_Entwurf_v01.docx')

checks = ['SDD', 'FHNW Styleguide V5', 'Konversationelle Optimierung',
          '15 Iterationen', 'Phase 3b', 'AP-zentrierte', 'R54', 'R55',
          'Design-Input durch Iwo', 'Claude Code Beitrag']
found = {k: False for k in checks}
for p in doc.paragraphs:
    for k in found:
        if k in p.text:
            found[k] = True

print('=== Checks ===')
for k, v in found.items():
    status = 'OK  ' if v else 'MISS'
    print(f'  [{status}] {k}')

print()
print('=== 2.4 structure ===')
in24 = False
for i, p in enumerate(doc.paragraphs):
    t = p.text.strip()
    if '2.4' in t and 'Vorgehen' in t:
        in24 = True
    if in24 and (t.startswith('2.5') or t.startswith('3 ')):
        break
    if in24 and t:
        print(f'  [{i:4d}] {p.style.name[:15]} | {t[:100]}')

print()
print('=== 3.3 first 20 items ===')
in33 = False
count = 0
for i, p in enumerate(doc.paragraphs):
    t = p.text.strip()
    if '3.3' in t and 'Demons' in t:
        in33 = True
    if in33 and t.startswith('3.4'):
        break
    if in33 and t:
        print(f'  [{i:4d}] {p.style.name[:15]} | {t[:100]}')
        count += 1
        if count > 20:
            print('  ...')
            break
