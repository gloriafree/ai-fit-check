import { Link } from 'react-router-dom';

const FIT_DOT_COLORS = {
  green: 'bg-sage',
  yellow: 'bg-gold',
  red: 'bg-rose',
};

export default function ProductCard({ product }) {
  return (
    <Link
      to={`/product/${product.id}`}
      className="block bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-shadow"
    >
      <div className="aspect-square flex items-center justify-center bg-cream/50 relative">
        <span className="text-4xl">{product.emoji}</span>
        {product.quickFit && (
          <span
            className={`absolute top-2 right-2 w-3 h-3 rounded-full ${FIT_DOT_COLORS[product.quickFit]}`}
            title={product.quickFit}
          />
        )}
      </div>
      <div className="p-3">
        <p className="text-xs text-espresso/40 mb-0.5">{product.brand}</p>
        <h3 className="text-sm font-medium leading-tight mb-1 line-clamp-2">{product.name}</h3>
        <div className="flex items-center justify-between">
          <span className="text-sm font-semibold text-gold">${product.price}</span>
          <span className="text-xs text-espresso/30 capitalize">{product.fitType}</span>
        </div>
      </div>
    </Link>
  );
}
