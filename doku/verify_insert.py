import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from docx import Document
doc = Document(r"doku\HKTracker_CAS_Abschlussarbeit_Entwurf_v01.docx")
all_text = "\n".join(p.text for p in doc.paragraphs)

checks = [
    ("2.4.1 Traceability-Intro",       "Anforderungsherleitung aus Stakeholder-Interviews"),
    ("2.4.1 Traceability-Tabelle OK",  "Heinz/Viktor"),
    ("3.4 Synthese-Header",            "Durchgef"),
    ("3.4 Altin-Bullet",              "Altin (Lernende, Persona"),
    ("3.4 Tobias-Bullet",             "Tobias (Praxisbildner"),
    ("3.4 Iwo-Bullet",               "Iwo Kuhn (Berufsbildner"),
    ("3.4 Synthese-Para",             "bergreifende Erkenntnis"),
    ("4.4 Weiterentwicklung-Header",   "Interview-basierte Weiterentwicklung"),
    ("4.4 Push-Benachrichtigungen",    "Push-Benachrichtigungen"),
    ("4.4 AV-Dashboard",              "AV-Übersichts-Dashboard"),
    ("4.4 Reflexionspflicht",          "Reflexionspflicht"),
    ("4.4 Informelle Lernmomente",    "informelle Lernmomente"),
    ("4.4 Rotationsplanung",          "Rotationsplanung mit Interessenprofil"),
]

for label, needle in checks:
    ok = needle in all_text
    status = "OK   " if ok else "FEHLT"
    print(f"  [{status}] {label}")
