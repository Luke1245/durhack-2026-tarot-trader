import theStar from '@/assets/home/the-star.svg'

export function TheStar() {
  return (
    <section
      aria-labelledby="the-star-title"
      className="relative bg-home-background px-6 py-14 min-[1200px]:h-[540px] min-[1200px]:px-0 min-[1200px]:py-0"
    >
      <div className="relative mx-auto max-w-[1440px] min-[1200px]:h-full">
        <img
          src={theStar}
          alt="The Star, card XVII"
          className="relative mx-auto block h-auto w-[271px] max-w-full min-[1200px]:absolute min-[1200px]:left-[219px] min-[1200px]:top-[34px] min-[1200px]:h-[461px] min-[1200px]:max-w-none"
        />

        <div className="mt-10 min-[1200px]:static min-[1200px]:mt-0">
          <p className="text-[10px] leading-[1.6] tracking-[2px] text-home-gold min-[1200px]:absolute min-[1200px]:left-[690px] min-[1200px]:top-[79px] min-[1200px]:w-[650px]">
            A MOMENT BEFORE THE MARKET
          </p>
          <h2
            id="the-star-title"
            className="mt-4 font-display text-[56px] leading-[1.1] min-[1200px]:absolute min-[1200px]:left-[686px] min-[1200px]:top-[119px] min-[1200px]:mt-0 min-[1200px]:w-[580px] min-[1200px]:text-[68px]"
          >
            The Star
          </h2>
          <p className="mt-4 text-[10px] leading-[1.6] tracking-[2px] text-home-gold min-[1200px]:absolute min-[1200px]:left-[690px] min-[1200px]:top-[209px] min-[1200px]:mt-0 min-[1200px]:w-[650px]">
            XVII&nbsp;&nbsp;&nbsp;/&nbsp;&nbsp;&nbsp;PATIENCE · PERSPECTIVE · POSSIBILITY
          </p>
          <div className="mt-8 font-display text-[30px] italic leading-[1.1] min-[1200px]:absolute min-[1200px]:left-[690px] min-[1200px]:top-[249px] min-[1200px]:mt-0 min-[1200px]:w-[630px] min-[1200px]:text-[33px]">
            <p>A reminder to look forward,</p>
            <p>without losing sight of risk.</p>
          </div>
          <div className="mt-7 text-[15px] leading-[1.6] text-home-muted min-[1200px]:absolute min-[1200px]:left-[690px] min-[1200px]:top-[344px] min-[1200px]:mt-0 min-[1200px]:w-[635px]">
            <p>The Star is one of the cards waiting in your trading deck.</p>
            <p>Shuffle, draw, and discover the trade your spread reveals.</p>
            <p>Tarot outcomes are entertainment, not financial advice.</p>
          </div>
        </div>
      </div>
    </section>
  )
}
