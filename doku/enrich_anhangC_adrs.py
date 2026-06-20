"""
Creates 7 ADRs in MADR v4 format and inserts them into Anhang C.
Also:
  - Replaces [TODO: ADR erstellen Azure OpenAI] with ref to ADR-003
  - Replaces [TODO: ADR-Index erstellen] with a proper index list
  - Updates placeholder text in Anhang C
  - Updates 3.1 bullet 'ADRs mit MADR v4-Format (geplant)' → '(implementiert, Anhang C)'

ADRs:
  ADR-001: React 19 + TypeScript + Vite statt Angular/Vue
  ADR-002: ASP.NET Core 8 statt Node.js/Python
  ADR-003: Azure OpenAI statt direktem OpenAI / On-Premise
  ADR-004: LiteLLM als Provider-Gateway (geplant)
  ADR-005: SQL Server / Azure SQL statt PostgreSQL
  ADR-006: Claude Code + SDD als Entwicklungsmethodik
  ADR-007: Merge-Strategie KI → Human (nur leere Felder befüllen)
"""
import sys
from xml.sax.saxutils import escape as xml_escape
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from lxml import etree

DOCX_PATH = r'doku\HKTracker_CAS_Abschlussarbeit_Entwurf_v01.docx'

NRM = 'Standard'
H2  = 'berschrift2'
H3  = 'berschrift3'
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


# =========================================================================
# ADR CONTENT  (MADR v4 structure)
# Each ADR: list of (text, style) tuples
# =========================================================================

def adr(title, status, date, deciders, context, drivers, options_list,
        decision, pos_cons, neg_cons, options_detail):
    """Build ADR paragraph list in MADR v4 format."""
    items = [
        (title, H2),
        (f'Status: {status}  |  Datum: {date}  |  Entscheider: {deciders}', (NRM, 'italic')),
        ('Kontext und Problemstellung', H3),
        (context, NRM),
        ('Entscheidungstreiber', H3),
    ]
    for d in drivers:
        items.append((d, LB))
    items.append(('Betrachtete Optionen', H3))
    for o in options_list:
        items.append((o, LB))
    items.append(('Entscheidung', H3))
    items.append((decision, NRM))
    items.append(('Konsequenzen', H3))
    for c in pos_cons:
        items.append((f'+ {c}', LB))
    for c in neg_cons:
        items.append((f'– {c}', LB))
    items.append(('Optionenvergleich', H3))
    for opt_name, pros, cons in options_detail:
        items.append((opt_name, (LB, 'bold')))
        for p in pros:
            items.append((f'+ {p}', LB2))
        for c in cons:
            items.append((f'– {c}', LB2))
    return items


ADR_001 = adr(
    title='ADR-001: React 19 + TypeScript + Vite statt Angular oder Vue',
    status='Accepted',
    date='2026-03-01',
    deciders='Iwo Kuhn (Projektverantwortlicher)',
    context=(
        'Für den HK-Tracker wird ein modernes, wartbares Single-Page-Application-Framework '
        'benötigt. Der Projektverantwortliche hat keine aktiven Programmierkenntnisse; die '
        'Wahl muss daher gut zu Claude Code (KI-Entwicklungsassistent) passen und '
        'starke Typsicherheit bieten, um KI-generierte Fehler früh zu erkennen.'
    ),
    drivers=[
        'Starke TypeScript-Integration (weniger Laufzeitfehler in KI-generiertem Code)',
        'Vite als Build-Tool: Hot Module Replacement <100 ms, schnelle Iterationszyklen',
        'Grösstmögliches Ökosystem (TanStack Query, React Router, shadcn/ui)',
        'FHNW Styleguide V5 [R54] umsetzbar via Tailwind CSS + Design-Tokens',
        'Claude Code kennt React/TypeScript-Ökosystem am besten → weniger Halluzinationen',
    ],
    options_list=[
        'Option A: React 19 + TypeScript + Vite (gewählt)',
        'Option B: Angular 17 + TypeScript',
        'Option C: Vue 3 + TypeScript + Vite',
    ],
    decision=(
        'Gewählt: Option A — React 19 + TypeScript (strict) + Vite. '
        'React bietet das grösste Ökosystem, hervorragende Claude-Code-Unterstützung '
        'und ermöglicht durch TypeScript strict mode eine hohe Codequalität ohne '
        'manuelle Code-Reviews.'
    ),
    pos_cons=[
        'Ekosystem: TanStack Query v5 (Server-State), React Router v7, shadcn/ui',
        'TypeScript strict: Typsystem fängt KI-generierte Fehler vor Runtime ab',
        'Vite: Build in <500 ms, HMR in <100 ms — kurze Feedback-Loops im SDD-Prozess',
        'FHNW CI umsetzbar: Tailwind + FHNW Design-Tokens (fhnw-navy, fhnw-yellow)',
    ],
    neg_cons=[
        'Kein opinioniertes Routing (React Router als separate Dependency)',
        'State-Management explizit wählen (→ ADR-008: kein Redux, TanStack Query)',
        'Mehr Boilerplate als Vue 3 für einfache Komponenten',
    ],
    options_detail=[
        ('Option A: React 19 + TypeScript + Vite',
         ['Bestes Ökosystem', 'Claude Code support exzellent', 'Vite ultra-schnell'],
         ['Kein built-in Router/State']),
        ('Option B: Angular 17',
         ['Vollständiges Framework (Router, State, DI)', 'Starke Typisierung'],
         ['Hohe Lernkurve', 'Schwergewichtig', 'Claude Code Support schwächer']),
        ('Option C: Vue 3',
         ['Einfache Syntax', 'Vite-nativ'],
         ['Kleineres Ökosystem', 'TypeScript-Integration weniger ausgereift als React']),
    ]
)

