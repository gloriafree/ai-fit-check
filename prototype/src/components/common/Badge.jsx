export default function Badge({ children, color = 'gold' }) {
  const colorMap = {
    gold: 'bg-gold/15 text-gold',
    green: 'bg-sage/20 text-sage',
    red: 'bg-rose/20 text-rose',
  };

  return (
    <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${colorMap[color] || colorMap.gold}`}>
      {children}
    </span>
  );
}
