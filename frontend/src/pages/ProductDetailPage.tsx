import { useParams, useSearchParams } from 'react-router-dom';
import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { useProductDetail } from '../hooks/useProductDetail';
import { normalizeWindowThreshold } from '../lib/query';
import { Card } from '../components/Card';
import { Badge } from '../components/Badge';
import { PushDealButton } from '../components/PushDealButton';
import { formatCents, formatPct, formatTime } from '../lib/format';
import type { ProductListingDetailSchema } from '../api/types';

function getStatusBadgeKind(alertStatus: string): 'alert' | 'watch' | 'ok' | 'muted' {
  const status = alertStatus.toLowerCase();
  if (status === 'alert') return 'alert';
  if (status === 'watch') return 'watch';
  if (status === 'ok') return 'ok';
  return 'muted';
}

export function ProductDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [searchParams] = useSearchParams();
  const { window_hours, threshold_pct } = normalizeWindowThreshold(searchParams);
  const productId = id ? parseInt(id, 10) : 0;

  const { detail, historiesByListingId, alertHistory, isLoading, error, refetch } =
    useProductDetail(productId, window_hours, threshold_pct);

  if (isLoading) {
    return (
      <div
        style={{
          textAlign: 'center',
          padding: 'var(--space-xl)',
          color: 'var(--text-muted)',
        }}
      >
        Loading product details...
      </div>
    );
  }

  if (error) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: 'var(--space-lg)' }}>
          <div
            style={{ color: 'var(--color-alert)', marginBottom: 'var(--space-md)' }}
          >
            Error: {error}
          </div>
          <button onClick={refetch}>Retry</button>
        </div>
      </Card>
    );
  }

  if (!detail) {
    return null;
  }

  // Prepare chart data
  const chartData = prepareChartData(detail.listings, historiesByListingId);
  
  // Find best retailer for push deal (lowest price among listings with good price drops)
  const goodDealListings = detail.listings.filter(
    (listing) => listing.alert_status.toLowerCase() === 'ok'
  );
  const bestDealListing = goodDealListings.length > 0
    ? goodDealListings.reduce((best, current) => {
        const bestPrice = best.current_price_cents ?? Infinity;
        const currentPrice = current.current_price_cents ?? Infinity;
        return currentPrice < bestPrice ? current : best;
      })
    : null;
  
  // Debug: Log what we have
  console.log('ProductDetailPage render:', {
    productId,
    listingsCount: detail.listings.length,
    historiesCount: Object.keys(historiesByListingId).length,
    historiesByListingId,
    listingIds: detail.listings.map(l => l.listing_id),
  });

  return (
    <div
      style={{ display: 'flex', flexDirection: 'column', gap: 'clamp(1rem, 3vw, 2rem)' }}
    >
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--space-md)' }}>
        <div>
          <h1 style={{ fontSize: 'clamp(1.5rem, 4vw, 1.75rem)', margin: 0 }}>
            {detail.product_name}
          </h1>
          {detail.brand && (
            <div
              style={{
                fontSize: '1rem',
                color: 'var(--text-muted)',
                marginTop: 'var(--space-xs)',
              }}
            >
              {detail.brand}
            </div>
          )}
        </div>
        {bestDealListing && (
          <PushDealButton
            productId={detail.product_id}
            input={{
              productName: detail.product_name,
              retailerName: bestDealListing.retailer_name,
              priceCents: bestDealListing.current_price_cents,
              storeUrl: bestDealListing.url,
            }}
            compact={false}
          />
        )}
      </div>

      {/* Retailer Comparison */}
      <Card>
        <h3 style={{ marginBottom: 'var(--space-lg)' }}>Retailer Comparison</h3>
        <div
          style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}
        >
          {detail.listings.map((listing) => (
            <ListingRow
              key={listing.listing_id}
              listing={listing}
              history={historiesByListingId[String(listing.listing_id)]}
              isLoading={isLoading}
            />
          ))}
        </div>
        {detail.listings.length === 0 && (
          <div style={{ textAlign: 'center', padding: 'var(--space-lg)', color: 'var(--text-muted)' }}>
            No listings available
          </div>
        )}
      </Card>

      {/* Price History Chart */}
      <Card>
        <h3 style={{ marginBottom: 'var(--space-lg)' }}>Price History</h3>
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
              <XAxis
                dataKey="ts"
                stroke="var(--text-muted)"
                tick={{ fill: 'var(--text-secondary)' }}
                tickFormatter={(ts) => {
                  const date = new Date(ts);
                  return date.toLocaleDateString();
                }}
              />
              <YAxis
                stroke="var(--text-muted)"
                tick={{ fill: 'var(--text-secondary)' }}
                tickFormatter={(cents) => formatCents(cents)}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--bg-elevated)',
                  border: '1px solid var(--border-muted)',
                  borderRadius: 'var(--radius-sm)',
                }}
                labelStyle={{ color: 'var(--text-primary)' }}
                itemStyle={{ color: 'var(--text-secondary)' }}
                formatter={(value) => formatCents(value as number)}
                labelFormatter={(ts) => new Date(ts).toLocaleString()}
              />
              <Legend
                wrapperStyle={{ color: 'var(--text-secondary)' }}
              />
              {detail.listings.map((listing, index) => {
                const history = historiesByListingId[String(listing.listing_id)];
                const hasHistory = history && history.points && history.points.length > 0;
                
                // Always show all retailers, even if history is still loading
                // In demo DB, all listings have history, so this ensures consistency
                return (
                  <Line
                    key={listing.listing_id}
                    type="monotone"
                    dataKey={`listing_${listing.listing_id}`}
                    name={`${listing.retailer_name}${!hasHistory ? ' (loading...)' : ''}`}
                    stroke={getLineColor(index)}
                    strokeWidth={2}
                    dot={false}
                    connectNulls
                    strokeOpacity={hasHistory ? 1 : 0.3}
                  />
                );
              })}
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div
            style={{
              textAlign: 'center',
              padding: 'var(--space-lg)',
              color: 'var(--text-muted)',
            }}
          >
            {isLoading ? 'Loading price history...' : 'No price history available yet'}
          </div>
        )}
      </Card>

      {/* Alert History */}
      {alertHistory && (
        <Card>
          <h3 style={{ marginBottom: 'var(--space-lg)' }}>Alert History</h3>
          {alertHistory.events.length > 0 ? (
            <div
              style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}
            >
              {alertHistory.events.map((event) => (
                <div
                  key={event.alert_event_id}
                  style={{
                    padding: 'var(--space-md)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-sm)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    flexWrap: 'wrap',
                    gap: 'var(--space-md)',
                  }}
                >
                  <div style={{ flex: 1, minWidth: '200px' }}>
                    <div style={{ fontWeight: 500 }}>{event.retailer_name}</div>
                    <div
                      style={{
                        fontSize: '0.875rem',
                        color: 'var(--text-muted)',
                        marginTop: 'var(--space-xs)',
                      }}
                    >
                      {formatTime(event.triggered_at)}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <Badge kind="alert">{formatPct(event.delta_pct)}</Badge>
                    <div
                      style={{
                        fontSize: '0.875rem',
                        color: 'var(--text-muted)',
                        marginTop: 'var(--space-xs)',
                      }}
                    >
                      {formatCents(event.prev_price_cents)} →{' '}
                      {formatCents(event.new_price_cents)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div
              style={{
                textAlign: 'center',
                padding: 'var(--space-lg)',
                color: 'var(--text-muted)',
              }}
            >
              No alerts yet
            </div>
          )}
        </Card>
      )}
    </div>
  );
}

function ListingRow({
  listing,
  history,
  isLoading,
}: {
  listing: ProductListingDetailSchema;
  history?: { listing_id: number; points: Array<{ ts: string; price_cents: number }> };
  isLoading: boolean;
}) {
  const [isExpanded, setIsExpanded] = React.useState(false);
  
  // Debug logging
  React.useEffect(() => {
    if (history) {
      console.log(`ListingRow ${listing.listing_id} (${listing.retailer_name}):`, {
        hasHistory: !!history,
        pointsCount: history.points?.length || 0,
        isLoading,
      });
    } else {
      console.log(`ListingRow ${listing.listing_id} (${listing.retailer_name}): No history object`, { isLoading });
    }
  }, [listing.listing_id, listing.retailer_name, history, isLoading]);

  return (
    <div
      style={{
        background: 'var(--bg-elevated)',
        borderRadius: 'var(--radius-sm)',
        overflow: 'hidden',
      }}
    >
      {/* Main row */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: 'var(--space-md)',
          flexWrap: 'wrap',
          gap: 'var(--space-md)',
        }}
      >
        <div style={{ flex: 1, minWidth: '150px' }}>
          <div style={{ fontWeight: 500, marginBottom: 'var(--space-xs)' }}>
            {listing.retailer_name}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-xs)' }}>
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              style={{
                fontSize: '0.875rem',
                background: 'none',
                border: 'none',
                padding: 0,
                color: 'var(--color-accent)',
                cursor: 'pointer',
              }}
            >
              {isExpanded ? '▼' : '▶'} View retailer history
            </button>
            {isLoading && (
              <span
                style={{
                  fontSize: '0.75rem',
                  color: 'var(--text-muted)',
                  fontStyle: 'italic',
                }}
              >
                Loading history...
              </span>
            )}
            {!isLoading && (!history || !history.points || history.points.length === 0) && (
              <span
                style={{
                  fontSize: '0.75rem',
                  color: 'var(--text-muted)',
                  fontStyle: 'italic',
                }}
              >
                No history yet
              </span>
            )}
            {!isLoading && history && history.points && history.points.length > 0 && (
              <span
                style={{
                  fontSize: '0.75rem',
                  color: 'var(--color-ok)',
                }}
              >
                {history.points.length} points loaded
              </span>
            )}
          </div>
        </div>
        <div
          style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)' }}
        >
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '1.125rem', fontWeight: 600 }}>
              {formatCents(listing.current_price_cents)}
            </div>
            {listing.delta_pct !== null && (
              <div
                style={{
                  fontSize: '0.875rem',
                  color: 'var(--text-muted)',
                  marginTop: 'var(--space-xs)',
                }}
              >
                {formatPct(listing.delta_pct)}
              </div>
            )}
          </div>
          <Badge kind={getStatusBadgeKind(listing.alert_status)}>
            {listing.alert_status}
          </Badge>
        </div>
      </div>

      {/* Expanded history */}
      {isExpanded && history && history.points.length > 0 && (
        <div
          style={{
            borderTop: '1px solid var(--border-subtle)',
            padding: 'var(--space-lg)',
            background: 'var(--bg-surface)',
          }}
        >
          <h4
            style={{
              margin: 0,
              marginBottom: 'var(--space-md)',
              fontSize: '0.875rem',
              color: 'var(--text-secondary)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
            }}
          >
            Price History for {listing.retailer_name}
          </h4>
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--space-xs)',
              maxHeight: '400px',
              overflowY: 'auto',
            }}
          >
            {history.points
              .slice()
              .reverse()
              .map((point, idx) => {
                // Calculate price change from previous point
                const prevPoint = history.points
                  .slice()
                  .reverse()[idx + 1];
                const priceChange = prevPoint
                  ? point.price_cents - prevPoint.price_cents
                  : null;
                const priceChangePct =
                  prevPoint && prevPoint.price_cents !== 0
                    ? ((point.price_cents - prevPoint.price_cents) /
                        prevPoint.price_cents) *
                      100
                    : null;

                return (
                  <div
                    key={idx}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: 'var(--space-sm) var(--space-md)',
                      background: 'var(--bg-elevated)',
                      borderRadius: 'var(--radius-sm)',
                      borderLeft:
                        priceChange !== null && priceChange < 0
                          ? '3px solid var(--color-ok)'
                          : priceChange !== null && priceChange > 0
                          ? '3px solid var(--color-alert)'
                          : '3px solid transparent',
                    }}
                  >
                    <div style={{ flex: 1 }}>
                      <div
                        style={{
                          fontSize: '0.75rem',
                          color: 'var(--text-muted)',
                          marginBottom: 'var(--space-xs)',
                        }}
                      >
                        {new Date(point.ts).toLocaleString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric',
                          hour: 'numeric',
                          minute: '2-digit',
                          hour12: true,
                        })}
                      </div>
                      <div
                        style={{
                          fontSize: '1rem',
                          fontWeight: 600,
                          color: 'var(--text-primary)',
                        }}
                      >
                        {formatCents(point.price_cents)}
                      </div>
                    </div>
                    {priceChange !== null && (
                      <div style={{ textAlign: 'right' }}>
                        <div
                          style={{
                            fontSize: '0.875rem',
                            fontWeight: 500,
                            color:
                              priceChange < 0
                                ? 'var(--color-ok)'
                                : priceChange > 0
                                ? 'var(--color-alert)'
                                : 'var(--text-muted)',
                          }}
                        >
                          {priceChange > 0 ? '+' : ''}
                          {formatCents(Math.abs(priceChange))}
                        </div>
                        {priceChangePct !== null && (
                          <div
                            style={{
                              fontSize: '0.75rem',
                              color: 'var(--text-muted)',
                            }}
                          >
                            {priceChangePct > 0 ? '+' : ''}
                            {priceChangePct.toFixed(1)}%
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
          </div>
          <div
            style={{
              marginTop: 'var(--space-md)',
              fontSize: '0.75rem',
              color: 'var(--text-muted)',
              textAlign: 'center',
            }}
          >
            {history.points.length} price snapshots • Most recent first
          </div>
        </div>
      )}

      {isExpanded && (!history || history.points.length === 0) && (
        <div
          style={{
            borderTop: '1px solid var(--border-subtle)',
            padding: 'var(--space-lg)',
            background: 'var(--bg-surface)',
            textAlign: 'center',
            color: 'var(--text-muted)',
            fontSize: '0.875rem',
          }}
        >
          No price history available
        </div>
      )}
    </div>
  );
}