ADR_002 = adr(
    title='ADR-002: ASP.NET Core 8 (Clean Architecture) statt Node.js oder Python/FastAPI',
    status='Accepted',
    date='2026-04-01',
    deciders='Iwo Kuhn + FHNW Enterprise Architekt (Entscheid bindend)',
    context=(
        'Der HK-Tracker benötigt ein Backend für die REST-API, EF-Core-Datenbankanbindung '
        'und Azure-Service-Integration. Das ursprüngliche Python/FastAPI-Backend wurde '
        'durch einen FHNW-EA-Entscheid abgelöst: Der .NET-Stack ist FHNW-Standard '
        'und damit Voraussetzung für produktives Azure-Deployment.'
    ),
    drivers=[
        'FHNW Enterprise Architekt: .NET-Stack als verbindlicher Standard',
        'Azure-Integration: Microsoft.Identity.Web, Azure SDK nativ verfügbar',
        'Clean Architecture: HK.Domain / HK.Application / HK.Infrastructure / HK.API',
        'EF Core 8: typsichere Datenbankzugriffe, Migrations-Support',
        'Starke Typisierung: C# reduziert KI-generierte Fehler im Backend',
    ],
    options_list=[
        'Option A: ASP.NET Core 8 + EF Core 8 + Clean Architecture (gewählt)',
        'Option B: Node.js + Express + Prisma',
        'Option C: Python / FastAPI + SQLAlchemy (ursprünglicher Prototyp)',
    ],
    decision=(
        'Gewählt: Option A — ASP.NET Core 8 mit Clean Architecture (4 Projekte: '
        'HK.Domain, HK.Application, HK.Infrastructure, HK.API). '
        'Entscheid war nicht frei wählbar: FHNW Enterprise Architekt hat .NET als '
        'verbindlichen Standard definiert. Die Migration von Python/FastAPI auf .NET '
        'wurde in Phase 2 (April–Mai 2026) vollständig umgesetzt.'
    ),
    pos_cons=[
        'FHNW-EA-konform: Deployment auf Azure App Service ohne Sonderfreigabe',
        'Clean Architecture: klare Schichtentrennung, gut testbar',
        'EF Core 8: Migrations, snake_case JSON-Serialisierung, LINQ-Queries',
        'Microsoft.Identity.Web: MSAL-Integration für Phase 4 (Auth)',
    ],
    neg_cons=[
        'Migration von Python/FastAPI nötig (Phase 2, ~3 Wochen Aufwand)',
        '.NET-Setup komplexer für Claude Code als Python-basierte Backends',
        'Windows-abhängige Toolchain (dotnet CLI, Visual Studio)',
    ],
    options_detail=[
        ('Option A: ASP.NET Core 8',
         ['FHNW-Standard', 'Native Azure-Integration', 'Starke Typisierung'],
         ['Migration von Python nötig']),
        ('Option B: Node.js + Express',
         ['Schnelle Entwicklung', 'JS/TS-Konsistenz mit Frontend'],
         ['Kein FHNW-Standard', 'Schwächere Typsicherheit (ohne TS strict)']),
        ('Option C: Python/FastAPI',
         ['Ursprünglich verwendet', 'Schneller Prototyp'],
         ['Nicht FHNW-Standard', 'Kein Azure SDK nativ', 'Schwächere Typsicherheit']),
    ]
)

