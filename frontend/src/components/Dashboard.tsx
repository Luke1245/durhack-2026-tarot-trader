import { useState } from 'react'

import { useCards } from '@/api/cards'
import { useCreateReading } from '@/api/readings'
import { useCreatePosition } from '@/api/positions'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import type { components } from '@/api/schema'

type DrawnCardModel = components['schemas']['DrawnCard']
type Reading = components['schemas']['ReadingResponse']
type ReadingCreate = components['schemas']['ReadingCreate']
type Market = NonNullable<ReadingCreate['market']>
type Phase = 'idle' | 'shuffling' | 'waiting' | 'revealed'

const POSITIONS = ['past', 'present', 'future'] as const
const MARKETS: { value: Market; label: string }[] = [
  { value: 'all', label: 'All markets' },
  { value: 'stocks', label: 'Stocks' },
  { value: 'crypto', label: 'Crypto 24/7' },
]
const POSITION_COPY = [
  { label: 'What happened', helper: 'Recent moves and what drove them.' },
  { label: 'What to do now', helper: 'Buy, sell or wait—the card’s view.' },
  { label: 'What might happen', helper: 'What the cards suggest for the asset.' },
]

export function Dashboard() {
  const cards = useCards()
  const createReading = useCreateReading()
  const [phase, setPhase] = useState<Phase>('idle')
  const [market, setMarket] = useState<Market>('all')

  function startShuffle() {
    if (!cards.data?.length || createReading.isPending) return

    createReading.reset()
    setPhase('shuffling')
    createReading.mutate(
      { market },
      {
        onSuccess: () => setPhase((current) => current === 'waiting' ? 'revealed' : current),
        onError: () => setPhase((current) => current === 'waiting' ? 'idle' : current),
      },
    )
  }

  function stopShuffle() {
    if (createReading.isSuccess) setPhase('revealed')
    else if (createReading.isError) setPhase('idle')
    else setPhase('waiting')
  }

  const revealed = phase === 'revealed' ? createReading.data : undefined
  const stage = phase === 'revealed' ? 2 : phase === 'waiting' ? 1 : 0
  const actionLabel = phase === 'shuffling'
    ? 'Stop and draw'
    : phase === 'waiting'
      ? 'Drawing…'
      : phase === 'revealed'
        ? 'Shuffle again'
        : 'Start shuffling'

  return (
    <main className="min-h-screen bg-home-background font-home-sans text-home-text">
      <div className="mx-auto w-full max-w-[1296px] px-6 pb-10 pt-12 min-[1344px]:px-0">
        <section aria-labelledby="draw-title">
          <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <p className="text-[10px] leading-[1.5] tracking-[1.8px] text-home-gold">
                01 / THREE-CARD READING
              </p>
              <h1 id="draw-title" className="mt-3 font-display text-[clamp(2.8rem,5vw,4rem)] leading-[1.1] text-home-text">
                Pick a trade.
              </h1>
              <p className="mt-5 max-w-3xl text-[14px] leading-[1.5] text-[#aaa0b1] sm:text-[16px]">
                Shuffle the deck, then stop to draw three cards for an asset’s past, present and future.
              </p>
            </div>
            <span className="inline-flex h-[35px] w-[198px] shrink-0 items-center rounded-[6px] border border-[#3b3048] bg-[#211b2b] px-[15px] text-[10px] tracking-[1.8px] text-home-gold sm:mt-0">
              <span aria-hidden="true" className="mr-2">✦</span>
              3-CARD READING
            </span>
          </div>
        </section>

        <ReadingProgress stage={stage} />

        <section className="mt-9 overflow-hidden rounded-[6px] border border-[#51412f] bg-[#130f1b] min-[1254px]:grid min-[1254px]:grid-cols-[364px_minmax(0,1fr)]" aria-label="Three-card reading table">
          <aside className="border-b border-[#3b3048] px-6 py-7 sm:px-8 min-[1254px]:min-h-[900px] min-[1254px]:border-b-0 min-[1254px]:border-r min-[1254px]:px-[30px] min-[1254px]:py-[28px]">
            <p className="text-center text-[10px] tracking-[1.8px] text-home-gold">THE DECK</p>
            <DeckArtwork shuffling={phase === 'shuffling'} />
            <h2 className="mt-7 text-center font-display text-[28px] italic leading-[1.1] text-home-text">
              {phase === 'revealed' ? 'Three cards drawn' : phase === 'shuffling' || phase === 'waiting' ? 'Shuffling…' : 'Ready to shuffle'}
            </h2>
            <p className="mt-2 text-center text-[13px] leading-[1.5] text-[#aaa0b1]">
              {phase === 'revealed' ? 'Read the spread from left to right.' : 'Stop the deck to draw three cards.'}
            </p>
            <Button
              onClick={phase === 'shuffling' ? stopShuffle : startShuffle}
              disabled={phase === 'waiting' || cards.isLoading || !cards.data?.length}
              className="mt-5 h-[54px] w-full rounded-[6px] bg-home-gold text-[14px] font-medium text-home-background hover:bg-home-gold/90 disabled:opacity-60"
            >
              {cards.isLoading ? 'Loading cards…' : actionLabel}
            </Button>
            {cards.isError && <p className="mt-2 text-xs text-[#e3a29b]" role="alert">Could not load the card deck. Try again shortly.</p>}
            {createReading.isError && <p className="mt-2 text-xs text-[#e3a29b]" role="alert">{createReading.error.message}</p>}

            <div className="mt-[30px] rounded-[6px] border border-[#3b3048] bg-[#1b1424] px-[17px] py-[13px]">
              <p className="text-[10px] tracking-[1.6px] text-home-gold">READING FOR</p>
              <p className="mt-1 font-display text-[24px] leading-tight text-home-text">
                {revealed?.asset ? `${revealed.asset.name} · ${revealed.asset.symbol}` : 'Your next draw'}
              </p>
            </div>
            <MarketPicker market={market} onChange={setMarket} disabled={phase === 'shuffling' || phase === 'waiting'} />
            <p className="mt-5 text-[13px] leading-[1.5] text-[#aaa0b1]">
              One news story may add context to all three cards.
            </p>
          </aside>

          <div className="px-6 py-7 sm:px-8 min-[1254px]:pb-8 min-[1254px]:pl-[48px] min-[1254px]:pr-[89px] min-[1254px]:pt-[25px]">
            <div className="grid grid-cols-1 gap-8 sm:grid-cols-3 sm:gap-5 min-[1254px]:grid-cols-[repeat(3,230px)] min-[1254px]:gap-[52px]">
              {POSITIONS.map((position, index) => (
                <CardSlot
                  key={position}
                  position={position}
                  index={index}
                  card={revealed?.cards.find((drawnCard) => drawnCard.position === position)}
                  isRevealed={Boolean(revealed)}
                />
              ))}
            </div>
            <NewsStory reading={revealed} />
          </div>
        </section>

        {revealed && (
          <AdviceBlock
            key={revealed.id}
            reading={revealed}
            onDecline={() => setPhase('idle')}
            onTaken={() => setPhase('idle')}
          />
        )}

        <div className="mt-7 flex flex-col gap-3 text-[10px] leading-[1.5] sm:flex-row sm:items-start sm:justify-between">
          <p className="shrink-0 tracking-[1.2px] text-home-gold">ABOUT THE NEWS</p>
          <p className="text-[#aaa0b1] sm:max-w-[84%]">
            News adds context to the reading. It doesn’t make the cards’ predictions certain.
          </p>
        </div>

        <footer className="mt-16 border-t border-home-border pt-5 text-[10px] leading-[1.5] text-home-muted sm:flex sm:items-start sm:justify-between sm:gap-6">
          <p className="shrink-0">© {new Date().getFullYear()} Tarot Trader <span className="mx-2">/</span> DEMO READING · PAPER TRADES ONLY</p>
          <p className="mt-2 sm:mt-0">Tarot is not a market forecast or financial advice.</p>
        </footer>
      </div>
    </main>
  )
}

