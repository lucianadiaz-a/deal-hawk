interface FeedListProps {
  children: React.ReactNode;
  emptyMessage?: string;
}

export function FeedList({ children, emptyMessage = 'No items' }: FeedListProps) {
  const hasChildren = Array.isArray(children) ? children.length > 0 : !!children;

  if (!hasChildren) {
    return <div className="empty-state">{emptyMessage}</div>;
  }

  return <div className="feed-list">{children}</div>;
}