ADR_003 = adr(
    title='ADR-003: Azure OpenAI Service statt direktem OpenAI oder On-Premise LLM',
    status='Accepted',
    date='2026-05-01',
    deciders='Iwo Kuhn + FHNW Enterprise Architekt',
    context=(
        'Der HK-Tracker sendet Lernenden-Dokumente an ein LLM zur Bloom-Bewertung '
        '(KI 2, KI 5). Diese Inhalte enthalten indirekt personenbezogene Daten '
        '(Berichte von Lernenden). Die Wahl des KI-Providers hat direkte '
        'datenschutzrechtliche und compliance-technische Konsequenzen nach DSG '
        '(Schweiz), FHNW Datenschutzrichtlinie [R53] und EU AI Act [R52].'
    ),
    drivers=[
        'FHNW Datenschutzrichtlinie §3c + §6: Daten müssen im FHNW-Tenant bleiben',
        'DSG Art. 6 (Zweckbindung): Lernenden-Texte dürfen nicht für KI-Training genutzt werden',
        'EU AI Act (Danner 2026 [R52]): Transparenzpflicht für KI-Interaktionen',
        'EU Data Boundary: Microsoft garantiert Verarbeitung im EU/Schweiz-Raum',
        'FHNW EA: Azure als strategische Cloud-Plattform der FHNW',
    ],
    options_list=[
        'Option A: Azure OpenAI Service (FHNW-Tenant, GPT-4o) — gewählt',
        'Option B: OpenAI direkt (api.openai.com)',
        'Option C: Anthropic Claude API direkt',
        'Option D: On-Premise LLM (Ollama / llama.cpp)',
    ],
    decision=(
        'Gewählt: Option A — Azure OpenAI Service im FHNW-Tenant (GPT-4o Deployment). '
        'Einzig diese Option erfüllt alle datenschutzrechtlichen Anforderungen: '
        'Daten verlassen den FHNW-Azure-Tenant nicht, kein Training auf Kundendaten '
        '(vertragliche Opt-Out-Garantie), EU Data Boundary. '
        'Der Mouseover-Tooltip im UI informiert explizit: '
        '«betrieben im Azure-Tenant der FHNW» (EU AI Act Transparenzpflicht, [R52] Folie 35).'
    ),
    pos_cons=[
        'Datenschutz: Lernenden-Daten verlassen FHNW-Infrastruktur nicht',
        'Kein KI-Training: Microsoft-Vertrag schliesst Training auf Inhaltsdaten aus',
        'EU Data Boundary: Verarbeitung in EU/Schweiz-Region garantiert',
        'Transparenz: Azure-Tenant im UI ausgewiesen (EU AI Act-konform)',
        'Kompatibel mit LiteLLM Gateway (ADR-004) für Provider-Fallback',
    ],
    neg_cons=[
        'Abhängigkeit von FHNW IT für API-Key-Vergabe (verzögert Phase 2)',
        'Höhere Latenz als direkter OpenAI-Aufruf (Azure-Proxy-Overhead, <200 ms)',
        'Vendor Lock-in Microsoft Azure (mitigiert durch LiteLLM Gateway)',
    ],
    options_detail=[
        ('Option A: Azure OpenAI (FHNW-Tenant)',
         ['DSG-konform', 'EU Data Boundary', 'Kein Training', 'FHNW-Standard'],
         ['IT-Abhängigkeit für Key', 'Leicht höhere Latenz']),
        ('Option B: OpenAI direkt',
         ['Einfache Integration', 'Günstiger'],
         ['Daten verlassen FHNW', 'Kein FHNW-Tenant', 'DSG-Risiko']),
        ('Option C: Anthropic Claude API',
         ['Hohe Modellqualität (Claude Sonnet)'],
         ['Kein FHNW-Tenant', 'Kein Azure-Vertrag', 'DSG-Risiko']),
        ('Option D: On-Premise LLM',
         ['Volle Datenkontrolle', 'Keine externen Kosten'],
         ['Performance unzureichend für Echtzeit', 'GPU-Infrastruktur nötig', 'Hoher Betriebsaufwand']),
    ]
)

