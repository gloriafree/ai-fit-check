export default function Button({ children, onClick, disabled, variant = 'primary' }) {
  const base = 'w-full py-3 rounded-xl font-semibold text-sm transition-colors';
  const styles = {
    primary: `${base} bg-espresso text-cream hover:bg-espresso/90 disabled:opacity-40 disabled:cursor-not-allowed`,
    secondary: `${base} bg-white text-espresso border border-espresso/20 hover:bg-espresso/5`,
  };

  return (
    <button onClick={onClick} disabled={disabled} className={styles[variant]}>
      {children}
    </button>
  );
}
