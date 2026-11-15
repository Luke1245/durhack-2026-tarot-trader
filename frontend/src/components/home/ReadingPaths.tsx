import type { AppPage } from '@/components/AppHeader'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

type ReadingPath = {
  page: Exclude<AppPage, 'home'>
  symbol: string
  eyebrow: string
  title: string
  description: string[]
  action: string
  tag: string
  badge?: string
  className: string
}

const READING_PATHS: ReadingPath[] = [
  {
    page: 'draw',
    symbol: '✧',
    eyebrow: 'YOUR NEXT OPPORTUNITY',
    title: 'Pick a trade',
    description: ['Draw three cards to tap into your intuition and the wisdom of the universe.'],
    action: 'Pick trade  ↗',
    tag: 'DISCOVER',
    className: 'border-home-border bg-home-surface hover:bg-home-surface',
  },
  {
    page: 'portfolio',
    symbol: '☾',
    eyebrow: 'YOUR PREVIOUS POSITIONS',
    title: 'View portfolio',
    description: ['See your holdings, track performance,', 'and understand your exposure.'],
    action: 'View portfolio  ↗',
    tag: 'TRACK',
    badge: 'THE BIG PICTURE',
    className: 'border-home-gold-border bg-home-elevated hover:bg-home-elevated',
  },
]

type ReadingPathsProps = {
  onNavigate: (page: Exclude<AppPage, 'home'>) => void
}

export function ReadingPaths({ onNavigate }: ReadingPathsProps) {
  return (
    <section
      aria-labelledby="reading-paths-title"
      className="relative bg-home-background px-6 py-14 min-[1200px]:h-[620px] min-[1200px]:px-0 min-[1200px]:py-0"
    >
      <div className="relative mx-auto max-w-[1440px] min-[1200px]:h-full">
        <p className="text-[10px] leading-[1.6] tracking-[2px] text-home-gold min-[1200px]:absolute min-[1200px]:left-[72px] min-[1200px]:top-[69px] min-[1200px]:w-[650px]">
          YOUR TRADING JOURNEY
        </p>
        <h2
          id="reading-paths-title"
          className="mt-4 font-display text-[42px] leading-[1.1] min-[1200px]:absolute min-[1200px]:left-[72px] min-[1200px]:top-[99px] min-[1200px]:mt-0 min-[1200px]:w-[820px] min-[1200px]:text-[54px]"
        >
          Your next move starts here.
        </h2>
        <div className="mx-auto mt-10 grid max-w-[856px] gap-6 md:grid-cols-2 min-[1200px]:absolute min-[1200px]:left-1/2 min-[1200px]:top-[206px] min-[1200px]:mt-0 min-[1200px]:w-[856px] min-[1200px]:max-w-none min-[1200px]:-translate-x-1/2">
          {READING_PATHS.map((path) => (
            <ReadingPathCard key={path.page} path={path} onNavigate={onNavigate} />
          ))}
        </div>
      </div>
    </section>
  )
}

function ReadingPathCard({
  path,
  onNavigate,
}: {
  path: ReadingPath
  onNavigate: (page: Exclude<AppPage, 'home'>) => void
}) {
  return (
    <Button
      type="button"
      onClick={() => onNavigate(path.page)}
      aria-label={`${path.title} — ${path.eyebrow.toLowerCase()}`}
      className={cn(
        'group relative block h-[348px] w-full overflow-hidden whitespace-normal rounded-[8px] border text-left text-home-text outline-none transition-colors hover:text-home-text focus-visible:ring-2 focus-visible:ring-home-gold/70',
        path.className,
      )}
    >
      <span className="absolute left-[27px] top-[24px] flex h-[67px] w-[47px] items-start justify-center overflow-hidden rounded-[3px] border border-home-gold px-1 pt-[6px] font-display text-[34px] leading-[1.1] text-home-gold">
        <span aria-hidden="true">{path.symbol}</span>
      </span>

      {path.badge && (
        <span className="absolute right-[26px] top-[23px] flex h-[25px] w-[105px] items-center justify-center bg-home-badge text-[8px] leading-[1.6] text-home-gold">
          {path.badge}
        </span>
      )}

      <span className="absolute left-[27px] right-[27px] top-[114px] text-[10px] leading-[1.6] tracking-[2px] text-home-gold">
        {path.eyebrow}
      </span>
      <span className="absolute left-[27px] right-[27px] top-[143px] font-display text-[34px] leading-[1.1] text-home-text">
        {path.title}
      </span>
      <span className="absolute left-[27px] right-[27px] top-[195px] text-[14px] leading-[1.6] text-home-muted">
        {path.description.map((line) => (
          <span key={line} className="block">
            {line}
          </span>
        ))}
      </span>
      <span className="absolute left-[27px] right-[27px] top-[268px] h-px bg-home-border" />
      <span className="absolute left-[27px] top-[290px] text-[14px] font-medium leading-[1.6] text-home-gold">
        {path.action}
      </span>
      <span className="absolute bottom-[39px] right-[19px] text-[9px] leading-[1.6] text-home-muted">
        {path.tag}
      </span>
    </Button>
  )
}