ADR_004 = adr(
    title='ADR-004: LiteLLM als Provider-Abstraktionsschicht (geplant)',
    status='Proposed',
    date='2026-05-01',
    deciders='Iwo Kuhn',
    context=(
        'Der direkte Azure OpenAI SDK-Aufruf erzeugt eine starke Kopplung an Microsoft. '
        'Ein LLM-Gateway ermöglicht Provider-Unabhängigkeit, Rate-Limit-Handling '
        'und zentrales Usage-Tracking — relevant für die geplante Produktivschaltung.'
    ),
    drivers=[
        'Provider-Unabhängigkeit: Fallback auf Anthropic Claude / andere Provider bei Azure-Ausfall',
        'Rate-Limit-Handling: zentrales Retry-Logic, Queue-Management',
        'Usage-Tracking: Kosten pro Lernenden/AP messbar (vgl. SusAF ökonomisch)',
        'OpenAI-kompatible API: kein Code-Umbau bei Provider-Wechsel',
    ],
    options_list=[
        'Option A: LiteLLM als Self-Hosted Gateway (gewählt, geplant)',
        'Option B: Direkter Azure OpenAI SDK-Aufruf (aktueller Stand)',
        'Option C: Azure API Management als Gateway',
    ],
    decision=(
        'Gewählt: Option A — LiteLLM als self-hosted Gateway (Implementierung in Phase 2). '
        'Aktuell wird der direkte SDK-Aufruf verwendet (Option B) bis '
        'die produktive Azure-Infrastruktur steht. LiteLLM wird bei Phase-2-Deployment integriert.'
    ),
    pos_cons=[
        'Provider-Unabhängigkeit: Fallback zwischen Azure OpenAI / Claude / anderen',
        'Einheitlicher Endpunkt für alle LLM-Calls (OpenAI-API-kompatibel)',
        'Usage-Tracking: Token-Kosten pro Request messbar',
        'Rate-Limit-Handling: automatisches Retry mit Exponential Backoff',
    ],
    neg_cons=[
        'Zusätzliche Infrastrukturkomponente (Betriebsaufwand)',
        'Single Point of Failure wenn Gateway nicht hochverfügbar',
        'Aktuell noch nicht implementiert (Phase 2)',
    ],
    options_detail=[
        ('Option A: LiteLLM Gateway',
         ['Provider-flexibel', 'Usage-Tracking', 'Rate-Limit'],
         ['Infrastrukturaufwand', 'Noch nicht implementiert']),
        ('Option B: Direkter Azure SDK-Aufruf',
         ['Einfach', 'Bereits implementiert', 'Weniger Abhängigkeiten'],
         ['Azure-Lock-in', 'Kein zentrales Rate-Limiting', 'Kein Usage-Tracking']),
        ('Option C: Azure API Management',
         ['Enterprise-tauglich', 'FHNW-Infrastruktur'],
         ['Hohe Kosten', 'Komplex zu konfigurieren', 'FHNW IT-Abhängigkeit']),
    ]
)

