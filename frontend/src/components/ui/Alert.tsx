import type { ReactNode } from 'react';
import {
  Info,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  X,
} from 'lucide-react';

type AlertVariant = 'info' | 'success' | 'warning' | 'error';

interface AlertProps {
  variant?: AlertVariant;
  title?: string;
  children: ReactNode;
  onDismiss?: () => void;
  className?: string;
}

const config: Record<
  AlertVariant,
  { icon: typeof Info; bg: string; border: string; text: string }
> = {
  info: {
    icon: Info,
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    text: 'text-blue-800',
  },
  success: {
    icon: CheckCircle2,
    bg: 'bg-emerald-50',
    border: 'border-emerald-200',
    text: 'text-emerald-800',
  },
  warning: {
    icon: AlertTriangle,
    bg: 'bg-amber-50',
    border: 'border-amber-200',
    text: 'text-amber-800',
  },
  error: {
    icon: XCircle,
    bg: 'bg-red-50',
    border: 'border-red-200',
    text: 'text-red-800',
  },
};

export default function Alert({
  variant = 'info',
  title,
  children,
  onDismiss,
  className = '',
}: AlertProps) {
  const { icon: Icon, bg, border, text } = config[variant];

  return (
    <div
      role="alert"
      className={`flex gap-3 p-4 rounded-lg border ${bg} ${border} ${className}`}
    >
      <Icon className={`h-5 w-5 shrink-0 mt-0.5 ${text}`} />
      <div className="flex-1 min-w-0">
        {title && (
          <h4 className={`text-sm font-semibold ${text} mb-0.5`}>{title}</h4>
        )}
        <div className={`text-sm ${text} opacity-90`}>{children}</div>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className={`p-0.5 rounded hover:bg-black/5 transition-colors shrink-0 ${text}`}
          aria-label="Dismiss alert"
        >
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  );
}
