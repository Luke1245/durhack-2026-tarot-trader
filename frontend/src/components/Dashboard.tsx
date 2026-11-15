import { useEffect, useRef, useState } from 'react'

import { useCards } from '@/api/cards'
import { useCreateReading } from '@/api/readings'
import { useCreatePosition } from '@/api/positions'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import type { components } from '@/api/schema'

type DrawnCardModel = components['schemas']['DrawnCard']

const POSITIONS = ['past', 'present', 'future'] as const
const SHUFFLE_INTERVAL_MS = 120

type Phase = 'idle' | 'shuffling' | 'revealed'
type ReadingCreate = components['schemas']['ReadingCreate']
type Market = NonNullable<ReadingCreate['market']>

const MARKETS: { value: Market; label: string }[] = [
  { value: 'all', label: 'All markets' },
  { value: 'stocks', label: 'Stocks' },
  { value: 'crypto', label: 'Crypto 24/7' },
]

function shufflePick<T>(items: T[]): T {
  return items[Math.floor(Math.random() * items.length)]
}

export function Dashboard() {
  const cards = useCards()
  const createReading = useCreateReading()

  const [phase, setPhase] = useState<Phase>('idle')
  const [market, setMarket] = useState<Market>('all')
  const [awaitingReveal, setAwaitingReveal] = useState(false)
  const [flashing, setFlashing] = useState<(string | null)[]>([null, null, null])
  const timer = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    return () => clearInterval(timer.current ?? undefined)
    // note: a fire-and-forget draw that never reveals leaves its reading
    // row server-side (accepted: readings are cheap) — deliberately no
    // mutation reset here; resetting inside effect cleanup re-renders
    // forever because the mutation object's identity changes every render
  }, [])

  // The draw is decided the moment shuffling starts; STOP only reveals it.
  useEffect(() => {
    if (!awaitingReveal) return
    if (createReading.isSuccess) {
      setAwaitingReveal(false)
      setPhase('revealed')
    } else if (createReading.isError) {
      setAwaitingReveal(false)
      setPhase('idle')
    }
  }, [awaitingReveal, createReading.isSuccess, createReading.isError])

  function startShuffle() {
    if (!cards.data?.length) return
    setPhase('shuffling')
    setAwaitingReveal(false)
    createReading.reset()
    createReading.mutate({ market }) // fire and forget: server draws + consults Gemini now
    timer.current = setInterval(() => {
      setFlashing([shufflePick(cards.data!), shufflePick(cards.data!), shufflePick(cards.data!)].map((c) => c.image_path))
    }, SHUFFLE_INTERVAL_MS)
  }

  function stopShuffle() {
    clearInterval(timer.current ?? undefined)
    timer.current = null
    setFlashing([null, null, null])
    if (createReading.isSuccess) {
      setPhase('revealed')
    } else if (createReading.isError) {
      setPhase('idle')
    } else {
      setAwaitingReveal(true) // still in flight: reveal via effect when it lands
    }
  }

  return (
    <div className="mx-auto flex max-w-5xl flex-col items-center gap-6 py-10">
      <h1 className="text-2xl font-semibold">Draw your cards</h1>

      <div className="flex gap-1 rounded-lg border p-1" role="group" aria-label="Market">
        {MARKETS.map((m) => (
          <button
            key={m.value}
            type="button"
            onClick={() => setMarket(m.value)}
            disabled={phase === 'shuffling'}
            className={
              market === m.value
                ? 'rounded-md bg-primary px-3 py-1 text-xs font-medium text-primary-foreground'
                : 'rounded-md px-3 py-1 text-xs text-muted-foreground hover:text-foreground'
            }
          >
            {m.label}
          </button>
        ))}
      </div>

      <div className="flex gap-6">
        {POSITIONS.map((position, i) => (
          <div key={position} className="flex flex-col items-center gap-2">
            <div className="h-84 w-52 overflow-hidden rounded-lg border bg-muted">
              {phase === 'revealed' && createReading.data ? (
                <DrawnCard card={createReading.data.cards[i]} />
              ) : (
                <div className="flex h-full w-full items-center justify-center">
                  {phase === 'shuffling' && flashing[i] ? (
                    <img src={flashing[i]!} alt="" className="h-full w-full object-cover opacity-80" />
                  ) : null}
                </div>
              )}
            </div>
            <span className="text-xs uppercase tracking-widest text-muted-foreground">
              {phase === 'revealed' ? createReading.data!.cards[i].position : position}
            </span>
          </div>
        ))}
      </div>

      {phase !== 'revealed' ? (
        <div className="flex flex-col items-center gap-2">
          <Button
            size="lg"
            onClick={phase === 'shuffling' ? stopShuffle : startShuffle}
            disabled={awaitingReveal}
          >
            {phase === 'shuffling'
              ? 'STOP'
              : createReading.isPending
                ? 'Drawing…'
                : 'Shuffle'}
          </Button>
          {createReading.isPending && (
            <p className="animate-pulse text-sm text-muted-foreground">
              Consulting the cards — the oracle is interpreting your spread…
            </p>
          )}
          {createReading.isError && (
            <p className="text-sm text-destructive">{createReading.error.message}</p>
          )}
        </div>
      ) : (
        <AdviceBlock
          reading={createReading.data!}
          onDecline={() => setPhase('idle')}
          onTaken={() => setPhase('idle')}
        />
      )}
    </div>
  )
}

