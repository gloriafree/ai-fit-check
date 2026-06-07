const REGION_COLORS = {
  shoulder: '#C9A96E',
  chest: '#C9A96E',
  waist: '#C9A96E',
  hip: '#C9A96E',
  arm: '#C9A96E',
};

const DEFAULT_COLOR = '#E8E0D4';

export default function BodySilhouette({ activeRegion, gender = 'female', regionScores }) {
  // regionScores: { chest: 'green', shoulder: 'red', ... } — used in result page
  const getColor = (region) => {
    if (regionScores) {
      const score = regionScores[region];
      if (score === 'green') return '#A8B5A2';
      if (score === 'yellow') return '#C9A96E';
      if (score === 'red') return '#D4A0A0';
      return DEFAULT_COLOR;
    }
    return activeRegion === region ? REGION_COLORS[region] : DEFAULT_COLOR;
  };

  return (
    <svg
      width="120"
      height="220"
      viewBox="0 0 120 220"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Head */}
      <ellipse cx="60" cy="24" rx="14" ry="16" fill="#E8E0D4" stroke="#3C2A21" strokeWidth="1" />

      {/* Neck */}
      <rect x="54" y="39" width="12" height="10" fill="#E8E0D4" stroke="#3C2A21" strokeWidth="1" />

      {/* Shoulders */}
      <rect
        x="18" y="48" width="84" height="14" rx="6"
        fill={getColor('shoulder')}
        stroke="#3C2A21" strokeWidth="1"
        className="transition-colors duration-300"
      />

      {/* Chest */}
      <path
        d={gender === 'female'
          ? 'M18 62 L18 90 C18 92 22 100 36 100 L84 100 C98 100 102 92 102 90 L102 62 Z'
          : 'M18 62 L18 100 L102 100 L102 62 Z'
        }
        fill={getColor('chest')}
        stroke="#3C2A21" strokeWidth="1"
        className="transition-colors duration-300"
      />

      {/* Waist */}
      <path
        d={gender === 'female'
          ? 'M28 100 L92 100 L88 130 L32 130 Z'
          : 'M22 100 L98 100 L94 130 L26 130 Z'
        }
        fill={getColor('waist')}
        stroke="#3C2A21" strokeWidth="1"
        className="transition-colors duration-300"
      />

      {/* Hip */}
      <path
        d={gender === 'female'
          ? 'M32 130 L88 130 C92 140 94 148 94 152 L26 152 C26 148 28 140 32 130 Z'
          : 'M26 130 L94 130 L96 152 L24 152 Z'
        }
        fill={getColor('hip')}
        stroke="#3C2A21" strokeWidth="1"
        className="transition-colors duration-300"
      />

      {/* Left arm */}
      <rect
        x="4" y="52" width="12" height="60" rx="6"
        fill={getColor('arm')}
        stroke="#3C2A21" strokeWidth="1"
        className="transition-colors duration-300"
      />

      {/* Right arm */}
      <rect
        x="104" y="52" width="12" height="60" rx="6"
        fill={getColor('arm')}
        stroke="#3C2A21" strokeWidth="1"
        className="transition-colors duration-300"
      />

      {/* Left leg */}
      <rect x="30" y="152" width="20" height="60" rx="6" fill="#E8E0D4" stroke="#3C2A21" strokeWidth="1" />

      {/* Right leg */}
      <rect x="70" y="152" width="20" height="60" rx="6" fill="#E8E0D4" stroke="#3C2A21" strokeWidth="1" />

      {/* Region labels when active */}
      {activeRegion && (
        <text
          x="60" y={activeRegion === 'shoulder' ? 44 : activeRegion === 'chest' ? 84 : activeRegion === 'waist' ? 118 : activeRegion === 'hip' ? 144 : 84}
          textAnchor="middle"
          className="text-[9px] font-semibold fill-espresso"
        >
          {activeRegion.toUpperCase()}
        </text>
      )}
    </svg>
  );
}
