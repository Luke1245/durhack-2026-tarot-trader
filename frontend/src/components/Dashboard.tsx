import { useEffect, useRef, useState } from 'react'

import { useCards } from '@/api/cards'
import { useCreateReading } from '@/api/readings'
import { Button } from '@/components/ui/button'
import type { components } from '@/api/schema'

type DrawnCardModel = components['schemas']['DrawnCard']

const POSITIONS = ['past', 'present', 'future'] as const
const SHUFFLE_INTERVAL_MS = 120

type Phase = 'idle' | 'shuffling' | 'revealed'

function shufflePick<T>(items: T[]): T {
  return items[Math.floor(Math.random() * items.length)]
}

export function Dashboard() {
  const cards = useCards()
  const createReading = useCreateReading()

  const [phase, setPhase] = useState<Phase>('idle')
  const [flashing, setFlashing] = useState<(string | null)[]>([null, null, null])
  const timer = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    return () => clearInterval(timer.current ?? undefined)
  }, [])

  function startShuffle() {
    if (!cards.data?.length) return
    setPhase('shuffling')
    createReading.reset()
    timer.current = setInterval(() => {
      setFlashing([shufflePick(cards.data!), shufflePick(cards.data!), shufflePick(cards.data!)].map((c) => c.image_path))
    }, SHUFFLE_INTERVAL_MS)
  }

  async function stopShuffle() {
    clearInterval(timer.current ?? undefined)
    timer.current = null
    setFlashing([null, null, null])
    try {
      await createReading.mutateAsync({})
      setPhase('revealed')
    } catch {
      setPhase('idle')
    }
  }

  return (
    <div className="mx-auto flex max-w-5xl flex-col items-center gap-6 py-10">
      <h1 className="text-2xl font-semibold">Draw your cards</h1>

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
          <Button size="lg" onClick={phase === 'shuffling' ? stopShuffle : startShuffle} disabled={createReading.isPending}>
            {createReading.isPending ? 'Drawing…' : phase === 'shuffling' ? 'STOP' : 'Shuffle'}
          </Button>
          {createReading.isError && (
            <p className="text-sm text-destructive">{createReading.error.message}</p>
          )}
        </div>
      ) : (
        <div className="max-w-md space-y-3 text-center">
          <p className="text-sm text-muted-foreground">{createReading.data!.interpretation}</p>
          <Button variant="outline" onClick={() => setPhase('idle')}>
            Draw again
          </Button>
        </div>
      )}
    </div>
  )
}

function DrawnCard({ card }: { card: DrawnCardModel }) {
  const [flipped, setFlipped] = useState(false)
  return (
    <button
      type="button"
      onClick={() => setFlipped((f) => !f)}
      className="relative h-full w-full text-left"
      title={card.meaning}
    >
      {flipped ? (
        <div className="flex h-full w-full flex-col items-center justify-center gap-2 bg-card p-2 text-center">
          <span className="text-sm font-medium">{card.name}</span>
          {card.reversed && <span className="text-xs text-destructive">reversed</span>}
          <span className="text-xs text-muted-foreground">{card.meaning}</span>
        </div>
      ) : (
        <img
          src={card.image_path ?? undefined}
          alt={card.name}
          className={card.reversed ? 'h-full w-full rotate-180 object-cover' : 'h-full w-full object-cover'}
        />
      )}
    </button>
  )
}