function ReadingProgress({ stage }: { stage: number }) {
  const steps = ['01  SHUFFLE', '02  STOP AND DRAW', '03  READ THE CARDS']
  return (
    <ol className="mt-[40px] grid min-h-[64px] grid-cols-1 content-center gap-2 rounded-[6px] border border-[#3b3048] bg-[#100d16] px-6 py-4 text-[10px] tracking-[1.4px] sm:grid-cols-3 sm:gap-4 sm:px-[25px] sm:py-0">
      {steps.map((step, index) => (
        <li key={step} aria-current={index === stage ? 'step' : undefined} className={index === stage ? 'text-home-gold' : 'text-[#82788c]'}>
          {step}
        </li>
      ))}
    </ol>
  )
}

function DeckArtwork({ shuffling }: { shuffling: boolean }) {
  return (
    <div className={`relative mx-auto mt-8 h-[300px] w-[180px] ${shuffling ? 'deck-shuffling' : ''}`} aria-hidden="true">
      <div className="absolute inset-0 rotate-[6deg] rounded-[6px] border border-[#8d784f] bg-[#21182c]" />
      <div className="absolute inset-0 -rotate-[5deg] rounded-[6px] border border-[#8d784f] bg-[#21182c]" />
      <div className="deck-top-card absolute inset-0 overflow-hidden rounded-[6px] border border-[#8d784f] bg-[#17121f]">
        <div className="absolute inset-[8px] rounded-[4px] border border-[#51412f]" />
        <span className="absolute inset-x-0 top-[28px] text-center text-[22px] text-home-gold/80">✧</span>
        <span className="absolute inset-0 flex items-center justify-center font-display text-[72px] text-[#8d784f]/80">✦</span>
        <span className="absolute inset-x-0 bottom-[28px] text-center text-[22px] text-home-gold/80">✧</span>
      </div>
    </div>
  )
}