function prepareChartData(
  listings: ProductListingDetailSchema[],
  historiesByListingId: Record<string, { listing_id: number; points: Array<{ ts: string; price_cents: number }> }>
): Array<Record<string, string | number>> {
  // Filter to only listings that have history data (use string keys)
  const listingsWithHistory = listings.filter((listing) => {
    const history = historiesByListingId[String(listing.listing_id)];
    return history && history.points && history.points.length > 0;
  });

  if (listingsWithHistory.length === 0) {
    return [];
  }

  // Build a map of points by listing_id for efficient lookup
  const pointsByListing: Record<number, Array<{ ts: string; price_cents: number }>> = {};
  listingsWithHistory.forEach((listing) => {
    const history = historiesByListingId[String(listing.listing_id)];
    if (history && history.points) {
      // Sort points by timestamp ascending
      pointsByListing[listing.listing_id] = [...history.points].sort((a, b) => a.ts.localeCompare(b.ts));
    }
  });

  // Collect all unique timestamps across all listings
  const allTimestamps = new Set<string>();
  Object.values(pointsByListing).forEach((points) => {
    points.forEach((point) => allTimestamps.add(point.ts));
  });
  const sortedTimestamps = Array.from(allTimestamps).sort();

  // Build chart data with forward-fill
  const chartData: Array<Record<string, string | number>> = [];
  const lastKnownPrices: Record<number, number | undefined> = {};
  const pointIndices: Record<number, number> = {}; // Track current index for each listing

  // Initialize indices
  listingsWithHistory.forEach((listing) => {
    pointIndices[listing.listing_id] = 0;
  });

  sortedTimestamps.forEach((ts) => {
    const dataPoint: Record<string, string | number> = { ts };

    // For each listing, check if this timestamp has a new price point
    listingsWithHistory.forEach((listing) => {
      const listingId = listing.listing_id;
      const points = pointsByListing[listingId];
      const currentIndex = pointIndices[listingId];

      // Check if we have a point at this timestamp
      if (currentIndex < points.length && points[currentIndex].ts === ts) {
        // Update price and advance index
        lastKnownPrices[listingId] = points[currentIndex].price_cents;
        pointIndices[listingId]++;
      }

      // Add price to data point (use last known if available)
      const price = lastKnownPrices[listingId];
      if (price !== undefined) {
        dataPoint[`listing_${listingId}`] = price;
      }
    });

    chartData.push(dataPoint);
  });

  return chartData;
}

function getLineColor(index: number): string {
  const colors = [
    '#5b8ff9', // blue
    '#5ad8a6', // green
    '#f6bd16', // yellow
    '#e86452', // red
    '#6dc8ec', // cyan
    '#945fb9', // purple
    '#ff9845', // orange
    '#1e9493', // teal
    '#ff99c3', // pink
  ];
  return colors[index % colors.length];
}
