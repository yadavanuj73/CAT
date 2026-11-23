import type { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  header?: ReactNode;
  className?: string;
  noPadding?: boolean;
}

export default function Card({
  children,
  header,
  className = '',
  noPadding = false,
}: CardProps) {
  return (
    <div
      className={`bg-surface border border-border rounded-xl overflow-hidden ${className}`}
    >
      {header && (
        <div className="px-6 py-4 border-b border-border">{header}</div>
      )}
      <div className={noPadding ? '' : 'p-6'}>{children}</div>
    </div>
  );
}
