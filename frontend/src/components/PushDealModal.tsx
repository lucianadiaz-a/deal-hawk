import { useState } from 'react';
import { Modal } from './Modal';
import { buildPushDealPayload } from '../lib/pushDeal';
import type { PushDealInput } from '../lib/pushDeal';

interface PushDealModalProps {
  isOpen: boolean;
  onClose: () => void;
  input: PushDealInput;
  isPushed: boolean;
  onMarkAsPushed: (pushed: boolean) => void;
}

export function PushDealModal({
  isOpen,
  onClose,
  input,
  isPushed,
  onMarkAsPushed,
}: PushDealModalProps) {
  const [copied, setCopied] = useState(false);
  const payload = buildPushDealPayload(input);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(payload.text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = payload.text;
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();
      try {
        document.execCommand('copy');
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      } catch (fallbackErr) {
        console.error('Fallback copy failed:', fallbackErr);
      }
      document.body.removeChild(textarea);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Push Deal Payload">
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
        {/* Payload text block */}
        <div
          style={{
            background: 'var(--bg-primary)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            padding: 'var(--space-md)',
            fontFamily: 'monospace',
            fontSize: '0.875rem',
            lineHeight: 1.6,
            color: 'var(--text-secondary)',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
            userSelect: 'text',
            maxHeight: '400px',
            overflowY: 'auto',
          }}
        >
          {payload.text}
        </div>

        {/* Actions */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: 'var(--space-md)',
            flexWrap: 'wrap',
          }}
        >
          <button
            onClick={handleCopy}
            style={{
              background: copied ? 'var(--color-ok)' : 'var(--bg-elevated)',
              border: `1px solid ${copied ? 'var(--color-ok)' : 'var(--border-muted)'}`,
              borderRadius: 'var(--radius-sm)',
              color: 'var(--text-primary)',
              padding: 'var(--space-sm) var(--space-md)',
              fontSize: '0.875rem',
              cursor: 'pointer',
              transition: 'background 0.15s ease, border-color 0.15s ease',
            }}
          >
            {copied ? '✓ Copied' : 'Copy'}
          </button>

          <label
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--space-sm)',
              fontSize: '0.875rem',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
            }}
          >
            <input
              type="checkbox"
              checked={isPushed}
              onChange={(e) => onMarkAsPushed(e.target.checked)}
              style={{
                cursor: 'pointer',
              }}
            />
            <span>Mark as pushed</span>
          </label>
        </div>

        {/* Summary info */}
        <div
          style={{
            padding: 'var(--space-md)',
            background: 'var(--bg-elevated)',
            borderRadius: 'var(--radius-sm)',
            fontSize: '0.875rem',
            color: 'var(--text-secondary)',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--space-xs)' }}>
            <span>Price:</span>
            <span style={{ fontWeight: 500 }}>${(payload.priceCents / 100).toFixed(2)}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--space-xs)' }}>
            <span>Commission:</span>
            <span style={{ fontWeight: 500 }}>${(payload.commissionCents / 100).toFixed(2)}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid var(--border-subtle)', paddingTop: 'var(--space-xs)', marginTop: 'var(--space-xs)' }}>
            <span style={{ fontWeight: 500 }}>Total:</span>
            <span style={{ fontWeight: 600 }}>${(payload.totalCents / 100).toFixed(2)}</span>
          </div>
        </div>
      </div>
    </Modal>
  );
}

