import celestialOrbits from '@/assets/home/celestial-orbits.svg'
import moonCard from '@/assets/home/moon-card.svg'
import softPlumAura from '@/assets/home/soft-plum-aura.svg'
import starCard from '@/assets/home/star-card.svg'
import sunCard from '@/assets/home/sun-card.svg'
import type { AppPage } from '@/components/AppHeader'
import { FinalInvitation } from '@/components/home/FinalInvitation'
import { HomeFooter } from '@/components/home/HomeFooter'
import { Invitation } from '@/components/home/Invitation'
import { ReadingPaths } from '@/components/home/ReadingPaths'
import { Reflection } from '@/components/home/Reflection'
import { Ritual } from '@/components/home/Ritual'
import { TheStar } from '@/components/home/TheStar'
import { Button } from '@/components/ui/button'

type HomePageProps = {
  onNavigate: (page: AppPage) => void
}

export function HomePage({ onNavigate }: HomePageProps) {
  return (
    <main className="bg-home-background font-home-sans text-home-text">
      <section
        aria-labelledby="home-hero-title"
        className="relative mx-auto max-w-[1440px] overflow-hidden px-6 pb-14 pt-14 min-[1200px]:h-[760px] min-[1200px]:px-0 min-[1200px]:pb-0 min-[1200px]:pt-0"
      >
        <img
          src={softPlumAura}
          alt=""
          aria-hidden="true"
          className="pointer-events-none absolute left-1/2 top-[30%] h-[740px] w-[800px] max-w-none -translate-x-1/2 min-[1200px]:left-[660px] min-[1200px]:top-[-10px] min-[1200px]:translate-x-0"
        />

        <p className="relative z-10 text-[10px] leading-[1.6] tracking-[2px] text-home-gold min-[1200px]:absolute min-[1200px]:left-[72px] min-[1200px]:top-[98px] min-[1200px]:w-[600px] min-[1200px]:text-[11px] min-[1200px]:tracking-[2.4px]">
          A LITTLE INTUITION. A CLEARER STRATEGY.
        </p>

        <h1
          id="home-hero-title"
          className="relative z-10 mt-6 max-w-[655px] font-display text-[clamp(3.5rem,7vw,5.375rem)] leading-[1.04] min-[1200px]:absolute min-[1200px]:left-[72px] min-[1200px]:top-[145px] min-[1200px]:mt-0 min-[1200px]:w-[655px] min-[1200px]:text-[86px]"
        >
          An astral approach to trading
        </h1>

        <p className="relative z-10 mt-6 font-display text-[34px] italic leading-[1.04] text-home-gold min-[1200px]:absolute min-[1200px]:left-[76px] min-[1200px]:top-[358px] min-[1200px]:mt-0 min-[1200px]:w-[595px] min-[1200px]:text-[44px]">
          Let the cards make the call.
        </p>

        <div className="relative z-10 mt-6 max-w-[575px] text-[15px] leading-[1.6] text-home-muted min-[1200px]:absolute min-[1200px]:left-[78px] min-[1200px]:top-[438px] min-[1200px]:mt-0 min-[1200px]:w-[575px] min-[1200px]:text-[16px]">
          <p>Shuffle the deck. Deal your trade. Ask the cards for a yes or no.</p>
          <p>A trading ritual led by tarot.</p>
        </div>

        <div className="relative z-10 mt-8 flex flex-wrap items-center gap-4 min-[1200px]:absolute min-[1200px]:left-[78px] min-[1200px]:top-[534px] min-[1200px]:mt-0 min-[1200px]:flex-nowrap min-[1200px]:gap-0">
          <Button
            onClick={() => onNavigate('draw')}
            className="h-[54px] w-[222px] justify-start rounded-[3px] bg-home-gold px-[20px] text-left text-[14px] font-medium text-home-background hover:bg-home-gold/85"
          >
            Pick your trade&nbsp;&nbsp;↗
          </Button>
          <button
            type="button"
            onClick={() => onNavigate('portfolio')}
            className="flex h-[54px] w-[190px] items-center px-2 text-left text-[14px] leading-[1.6] text-home-text outline-none hover:text-home-gold focus-visible:ring-2 focus-visible:ring-home-gold/60 min-[1200px]:ml-[29px] min-[1200px]:px-0"
          >
            View portfolio&nbsp;&nbsp;→
          </button>
        </div>

        <p className="relative z-10 mt-8 text-[9px] leading-[1.6] tracking-[1.2px] text-home-muted min-[1200px]:absolute min-[1200px]:left-[78px] min-[1200px]:top-[616px] min-[1200px]:mt-0 min-[1200px]:w-[580px] min-[1200px]:text-[10px] min-[1200px]:tracking-[1.4px]">
          PAPER TRADING&nbsp;&nbsp;·&nbsp;&nbsp;EXAMPLE DATA&nbsp;&nbsp;·&nbsp;&nbsp;NO REAL ORDERS
        </p>

        <CelestialArtwork />

        <p
          aria-hidden="true"
          className="absolute right-5 top-5 z-10 text-[30px] leading-[1.6] text-home-gold min-[1200px]:left-[1307px] min-[1200px]:right-auto min-[1200px]:top-[63px] min-[1200px]:w-[42px] min-[1200px]:text-[42px]"
        >
          ✧
        </p>
      </section>
      <Invitation />
      <ReadingPaths onNavigate={onNavigate} />
      <Ritual />
      <TheStar />
      <Reflection />
      <FinalInvitation onNavigate={onNavigate} />
      <HomeFooter onNavigate={onNavigate} />
    </main>
  )
}

