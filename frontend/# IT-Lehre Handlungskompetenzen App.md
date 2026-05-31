# IT-Lehre Handlungskompetenzen App – Projektkontext für Claude Code

## Projektübersicht

App zur Erfassung und Verfolgung von Handlungskompetenzen für Informatik-Lernende (EFZ) gemäss
Bildungsplan 88611. Bewertet Leistungsziele nach Bloom-Taxonomie (K0–K6), visualisiert
Lernfortschritt, exportiert PDF-Berichte und plant Ausbildungsplatz-Rotationen (Gantt).

**Aktueller Stand:** Migration von Phase-2-Prototyp (Python/FastAPI + React ohne TS) auf
Ziel-Techstack. Konzeptdokument: `Konzept_HK-App_Umsetzung_v4.docx`

---

## Ziel-Techstack (produktive Version)

### Frontend
| Paket | Zweck |
|---|---|
| React 18 + TypeScript | UI-Framework |
| Vite | Build-Tool / Dev-Server |
| React Router (react-router-dom) | Clientseitiges Routing |
| TanStack Query | Server-State, Caching, API-Calls |
| Tailwind CSS | Styling (FHNW CI, siehe unten) |
| @azure/msal-browser + @azure/msal-react | OIDC / Microsoft Entra ID Auth |
| @dnd-kit/core + @dnd-kit/utilities | Drag & Drop (Gantt-Rotationsplanung, Phase 3b) |
| Axios | HTTP-Client mit Bearer-Token-Interceptor |

