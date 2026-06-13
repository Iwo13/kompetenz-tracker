"""
Thesis enrichment script – CORRECTED VERSION
Adds content from CAS module materials (Tag 10 Security/Maintenance,
Tag 11 SusAF/Personas/Personalisierung) into thesis docx.

Insertion rules:
  insert_paras_after(ref_para, items) → addnext + reversed(items)  → correct forward order after ref
  insert_paras_before(ref_para, items) → insert_paragraph_before in forward order → correct order before ref
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

SRC = r'C:\Projekte\IT-Lehre Handlungskompetenzen\doku\HKTracker_CAS_Abschlussarbeit_Entwurf_v01.docx'

doc = Document(SRC)

# Style name → Word XML style ID for this German template
STYLE_ID = {
    'Normal':          'Standard',
    'Heading 1':       'berschrift1',
    'Heading 2':       'berschrift2',
    'Heading 3':       'berschrift3',
    'List Bullet':     'Aufzhlungszeichen',
    'List Bullet 2':   'Aufzhlungszeichen2',
    'List Paragraph':  'Listenabsatz',
}


def make_xml_para(text, style_name):
    """Create a bare lxml <w:p> element with the given style and text."""
    p = OxmlElement('w:p')
    pPr = OxmlElement('w:pPr')
    pStyle = OxmlElement('w:pStyle')
    pStyle.set(qn('w:val'), STYLE_ID.get(style_name, 'Standard'))
    pPr.append(pStyle)
    p.append(pPr)
    r = OxmlElement('w:r')
    t = OxmlElement('w:t')
    t.text = text
    if text and (text[0] == ' ' or text[-1] == ' '):
        t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    r.append(t)
    p.append(r)
    return p


def insert_paras_after(ref_para, items):
    """Insert (text, style) items in FORWARD order AFTER ref_para."""
    ref_p = ref_para._p
    for text, style in reversed(items):
        ref_p.addnext(make_xml_para(text, style))


def insert_paras_before(ref_para, items):
    """Insert (text, style) items in FORWARD order BEFORE ref_para."""
    for text, style in items:
        ref_para.insert_paragraph_before(text, style)


def find_para(doc, text_fragment, style_name=None):
    """Return first paragraph containing text_fragment (optionally matching style)."""
    for p in doc.paragraphs:
        if text_fragment in p.text:
            if style_name is None or p.style.name == style_name:
                return p
    return None


# ── 1. SECTION 1.4: Persona sub-section ─────────────────────────────────────
# Insert AFTER the RAM/Constraints bullet (para containing "Constraints: DSG Datenschutz")

ram_para = find_para(doc, 'Constraints: DSG Datenschutz')
assert ram_para, 'RAM constraints para not found'

persona_items = [
    ('', 'Normal'),
    ('1.4.1  Personas (Nutzerprofile)', 'Heading 3'),
    ('Die vier zentralen Nutzergruppen wurden als Cooper-Personas (zielorientiert) modelliert '
     'und bilden die Grundlage für die Requirements-Erhebung sowie das UX-Design des '
     'HK-Trackers.  vgl. [R25] Cooper 1999', 'Normal'),
    ('', 'Normal'),
    ('Methodik: Im Unterschied zu klassischen Ad-hoc-Personas, die am Projektstart erstellt '
     'und danach nie validiert werden («created, never validated, never evolved» – '
     'Patkar & Seyff 2023), sollen die HK-Tracker-Personas im Pilotbetrieb mit echten '
     'Nutzerinnen und Nutzern validiert und bei Bedarf angepasst werden.  '
     'vgl. [R24] Patkar & Seyff REFSQ 2023', 'Normal'),
    ('', 'Normal'),
    ('Persona 1 – Heinz, 17, Lernender Informatik EFZ AppDev (1. Lehrjahr)', 'List Bullet'),
    ('Rolle: Lernender in Anwendungsentwicklungs-Rotation; erste Monate im Betrieb', 'List Bullet 2'),
    ('Bedürfnis: einfache Orientierung, klare Anforderungen, schnelle Erfassung von Lernnachweisen', 'List Bullet 2'),
    ('Frustration: Word-Formulare veraltet; unklar, welche Kompetenzen noch fehlen', 'List Bullet 2'),
    ('HK-Tracker Mehrwert: intuitive Web-App, strukturierter Überblick, Rotationsplanung sichtbar', 'List Bullet 2'),
    ('', 'Normal'),
    ('Persona 2 – Viktor, 18, Lernender ICT-Fachmann EFZ (2. Lehrjahr)', 'List Bullet'),
    ('Rolle: Lernender in Plattformbetrieb-Rotation, führt vor allem Support-Aufgaben durch', 'List Bullet 2'),
    ('Bedürfnis: nachvollziehbare Bewertung, wissen woran man ist, Lücken früh erkennen', 'List Bullet 2'),
    ('Frustration: Beurteilungen kommen spät, Kriterien unklar; Excel-Listen schwer lesbar', 'List Bullet 2'),
    ('HK-Tracker Mehrwert: Live-Fortschrittsanzeige, Eigeneinschätzung vor KI-Vorschlag', 'List Bullet 2'),
    ('', 'Normal'),
    ('Persona 3 – Michi, 35, Praxisbildner Softwareentwicklung', 'List Bullet'),
    ('Rolle: Software-Engineer, betreut Informatik-Lernende; kein Pädagogik-Studium', 'List Bullet 2'),
    ('Bedürfnis: schnelle Bloom-Einschätzung ohne Taxonomie-Expertenwissen, wenig Aufwand', 'List Bullet 2'),
    ('Frustration: unklare Abgrenzung K3 vs. K4; Dokumentationsaufwand frisst Entwicklungszeit', 'List Bullet 2'),
    ('HK-Tracker Mehrwert: KI-Vorschlag mit Begründung → Lerneffekt für Praxisbildner selbst', 'List Bullet 2'),
    ('', 'Normal'),
    ('Persona 4 – KUI, 50, Ausbildungsverantwortliche', 'List Bullet'),
    ('Rolle: Leiterin Berufsbildung FHNW, verantwortet Compliance, Budget, Reporting', 'List Bullet 2'),
    ('Bedürfnis: kompakte Übersichten, Audit-fähige Nachweise, Datenschutzkonformität', 'List Bullet 2'),
    ('Frustration: manuelle Aggregation über alle Lernenden in Excel; fehlende Transparenz', 'List Bullet 2'),
    ('HK-Tracker Mehrwert: automatische Gesamtauswertungen, Exportfunktion, DSGVO-Konformität', 'List Bullet 2'),
    ('', 'Normal'),
    ('Die Personas wurden im Rahmen von Modultag 11 (Seyff, FHNW) erarbeitet und '
     'orientieren sich am Cooper-Ansatz (zielorientiert). Sie werden im Pilotbetrieb '
     '(Phase 3) durch strukturierte Interviews nach RE-Methodik validiert.  '
     'vgl. [R24] Patkar & Seyff 2023; [R25] Cooper 1999; Tag 11 Seyff FHNW', 'Normal'),
    ('', 'Normal'),
]

insert_paras_after(ram_para, persona_items)
print('1.4 Personas: inserted')

# ── 2. SECTION 2.5: SusAF Nachhaltigkeitsanforderungen ───────────────────────
# Insert BEFORE the "3  Umsetzung" heading

umsetzung_heading = find_para(doc, '3  Umsetzung', style_name='Heading 1')
assert umsetzung_heading, '"3 Umsetzung" heading not found'

susaf_items = [
    ('', 'Normal'),
    ('2.5  Nachhaltigkeitsanforderungen aus SusAF-Analyse', 'Heading 2'),
    ('[Vorgabe] Nachhaltigkeitsanforderungen: Nicht-funktionale Anforderungen aus der '
     'Nachhaltigkeitsperspektive.  vgl. Tag 11 SusAF-Framework Becker et al.', 'Normal'),
    ('Methode: Sustainability Awareness Framework (SusAF) – 5 Dimensionen × 3 Ebenen '
     '(Immediate, Enabling, Systemic). Angewendet auf den HK-Tracker in Modultag 11.  '
     'vgl. [R26] Becker et al. 2016; [R27] Penzenstadler et al. 2014', 'Normal'),
    ('', 'Normal'),
    ('SusAF-Analyse (5 Dimensionen):', 'Normal'),
    ('Technisch: Cloud-Native-Architektur (12-Factor App); Wartbarkeit durch arc42 + ADRs; '
     'Risiko: Azure-OpenAI-Abhängigkeit', 'List Bullet'),
    ('Sozial: KI-Vorschläge unterstützen Berufsbildner, ersetzen kein pädagogisches Urteil; '
     'Transparenzpflicht gegenüber Lernenden (DSG Art. 19)', 'List Bullet'),
    ('Wirtschaftlich: Open-Source-Prototyp (kein Lizenzaufwand); Azure OpenAI-Kosten '
     'on-demand; Zeitersparnis > 50% Dokumentationsaufwand als wirtschaftlicher Nutzen', 'List Bullet'),
    ('Ökologisch: LLM-Aufrufe nur on-demand (kein Batch); Azure EU Data Center mit '
     'Renewable Energy Commitment; Bloom-Cache für Wiederholungsanfragen geplant', 'List Bullet'),
    ('Individuell: Lernende erhalten strukturiertes Kompetenz-Feedback; Berufsbildner '
     'lernen Bloom-Taxonomie durch KI-Begründungen (Upskilling-Effekt)', 'List Bullet'),
    ('', 'Normal'),
    ('Kernbotschaft: «KI als Reflexionsanstoss, nicht als Reflexionsersatz»  '
     'vgl. Tag 11 SusAF-Analyse HK-Tracker', 'Normal'),
    ('', 'Normal'),
    ('Ursache-Wirkungs-Ketten:', 'Normal'),
    ('Positiv 1: Lernnachweis erfasst → KI schlägt Bloom vor → Berufsbildner reflektiert '
     'Begründung → eigene Bloom-Expertise steigt → konsistentere Bewertungen → bessere '
     'Rotationsplanung', 'List Bullet'),
    ('Positiv 2: Eigeneinschätzung (NFA-S1) erzwungen → Lernende formulieren Stärken/'
     'Schwächen → strukturierte Reflexion → höhere Lernmotivation und Selbstwirksamkeit', 'List Bullet'),
    ('Negativ 1: KI-Vorschlag ohne kritische Prüfung übernommen → Automation Bias → '
     'Bloom-Bewertungen verlieren pädagogische Tiefe → Qualitätsverlust in der Ausbildung', 'List Bullet'),
    ('Negativ 2: Lernende erkennen Muster im KI-Vorschlag → passen Texte strategisch an '
     '→ Gaming-Effekt → Kompetenznachweise verlieren Authentizität', 'List Bullet'),
    ('', 'Normal'),
    ('Abgeleitete Nachhaltigkeitsanforderungen (NFA):', 'Normal'),
    ('NFA-S1: Pflichtfeld Eigeneinschätzung vor KI-Vorschlag – Lernende erfassen eigene '
     'Bloom-Einschätzung, bevor KI-Vorschlag angezeigt wird. Verhindert kognitive '
     'Passivität; stärkt Reflexionskompetenz. SusAF-Dimension: Individuell/Sozial.', 'List Bullet'),
    ('NFA-S2: Automatische Datenlöschung 2 Jahre nach Lehrabschluss – DSG-konform '
     '(Right to Erasure). SusAF-Dimension: Sozial/Technisch.', 'List Bullet'),
    ('NFA-S3: Kein Training externer KI-Modelle mit Inhaltsdaten – Azure OpenAI Contract '
     'muss «Opt-Out Training» sicherstellen; kein Fine-Tuning auf Lernendendaten. '
     'SusAF-Dimension: Sozial/Technisch.  vgl. [R30] Arditi et al. 2024', 'List Bullet'),
    ('NFA-S4: KI-Vorschläge als überarbeitbare Entwürfe kennzeichnen – im UI klar als '
     '«KI-Vorschlag» markieren; Berufsbildner-Entscheid separat speichern; verhindert '
     'Automation Bias. SusAF-Dimension: Sozial.  vgl. [R28] Veracode 2025', 'List Bullet'),
    ('', 'Normal'),
]

insert_paras_before(umsetzung_heading, susaf_items)
print('2.5 SusAF requirements: inserted')

# ── 3. SECTION 4.3: Security & SusAF sub-sections ────────────────────────────
# Insert AFTER the "Wartbarkeit: arc42-Dokumentation" bullet in 4.3

wartbarkeit_para = find_para(doc, 'Wartbarkeit: arc42-Dokumentation')
assert wartbarkeit_para, '"Wartbarkeit" para not found'

security_items = [
    ('', 'Normal'),
    ('4.3.1  Sicherheitsrisiken durch KI-generierten Code', 'Heading 3'),
    ('Ein bisher unterschätztes Risiko bei der KI-gestützten Softwareentwicklung betrifft '
     'die Sicherheit des generierten Codes.  vgl. Tag 10 Scherb – Security in the Age of AI', 'Normal'),
    ('', 'Normal'),
    ('Empirische Befunde:', 'Normal'),
    ('Veracode (2025): 45% des KI-generierten Codes enthält OWASP-Top-10-Schwachstellen  '
     'vgl. [R28] Veracode 2025', 'List Bullet'),
    ('Cotroneo, Improta & Liguori (2025): KI-Code weist 1,9–2,7× höhere Schwachstellen-'
     'dichte auf als menschlicher Code; 1,75× mehr Logikfehler; 2,74× mehr XSS  '
     'vgl. [R29] Cotroneo et al. 2025', 'List Bullet'),
    ('69% der Organisationen haben KI-eingebrachte Sicherheitslücken identifiziert  '
     'vgl. Tag 10 Scherb FHNW', 'List Bullet'),
    ('Amazon intern: ~5× mehr Betriebsprobleme 2025 vs. 2024 (korreliert mit skaliertem '
     'KI-Code-Einsatz)  vgl. Tag 10 Scherb', 'List Bullet'),
    ('', 'Normal'),
    ('Spezifische Risiken für den HK-Tracker:', 'Normal'),
    ('Lost Shared Knowledge: KI-Code «landet ohne» gemeinsames mentales Modell; '
     'Bus-Faktor ≈ 0 am ersten Tag – kritisch beim Solo-Entwickler-Ansatz', 'List Bullet'),
    ('Model Supply Chain Risk: Manipulierte System-Prompts in Coding-Tools (.cursor/rules) '
     'können Backdoors in scheinbar sauberem Code platzieren  '
     'vgl. [R33] Pillar Security 2025', 'List Bullet'),
    ('Prompt Injection: Lernenden-Freitexte, die an Azure OpenAI gesendet werden, sind '
     'attacker-controlled → Indirect-Prompt-Injection-Risiko  vgl. [R31] Greshake et al. 2023', 'List Bullet'),
    ('Abliteration: Open-Weight-Modelle können so modifiziert werden, dass '
     'Sicherheits-Refusals entfernt werden; Self-Hosting ist keine Sicherheitsgarantie  '
     'vgl. [R30] Arditi et al. 2024', 'List Bullet'),
    ('', 'Normal'),
    ('Gegenmassnahmen (Defense-in-Depth):', 'Normal'),
    ('Provenance: KI-generierte Abschnitte im Git-History markieren (co-authored-by); '
     'manuelle Security-Reviews', 'List Bullet'),
    ('Process: ESLint, statische Analyse vor Commit; Prinzip «Never let one model be both '
     'author and judge»', 'List Bullet'),
    ('Verification: HTTP-Snapshot-Regressionstests vor jeder KI-Integration; '
     'OWASP-Checkliste für API-Endpunkte', 'List Bullet'),
    ('Adversarial Review: Indirect Prompt Injection Simulation gegen eigenen Bloom-Endpunkt  '
     'vgl. [R31] Greshake et al. 2023', 'List Bullet'),
    ('', 'Normal'),
    ('4.3.2  Nachhaltigkeitsanalyse (SusAF)', 'Heading 3'),
    ('Die vollständige SusAF-Analyse (5 Dimensionen) und die abgeleiteten '
     'Nachhaltigkeitsanforderungen NFA-S1 bis NFA-S4 sind in Abschnitt 2.5 dokumentiert. '
     'Kernbefund: HK-Tracker hat primär positive Wirkung auf die Dimensionen Sozial und '
     'Individuell; ökologischer Footprint bleibt durch on-demand KI-Einsatz kontrolliert.  '
     'vgl. [R26] Becker et al. SusAF; Tag 11', 'Normal'),
    ('', 'Normal'),
]

insert_paras_after(wartbarkeit_para, security_items)
print('4.3 Security/SusAF sub-sections: inserted')

# ── 4. BIBLIOGRAPHY: Add R24–R38 after [R23] Fowler ─────────────────────────
# Use style-specific search to avoid the inline [R23] reference in section 1.3

r23_para = find_para(doc, '[R23] Fowler', style_name='List Paragraph')
assert r23_para, '[R23] Fowler List Paragraph not found'

new_refs = [
    '[R24] Patkar, V., & Seyff, N. (2023). From Personas to Persona Engines: Challenges and '
    'Opportunities. Proceedings of REFSQ 2023. https://doi.org/10.1007/978-3-031-29786-1_14',

    '[R25] Cooper, A. (1999). The Inmates Are Running the Asylum: Why High-Tech Products Drive '
    'Us Crazy and How to Restore the Sanity. Sams Publishing.',

    '[R26] Becker, C., Chitchyan, R., Duboc, L., Easterbrook, S., Penzenstadler, B., Seyff, N., '
    '& Venters, C. C. (2016). Sustainability Design and Software: The Karlskrona Manifesto. '
    'In Proceedings of ICSE 2015. IEEE. https://doi.org/10.1109/ICSE.2015.179',

    '[R27] Penzenstadler, B., Raturi, A., Richardson, D., & Tomlinson, B. (2014). Safety, '
    'security, now sustainability: The non-functional requirement for the 21st century. '
    'IEEE Software, 31(3), 40-47. https://doi.org/10.1109/MS.2014.53',

    '[R28] Veracode. (2025). State of Software Security: AI-Generated Code and Vulnerability '
    'Trends. Veracode Research Report 2025.',

    '[R29] Cotroneo, D., Improta, C., & Liguori, P. (2025). On the vulnerability of '
    'AI-generated code: An empirical study. [Konferenzpaper, DOI zu ergaenzen]',

    '[R30] Arditi, A., et al. (2024). Refusal in Language Models Is Mediated by a Single '
    'Direction. Advances in Neural Information Processing Systems (NeurIPS 2024). '
    'https://arxiv.org/abs/2406.11717',

    "[R31] Greshake, K., et al. (2023). Not what you've signed up for: Compromising "
    'Real-World LLM-Integrated Applications with Indirect Prompt Injection. '
    'AISec Workshop, ACM CCS 2023. https://arxiv.org/abs/2302.12173',

    '[R32] Yang, G., et al. (2025). Survey on LLM-based Automated Program Repair. '
    'arXiv:2506.23749.',

    '[R33] Pillar Security. (2025). Rules-File Backdoor: Supply Chain Attack via Cursor '
    'and Copilot System Prompts. Pillar Security Research Blog.',

    '[R34] Park, J. S., et al. (2023). Generative Agents: Interactive Simulacra of Human '
    'Behavior. Proceedings of UIST 2023. https://doi.org/10.1145/3586183.3606763',

    '[R35] Argyle, L. P., et al. (2023). Out of One, Many: Using Language Models to Simulate '
    'Human Samples. Political Analysis, 31(3), 337-351. '
    'https://doi.org/10.1017/pan.2023.2',

    '[R36] Oriol, M., et al. (2018). FAME: A Feedback Analytics Methodology for Continuous '
    'Requirements Engineering. IEEE International RE Conference (RE 2018). '
    'https://doi.org/10.1109/RE.2018.00052',

    '[R37] Jimenez, C. E., et al. (2024). SWE-Bench: Can Language Models Resolve '
    'Real-World GitHub Issues? ICLR 2024. https://arxiv.org/abs/2310.06770',

    '[R38] AWS. (2025). Statement on AI-generated code and operational issues. '
    'Amazon Web Services Official Account, X (formerly Twitter), 2025.',
]

ref_items = [(text, 'List Paragraph') for text in new_refs]
insert_paras_after(r23_para, ref_items)
print('Bibliography R24-R38: inserted')

# ── 5. GLOSSAR: Add new terms ─────────────────────────────────────────────────
glossar_last = find_para(doc, 'arc42: 12-Kapitel-Standard')
assert glossar_last, 'Glossar arc42 entry not found'

glossar_items = [
    ('APR: Automated Program Repair – KI-gestützte automatisierte Fehlerbehebung in Software. '
     'Benchmark: SWE-Bench (Jimenez et al. 2024).  vgl. [R37]',
     'List Paragraph'),

    ('MAPE-K: Monitor - Analyze - Plan - Execute + Knowledge – Steuerungsschleife fuer '
     'adaptive Systeme; Grundlage FAME-Framework fuer kontinuierliches RE.  vgl. [R36]',
     'List Paragraph'),

    ('OWASP Top 10: Die zehn haeufigsten Web-Anwendungssicherheitsrisiken (Open Worldwide '
     'Application Security Project), u.a. Injection, XSS, IDOR.  vgl. [R28] Veracode 2025',
     'List Paragraph'),

    ('SusAF: Sustainability Awareness Framework – analysiert Software-Systeme entlang '
     '5 Nachhaltigkeitsdimensionen (Technisch, Sozial, Wirtschaftlich, OEkologisch, '
     'Individuell) auf 3 Ebenen (Immediate, Enabling, Systemic).  vgl. [R26] Becker et al.',
     'List Paragraph'),

    ('SWE-Bench: Benchmark mit 2294 realen GitHub-Issues als Testfaelle fuer KI-basierte '
     'Software-Engineering-Assistenten (Jimenez et al. 2024).  vgl. [R37]',
     'List Paragraph'),

    ('Silicon Sampling: Methode, bei der LLMs als Proxy fuer Bevoelkerungsgruppen eingesetzt '
     'werden, um Umfragen zu simulieren (Argyle et al. 2023).  vgl. [R35]',
     'List Paragraph'),
]

insert_paras_after(glossar_last, glossar_items)
print('Glossar: 6 new terms inserted')

# ── 6. ABKÜRZUNGSVERZEICHNIS: Add missing abbreviations ──────────────────────
abbrev_last = find_para(doc, 'VSM:\tValue Stream Mapping')
assert abbrev_last, 'VSM abbreviation not found'

abbrev_items = [
    ('APR:\tAutomated Program Repair', 'List Paragraph'),
    ('MAPE-K:\tMonitor-Analyze-Plan-Execute-Knowledge', 'List Paragraph'),
    ('OWASP:\tOpen Worldwide Application Security Project', 'List Paragraph'),
    ('SusAF:\tSustainability Awareness Framework', 'List Paragraph'),
    ('XSS:\tCross-Site Scripting', 'List Paragraph'),
]

insert_paras_after(abbrev_last, abbrev_items)
print('Abkuerzungsverzeichnis: 5 terms added')

# ── 7. Fix bibliography TODO marker ──────────────────────────────────────────
for p in doc.paragraphs:
    if 'Tags 09' in p.text and '14 Referenzen ergaenzen' in p.text or \
       'Tags 09' in p.text and '14 Referenzen erg' in p.text or \
       ('Tags 09' in p.text and 'Unterlagen verfügbar' in p.text):
        for run in p.runs:
            if 'Tags 09' in run.text:
                run.text = run.text.replace(
                    run.text,
                    'Tags 10-11 Referenzen ergaenzt: R24-R38 (13.06.2026). Tags 12-14 noch ausstehend.'
                )
        break

# ── Save ──────────────────────────────────────────────────────────────────────
doc.save(SRC)
print(f'\nGespeichert: {SRC}')
print('Fertig! Thesis erfolgreich angereichert.')
