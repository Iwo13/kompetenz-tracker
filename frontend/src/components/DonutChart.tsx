interface Segment {
  value:  number;
  color:  string;
  label?: string;
}

interface DonutChartProps {
  segments:  Segment[];
  centerPct: number;
  size?:     number;
}

export default function DonutChart({ segments, centerPct, size = 180 }: DonutChartProps) {
  const cx = size / 2;
  const cy = size / 2;
  const r  = size * 0.42;
  const strokeW     = size * 0.17;
  const circumference = 2 * Math.PI * r;

  const total = segments.reduce((s, seg) => s + seg.value, 0);

  let offset = 0;
  const slices = segments.map(seg => {
    const dash  = total > 0 ? (seg.value / total) * circumference : 0;
    const slice = { ...seg, dash, offset };
    offset += dash;
    return slice;
  });

  if (total === 0) {
    return (
      <div className="donut-wrap" style={{ width: size, height: size }}>
        <svg width={size} height={size}>
          <circle cx={cx} cy={cy} r={r} fill="none" stroke="#e2e4e8" strokeWidth={strokeW} />
        </svg>
        <div className="donut-center-label">
          <span className="pct">0%</span>
          <span className="pct-sub">Gesamt-<br />fortschritt</span>
        </div>
      </div>
    );
  }

  return (
    <div className="donut-wrap" style={{ width: size, height: size }}>
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="#e2e4e8" strokeWidth={strokeW} />
        {slices.map((s, i) =>
          s.dash > 0 && (
            <circle
              key={i}
              cx={cx} cy={cy} r={r}
              fill="none"
              stroke={s.color}
              strokeWidth={strokeW}
              strokeDasharray={`${s.dash} ${circumference - s.dash}`}
              strokeDashoffset={-s.offset}
              strokeLinecap="butt"
            />
          )
        )}
      </svg>
      <div className="donut-center-label">
        <span className="pct">{centerPct}%</span>
        <span className="pct-sub">Gesamt-<br />fortschritt</span>
      </div>
    </div>
  );
}