function MarketPicker({ market, onChange, disabled }: { market: Market; onChange: (market: Market) => void; disabled: boolean }) {
  return (
    <fieldset className="mt-5">
      <legend className="mb-2 text-[9px] tracking-[1.4px] text-home-gold">MARKET</legend>
      <div className="grid grid-cols-3 gap-1 rounded-[4px] border border-[#3b3048] p-1" aria-label="Choose a market">
        {MARKETS.map((item) => (
          <button
            key={item.value}
            type="button"
            aria-pressed={market === item.value}
            disabled={disabled}
            onClick={() => onChange(item.value)}
            className={`min-h-8 rounded-[3px] px-1 text-[10px] transition-colors disabled:cursor-not-allowed disabled:opacity-50 ${market === item.value ? 'bg-home-gold font-medium text-home-background' : 'text-[#aaa0b1] hover:text-home-text'}`}
          >
            {item.label}
          </button>
        ))}
      </div>
    </fieldset>
  )
}

function CardSlot({ position, index, card, isRevealed }: { position: typeof POSITIONS[number]; index: number; card?: DrawnCardModel; isRevealed: boolean }) {
  const copy = POSITION_COPY[index]
  const number = ['I', 'II', 'III'][index]

  return (
    <article className="mx-auto w-full max-w-[230px]">
      <p className="text-center text-[10px] tracking-[1.8px] text-home-gold">0{index + 1} / {position.toUpperCase()}</p>
      <div className="mx-auto mt-8 aspect-[3/5] w-full max-w-[192px] overflow-hidden rounded-[6px] border border-[#51412f] bg-[#100c17] p-[8px]">
        <div className="relative flex size-full items-center justify-center overflow-hidden rounded-[4px] border border-[#30253c]">
          {isRevealed && card ? (
            <DrawnCard card={card} />
          ) : (
            <div className="text-center font-display text-[#6b586f]">
              <span className="block text-[53px] leading-none">{number}</span>
              <span className="mt-4 block text-[29px] leading-none">✧</span>
            </div>
          )}
        </div>
      </div>
      <h2 className="mt-6 text-center font-display text-[25px] leading-[1.1] text-home-text">
        {isRevealed && card ? card.name : copy.label}
      </h2>
      {isRevealed && card ? (
        <>
          <p className="mt-4 text-[9px] tracking-[1.4px] text-home-gold">AFTER THE DRAW</p>
          <p className="mt-2 text-[13px] leading-[1.5] text-[#aaa0b1]">{card.narrative ?? card.meaning}</p>
        </>
      ) : (
        <p className="mt-4 text-[13px] leading-[1.5] text-[#aaa0b1]">{copy.helper}</p>
      )}
    </article>
  )
}

function NewsStory({ reading }: { reading?: Reading }) {
  return (
    <section className="mt-8 min-h-[190px] rounded-[6px] border border-[#3b3048] bg-[#1b1424] p-5 sm:min-h-[222px]" aria-labelledby="news-story-title">
      <p className="text-[10px] tracking-[1.3px] text-home-gold">THE STORY BEHIND THE READING</p>
      <h2 id="news-story-title" className="mt-3 font-display text-[28px] leading-[1.1] text-home-text">
        {reading?.event_headline ?? 'Market context'}
      </h2>
      <p className="mt-3 max-w-3xl text-[13px] leading-[1.5] text-[#aaa0b1]">
        {reading?.event_headline
          ? 'This recent story was considered alongside the cards in your reading.'
          : 'A recent market story will appear here when one is available for your reading.'}
      </p>
      <div className="mt-6 flex items-center justify-between gap-4 text-[12px] text-[#aaa0b1] sm:mt-10">
        <span>{reading?.event_headline ? 'Selected market news' : 'News context'}</span>
        {reading?.event_url && (
          <a href={reading.event_url} target="_blank" rel="noopener noreferrer" className="shrink-0 text-home-gold hover:text-home-text">
            Read story ↗
          </a>
        )}
      </div>
    </section>
  )
}

