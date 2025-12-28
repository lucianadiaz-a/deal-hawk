interface ProductsFiltersProps {
  brand: string;
  deltaMin: string;
  deltaMax: string;
  sort: string;
  pageSize: number;
  onBrandChange: (value: string) => void;
  onDeltaMinChange: (value: string) => void;
  onDeltaMaxChange: (value: string) => void;
  onSortChange: (value: string) => void;
  onPageSizeChange: (value: number) => void;
  onRefresh: () => void;
}

export function ProductsFilters({
  brand,
  deltaMin,
  deltaMax,
  sort,
  pageSize,
  onBrandChange,
  onDeltaMinChange,
  onDeltaMaxChange,
  onSortChange,
  onPageSizeChange,
  onRefresh,
}: ProductsFiltersProps) {
  return (
    <div
      style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: 'var(--space-md)',
        alignItems: 'center',
        padding: 'var(--space-md) 0',
      }}
    >
      <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-xs)', fontSize: '0.875rem' }}>
        <span style={{ color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>Brand:</span>
        <input
          type="text"
          value={brand}
          onChange={(e) => onBrandChange(e.target.value)}
          placeholder="All"
          style={{ width: '120px' }}
        />
      </label>

      <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-xs)', fontSize: '0.875rem' }}>
        <span style={{ color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>Delta Min:</span>
        <input
          type="number"
          value={deltaMin}
          onChange={(e) => onDeltaMinChange(e.target.value)}
          placeholder="-100"
          style={{ width: '80px' }}
        />
        <span style={{ color: 'var(--text-muted)' }}>%</span>
      </label>

      <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-xs)', fontSize: '0.875rem' }}>
        <span style={{ color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>Delta Max:</span>
        <input
          type="number"
          value={deltaMax}
          onChange={(e) => onDeltaMaxChange(e.target.value)}
          placeholder="0"
          style={{ width: '80px' }}
        />
        <span style={{ color: 'var(--text-muted)' }}>%</span>
      </label>

      <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-xs)', fontSize: '0.875rem' }}>
        <span style={{ color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>Sort:</span>
        <select
          value={sort}
          onChange={(e) => onSortChange(e.target.value)}
          style={{ minWidth: '140px' }}
        >
          <option value="delta_desc">Delta (high to low)</option>
          <option value="delta_asc">Delta (low to high)</option>
          <option value="price_asc">Price (low to high)</option>
          <option value="name">Name (A-Z)</option>
        </select>
      </label>

      <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-xs)', fontSize: '0.875rem' }}>
        <span style={{ color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>Per page:</span>
        <select
          value={pageSize}
          onChange={(e) => onPageSizeChange(Number(e.target.value))}
          style={{ minWidth: '70px' }}
        >
          <option value="12">12</option>
          <option value="24">24</option>
          <option value="48">48</option>
        </select>
      </label>

      <button onClick={onRefresh}>Refresh</button>
    </div>
  );
}

