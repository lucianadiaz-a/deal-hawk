type BadgeKind = 'alert' | 'watch' | 'ok' | 'muted';

interface BadgeProps {
  kind: BadgeKind;
  children: React.ReactNode;
}

export function Badge({ kind, children }: BadgeProps) {
  return <span className={`badge badge-${kind}`}>{children}</span>;
}

