"""
create_interview_bb.py
Erstellt HK_Interview_Berufsbildner_Iwo_Protokoll.docx
im selben Format wie die drei bestehenden Interviews.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()

# ── Hilfsfunktionen ─────────────────────────────────────────────────
def h1(text):
    p = doc.add_paragraph(text, style='Heading 1')
    return p

def h2(text):
    p = doc.add_paragraph(text, style='Heading 2')
    return p

def normal(text=''):
    return doc.add_paragraph(text, style='Normal')

def bullet(text):
    return doc.add_paragraph(text, style='List Paragraph')

def qa(question, answer):
    """Frage fett, Antwort normal — wie in den bestehenden Interviews."""
    normal(question)
    normal(answer)

# ════════════════════════════════════════════════════════════════════
# Dokument
# ════════════════════════════════════════════════════════════════════
h1('Interview: Handlungskompetenzen in der Berufsbildung — Ausbildungsverantwortliche/r')

# ── Protokoll (B.4) ──────────────────────────────────────────────────
h2('Protokoll (B.4)')

normal('Datum / Uhrzeit / Ort:')
normal('26. Juni 2026, schriftliche Selbstreflexion, CIT FHNW')
normal('Interviewpartner (Rolle / Persona):')
normal('Iwo Kuhn, Leiter ICT Berufsbildung / Ausbildungsverantwortlicher, CIT FHNW — Persona KUI')
normal('Interviewer:')
normal('Iwo Kuhn (Selbstreflexion, schriftlich)')
normal('Einverständnis Tonaufnahme:')
normal('[ ] Ja  [x] Nein — schriftliche Selbstbefragung')
normal('Dauer:')
normal('schriftlich (ca. 20 Minuten)')
normal('Kontext-Beobachtungen (Umgebung, Stimmung, Auffälligkeiten):')
normal(
    'Schriftliche Selbstreflexion. Iwo Kuhn ist gleichzeitig Projektverantwortlicher des HK-Trackers '
    'und Interviewpartner in der Rolle des Ausbildungsverantwortlichen. Antworten präzise und ohne '
    'Ausweichen — spiegeln den operativen Alltag der Ausbildungsverantwortung direkt wider. '
    'Besonders markant: klare Hierarchie der Nutzen (Transparenz vor Qualität vor Zeit) und '
    'die Erkenntnis, dass quantitative Aussagen zum HK-Fortschritt heute schlicht nicht möglich sind.'
)

normal('Key Quotes (direkte Zitate, wörtlich):')
bullet('"Keine Chance, höchstens als sehr grobe Schätzung ohne Basis." '
       '(auf die Frage, ob Aussagen wie «X% der Lernenden haben HK4 erreicht» möglich sind)')
bullet('"Es muss einfach, übersichtlich und ohne grossen Aufwand zu führen sein. '
       'Keinen Mehraufwand für die Praxisbildner."')
bullet('"Transparenz, die zur Qualitätserhöhung führt." (wichtigster Nutzen des Systems)')
bullet('"Wir sind eine Bildungsinstitution, die den Anspruch auf entsprechende '
       'Vermittlung von Kompetenzen hat."')
bullet('"Die Lernenden sollen nicht die Bewertungen von anderen Lernenden sehen können." '
       '(nicht verhandelbare Datenschutzanforderung)')

normal('Key Insights (3–5 wichtigste Erkenntnisse):')
bullet(
    'Überblick über den HK-Fortschritt aller Lernenden ist heute nur mit erheblichem Aufwand möglich '
    '— strukturiertes Zusammentragen aus verschiedenen Quellen (Gespräche, Schulnoten, Bildungsberichte) '
    'fehlt vollständig.'
)
bullet(
    'Quantitative Aussagen zum Kompetenzstand («X% haben HK4 erreicht») sind heute unmöglich — '
    'höchstens als sehr grobe Schätzung.'
)
bullet(
    'DSG-Konformität ist bereits gegeben; die wichtigste nicht verhandelbare Anforderung ist die '
    'Zugriffstrennung: Lernende sehen ausschliesslich eigene Daten.'
)
bullet(
    'Schlüsselpersonen für die Adoption sind Praxisbildner (Hauptnutzer) und Lernende (Dateneingabe) — '
    'beide müssen vom System überzeugt werden.'
)
bullet(
    'Grösstes pädagogisches Risiko: Lernende könnten KI-Vorschläge unreflektiert übernehmen, '
    'ohne eigene Auseinandersetzung mit den Inhalten.'
)

normal('Offene Folgefragen / nächste Schritte:')
bullet(
    'Wie können Bildungsberichte direkt aus dem HK-Tracker generiert oder zumindest vorbereitet werden '
    '(SBFI-Konformität, Kantonsbehörde)?'
)
bullet(
    'Wie wird die rollenbasierte Zugriffstrennung technisch sichergestellt und kommuniziert '
    '(F22/F23, MSAL Azure AD)?'
)
bullet(
    'Wie werden Praxisbildner für die regelmässige Nutzung motiviert — '
    'welches Change-Management ist nötig?'
)
bullet(
    'Wie verhindert die App, dass Lernende KI-Vorschläge ohne Reflexion übernehmen '
    '(Mindestlänge Freitext, Pflichtfelder)?'
)

normal('Validierung Persona-Hypothese:')
normal(
    '[ ] bestätigt  [x] teilweise  [ ] widerlegt — Persona KUI ist pragmatischer als angenommen. '
    'Compliance-Anforderungen sind weniger komplex als befürchtet (DSG-Konformität bereits gegeben). '
    'Der grösste Schmerz liegt nicht im Audit-Trail, sondern im fehlenden strukturierten Überblick '
    'und der Unmöglichkeit, quantitative Aussagen zu machen.'
)

normal('Anpassungsbedarf HK-Tracker (Features / UX / Datenschutz):')
bullet(
    'Aggregierte Übersichtsseite für Ausbildungsverantwortliche: HK-Fortschritt aller Lernenden '
    'auf einen Blick (noch nicht implementiert — Phase 2).'
)
bullet(
    'Rollenbasierter Zugriff zwingend: Lernende sehen nur eigene Daten (F22/F23, bereits geplant, '
    'MSAL Phase 2).'
)
bullet(
    'Einfachheit und Übersichtlichkeit priorisieren — jeder zusätzliche Klick reduziert die '
    'Adoption bei Praxisbildnern.'
)
bullet(
    'Reflexionspflicht einbauen: KI-Vorschlag darf erst bestätigt werden, wenn eigener Kommentar '
    'erfasst ist (Mindestlänge oder Pflichtfeld).'
)

# ════════════════════════════════════════════════════════════════════
# Interview-Hauptteil
# ════════════════════════════════════════════════════════════════════
h2('1. Einstieg & Warm-Up')

normal('Wie erhältst du heute einen Überblick über den Ausbildungsstand aller Lernenden '
       '— was schaust du dir wann an?')
normal(
    'Regelmässige Gespräche mit den Lernenden und Praxisbildnern; am Ende des Semesters '
    'sicherstellen, dass die Praxisbildner den Bildungsbericht erstellen. Ergänzen der '
    'Bildungsberichte mit schulischen Zielen basierend auf den Schulnoten. Lernende '
    'motivieren, dass sie ihre Bildungsdokumentation führen anhand ihrer Arbeiten im Betrieb.'
)

normal('Welche Berichte oder Dokumente musst du regelmässig erstellen, einreichen oder vorlegen?')
normal(
    'Sicherstellen, dass Bildungsberichte regelmässig erstellt werden — halbjährlich durch '
    'die Praxisbildner, ergänzt durch schulische Informationen. Kein formales digitales '
    'Berichtswesen ausserhalb der Bildungsberichte.'
)

# ────────────────────────────────────────────────────────────────────
h2('2. IST-Prozess: Transparenz & Informationslücken')

normal('Welche Information fehlt dir für die Gesamtübersicht, '
       'die du heute nur mit grossem Aufwand bekommst?')
normal(
    'Wissen, welche Kompetenzen die Lernenden aufbauen. Welche Systeme, Programmiersprachen '
    'und Vorgehensweisen sie anwenden. Auf welchem Niveau sie sich das Wissen aneignen.'
)

normal('Wann hattest du zuletzt das Gefühl: «Wenn es ein Problem bei einem Lernenden gibt, '
       'erfahre ich das zu spät»?')
normal(
    'Durch die regelmässige Kommunikation mit Lernenden und Praxisbildnern sowie der '
    'Transparenz der Schulnoten sehe ich Probleme relativ zeitnah. Es ist aber mit viel '
    'Aufwand verbunden, die Informationen strukturiert zusammenzutragen.'
)

normal('Wie rechtfertigst du den Ressourcenaufwand für Berufsbildung gegenüber dem Management?')
normal(
    'Wir sind eine Bildungsinstitution, die den Anspruch auf entsprechende Vermittlung von '
    'Kompetenzen hat. Die Zusammenarbeit mit jungen Menschen wird in der Regel gerne gemacht. '
    'Die Lernenden bieten nach einer Einarbeitungszeit auch konkreten Mehrwert.'
)

normal('Wie schwierig ist es heute, Aussagen zu machen wie: «X% der Lernenden haben '
       'Handlungskompetenz HK4 erreicht»?')
normal(
    'Keine Chance, höchstens als sehr grobe Schätzung ohne Basis.'
)

# ────────────────────────────────────────────────────────────────────
h2('3. Compliance, Datenschutz & Audit')

normal('Welche datenschutzrechtlichen Anforderungen (DSG, interne FHNW-Richtlinien) '
       'sind für dich bei einem digitalen System nicht verhandelbar?')
normal(
    'So wie wir die Daten heute bewirtschaften, sind wir DSG-konform. Ein digitales System '
    'muss diese Konformität ebenfalls gewährleisten — insbesondere hinsichtlich der Trennung '
    'von Personendaten und Leistungsbeurteilungen.'
)

normal('Wie wichtig ist es für dich, dass das System einen Audit-Trail führt — '
       'wer hat wann welche Bewertung gemacht?')
normal(
    'Dies ist für mich eher nebensächlich. Klar, der Kontext, in welchem eine Bewertung '
    'gemacht wurde, hilft, diese besser einzuschätzen.'
)

normal('Was muss für das System dokumentiert sein, damit es bei einem externen Audit '
       '(SBFI, Kantonsbehörde) standhält?')
normal(
    'Wer auf welche Daten Zugriff hat. Die Lernenden sollen nicht die Bewertungen von '
    'anderen Lernenden sehen können.'
)

# ────────────────────────────────────────────────────────────────────
h2('4. Tool-Akzeptanz & Empfehlung')

normal('Was müsste das System können, damit du es in einer Leitungssitzung empfehlen würdest?')
normal(
    'Es muss einfach, übersichtlich und ohne grossen Aufwand zu führen sein. Keinen '
    'Mehraufwand für die Praxisbildner. Es muss eine gute Übersicht bieten und auch einen '
    'Mehrwert für die betreuenden Praxisbildner und die Lernenden selbst.'
)

normal('Wer müsste sonst noch überzeugt werden, bevor das System produktiv eingesetzt werden kann?')
normal(
    'Der Kreis der Praxisbildner sind sicher die Schlüsselpersonen. Aber auch die Lernenden '
    'selbst, da sie das Tool befüllen müssen.'
)

normal('Welche Risiken siehst du bei der Einführung eines KI-gestützten Beurteilungssystems '
       'in der Berufsbildung?')
normal(
    'Dass sich die Lernenden zu wenig selbst Gedanken machen und nur, dass sie es erledigt '
    'haben, ohne Reflexion und Ergänzung speichern.'
)

normal('Was wäre für dich der wichtigste Nutzen — Zeitersparnis, Qualitätserhöhung oder Transparenz?')
normal(
    'Transparenz, die zur Qualitätserhöhung führt.'
)

# ════════════════════════════════════════════════════════════════════
# Zusammenfassung
# ════════════════════════════════════════════════════════════════════
h2('5. Zusammenfassung der Kernaussagen')

# Subheadings: fetter Normal-Paragraph, dann List Paragraphs
p = doc.add_paragraph(style='Normal')
p.add_run('Überblick und Dokumentationsverhalten heute').bold = True

bullet(
    'Überblick über den Ausbildungsstand entsteht durch regelmässige Gespräche mit Lernenden '
    'und Praxisbildnern sowie durch Schulnoten — kein strukturiertes digitales System vorhanden.'
)
bullet(
    'Bildungsberichte werden halbjährlich durch die Praxisbildner erstellt; '
    'Koordination liegt beim Ausbildungsverantwortlichen.'
)
bullet(
    'Quantitative Aussagen zum Kompetenzstand («X% haben HK4 erreicht») sind heute '
    'schlicht nicht möglich — keine Datenbasis vorhanden.'
)

p = doc.add_paragraph(style='Normal')
p.add_run('Grösste Frustrationen & Engpässe').bold = True

bullet(
    'Fehlender strukturierter Überblick: Informationen müssen mühsam aus Gesprächen, '
    'Bildungsberichten und Schulnoten zusammengetragen werden.'
)
bullet(
    'Keine digitale Grundlage für aggregierte Aussagen zum HK-Fortschritt aller Lernenden.'
)
bullet(
    'Hoher Koordinationsaufwand für die Sicherstellung der Bildungsberichte — '
    'abhängig von Disziplin der Praxisbildner.'
)

p = doc.add_paragraph(style='Normal')
p.add_run('Bedürfnisse & Idealzustand').bold = True

bullet(
    'Einfaches, übersichtliches System — kein Mehraufwand für Praxisbildner, '
    'sonst keine nachhaltige Adoption.'
)
bullet(
    'Gesamtübersicht über HK-Fortschritt aller Lernenden auf einen Blick für den '
    'Ausbildungsverantwortlichen.'
)
bullet(
    'Rollenbasierter Datenschutz nicht verhandelbar: Lernende sehen ausschliesslich '
    'eigene Daten, keine Einsicht in Bewertungen anderer.'
)
bullet(
    'Schrittweise Einführung: erst Praxisbildner überzeugen, dann Lernende '
    '(Change Management).'
)

p = doc.add_paragraph(style='Normal')
p.add_run('Akzeptanz KI-Unterstützung').bold = True

bullet(
    'Grundsätzlich offen für KI, solange das System einfach bedienbar bleibt und '
    'keinen Mehraufwand erzeugt.'
)
bullet(
    'Zentrales Risiko: Lernende übernehmen KI-Vorschläge ohne eigene Reflexion — '
    'Gegensteuer durch verpflichtende Freitexteingabe oder Mindestlänge vor Bestätigung.'
)
bullet(
    'Wichtigster Nutzen: Transparenz als Grundlage für Qualitätserhöhung — '
    'Zeitersparnis ist explizit nur Sekundäreffekt (deckt sich mit B1/B2 der Benefit-Priorisierung).'
)

# ── Speichern ────────────────────────────────────────────────────────
OUT = r"doku\HK_Interview_Berufsbildner_Iwo_Protokoll.docx"
doc.save(OUT)
print(f"Erstellt: {OUT}")
