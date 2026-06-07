import { useEffect } from 'react';

export default function Toast({ message, onClose, duration = 2000 }) {
  useEffect(() => {
    const timer = setTimeout(onClose, duration);
    return () => clearTimeout(timer);
  }, [onClose, duration]);

  return (
    <div className="fixed bottom-20 left-1/2 -translate-x-1/2 z-50 animate-fade-in">
      <div className="bg-espresso text-cream px-4 py-2 rounded-lg shadow-lg text-sm">
        {message}
      </div>
    </div>
  );
}