ADR_005 = adr(
    title='ADR-005: SQL Server / Azure SQL Database statt PostgreSQL',
    status='Accepted',
    date='2026-04-01',
    deciders='Iwo Kuhn + FHNW Enterprise Architekt (Entscheid bindend)',
    context=(
        'Der HK-Tracker benötigt eine relationale Datenbank für '
        'Lernende, Kompetenzen, Bewertungen, Rotationen und Dokumente. '
        'In der Entwicklungsumgebung läuft SQL Server Express lokal; '
        'in Produktion ist Azure SQL Database vorgesehen.'
    ),
    drivers=[
        'FHNW Enterprise Architekt: SQL Server als Standard-Datenbankplattform',
        'Azure SQL Database: Managed Service, automatische Backups, Skalierung',
        'EF Core 8: native SQL Server-Provider, Migrations-Support',
        'Bestehende FHNW-Lizenzen decken Azure SQL ab',
    ],
    options_list=[
        'Option A: SQL Server Express (Dev) + Azure SQL Database (Prod) — gewählt',
        'Option B: PostgreSQL + pgvector (für spätere Embedding-Suche)',
        'Option C: SQLite (nur für lokale Entwicklung)',
    ],
    decision=(
        'Gewählt: Option A — SQL Server Express lokal, Azure SQL Database in Produktion. '
        'Der Entscheid wurde durch den FHNW Enterprise Architekten vorgegeben. '
        'Für die geplante Embedding-Suche (KI 3) wäre PostgreSQL + pgvector '
        'technisch besser geeignet; die FHNW-EA-Vorgabe hat jedoch Vorrang.'
    ),
    pos_cons=[
        'FHNW-EA-konform: kein Sonderprozess für Deployment-Freigabe',
        'Azure SQL Database: Managed Service, automatisches Backup, Monitoring via App Insights',
        'EF Core 8 + SQL Server: battle-tested, exzellente TypeScript/C#-Integration',
        'Lokale Dev-Umgebung mit SQL Server Express kostenlos',
    ],
    neg_cons=[
        'Embedding-Suche (KI 3, geplant): pgvector nicht nativ → Azure Cognitive Search als Alternative',
        'Vendor Lock-in Microsoft (langfristig)',
        'SQL Server Express: max. 10 GB Datenbankgrösse (für Prototyp ausreichend)',
    ],
    options_detail=[
        ('Option A: SQL Server / Azure SQL',
         ['FHNW-Standard', 'EF Core 8 nativ', 'Azure Managed Service'],
         ['Kein pgvector', 'Vendor Lock-in']),
        ('Option B: PostgreSQL + pgvector',
         ['Optimal für Embedding-Suche (KI 3)', 'Open Source', 'pgvector nativ'],
         ['Nicht FHNW-EA-Standard', 'Azure Deployment aufwendiger']),
        ('Option C: SQLite',
         ['Zero-Config für lokale Entwicklung'],
         ['Nicht produktionstauglich', 'Kein Concurrent-Write-Support']),
    ]
)

ADR_006 = adr(
    title='ADR-006: Claude Code + SDD als alleinige Entwicklungsmethodik',
    status='Accepted',
    date='2026-03-01',
    deciders='Iwo Kuhn',
    context=(
        'Der Projektverantwortliche verfügt über kein aktives Programmier-Knowhow '
        '(letzte Entwicklungstätigkeit ~20 Jahre zurück). Die App kann nur entstehen, '
        'wenn KI die vollständige Implementierung übernimmt. '
        'Dies ist keine Einschränkung, sondern das Kernargument der Arbeit: '
        'KI als Enabler — «sine qua non» (vgl. Kap. 2.2, KI 1).'
    ),
    drivers=[
        'Sine-qua-non: ohne Claude Code gibt es kein Produkt',
        'SDD-Prinzip (Tag 01 CAS AI-SE): Spezifikation vor Code — Mockup/Verbal → KI implementiert',
        'FHNW erstattet Claude Pro-Abo vollständig (~CHF 20/Monat)',
        'CLAUDE.md + Memory-System: persistenter Projektkontext über Sitzungen',
        'TypeScript strict + ESLint pre-commit: Qualitätssicherung ohne manuelle Reviews',
    ],
    options_list=[
        'Option A: Claude Code (Anthropic) mit SDD-Ansatz — gewählt',
        'Option B: Outsourcing an externen Entwickler',
        'Option C: Traditionelle Eigenentwicklung mit Pair-Programming',
        'Option D: GitHub Copilot / Cursor als Inline-KI-Assistent',
    ],
    decision=(
        'Gewählt: Option A — Claude Code als alleiniger Entwicklungspartner mit SDD-Methodik. '
        'Jedes Feature folgt dem 3-Schritt-Prozess: (1) Spezifikation '
        '(PPTX-Mockup oder verbale Beschreibung), (2) Implementierung durch Claude Code, '
        '(3) Konversationelle Optimierung im Browser (3–15 Iterationen). '
        'Das Modell claude-sonnet-4-6 wird über Claude.ai Pro eingesetzt.'
    ),
    pos_cons=[
        'Ermöglicht Full-Stack-Entwicklung (React + ASP.NET Core 8) ohne Coding-Kenntnisse',
        'PPTX-Mockups als Spezifikationsformat auch für Nicht-Programmierer geeignet',
        'Konversationelle Optimierung: schnelle Feedback-Loops (3–15 Iterationen pro Feature)',
        'CLAUDE.md + Memory: persistenter Kontext ermöglicht konsistente Multi-Session-Entwicklung',
        'Kosten: CHF ~20/Monat, vollständig von FHNW erstattet',
    ],
    neg_cons=[
        'Risiko Halluzinationen: mitigiert durch TypeScript strict mode + ESLint pre-commit',
        'Kein unabhängiges Code-Review: mitigiert durch Browser-Tests nach jedem Feature',
        'Kontextfenster-Grenzen bei sehr langen Sessions (mitigiert durch CLAUDE.md)',
        'Abhängigkeit von Anthropic-Dienstverfügbarkeit',
    ],
    options_detail=[
        ('Option A: Claude Code + SDD',
         ['Sine-qua-non Enabler', 'Iterativ', 'Günstig (~CHF 20/Mt.)', 'Kein externer Aufwand'],
         ['Halluzinationsrisiko', 'Kein unabhängiges Review']),
        ('Option B: Externer Entwickler',
         ['Professionelle Qualität', 'Unabhängiges Review'],
         ['Hohe Kosten (>CHF 10 000)', 'Wissenstransfer-Problem', 'Abhängigkeit']),
        ('Option C: Pair-Programming',
         ['Direktes Feedback', 'Wissensaufbau'],
         ['Coding-Kenntnisse nötig', 'Kein Programmier-Knowhow vorhanden']),
        ('Option D: GitHub Copilot / Cursor',
         ['IDE-integriert', 'Günstig'],
         ['Nur Inline-Completion, kein vollständiger Code-Agent', 'Kein Projektgedächtnis']),
    ]
)

