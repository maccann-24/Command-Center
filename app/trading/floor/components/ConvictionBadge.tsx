import { cn } from '@/lib/utils';

interface ConvictionBadgeProps {
  conviction: number;
  className?: string;
}

function getConvictionLevel(conviction: number): {
  label: string;
  colorClass: string;
} {
  if (conviction <= 40) {
    return {
      label: 'LOW',
      colorClass: 'bg-gray-500/10 text-gray-600 border-gray-500/20',
    };
  } else if (conviction <= 60) {
    return {
      label: 'MEDIUM',
      colorClass: 'bg-yellow-500/10 text-yellow-600 border-yellow-500/20',
    };
  } else if (conviction <= 75) {
    return {
      label: 'HIGH',
      colorClass: 'bg-orange-500/10 text-orange-600 border-orange-500/20',
    };
  } else {
    return {
      label: 'VERY HIGH',
      colorClass: 'bg-red-500/10 text-red-600 border-red-500/20',
    };
  }
}

export function ConvictionBadge({ conviction, className }: ConvictionBadgeProps) {
  const { label, colorClass } = getConvictionLevel(conviction);

  return (
    <span
      className={cn(
        'inline-flex items-center px-2 py-1 rounded-md text-xs font-semibold border',
        colorClass,
        className
      )}
    >
      {label} {conviction}%
    </span>
  );
}
