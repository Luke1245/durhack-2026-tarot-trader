import { useState } from 'react'
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import { useClosePosition, usePortfolio, usePositions } from '@/api/positions'
import { Button } from '@/components/ui/button'

export function PortfolioPage() {
  const portfolio = usePortfolio()
  const positions = usePositions()
  const closePosition = useClosePosition()
  const [confirmingId, setConfirmingId] = useState<string | null>(null)

  if (portfolio.isLoading || positions.isLoading) {
    return <p className="py-10 text-center text-muted-foreground">Loading portfolio…</p>
  }

  if (portfolio.isError || positions.isError) {
    return (
      <p className="py-10 text-center text-destructive">
        Could not load portfolio — the price feed may be down. Try again shortly.
      </p>
    )
  }

  const openPositions = (positions.data ?? []).filter((p) => p.status === 'open')
  const badgeClass =
    'w-14 rounded px-2 py-0.5 text-center text-xs font-bold uppercase '

  return (
    <div className="space-y-8 py-6">
      <section>
        <h2 className="text-lg font-semibold">Portfolio performance</h2>
        <p className="text-3xl font-bold">
          ${portfolio.data?.value.toFixed(2) ?? '0.00'}
        </p>
        <div className="mt-4 h-64 w-full">
          {portfolio.data && portfolio.data.history.length > 1 ? (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={portfolio.data.history}>
                <XAxis
                  dataKey="taken_at"
                  tickFormatter={(t: string) => new Date(t).toLocaleTimeString()}
                  fontSize={12}
                />
                <YAxis fontSize={12} domain={['auto', 'auto']} />
                <Tooltip
                  labelFormatter={(t) => new Date(String(t)).toLocaleString()}
                  formatter={(v) => [`$${Number(v).toFixed(2)}`, 'Value']}
                />
                <Line type="monotone" dataKey="value" dot={false} strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p className="flex h-full items-center justify-center text-sm text-muted-foreground">
              Not enough history yet — snapshots build up as you trade.
            </p>
          )}
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold">Open positions</h2>
        {openPositions.length === 0 ? (
          <p className="py-4 text-sm text-muted-foreground">No open positions.</p>
        ) : (
          <ul className="divide-y rounded-lg border">
            {openPositions.map((p) => (
              <li key={p.id} className="flex items-center justify-between gap-4 px-4 py-3">
                <div className="flex items-center gap-4">
                  <span
                    className={
                      badgeClass + (p.side === 'long' ? 'text-green-700' : 'text-red-600')
                    }
                  >
                    {p.side}
                  </span>
                    <div>
                      <p className="font-medium">{p.asset_symbol}</p>
                      <p className="text-xs text-muted-foreground">
                        {p.quantity} @ ${p.entry_price.toFixed(2)} → ${p.current_price?.toFixed(2) ?? '…'}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className={p.pnl != null && p.pnl >= 0 ? 'text-green-700' : 'text-red-600'}>
                      {p.pnl != null ? `${p.pnl >= 0 ? '+$' : '-$'}${Math.abs(p.pnl).toFixed(2)}` : '—'}
                    </span>
                    {confirmingId === p.id ? (
                      <div className="flex gap-2">
                        <Button size="sm" variant="destructive" disabled={closePosition.isPending} onClick={() => closePosition.mutate(p.id)}>
                          Confirm
                        </Button>
                        <Button size="sm" variant="ghost" onClick={() => setConfirmingId(null)}>
                          Cancel
                        </Button>
                      </div>
                    ) : (
                      <Button size="sm" variant="outline" onClick={() => setConfirmingId(p.id)}>
                        Close
                      </Button>
                    )}
                  </div>
                </li>
              ))}
          </ul>
        )}
      </section>
    </div>
  )
}