ADR_007 = adr(
    title='ADR-007: Merge-Strategie KI → Human (nur leere Felder befüllen)',
    status='Accepted',
    date='2026-05-15',
    deciders='Iwo Kuhn',
    context=(
        'Wenn die KI eine Bloom-Bewertung vorschlägt, stellt sich die Frage: '
        'Überschreibt die KI bestehende manuelle Einträge des Berufsbildners, '
        'oder befüllt sie nur leere Felder? Glickman & Sharot (2025, [R51]) '
        'zeigen, dass wiederholte Human-AI-Interaktionen menschliche Urteile '
        'kumulativ verzerren ("Schneeballeffekt", 53 % → 65 % Bias-Amplifikation). '
        'Die Merge-Strategie ist die primäre technische Gegenmassnahme.'
    ),
    drivers=[
        'Glickman & Sharot 2025 [R51]: Menschliche Urteile dürfen nicht durch KI-Overwrite verfälscht werden',
        'Human-in-the-Loop (Kap. 2.2 KI5): Berufsbildner trifft finale Entscheidung',
        'NFA-S4 (SusAF): KI-Vorschläge als überarbeitbare Entwürfe kennzeichnen',
        'Vertrauen: Berufsbildner muss jederzeit wissen, was er selbst entschieden hat',
        'Danner 2026 [R52]: Verstärkungseffekte durch Feedback Loops als ethische Herausforderung',
    ],
    options_list=[
        'Option A: KI befüllt nur leere Felder (Merge-Strategie) — gewählt',
        'Option B: KI überschreibt immer (Full-Overwrite)',
        'Option C: KI überschreibt mit Bestätigungsdialog bei Konflikten',
    ],
    decision=(
        'Gewählt: Option A — Merge-Strategie: die KI (AiEvaluationService.cs) '
        'befüllt ausschliesslich Felder, die noch keinen manuellen Eintrag haben. '
        'Bestehende Bloom-Bewertungen des Berufsbildners bleiben unverändert. '
        'Zusätzlich: konservativer System-Prompt (bei Unsicherheit niedrigere Bloom-Stufe), '
        'um systematische Über-Bewertung zu vermeiden.'
    ),
    pos_cons=[
        'Verhindert Überschreiben manuelle Berufsbildner-Entscheide',
        'Reduziert Human-AI Feedback Loop Risiko (Glickman & Sharot 2025 [R51])',
        'Transparenz: Berufsbildner weiss immer, was KI vs. was er selbst entschieden hat',
        'Konservativer Prompt: minimiert systematische Über-Bewertung',
        'Einfache Implementierung: ein if-check pro Feld in AiEvaluationService.cs',
    ],
    neg_cons=[
        'KI kann keine Korrekturen vorschlagen wenn Feld bereits befüllt',
        'Lernende könnten falsche manuelle Einträge nicht durch KI korrigieren lassen',
        'Berufsbildner muss Feld manuell leeren wenn er KI-Vorschlag für befülltes Feld will',
    ],
    options_detail=[
        ('Option A: Nur leere Felder (Merge)',
         ['Feedback-Loop-sicher', 'Menschliche Kontrolle erhalten', 'Einfach'],
         ['Keine KI-Korrekturen bei bestehenden Einträgen']),
        ('Option B: Full-Overwrite',
         ['Immer neuester KI-Vorschlag'],
         ['Zerstört manuelle Entscheide', 'Hohes Feedback-Loop-Risiko', 'Verlust menschlicher Urteile']),
        ('Option C: Overwrite mit Bestätigungsdialog',
         ['Flexibel'],
         ['Decision Fatigue (vgl. [R07] +33%)', 'Komplex zu implementieren', 'UX-Overhead']),
    ]
)

