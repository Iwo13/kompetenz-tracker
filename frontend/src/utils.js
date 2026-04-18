export const BLOOM = ['–', 'Wissen', 'Verstehen', 'Anwenden', 'Analysieren', 'Synthese', 'Beurteilen'];

export const SPECIALTY_LABEL = {
  platform:      'Plattformentwicklung',
  app:           'Applikationsentwicklung',
  'ict-fachmann': 'ICT-Fachmann/-frau EFZ',
};

export function getInitials(name) {
  return name.split(' ').map(p => p[0] || '').join('').substring(0, 2).toUpperCase();
}

export function getLehrjahrInfo(user) {
  const lehrDauer = user?.specialty === 'ict-fachmann' ? 3 : 4;
  if (!user?.startDate) return { current: 1, pct: 0, yearPcts: Array(lehrDauer).fill(0), lehrDauer };
  const start = new Date(user.startDate);
  const now = new Date();
  const totalDays = lehrDauer * 365.25;
  const elapsed = Math.max(0, Math.min((now - start) / 86400000, totalDays));
  const current = Math.min(lehrDauer, Math.floor(elapsed / 365.25) + 1);
  const yearPcts = Array.from({ length: lehrDauer }, (_, i) => {
    const ys = i * 365.25, ye = (i + 1) * 365.25;
    if (elapsed <= ys) return 0;
    if (elapsed >= ye) return 100;
    return Math.round((elapsed - ys) / 365.25 * 100);
  });
  return { current, pct: Math.round(elapsed / totalDays * 100), yearPcts, lehrDauer };
}

export function getAreaProgress(area, userGoals = {}) {
  const goals = area.subComps.flatMap(sc => sc.goals);
  const achieved = goals.filter(g => (userGoals[g.id]?.level ?? 0) >= g.max).length;
  return { achieved, total: goals.length, pct: goals.length ? Math.round(achieved / goals.length * 100) : 0 };
}

export function getOverallProgress(areas, userGoals = {}) {
  const all = areas.flatMap(a => a.subComps.flatMap(sc => sc.goals));
  const achieved = all.filter(g => (userGoals[g.id]?.level ?? 0) >= g.max).length;
  return { achieved, total: all.length, pct: all.length ? Math.round(achieved / all.length * 100) : 0 };
}
