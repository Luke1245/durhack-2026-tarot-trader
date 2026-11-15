import finalOrbitInner from '@/assets/home/final-orbit-inner.svg'
import finalOrbitMiddle from '@/assets/home/final-orbit-middle.svg'
import finalOrbitOuter from '@/assets/home/final-orbit-outer.svg'
import type { AppPage } from '@/components/AppHeader'
import { Button } from '@/components/ui/button'

type FinalInvitationProps = {
  onNavigate: (page: Exclude<AppPage, 'home'>) => void
}

export function FinalInvitation({ onNavigate }: FinalInvitationProps) {
  return (
    <section
      aria-labelledby="final-invitation-title"
      className="relative overflow-hidden bg-home-invitation px-6 py-14 text-center min-[1200px]:h-[380px] min-[1200px]:px-0 min-[1200px]:py-0"
    >
      <div className="relative mx-auto max-w-[1440px] min-[1200px]:h-full">
        <img
          src={finalOrbitInner}
          alt=""
          aria-hidden="true"
          className="pointer-events-none absolute left-1/2 top-1/2 size-[700px] max-w-none -translate-x-1/2 -translate-y-1/2 min-[1200px]:left-[370px] min-[1200px]:top-[-200px] min-[1200px]:translate-x-0 min-[1200px]:translate-y-0"
        />
        <img
          src={finalOrbitMiddle}
          alt=""
          aria-hidden="true"
          className="pointer-events-none absolute left-1/2 top-1/2 size-[860px] max-w-none -translate-x-1/2 -translate-y-1/2 min-[1200px]:left-[290px] min-[1200px]:top-[-280px] min-[1200px]:translate-x-0 min-[1200px]:translate-y-0"
        />
        <img
          src={finalOrbitOuter}
          alt=""
          aria-hidden="true"
          className="pointer-events-none absolute left-1/2 top-1/2 size-[1020px] max-w-none -translate-x-1/2 -translate-y-1/2 min-[1200px]:left-[210px] min-[1200px]:top-[-360px] min-[1200px]:translate-x-0 min-[1200px]:translate-y-0"
        />

        <p className="relative z-10 text-[10px] leading-[1.6] tracking-[2px] text-home-gold min-[1200px]:absolute min-[1200px]:left-1/2 min-[1200px]:top-[61px] min-[1200px]:w-[600px] min-[1200px]:-translate-x-1/2">
          YOUR NEXT MOVE STARTS HERE
        </p>
        <h2
          id="final-invitation-title"
          className="relative z-10 mx-auto mt-5 max-w-[980px] font-display text-[42px] leading-[1.1] min-[1200px]:absolute min-[1200px]:left-1/2 min-[1200px]:top-[105px] min-[1200px]:mt-0 min-[1200px]:w-[980px] min-[1200px]:-translate-x-1/2 min-[1200px]:text-[61px]"
        >
          Trade with a little more clarity.
        </h2>
        <p className="relative z-10 mx-auto mt-5 max-w-[800px] text-[15px] leading-[1.6] text-home-muted min-[1200px]:absolute min-[1200px]:left-1/2 min-[1200px]:top-[196px] min-[1200px]:mt-0 min-[1200px]:w-[800px] min-[1200px]:-translate-x-1/2 min-[1200px]:text-[16px]">
          See what guidance the deck can offer you for your next move.
        </p>
        <Button
          onClick={() => onNavigate('draw')}
          className="relative z-10 mx-auto mt-7 flex h-[54px] w-[266px] items-center justify-between rounded-[3px] bg-home-gold px-[20px] text-left text-[14px] font-medium text-home-background hover:bg-home-gold/85 min-[1200px]:absolute min-[1200px]:left-1/2 min-[1200px]:top-[251px] min-[1200px]:mt-0 min-[1200px]:-translate-x-1/2"
        >
          <span>Find your next trade</span>
          <span aria-hidden="true">↗</span>
        </Button>
        <p className="relative z-10 mx-auto mt-5 text-[11px] leading-[1.6] text-home-muted min-[1200px]:absolute min-[1200px]:left-1/2 min-[1200px]:top-[326px] min-[1200px]:mt-0 min-[1200px]:w-[580px] min-[1200px]:-translate-x-1/2">
          Paper trading only. No real money at risk.
        </p>
      </div>
    </section>
  )
}
