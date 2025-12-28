import { Link, useSearchParams } from 'react-router-dom';
import { Card } from './Card';
import { Badge } from './Badge';
import { formatCents, formatPct } from '../lib/format';
import { normalizeWindowThreshold, withWindowThreshold } from '../lib/query';
import type { ProductCardSchema } from '../api/types';

interface ProductCardProps {
  product: ProductCardSchema;
}

function getStatusBadgeKind(alertStatus: string): 'alert' | 'watch' | 'ok' | 'muted' {
  const status = alertStatus.toLowerCase();
  if (status === 'alert') return 'alert';
  if (status === 'watch') return 'watch';
  if (status === 'ok') return 'ok';
  return 'muted';
}

export function ProductCard({ product }: ProductCardProps) {
  const [searchParams] = useSearchParams();
  const { window_hours, threshold_pct } = normalizeWindowThreshold(searchParams);
  const params = withWindowThreshold(new URLSearchParams(), window_hours, threshold_pct);
  const toUrl = `/products/${product.product_id}${params.toString() ? `?${params.toString()}` : ''}`;

  return (
    <Card className="product-card">
      <Link
        to={toUrl}
        style={{
          cursor: 'pointer',
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--space-md)',
          minHeight: '180px',
          textDecoration: 'none',
          color: 'inherit',
        }}
      >
        {/* Header */}
        <div style={{ flex: 1 }}>
          <h3
            style={{
              margin: 0,
              fontSize: 'clamp(0.95rem, 2.5vw, 1rem)',
              lineHeight: 1.4,
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
              marginBottom: 'var(--space-xs)',
            }}
          >
            {product.product_name}
          </h3>
          {product.brand && (
            <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
              {product.brand}
            </div>
          )}
        </div>

        {/* Badge & Delta */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
          <Badge kind={getStatusBadgeKind(product.alert_status)}>
            {product.best_delta_pct !== null ? formatPct(product.best_delta_pct) : '—'}
          </Badge>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            {product.listing_count} {product.listing_count === 1 ? 'listing' : 'listings'}
          </div>
        </div>

        {/* Footer */}
        <div style={{ marginTop: 'auto', paddingTop: 'var(--space-sm)', borderTop: '1px solid var(--border-subtle)' }}>
          <div style={{ fontSize: 'clamp(1rem, 2.5vw, 1.125rem)', fontWeight: 600 }}>
            {formatCents(product.lowest_price_cents)}
          </div>
          {product.lowest_price_retailer && (
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 'var(--space-xs)' }}>
              at {product.lowest_price_retailer}
            </div>
          )}
        </div>
      </Link>
    </Card>
  );
}