### Backend
| Paket | Zweck |
|---|---|
| ASP.NET Core 8 Web API (C#) | REST API |
| Entity Framework Core 8 | ORM, Code-First Migrations |
| Microsoft.Identity.Web | JWT-Validierung, Policy-based Auth |
| AutoMapper | DTO-Mapping |
| FluentValidation | Eingabevalidierung |
| Serilog | Logging |
| xUnit | Tests |

### Infrastruktur
- Datenbank: Microsoft SQL Server (SQLEXPRESS)
- Identity Provider: Microsoft Entra ID (OIDC)

---

## FHNW Corporate Identity – Tailwind-Konfiguration

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        'fhnw-navy':   '#003366',
        'fhnw-yellow': '#FDE70E',
        'fhnw-light':  '#D5E8F0',
      }
    }
  }
};
```

Diese Tokens immer verwenden statt Hex-Werten direkt im JSX/TSX.

---

## Projektstruktur (Clean Architecture Backend)

```
HK.API/          – Controller, Middleware, Swagger, Auth-Policies
HK.Application/  – Use Cases, DTOs, Service-Interfaces
HK.Domain/       – Entitäten, Domain-Logik, Repository-Interfaces
HK.Infrastructure/ – EF Core DbContext, Repositories, Seed-Daten
HK.Tests/        – Unit- und Integrationstests
```

---

## Authentifizierung und Rollen

- Zwei Rollen via Entra ID App Roles: `Berufsbildner`, `Lernender`
- `roles`-Claim ist direkt im JWT enthalten
- Frontend: `AuthGuard` (Login-Redirect), `RoleGuard` (Routen/Navigation)
- Backend: Policy-based Auth via `Microsoft.Identity.Web`
- OIDC-Linking: `Users.ExternalId` = AAD ObjectId (`oid`-Claim)

```ts
// authConfig.ts (Platzhalter – echte IDs in .env)
export const msalConfig = {
  auth: {
    clientId:    process.env.VITE_CLIENT_ID,
    authority:   `https://login.microsoftonline.com/${process.env.VITE_TENANT_ID}`,
    redirectUri: 'http://localhost:5173'
  }
};
export const loginRequest = {
  scopes: [`api://${process.env.VITE_CLIENT_ID}/access_as_user`]
};
```

---

## Wichtige Frontend-Komponenten

| Komponente | Beschreibung |
|---|---|
| `AuthGuard` | Leitet nicht angemeldete Nutzer zum Login um |
| `RoleGuard` | Versteckt Routen/Nav je nach Rolle |
| `App.tsx / AppContext` | Router, globaler State (currentUser, Rolle, aktiver AP) |
| `Header` | FHNW-Header, Lernenden-Auswahl (nur BB), AP-Badge |
| `Overview, AreaView, GoalRow` | Kernkomponenten Kompetenzbewertung |
| `UserModal` | Lernenden anlegen/bearbeiten + E-Mail für OIDC-Linking |
| `RotationModal` | AP-Wechsel: AP-Auswahl, Von-Datum, opt. Bis-Datum |
| `APFilter` | Filter-Chips Lernendenliste nach AP (nur BB) |
| `APToggle` | Toggle «Nur AP-relevante Bereiche» in AreaView/Overview |
| `RotationsplanungView` | Gantt-Hauptansicht (Phase 3b) |
| `GanttBar` | Einzelner Gantt-Balken mit Drag, Resize, Delete |
| `useRotationGantt` | Custom Hook: Koordinatensystem, Zoom, Drag-State |
| `useConflictDetection` | Custom Hook: AP-Doppelbelegung → gelber Rahmen (#FDE70E) |

---

## Datenmodell (Kerntabellen)

```
User            – Id, Name, Specialty, StartDate, ExternalId (AAD oid), Email
GoalEntry       – Id, UserId, GoalId, Level (0–6), Comment, UpdatedAt
Competency      – GoalId, AreaCode, Title, MaxLevel, Specialty
Area            – Code (A–H), Name, Color
Ausbildungsplatz – Code (BLB/SDM/SWE/...), Bezeichnung, AbLehrjahr
AusbildungsplatzHKBereich – APCode, AreaCode, IsPrimary  [EF Core Seed]
UserRotation    – UserId, APCode, Von (DATE), Bis (DATE?)  -- Bis=null = aktiv
```

---

## API-Endpunkte (Auswahl)

```
GET/POST        /api/v1/users
GET/PUT/DELETE  /api/v1/users/{id}
GET/PUT         /api/v1/users/{id}/goals/{goalId}
GET/POST        /api/v1/users/{id}/rotations
GET             /api/v1/me                        ← OIDC-Linking
GET             /api/v1/ausbildungsplaetze
GET/PUT         /api/v1/ausbildungsplaetze/{code}/bereiche
GET/PUT         /api/v1/rotationsplanung          ← Gantt (nur BB)
```

Alle Endpunkte verlangen Bearer Token. Lernende sehen nur eigene Daten (UserId-Filter im Backend).

---

## Migrations- und Integrationsreihenfolge

**Wichtig:** Reihenfolge einhalten — Gantt NICHT vor Stack-Migration implementieren.

### Phase 1 – Fundament (aktuell)
1. Vite + React + TypeScript Projekt aufsetzen
2. Tailwind CSS + FHNW-Tokens konfigurieren
3. MSAL-React einrichten (zuerst Dummy-Config, echte IDs später)
4. TanStack Query + React Router einbinden
5. Bestehende JSX-Komponenten → TSX portieren und typisieren

### Phase 2 – Kernfunktionen
- REST-API Endpunkte, Datenisolation, OIDC-Linking
- Alle Kern-Komponenten (Overview, AreaView, GoalRow, UserModal)
- PDF-Export serverseitig

### Phase 3 – Ausbildungsplatzverwaltung
- EF Core Migrations, Seed-Daten (16 Ausbildungsplätze)
- RotationModal, AP-Badge, APFilter, APToggle

### Phase 3b – Rotationsplanung Gantt
- @dnd-kit/core installieren
- useRotationGantt, useConflictDetection, GanttBar, RotationsplanungView
- Referenz-Implementierung: `Rotationsplanung_Mockup.html` (vollständig funktionierender HTML-Prototyp)

### Phase 4 – KI-Integration
- OpenAI API oder lokales Modell für Kompetenzstufen-Empfehlungen

---

## Gantt-Koordinatensystem (Referenz für Phase 3b)

```ts
// Monatsindex: Monate seit Lehrstart (August 2024 = 0)
const mo = (year: number, month: number) => (year - 2024) * 12 + (month - 8);

// Column Width je Zoom-Stufe
const CW = () => zoom === 'sem' ? 104 : 38; // px

// Monatsindex → Pixel-X
const mToX = (m: number) => zoom === 'sem' ? (m / 6) * CW() : m * CW();

// Pixel-Delta → Monats-Delta
const dxToMo = (dx: number) =>
  zoom === 'sem' ? Math.round(dx / CW() * 6) : Math.round(dx / CW());

// Balken-Geometrie: v = erster Monat (inkl.), b = letzter Monat (inkl.)
// Rechte Kante = mToX(b+1) → keine Lücke zwischen Nachbarbalken
const barGeom = (rot: Rotation) => ({
  x: mToX(rot.v),
  w: Math.max(mToX(rot.b + 1) - mToX(rot.v), 18)
});

// Konflikte: gleicher AP, gleicher Monat, mehrere Lernende → #FDE70E Rahmen
```

---

## Bekannte Entscheide / Nicht nochmal diskutieren

- **Kein Redux** – TanStack Query reicht für Server-State
- **Kein eigenes Session-Management** – MSAL übernimmt alles
- **Kein Einzelziel-Mapping** für AP-HK – Bereich-Ebene (A–H) ist bewusst «etwas grösser gefasst»
- **Gantt mit @dnd-kit**, nicht mit nativer HTML5 Drag API (Barrierefreiheit, Touch-Support)
- **Stack-Migration vor Gantt-Integration** (verhindert Doppelmigration der komplexen Komponente)