function CelestialArtwork() {
  return (
    <div className="relative z-[1] mx-auto mt-10 aspect-[720/700] w-full max-w-[620px] min-[1200px]:absolute min-[1200px]:left-[704px] min-[1200px]:top-[25px] min-[1200px]:m-0 min-[1200px]:h-[700px] min-[1200px]:w-[720px] min-[1200px]:max-w-none">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute inset-[7.71%_9.31%_8.43%_9.44%]">
          <img src={celestialOrbits} alt="" aria-hidden="true" className="absolute block size-full max-w-none" />
        </div>

        <div
          className="absolute inset-[18.58%_46.96%_15.72%_5.57%] flex items-center justify-center"
          style={{ containerType: 'size' }}
        >
          <div className="-rotate-17 h-[hypot(35.0776cqw,85.2516cqh)] w-[hypot(64.9224cqw,-14.7484cqh)] flex-none">
            <div className="relative size-full">
              <div className="absolute inset-[-0.18%_-0.32%]">
                <img src={moonCard} alt="" aria-hidden="true" className="block size-full max-w-none" />
              </div>
            </div>
          </div>
        </div>

        <div
          className="absolute inset-[18.58%_5.57%_15.72%_46.96%] flex items-center justify-center"
          style={{ containerType: 'size' }}
        >
          <div className="h-[hypot(-35.0776cqw,85.2516cqh)] w-[hypot(64.9224cqw,14.7484cqh)] rotate-17 flex-none">
            <div className="relative size-full">
              <div className="absolute inset-[-0.18%_-0.32%]">
                <img src={sunCard} alt="" aria-hidden="true" className="block size-full max-w-none" />
              </div>
            </div>
          </div>
        </div>

        <div className="absolute inset-[13.29%_32.64%_16.71%_32.64%]">
          <div className="absolute inset-[-0.17%_-0.34%]">
            <img src={starCard} alt="" aria-hidden="true" className="block size-full max-w-none" />
          </div>
        </div>
      </div>

      <p className="absolute inset-x-0 bottom-[7%] mx-auto w-full max-w-[400px] text-center text-[9px] leading-[1.6] tracking-[1.6px] text-home-gold min-[1200px]:left-[202px] min-[1200px]:right-auto min-[1200px]:top-[650px] min-[1200px]:bottom-auto min-[1200px]:text-[10px] min-[1200px]:tracking-[2px]">
        STAY CURIOUS. TRADE WITH A PLAN.
      </p>
    </div>
  )
}
