import { Card } from './Card';

interface MetricCardProps {
  label: string;
  value: number | string;
}

export function MetricCard({ label, value }: MetricCardProps) {
  return (
    <Card>
      <div style={{ color: 'var(--text-muted)', fontSize: 'clamp(0.75rem, 2vw, 0.875rem)', marginBottom: 'var(--space-sm)' }}>
        {label}
      </div>
      <div style={{ fontSize: 'clamp(1.5rem, 4vw, 2rem)', fontWeight: 600, lineHeight: 1 }}>
        {value}
      </div>
    </Card>
  );
}

