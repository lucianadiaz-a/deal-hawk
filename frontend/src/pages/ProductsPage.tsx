import { useSearchParams } from 'react-router-dom';
import { useProducts } from '../hooks/useProducts';
import { normalizeWindowThreshold } from '../lib/query';
import { Card } from '../components/Card';
import { ProductCard } from '../components/ProductCard';
import { ProductsFilters } from '../components/ProductsFilters';
import { Pagination } from '../components/Pagination';

export function ProductsPage() {
  const [searchParams, setSearchParams] = useSearchParams();

  // Read params from URL (with defaults)
  const brand = searchParams.get('brand') || '';
  const deltaMin = searchParams.get('delta_min') || '';
  const deltaMax = searchParams.get('delta_max') || '';
  const sort = searchParams.get('sort') || 'delta_desc';
  const page = parseInt(searchParams.get('page') || '1', 10);
  const pageSize = parseInt(searchParams.get('page_size') || '24', 10);
  const { window_hours, threshold_pct } = normalizeWindowThreshold(searchParams);

  // Fetch data
  const { data, isLoading, error, refetch } = useProducts({
    brand: brand || undefined,
    delta_min: deltaMin ? parseFloat(deltaMin) : undefined,
    delta_max: deltaMax ? parseFloat(deltaMax) : undefined,
    sort,
    page,
    page_size: pageSize,
    window_hours,
    threshold_pct,
  });

  // Update URL params helper
  const updateParams = (updates: Record<string, string | number | undefined>, resetPage = true) => {
    const newParams = new URLSearchParams(searchParams);
    
    Object.entries(updates).forEach(([key, value]) => {
      if (value === undefined || value === '') {
        newParams.delete(key);
      } else {
        newParams.set(key, String(value));
      }
    });

    if (resetPage && updates.page === undefined) {
      newParams.set('page', '1');
    }

    setSearchParams(newParams);
  };

  const totalPages = data ? Math.ceil(data.pagination.total / pageSize) : 1;

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: 'var(--space-xl)', color: 'var(--text-muted)' }}>
        Loading products...
      </div>
    );
  }

  if (error) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: 'var(--space-lg)' }}>
          <div style={{ color: 'var(--color-alert)', marginBottom: 'var(--space-md)' }}>
            Error: {error}
          </div>
          <button onClick={refetch}>Retry</button>
        </div>
      </Card>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'clamp(1rem, 3vw, 2rem)' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--space-md)' }}>
        <h1 style={{ fontSize: 'clamp(1.5rem, 4vw, 1.75rem)', margin: 0 }}>Products</h1>
        <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
          {data?.pagination.total || 0} total
        </div>
      </div>

      {/* Filters */}
      <ProductsFilters
        brand={brand}
        deltaMin={deltaMin}
        deltaMax={deltaMax}
        sort={sort}
        pageSize={pageSize}
        onBrandChange={(value) => updateParams({ brand: value })}
        onDeltaMinChange={(value) => updateParams({ delta_min: value })}
        onDeltaMaxChange={(value) => updateParams({ delta_max: value })}
        onSortChange={(value) => updateParams({ sort: value })}
        onPageSizeChange={(value) => updateParams({ page_size: value })}
        onRefresh={refetch}
      />

      {/* Products Grid */}
      {data && data.products.length > 0 ? (
        <>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(min(250px, 100%), 1fr))',
              gap: 'clamp(0.75rem, 2vw, 1.5rem)',
            }}
          >
            {data.products.map((product) => (
              <ProductCard key={product.product_id} product={product} />
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <Pagination
              currentPage={page}
              totalPages={totalPages}
              onPageChange={(newPage) => updateParams({ page: newPage }, false)}
            />
          )}
        </>
      ) : (
        <Card>
          <div style={{ textAlign: 'center', padding: 'var(--space-xl)', color: 'var(--text-muted)' }}>
            No products match your filters.
          </div>
        </Card>
      )}
    </div>
  );
}
