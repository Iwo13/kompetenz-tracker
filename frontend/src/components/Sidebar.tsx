import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { getAreaProgress, getAPLernProgress, SPECIALTY_LABEL } from '../utils';
import type { Area, Ausbildungsplatz } from '../types';

function calcApCoverage(
  ap: Ausbildungsplatz | null,
  bildungsplan: string,
  allHks: string[]
): { covered: number; total: number } {
  if (!ap?.hk_coverage?.[bildungsplan]) return { covered: 0, total: allHks.length };
  const coverage = ap.hk_coverage[bildungsplan];
  const covered  = allHks.filter(id => coverage[id] === 'primary').length;
  return { covered, total: allHks.length };
}

interface SidebarProps {
  isOpen:  boolean;
  onClose: () => void;
}

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  const { currentUser, areas, role, currentAP, areasInformatiker, areasIct, ausbildungsplaetze } = useApp();
  const navigate  = useNavigate();
  const location  = useLocation();
  const isOverview      = location.pathname === '/overview' || location.pathname === '/';
  const isLernenderView = isOverview || location.pathname.startsWith('/area/');
  const isAPView        = location.pathname.startsWith('/ap-abdeckung');
  const isBB = role === 'berufsbildner';


  useEffect(() => { onClose(); }, [location.pathname]);

  function go(path: string) { navigate(path); onClose(); }

  const ictHks = (areasIct ?? []).flatMap((a: Area) => a.subComps.map(sc => sc.id));

  function getHksForFachrichtung(fachrichtung: string) {
    return (areasInformatiker ?? [])
      .filter((a: Area) => a.specialty === 'both' || a.specialty === fachrichtung)
      .flatMap((a: Area) => a.subComps.map(sc => sc.id));
  }

  return (
    <>
      <aside className={`sidebar${isOpen ? ' open' : ''}`}>

        <div className="sidebar-brand">
          <div className="sidebar-brand-title">Handlungskompetenz-<br />Tracker</div>
          <div className="sidebar-brand-sub">
            {isAPView
              ? (currentAP ? `${currentAP.code} – ${currentAP.name}` : 'Ausbildungsplätze')
              : currentUser
                ? (SPECIALTY_LABEL[currentUser.specialty] ?? currentUser.specialty)
                : 'Informatik EFZ'}
          </div>
        </div>

        {/* Navigation */}
        {(() => {
          const overviewPath   = isAPView ? '/ap-abdeckung' : '/overview';
          const overviewActive = isAPView ? location.pathname === '/ap-abdeckung' : isOverview;
          return (
            <div className="sidebar-section">
              <div className="sidebar-section-title">Navigation</div>
              <button className={`sidebar-item${overviewActive ? ' active' : ''}`}
                onClick={() => go(overviewPath)}>
                <span className="item-id">
                  <img src="/IconBuch.png" style={{ height: '16px', width: '16px', objectFit: 'contain', display: 'block' }} alt="" />
                </span>
                <span className="item-name">Übersicht</span>
              </button>
            </div>
          );
        })()}

        {/* Kompetenzbereiche */}
        {!isAPView && areas.length > 0 && (
          <div className="sidebar-section">
            <div className="sidebar-section-title">Erlangte Kompetenzen</div>
            {areas.map(area => {
              const prog     = getAreaProgress(area, currentUser?.goals);
              const isActive = location.pathname === `/area/${area.id}`;
              return (
                <button key={area.id}
                  className={`sidebar-item${isActive ? ' active' : ''}`}
                  onClick={() => go(`/area/${area.id}`)}>
                  <span className="item-id">{area.id.toUpperCase()}</span>
                  <span className="item-name">{area.name}</span>
                  <span className={`item-badge${prog.pct === 100 ? ' done' : ''}`}>{prog.pct}%</span>
                </button>
              );
            })}
          </div>
        )}

        {/* Kompetenzabdeckung Ausbildungsplätze */}
        {isAPView && currentAP && (
          <div className="sidebar-section">
            <div className="sidebar-section-title">Kompetenzabdeckung Ausbildungsplätze</div>
            <div className="sidebar-bp-group">
              <div className="sidebar-bp-label">Informatiker/in</div>
              {[
                { fach: 'platform', label: 'Plattform' },
                { fach: 'app',      label: 'Appli' },
              ].map(({ fach, label }) => {
                const hks = getHksForFachrichtung(fach);
                const { covered, total } = calcApCoverage(currentAP, 'informatiker', hks);
                const pct  = total ? Math.round(covered / total * 100) : 0;
                const path = `/ap-abdeckung/informatiker-${fach}`;
                return (
                  <button key={fach}
                    className={`sidebar-item sidebar-item-sub${location.pathname === path ? ' active' : ''}`}
                    onClick={() => go(path)}>
                    <span className="item-name">- {label}</span>
                    <span className={`item-badge${pct === 100 ? ' done' : ''}`}>{pct}%</span>
                  </button>
                );
              })}
            </div>
            {(() => {
              const { covered, total } = calcApCoverage(currentAP, 'ict-fachmann', ictHks);
              const pct  = total ? Math.round(covered / total * 100) : 0;
              const path = '/ap-abdeckung/ict-fachmann';
              return (
                <button className={`sidebar-item${location.pathname === path ? ' active' : ''}`}
                  onClick={() => go(path)}>
                  <span className="item-name">ICT-Fachmann</span>
                  <span className={`item-badge${pct === 100 ? ' done' : ''}`}>{pct}%</span>
                </button>
              );
            })()}
          </div>
        )}

        {/* Ausbildungsplätze des aktuellen Lernenden */}
        {!isAPView && currentUser && currentUser.rotations?.length > 0 && (() => {
          const bildungsplan = currentUser.specialty === 'ict-fachmann' ? 'ict-fachmann' : 'informatiker';
          const uniqueApCodes = [...new Set(currentUser.rotations.map(r => r.ap_code))];
          const learnerAPs = uniqueApCodes
            .map(code => ausbildungsplaetze.find(ap => ap.code === code))
            .filter((ap): ap is Ausbildungsplatz => !!ap);
          if (learnerAPs.length === 0) return null;
          return (
            <div className="sidebar-section">
              <div className="sidebar-section-title">Ausbildungsplätze</div>
              {learnerAPs.map(ap => {
                const apCov = (ap.hk_coverage?.[bildungsplan] ?? {}) as Record<string, string>;
                const prog  = getAPLernProgress(apCov, areas, currentUser.goals);
                const path  = `/ap-view/${ap.code}`;
                const isActive = location.pathname === path;
                return (
                  <button key={ap.code}
                    className={`sidebar-item${isActive ? ' active' : ''}`}
                    onClick={() => go(path)}>
                    <span className="item-name" style={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                      <span style={{ fontWeight: 800, fontSize: '0.8rem' }}>{ap.code}</span>
                      <span style={{ fontSize: '0.72rem', opacity: 0.65 }}>{ap.name}</span>
                    </span>
                    <span className={`item-badge${prog.pct === 100 ? ' done' : ''}`}>{prog.pct}%</span>
                  </button>
                );
              })}
            </div>
          );
        })()}

        {/* Administration (nur Berufsbildner) */}
        {isBB && (
          <div className="sidebar-section">
            <div className="sidebar-section-title">Administration</div>

            {/* Lernende */}
            <button className={`sidebar-item${isLernenderView ? ' active' : ''}`}
              onClick={() => go('/overview')}>
              <span className="item-id sidebar-admin-icon">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 12c2.67 0 8 1.34 8 4v2H4v-2c0-2.66 5.33-4 8-4zm0-2a4 4 0 1 0 0-8 4 4 0 0 0 0 8z" />
                </svg>
              </span>
              <span className="item-name">Lernende</span>
            </button>

            {/* Ausbildungsplätze */}
            <button className={`sidebar-item${isAPView ? ' active' : ''}`}
              onClick={() => go('/ap-abdeckung')}>
              <span className="item-id sidebar-admin-icon">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 7V3H2v18h20V7H12zM6 19H4v-2h2v2zm0-4H4v-2h2v2zm0-4H4V9h2v2zm0-4H4V5h2v2zm4 12H8v-2h2v2zm0-4H8v-2h2v2zm0-4H8V9h2v2zm0-4H8V5h2v2zm10 12h-8v-2h2v-2h-2v-2h2v-2h-2V9h8v10zm-2-8h-2v2h2v-2zm0 4h-2v2h2v-2z" />
                </svg>
              </span>
              <span className="item-name">Ausbildungsplätze</span>
            </button>

            {/* Rotationsplanung (Gantt-Ansicht) */}
            <button
              className={`sidebar-item${location.pathname === '/rotationsplanung' ? ' active' : ''}`}
              onClick={() => go('/rotationsplanung')}
            >
              <span className="item-id sidebar-admin-icon">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M3 3h18v2H3V3zm0 4h12v2H3V7zm0 4h18v2H3v-2zm0 4h12v2H3v-2zm0 4h18v2H3v-2z"/>
                </svg>
              </span>
              <span className="item-name">Rotationsplanung</span>
            </button>

            {/* Rotationen eines Lernenden verwalten */}
          </div>
        )}
      </aside>
    </>
  );
}