# =========================================================================
# ADR INDEX (für 3.2 und 3.1 TODO)
# =========================================================================
ADR_INDEX_ITEMS = [
    ('ADR-001: React 19 + TypeScript + Vite statt Angular/Vue — Accepted (2026-03)', LB),
    ('ADR-002: ASP.NET Core 8 (Clean Architecture) statt Node.js/Python — Accepted (2026-04)', LB),
    ('ADR-003: Azure OpenAI statt direktem OpenAI / On-Premise LLM — Accepted (2026-05)', LB),
    ('ADR-004: LiteLLM als Provider-Gateway — Proposed (Phase 2)', LB),
    ('ADR-005: SQL Server / Azure SQL statt PostgreSQL — Accepted (2026-04)', LB),
    ('ADR-006: Claude Code + SDD als Entwicklungsmethodik — Accepted (2026-03)', LB),
    ('ADR-007: Merge-Strategie KI → Human (nur leere Felder) — Accepted (2026-05)', LB),
    ('Vollständige ADRs im MADR v4-Format: Anhang C', (LB, 'italic')),
]

# Flatten all ADR content
ALL_ADRS = (
    ADR_001 + [('', NRM)]
    + ADR_002 + [('', NRM)]
    + ADR_003 + [('', NRM)]
    + ADR_004 + [('', NRM)]
    + ADR_005 + [('', NRM)]
    + ADR_006 + [('', NRM)]
    + ADR_007
)


