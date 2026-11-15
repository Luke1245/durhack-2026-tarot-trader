import ritualStep from '@/assets/home/ritual-step.svg'

const STEPS = [
  {
    number: '01',
    title: 'Start the shuffle',
    description: 'Allow yourself to connect to the deck through your intuition.',
  },
  {
    number: '02',
    title: 'Stop when it feels right',
    description: 'Choose the exact stopping point that feels right to you.',
  },
  {
    number: '03',
    title: 'Uncover recommendations',
    description: 'See what asset and move is recommended to you/',
  },
]

export function Ritual() {
  return (
    <section
      aria-labelledby="ritual-title"
      className="relative bg-home-band px-6 py-14 min-[1200px]:h-[440px] min-[1200px]:px-0 min-[1200px]:py-0"
    >
      <div className="relative mx-auto max-w-[1440px] min-[1200px]:h-full">
        <p className="text-[10px] leading-[1.6] tracking-[2px] text-home-gold min-[1200px]:absolute min-[1200px]:left-[72px] min-[1200px]:top-[66px] min-[1200px]:w-[550px]">
          A RITUAL FOR YOUR STRATEGY
        </p>
        <h2
          id="ritual-title"
          className="mt-4 font-display text-[42px] leading-[1.1] min-[1200px]:absolute min-[1200px]:left-[72px] min-[1200px]:top-[100px] min-[1200px]:mt-0 min-[1200px]:w-[600px] min-[1200px]:text-[54px]"
        >
          Tap in to your intuition
        </h2>
        <p className="mt-3 text-[14px] leading-[1.6] text-home-muted min-[1200px]:absolute min-[1200px]:left-[805px] min-[1200px]:top-[128px] min-[1200px]:mt-0 min-[1200px]:w-[565px]">
          Your next move is in the cards.
        </p>

        <div className="hidden min-[1200px]:absolute min-[1200px]:left-[90px] min-[1200px]:right-[110px] min-[1200px]:top-[219px] min-[1200px]:h-px min-[1200px]:bg-home-border min-[1200px]:block" />
        <ol className="mt-10 grid gap-10 min-[1200px]:absolute min-[1200px]:left-[72px] min-[1200px]:right-[72px] min-[1200px]:top-[199px] min-[1200px]:mt-0 min-[1200px]:grid-cols-3 min-[1200px]:gap-6">
          {STEPS.map((step) => (
            <li key={step.number} className="relative">
              <div className="relative size-[42px]">
                <img src={ritualStep} alt="" aria-hidden="true" className="absolute block size-full max-w-none" />
                <span className="absolute inset-0 flex items-center justify-center text-[12px] leading-[1.6] text-home-gold">
                  {step.number}
                </span>
              </div>
              <h3 className="mt-[22px] font-display text-[29px] leading-[1.1] text-home-text min-[1200px]:text-[31px]">
                {step.title}
              </h3>
              <p className="mt-4 max-w-[401px] text-[14px] leading-[1.6] text-home-muted">
                {step.description}
              </p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  )
}