function AdviceBlock({ reading, onDecline, onTaken }: { reading: Reading; onDecline: () => void; onTaken: () => void }) {
  const createPosition = useCreatePosition()
  const [amount, setAmount] = useState('')
  const [taken, setTaken] = useState(false)
  const quantity = Number(amount)

  async function takeAdvice() {
    if (!reading.asset || !reading.side) return
    await createPosition.mutateAsync({
      asset_id: reading.asset.id,
      side: reading.side,
      quantity,
      reading_id: reading.id,
    })
    setTaken(true)
  }

  return (
    <section className="mt-7 rounded-[6px] border border-[#3b3048] bg-[#1b1424] px-6 py-5 sm:px-[25px]" aria-labelledby="reading-result-title">
      <p className="text-[10px] tracking-[1.8px] text-home-gold">
        {reading.asset ? `${reading.asset.name.toUpperCase()} / ${reading.asset.symbol}` : 'READING RESULT'}
      </p>
      <div className="mt-2 flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
        <h2 id="reading-result-title" className="font-display text-[28px] leading-[1.15] text-home-text sm:text-[33px]">
          {taken
            ? 'Position opened. May the cards be right.'
            : reading.side
              ? `${reading.side === 'short' ? 'Sell' : 'Buy'} · ${reading.interpretation}`
              : reading.interpretation}
        </h2>
        {taken ? (
          <Button variant="outline" onClick={onTaken} className="shrink-0 border-home-border bg-transparent text-home-text hover:bg-home-surface hover:text-home-text">
            Draw again
          </Button>
        ) : reading.asset && reading.side ? (
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
            <Input
              type="number"
              min="0"
              step="any"
              placeholder="Amount (shares)"
              aria-label="Amount in shares"
              value={amount}
              onChange={(event) => setAmount(event.target.value)}
              className="w-full border-home-border bg-[#100d16] text-home-text placeholder:text-home-muted sm:w-40"
            />
            <Button
              disabled={!Number.isFinite(quantity) || quantity <= 0 || createPosition.isPending}
              onClick={() => takeAdvice().catch(() => undefined)}
              className="shrink-0 bg-home-gold text-home-background hover:bg-home-gold/90"
            >
              {createPosition.isPending ? 'Opening…' : 'Take the advice'}
            </Button>
          </div>
        ) : (
          <p className="text-[13px] text-[#aaa0b1]">No tradeable assets are available for this draw.</p>
        )}
      </div>
      {createPosition.isError && <p className="mt-3 text-[12px] text-[#e3a29b]" role="alert">Could not open the position. Try again.</p>}
      {reading.asset && reading.side && !taken && (
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-home-border/70 pt-4">
          <p className="text-[13px] text-[#aaa0b1]">
            The cards advise <span className={reading.side === 'long' ? 'text-[#9dc3ab]' : 'text-[#e3a29b]'}>{reading.side.toUpperCase()}</span> on {reading.asset.name} ({reading.asset.symbol}).
          </p>
          <Button variant="ghost" onClick={onDecline} className="text-home-muted hover:bg-home-surface hover:text-home-text">Decline</Button>
        </div>
      )}
      {(!reading.asset || !reading.side) && !taken && (
        <Button variant="ghost" onClick={onDecline} className="mt-3 text-home-muted hover:bg-home-surface hover:text-home-text">Draw again</Button>
      )}
    </section>
  )
}

function DrawnCard({ card }: { card: DrawnCardModel }) {
  const [flipped, setFlipped] = useState(false)
  return (
    <button
      type="button"
      onClick={() => setFlipped((current) => !current)}
      className="group relative size-full text-left"
      title={card.narrative ?? card.meaning}
      aria-label={`${card.name}, ${card.reversed ? 'reversed' : 'upright'}. Click to ${flipped ? 'show the card' : 'read its meaning'}.`}
    >
      {flipped ? (
        <span className="flex size-full flex-col items-center justify-center gap-2 overflow-y-auto bg-[#100c17] p-2 text-center">
          <span className="font-display text-[20px] text-home-text">{card.name}</span>
          {card.reversed && <span className="text-xs text-[#e3a29b]">reversed</span>}
          <span className="text-[11px] leading-[1.4] text-[#aaa0b1]">{card.meaning}</span>
        </span>
      ) : (
        <>
          {card.image_path ? (
            <img src={card.image_path} alt={card.name} className={`size-full object-cover ${card.reversed ? 'rotate-180' : ''}`} />
          ) : (
            <span className="flex size-full items-center justify-center bg-[#17121f] p-3 text-center font-display text-[22px] text-home-text">{card.name}</span>
          )}
          {card.narrative && (
            <span className="absolute inset-0 flex flex-col justify-center gap-2 overflow-y-auto bg-[#100c17]/95 p-3 text-center opacity-0 transition-opacity duration-200 group-hover:opacity-100">
              <span className="text-[10px] font-medium uppercase tracking-[1.4px] text-home-gold">{card.position}</span>
              <span className="text-[12px] leading-[1.45] text-home-text">{card.narrative}</span>
              <span className="text-[9px] text-home-muted">Click for card meaning</span>
            </span>
          )}
        </>
      )}
    </button>
  )
}