def main():
    doc = Document(DOCX_PATH)
    paras = doc.paragraphs

    # ---- Find anchors ----
    anhang_c_para = None
    anhang_d_para = None
    todo_azure_para = None    # para 225: [TODO: ADR erstellen Azure OpenAI]
    todo_index_para = None    # para 357: [TODO: ADR-Index erstellen]
    adr_geplant_para = None   # para 355: 'ADRs mit MADR v4-Format (geplant)'
    placeholder_para = None   # para 848: Platzhalter: ADR-001 bis...

    for para in paras:
        t = para.text.strip()
        s = para.style.name
        if ('berschrift1' in s or 'Heading 1' in s) and 'Anhang C' in t:
            anhang_c_para = para
        if ('berschrift1' in s or 'Heading 1' in s) and 'Anhang D' in t:
            anhang_d_para = para
        if '[TODO: ADR erstellen' in t and 'Azure OpenAI' in t:
            todo_azure_para = para
        if '[TODO: ADR-Index erstellen' in t:
            todo_index_para = para
        if 'ADRs mit MADR v4-Format' in t and 'geplant' in t:
            adr_geplant_para = para
        if 'Platzhalter: ADR-001' in t:
            placeholder_para = para

    if anhang_c_para is None:
        print("ERROR: Anhang C heading not found"); sys.exit(1)
    print(f"Anhang C: para found: {anhang_c_para.text[:60]}")
    print(f"Anhang D: {'found' if anhang_d_para else 'NOT FOUND'}")
    print(f"TODO Azure: {'found' if todo_azure_para else 'NOT FOUND'}")
    print(f"TODO Index: {'found' if todo_index_para else 'NOT FOUND'}")
    print(f"'geplant' bullet: {'found' if adr_geplant_para else 'NOT FOUND'}")

    # =========================================================================
    # 1. Insert ADR content into Anhang C (before Anhang D)
    # =========================================================================
    anchor_p = (anhang_d_para or placeholder_para or anhang_c_para)._p
    if anchor_p is (placeholder_para or anhang_c_para)._p:
        # Insert after Anhang C heading
        for text, style in reversed(ALL_ADRS):
            if isinstance(style, tuple):
                st, *flags = style
                bold = 'bold' in flags; italic = 'italic' in flags
            else:
                st = style; bold = italic = False
            if text:
                anhang_c_para._p.addnext(make_para(text, st, bold=bold, italic=italic))
    else:
        # Insert before Anhang D
        for text, style in ALL_ADRS:
            if not text:
                continue
            if isinstance(style, tuple):
                st, *flags = style
                bold = 'bold' in flags; italic = 'italic' in flags
            else:
                st = style; bold = italic = False
            anchor_p.addprevious(make_para(text, st, bold=bold, italic=italic))

    print(f"OK: Inserted {len([x for x in ALL_ADRS if x[0]])} paragraphs (7 ADRs) into Anhang C")

    # =========================================================================
    # 2. Remove placeholder paragraph in Anhang C
    # =========================================================================
    if placeholder_para:
        placeholder_para._p.getparent().remove(placeholder_para._p)
        print("OK: Removed placeholder paragraph")

    # =========================================================================
    # 3. Replace [TODO: ADR erstellen Azure OpenAI] with reference
    # =========================================================================
    if todo_azure_para:
        ok = fix_text(
            todo_azure_para,
            '[TODO: ADR erstellen',
            'Architekturentscheid Azure OpenAI: siehe ADR-003 (Anhang C) — '
            'Status: Accepted. Datenschutz (DSG [R53], EU Data Boundary), '
            'FHNW-Tenant-Konformität und EU AI Act Transparenzpflicht [R52] '
            'begründen die Wahl gegenüber direktem OpenAI oder On-Premise LLM.'
        )
        print(f"OK: Azure TODO replaced: {ok}")

    # =========================================================================
    # 4. Replace [TODO: ADR-Index erstellen] with proper index
    # =========================================================================
    if todo_index_para:
        ok = fix_text(
            todo_index_para,
            '[TODO: ADR-Index erstellen',
            'ADR-Index (arc42 Kapitel 9) — vollständige ADRs im MADR v4-Format in Anhang C:'
        )
        print(f"OK: Index TODO replaced with header: {ok}")
        # Insert index bullets after this paragraph
        ref_p = todo_index_para._p
        for text, style in reversed(ADR_INDEX_ITEMS):
            if isinstance(style, tuple):
                st, *flags = style
                italic = 'italic' in flags
            else:
                st = style; italic = False
            ref_p.addnext(make_para(text, st, italic=italic))
        print(f"OK: Inserted {len(ADR_INDEX_ITEMS)} ADR index bullets")

    # =========================================================================
    # 5. Update 'ADRs mit MADR v4-Format (geplant)' → implemented
    # =========================================================================
    if adr_geplant_para:
        ok = fix_text(
            adr_geplant_para,
            'ADRs mit MADR v4-Format (geplant)',
            'ADRs mit MADR v4-Format (7 ADRs implementiert, siehe Anhang C)'
        )
        print(f"OK: 'geplant' bullet updated: {ok}")

    # =========================================================================
    # Save
    # =========================================================================
    out = DOCX_PATH.replace('.docx', '_ADR_DRAFT.docx')
    doc.save(out)
    print(f"\nSaved DRAFT: {out}")
    print("=> Close Word, then rename/copy this file over the original.")
    adr_count = len([x for x in ALL_ADRS if x[0] and x[1] == H2])
    print(f"ADRs created: {adr_count} (ADR-001 to ADR-007)")


if __name__ == '__main__':
    main()