function AdviceBlock({
  reading,
  onDecline,
  onTaken,
}: {
  reading: components['schemas']['ReadingResponse']
  onDecline: () => void
  onTaken: () => void
}) {
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

  if (taken) {
    return (
      <div className="space-y-3 text-center">
        <p className="font-medium">Position opened. May the cards be right.</p>
        <Button variant="outline" onClick={onTaken}>
          Draw again
        </Button>
      </div>
    )
  }

  return (
    <div className="w-full max-w-md space-y-4 text-center">
      <p className="text-sm text-muted-foreground">{reading.interpretation}</p>
      {reading.asset && reading.side ? (
        <div className="rounded-lg border p-4">
          <p className="text-lg font-semibold">
            The cards advise{' '}
            <span className={reading.side === 'long' ? 'text-green-700' : 'text-red-600'}>
              {reading.side.toUpperCase()}
            </span>{' '}
            on <span className="font-bold">{reading.asset.symbol}</span>
          </p>
          <p className="mt-1 text-xs text-muted-foreground">
            {reading.asset.name} — hover a card to see how it maps to the price
          </p>
          {reading.event_headline && (
            <p className="mt-2 text-sm text-muted-foreground">
              Chosen because:{' '}
              {reading.event_url ? (
                <a
                  href={reading.event_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="underline underline-offset-2 hover:text-foreground"
                >
                  {reading.event_headline}
                </a>
              ) : (
                reading.event_headline
              )}
            </p>
          )}
          <div className="mt-3 flex items-center justify-center gap-2">
            <Input
              type="number"
              min="0"
              step="any"
              placeholder="Amount (shares)"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="w-40"
            />
            <Button
              disabled={!Number.isFinite(quantity) || quantity <= 0 || createPosition.isPending}
              onClick={() => takeAdvice().catch(() => undefined)}
            >
              {createPosition.isPending ? 'Opening…' : 'Take the advice'}
            </Button>
          </div>
          {createPosition.isError && (
            <p className="mt-2 text-sm text-destructive">{createPosition.error.message}</p>
          )}
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">
          No tradeable assets are seeded, so no advice can be given for this draw.
        </p>
      )}
      <Button variant="ghost" onClick={onDecline}>
        {reading.asset ? 'Decline' : 'Draw again'}
      </Button>
    </div>
  )
}

function DrawnCard({ card }: { card: DrawnCardModel }) {
  const [flipped, setFlipped] = useState(false)
  return (
    <button
      type="button"
      onClick={() => setFlipped((f) => !f)}
      className="group relative h-full w-full text-left"
      title={card.narrative ?? card.meaning}
    >
      {flipped ? (
        <div className="flex h-full w-full flex-col items-center justify-center gap-2 overflow-y-auto bg-card p-2 text-center">
          <span className="text-sm font-medium">{card.name}</span>
          {card.reversed && <span className="text-xs text-destructive">reversed</span>}
          <span className="text-xs text-muted-foreground">{card.meaning}</span>
        </div>
      ) : (
        <>
          <img
            src={card.image_path ?? undefined}
            alt={card.name}
            className={card.reversed ? 'h-full w-full rotate-180 object-cover' : 'h-full w-full object-cover'}
          />
          {card.narrative && (
            <div className="absolute inset-0 flex flex-col justify-center gap-1 overflow-y-auto bg-card/95 p-3 text-center opacity-0 transition-opacity duration-200 group-hover:opacity-100">
              <span className="text-xs font-bold uppercase tracking-widest text-muted-foreground">
                {card.position}
              </span>
              <span className="text-xs italic">{card.narrative}</span>
              <span className="mt-1 text-[10px] text-muted-foreground">click for card meaning</span>
            </div>
          )}
        </>
      )}
    </button>
  )
}
