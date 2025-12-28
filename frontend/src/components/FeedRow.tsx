import React from 'react';

interface FeedRowProps {
  title: string | React.ReactNode;
  subtitle?: string;
  right?: React.ReactNode;
}

export function FeedRow({ title, subtitle, right }: FeedRowProps) {
  return (
    <div className="feed-row">
      <div className="feed-row-content">
        <div className="feed-row-title">{title}</div>
        {subtitle && <div className="feed-row-subtitle">{subtitle}</div>}
      </div>
      {right && <div className="feed-row-right">{right}</div>}
    </div>
  );
}

