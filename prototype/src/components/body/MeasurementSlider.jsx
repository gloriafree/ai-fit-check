export default function MeasurementSlider({ label, value, onChange, min, max, step, unit, onFocus }) {
  return (
    <div className="mb-4" onFocus={onFocus}>
      <div className="flex justify-between items-center mb-1">
        <label className="text-sm font-medium">{label}</label>
        <span className="text-sm font-semibold text-gold">
          {value} {unit}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full"
      />
      <div className="flex justify-between text-xs text-espresso/30 mt-0.5">
        <span>{min}</span>
        <span>{max}</span>
      </div>
    </div>
  );
}
