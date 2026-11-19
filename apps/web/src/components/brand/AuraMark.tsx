import { useId } from 'react'
import { cn } from '@/lib/utils'

/** Luminous AURA mark: a core with two orbiting particles. Pure SVG/CSS (no WebGL) so it is cheap everywhere. */
export function AuraMark({ size = 40, animated = true, className }: { size?: number; animated?: boolean; className?: string }) {
  const id = useId()
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" role="img" aria-label="AURA" className={cn('shrink-0', className)}>
      <defs>
        <radialGradient id={`${id}core`} cx="50%" cy="45%" r="55%">
          <stop offset="0%" stopColor="#ffffff" />
          <stop offset="35%" stopColor="#c4b5fd" />
          <stop offset="100%" stopColor="#7c3aed" stopOpacity="0" />
        </radialGradient>
        <linearGradient id={`${id}ring`} x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stopColor="#8b5cf6" />
          <stop offset="100%" stopColor="#22d3ee" />
        </linearGradient>
      </defs>
      <circle cx="32" cy="32" r="18" fill={`url(#${id}core)`} />
      <ellipse
        cx="32"
        cy="32"
        rx="27"
        ry="11"
        fill="none"
        stroke={`url(#${id}ring)`}
        strokeWidth="2"
        transform="rotate(-25 32 32)"
        opacity="0.9"
      />
      <g style={animated ? { transformOrigin: '32px 32px', animation: 'aura-orbit 6s linear infinite' } : undefined}>
        <circle cx="59" cy="32" r="2.6" fill="#22d3ee" />
        <circle cx="5" cy="32" r="1.8" fill="#a78bfa" />
      </g>
    </svg>
  )
}
