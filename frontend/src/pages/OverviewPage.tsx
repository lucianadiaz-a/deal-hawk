import { Link, useSearchParams } from 'react-router-dom';
import { useOverview } from '../hooks/useOverview';
import { Card } from '../components/Card';
import { MetricCard } from '../components/MetricCard';
import { Badge } from '../components/Badge';
import { FeedList } from '../components/FeedList';
import { FeedRow } from '../components/FeedRow';
import { PushDealButton } from '../components/PushDealButton';
import { formatCents, formatPct, formatTime } from '../lib/format';
import { withWindowThreshold } from '../lib/query';

export function OverviewPage() {
  const [searchParams] = useSearchParams();
  const {
    data,
    isLoading,
    error,
    windowHours,
    thresholdPct,
    setWindowHours,
    setThresholdPct,
    refetch,
  } = useOverview();

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: 'var(--space-xl)', color: 'var(--text-muted)' }}>
        Loading...
      </div>
    );
  }

  if (error) {
    return (
      <Card>
        <div style={{ color: 'var(--color-alert)' }}>Error: {error}</div>
      </Card>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'clamp(1rem, 3vw, 2rem)' }}>
      {/* Header with controls */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--space-md)' }}>
        <h1 style={{ fontSize: 'clamp(1.5rem, 4vw, 1.75rem)' }}>Overview</h1>
        <div style={{ display: 'flex', gap: 'var(--space-md)', alignItems: 'center', flexWrap: 'wrap' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-xs)', fontSize: 'clamp(0.75rem, 2vw, 0.875rem)' }}>
            <span style={{ color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
              Window:
            </span>
            <input
              type="number"
              value={windowHours}
              onChange={(e) => setWindowHours(Number(e.target.value))}
              style={{ width: '70px' }}
              min="1"
            />
            <span style={{ color: 'var(--text-muted)' }}>hrs</span>
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-xs)', fontSize: 'clamp(0.75rem, 2vw, 0.875rem)' }}>
            <span style={{ color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
              Threshold:
            </span>
            <input
              type="number"
              value={thresholdPct}
              onChange={(e) => setThresholdPct(Number(e.target.value))}
              style={{ width: '70px' }}
              min="0"
            />
            <span style={{ color: 'var(--text-muted)' }}>%</span>
          </label>
          <button onClick={refetch}>Refresh</button>
        </div>
      </div>

      {/* Metrics row */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(min(180px, 100%), 1fr))',
          gap: 'clamp(0.75rem, 2vw, 1.5rem)',
        }}
      >
        <MetricCard label="Total Products" value={data.metrics.total_products} />
        <MetricCard label="Total Listings" value={data.metrics.total_listings} />
        <MetricCard label="Active Alerts" value={data.metrics.active_alerts} />
        <MetricCard label="Near Misses" value={data.metrics.near_misses} />
      </div>

      {/* Feeds row */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(min(400px, 100%), 1fr))',
          gap: 'clamp(0.75rem, 2vw, 1.5rem)',
        }}
      >
        {/* Recent Alerts */}
        <Card>
          <h3 style={{ marginBottom: 'var(--space-lg)' }}>Recent Alerts</h3>
          <FeedList emptyMessage="No recent alerts">
            {data.recent_alerts.map((alert, idx) => {
              const params = withWindowThreshold(searchParams, windowHours, thresholdPct);
              const toUrl = `/products/${alert.product_id}?${params.toString()}`;
              
              // Determine if alert is active (delta_pct <= -threshold)
              const isActiveAlert = alert.delta_pct <= -thresholdPct;
              
              return (
                <FeedRow
                  key={idx}
                  title={
                    <Link
                      to={toUrl}
                      style={{
                        color: 'var(--text-primary)',
                        textDecoration: 'none',
                        fontWeight: 500,
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.color = 'var(--color-accent)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.color = 'var(--text-primary)';
                      }}
                    >
                      {alert.product_name}
                    </Link>
                  }
                subtitle={`${alert.retailer_name} • ${formatTime(alert.triggered_at)}`}
                right={
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)', flexWrap: 'wrap' }}>
                    <div style={{ textAlign: 'right' }}>
                      <Badge kind="ok">{formatPct(alert.delta_pct)}</Badge>
                      <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: 'var(--space-xs)' }}>
                        {formatCents(alert.prev_price_cents)} → {formatCents(alert.new_price_cents)}
                      </div>
                    </div>
                    {isActiveAlert && (
                      <PushDealButton
                        productId={alert.product_id}
                        input={{
                          productName: alert.product_name,
                          retailerName: alert.retailer_name,
                          priceCents: alert.new_price_cents,
                          storeUrl: null, // Not available in alert feed
                        }}
                        compact={true}
                      />
                    )}
                  </div>
                }
                />
              );
            })}
          </FeedList>
        </Card>

        {/* Near Misses */}
        <Card>
          <h3 style={{ marginBottom: 'var(--space-lg)' }}>Near Misses</h3>
          <FeedList emptyMessage="No near misses">
            {data.near_misses.map((miss, idx) => {
              const params = withWindowThreshold(searchParams, windowHours, thresholdPct);
              const toUrl = `/products/${miss.product_id}?${params.toString()}`;
              return (
                <FeedRow
                  key={idx}
                  title={
                    <Link
                      to={toUrl}
                      style={{
                        color: 'var(--text-primary)',
                        textDecoration: 'none',
                        fontWeight: 500,
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.color = 'var(--color-accent)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.color = 'var(--text-primary)';
                      }}
                    >
                      {miss.product_name}
                    </Link>
                  }
                subtitle={miss.retailer_name}
                right={
                  <div style={{ textAlign: 'right' }}>
                    <Badge kind="watch">{formatPct(miss.delta_pct)}</Badge>
                    <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: 'var(--space-xs)' }}>
                      {formatCents(miss.current_price_cents)}
                    </div>
                  </div>
                }
                />
              );
            })}
          </FeedList>
        </Card>
      </div>
    </div>
  );
}
