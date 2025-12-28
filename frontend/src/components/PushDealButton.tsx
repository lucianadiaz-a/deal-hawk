import { useState } from 'react';
import { PushDealModal } from './PushDealModal';
import type { PushDealInput } from '../lib/pushDeal';

interface PushDealButtonProps {
  productId: number;
  input: PushDealInput;
  compact?: boolean;
}

// Session state: track which products have been marked as "pushed"
// Uses a simple Map in module scope (frontend-only, no persistence)
const pushedProducts = new Set<number>();

export function PushDealButton({ productId, input, compact = false }: PushDealButtonProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isPushed, setIsPushed] = useState(pushedProducts.has(productId));

  const handleOpen = () => {
    setIsModalOpen(true);
  };

  const handleClose = () => {
    setIsModalOpen(false);
  };

  const handleMarkAsPushed = (pushed: boolean) => {
    if (pushed) {
      pushedProducts.add(productId);
    } else {
      pushedProducts.delete(productId);
    }
    setIsPushed(pushed);
  };

  if (isPushed) {
    return (
      <>
        <button
          style={{
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border-muted)',
            borderRadius: 'var(--radius-sm)',
            color: 'var(--text-muted)',
            padding: compact ? 'var(--space-xs) var(--space-sm)' : 'var(--space-sm) var(--space-md)',
            fontSize: compact ? '0.75rem' : '0.875rem',
            cursor: 'default',
            textTransform: 'uppercase',
            letterSpacing: '0.03em',
            fontWeight: 500,
            width: '90px',
            textAlign: 'center',
            flexShrink: 0,
          }}
          disabled
        >
          PUSHED
        </button>
        <PushDealModal
          isOpen={isModalOpen}
          onClose={handleClose}
          input={input}
          isPushed={isPushed}
          onMarkAsPushed={handleMarkAsPushed}
        />
      </>
    );
  }

  return (
    <>
      <button
        onClick={handleOpen}
        style={{
          background: 'var(--color-accent)',
          border: '1px solid var(--color-accent)',
          borderRadius: 'var(--radius-sm)',
          color: 'var(--text-primary)',
          padding: compact ? 'var(--space-xs) var(--space-sm)' : 'var(--space-sm) var(--space-md)',
          fontSize: compact ? '0.75rem' : '0.875rem',
          cursor: 'pointer',
          textTransform: 'uppercase',
          letterSpacing: '0.03em',
          fontWeight: 500,
          transition: 'background 0.15s ease, border-color 0.15s ease',
          minWidth: compact ? '75px' : '90px',
          textAlign: 'center',
          flexShrink: 0,
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = 'var(--color-accent-hover)';
          e.currentTarget.style.borderColor = 'var(--color-accent-hover)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = 'var(--color-accent)';
          e.currentTarget.style.borderColor = 'var(--color-accent)';
        }}
      >
        PUSH DEAL
      </button>
      <PushDealModal
        isOpen={isModalOpen}
        onClose={handleClose}
        input={input}
        isPushed={isPushed}
        onMarkAsPushed={handleMarkAsPushed}
      />
    </>
  );
}

