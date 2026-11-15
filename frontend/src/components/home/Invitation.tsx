export function Invitation() {
  return (
    <section
      aria-label="Tarot Trader principles"
      className="relative bg-home-band px-6 py-8 min-[1200px]:h-[110px] min-[1200px]:px-0 min-[1200px]:py-0"
    >
      <div className="relative mx-auto max-w-[1440px] min-[1200px]:h-full">
        <div className="absolute inset-x-6 top-0 h-px bg-home-border min-[1200px]:left-[72px] min-[1200px]:right-[72px]" />
        <p className="font-display text-[27px] leading-[1.04] min-[1200px]:absolute min-[1200px]:left-[72px] min-[1200px]:top-[32px] min-[1200px]:w-[560px] min-[1200px]:text-[30px]">
          For when you can’t trust your gut.
        </p>

        <div className="mt-5 flex flex-wrap items-center gap-x-5 gap-y-2 text-[10px] tracking-[1.5px] text-home-muted min-[1200px]:absolute min-[1200px]:left-[783px] min-[1200px]:top-[39px] min-[1200px]:mt-0 min-[1200px]:gap-0 min-[1200px]:text-[11px]">
          <span className="min-[1200px]:w-[180px]">DISCOVERY</span>
          <span aria-hidden="true" className="text-[18px] leading-[1.6] text-home-gold min-[1200px]:ml-[13px] min-[1200px]:w-[30px]">
            ✦
          </span>
          <span className="min-[1200px]:ml-[34px] min-[1200px]:w-[100px]">STRATEGY</span>
          <span aria-hidden="true" className="text-[18px] leading-[1.6] text-home-gold min-[1200px]:ml-[20px] min-[1200px]:w-[30px]">
            ✦
          </span>
          <span className="min-[1200px]:ml-[30px] min-[1200px]:w-[160px]">REFLECTION</span>
        </div>
      </div>
    </section>
  )
}
