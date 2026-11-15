import type { AppPage } from '@/components/AppHeader'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

const FOOTER_LINKS: { page: AppPage; label: string; className: string }[] = [
  { page: 'home', label: 'Home', className: 'min-[1200px]:w-[90px]' },
  { page: 'draw', label: 'Pick Trade', className: 'min-[1200px]:ml-[21px] min-[1200px]:w-[125px]' },
  { page: 'portfolio', label: 'View Portfolio', className: 'min-[1200px]:ml-[18px] min-[1200px]:w-[155px]' },
]

type HomeFooterProps = {
  onNavigate: (page: AppPage) => void
}

export function HomeFooter({ onNavigate }: HomeFooterProps) {
  return (
    <footer className="relative bg-home-background px-6 py-10 min-[1200px]:h-[180px] min-[1200px]:px-0 min-[1200px]:py-0">
      <div className="relative mx-auto max-w-[1440px] min-[1200px]:h-full">
        <p className="font-display text-[26px] leading-[1.1] tracking-[2px] text-home-text min-[1200px]:absolute min-[1200px]:left-[72px] min-[1200px]:top-[40px] min-[1200px]:w-[430px]">
          ✦&nbsp;&nbsp;TAROT TRADER
        </p>
        <p className="mt-3 text-[12px] leading-[1.6] text-home-muted min-[1200px]:absolute min-[1200px]:left-[72px] min-[1200px]:top-[88px] min-[1200px]:mt-0 min-[1200px]:w-[570px]">
          A clearer perspective on your next move.
        </p>

        <nav aria-label="Footer navigation" className="mt-6 flex flex-wrap gap-5 min-[1200px]:absolute min-[1200px]:left-[770px] min-[1200px]:top-[47px] min-[1200px]:mt-0 min-[1200px]:gap-0">
          {FOOTER_LINKS.map((link) => (
            <Button
              key={link.page}
              variant="ghost"
              onClick={() => onNavigate(link.page)}
              className={cn(
                'h-auto rounded-none px-0 py-0 text-left text-[13px] font-normal leading-[1.6] text-home-muted hover:bg-transparent hover:text-home-text',
                link.className,
              )}
            >
              {link.label}
            </Button>
          ))}
        </nav>

        <div className="mt-8 h-px bg-home-border min-[1200px]:absolute min-[1200px]:left-[72px] min-[1200px]:right-[72px] min-[1200px]:top-[123px] min-[1200px]:mt-0" />
        <p className="mt-4 text-[10px] leading-[1.6] text-home-muted min-[1200px]:absolute min-[1200px]:left-[72px] min-[1200px]:top-[142px] min-[1200px]:mt-0 min-[1200px]:w-[250px]">
          © 2026 Tarot Trader
        </p>
        <p className="mt-2 text-[10px] leading-[1.6] text-home-muted min-[1200px]:absolute min-[1200px]:right-[72px] min-[1200px]:top-[142px] min-[1200px]:mt-0 min-[1200px]:w-[528px] min-[1200px]:text-right">
          Example data. Not financial advice. Trading involves risk.
        </p>
      </div>
    </footer>
  )
}
