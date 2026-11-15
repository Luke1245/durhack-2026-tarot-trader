import { useState } from 'react'
import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceDot,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { useClosePosition, usePortfolio, usePositions } from '@/api/positions'
import { Button } from '@/components/ui/button'
import type { components } from '@/api/schema'

type Position = components['schemas']['PositionResponse']
type PortfolioPoint = components['schemas']['PortfolioPoint']

const CURRENCY = new Intl.NumberFormat(undefined, {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
})

const COMPACT_CURRENCY = new Intl.NumberFormat(undefined, {
  style: 'currency',
  currency: 'USD',
  currencyDisplay: 'narrowSymbol',
  notation: 'compact',
  maximumFractionDigits: 1,
})

function formatCurrency(value: number) {
  return `$${CURRENCY.format(value)}`
}

function formatSignedCurrency(value: number) {
  const sign = value > 0 ? '+' : value < 0 ? '−' : ''
  return `${sign}${formatCurrency(Math.abs(value))}`
}

function formatQuantity(value: number) {
  return new Intl.NumberFormat(undefined, {
    maximumFractionDigits: 4,
  }).format(value)
}

function formatSnapshotTick(value: string, history: PortfolioPoint[]) {
  const date = new Date(value)
  const firstDate = history[0] ? new Date(history[0].taken_at) : date
  const isSameDay = history.every((point) => {
    const pointDate = new Date(point.taken_at)
    return pointDate.toDateString() === firstDate.toDateString()
  })

  return isSameDay
    ? date.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' })
    : date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

function positionMarketValue(position: Position) {
  return position.current_price == null
    ? null
    : position.current_price * position.quantity
}

function getOpenExposure(positions: Position[]) {
  if (positions.some((position) => position.current_price == null)) return null

  return positions.reduce(
    (total, position) => total + (position.current_price ?? 0) * position.quantity,
    0,
  )
}

function getTotalPnl(positions: Position[]) {
  if (positions.some((position) => position.pnl == null)) return null

  return positions.reduce((total, position) => total + (position.pnl ?? 0), 0)
}

function getAllocation(positions: Position[]) {
  const values = new Map<string, number>()
  let hasUnavailableQuote = false

  for (const position of positions) {
    const marketValue = positionMarketValue(position)
    if (marketValue == null) {
      hasUnavailableQuote = true
      continue
    }
    values.set(position.asset_symbol, (values.get(position.asset_symbol) ?? 0) + marketValue)
  }

  const total = Array.from(values.values()).reduce((sum, value) => sum + value, 0)
  const items = Array.from(values, ([symbol, value]) => ({
    symbol,
    value,
    percentage: total > 0 ? (value / total) * 100 : 0,
  })).sort((a, b) => b.value - a.value)

  return { items, hasUnavailableQuote }
}

function MetricCard({
  label,
  value,
  detail,
  valueClassName = 'text-home-text',
}: {
  label: string
  value: string
  detail: string
  valueClassName?: string
}) {
  return (
    <article className="min-h-[127px] rounded-[6px] border border-home-border bg-home-surface px-5 py-4">
      <p className="text-[10px] uppercase leading-[1.5] tracking-[1.7px] text-home-gold">
        {label}
      </p>
      <p className={`mt-2 font-display text-[34px] leading-[1.1] ${valueClassName}`}>
        {value}
      </p>
      <p className="mt-2 text-[12px] leading-[1.5] text-home-muted">{detail}</p>
    </article>
  )
}

function PositionActions({
  position,
  confirming,
  disabled,
  onBegin,
  onConfirm,
  onCancel,
}: {
  position: Position
  confirming: boolean
  disabled: boolean
  onBegin: () => void
  onConfirm: () => void
  onCancel: () => void
}) {
  if (confirming) {
    return (
      <div className="flex shrink-0 gap-2">
        <Button
          size="sm"
          variant="destructive"
          className="h-[30px] px-2"
          disabled={disabled}
          onClick={onConfirm}
          aria-label={`Confirm closing ${position.asset_symbol} ${position.side} position`}
        >
          Confirm
        </Button>
        <Button size="sm" variant="ghost" className="h-[30px] px-2" disabled={disabled} onClick={onCancel}>
          Cancel
        </Button>
      </div>
    )
  }

  return (
    <Button
      size="sm"
      variant="outline"
      disabled={disabled}
      onClick={onBegin}
      aria-label={`Close ${position.asset_symbol} ${position.side} position`}
      className="h-[30px] border-home-border bg-transparent px-2 text-home-text hover:bg-home-border/60 hover:text-home-text"
    >
      Close
    </Button>
  )
}

function PositionName({ position }: { position: Position }) {
  return (
      <div className="flex min-w-0 items-center gap-2">
        <p className="truncate text-[13px] text-home-text">
          <span>{position.asset_symbol}</span>
          <span className="text-home-muted"> / {position.asset_name}</span>
        </p>
        <span
          className={`inline-flex shrink-0 rounded-[3px] border px-1.5 py-0.5 text-[8px] uppercase tracking-[0.8px] ${
            position.side === 'long'
              ? 'border-[#9dc3ab]/30 text-[#9dc3ab]'
              : 'border-[#e3a29b]/30 text-[#e3a29b]'
          }`}
        >
          {position.side}
        </span>
    </div>
  )
}

function HoldingDetails({ position }: { position: Position }) {
  const marketValue = positionMarketValue(position)
  const pnlClassName =
    position.pnl == null
      ? 'text-home-muted'
      : position.pnl >= 0
        ? 'text-[#9dc3ab]'
        : 'text-[#e3a29b]'

  return (
    <dl className="grid grid-cols-2 gap-x-4 gap-y-3 text-[12px] sm:grid-cols-4">
      <div>
        <dt className="text-[9px] uppercase tracking-[1.2px] text-home-gold">Shares</dt>
        <dd className="mt-1 text-home-text">{formatQuantity(position.quantity)}</dd>
      </div>
      <div>
        <dt className="text-[9px] uppercase tracking-[1.2px] text-home-gold">Avg. cost</dt>
        <dd className="mt-1 text-home-text">{formatCurrency(position.entry_price)}</dd>
      </div>
      <div>
        <dt className="text-[9px] uppercase tracking-[1.2px] text-home-gold">Last price</dt>
        <dd className="mt-1 text-home-text">
          {position.current_price == null ? '—' : formatCurrency(position.current_price)}
        </dd>
      </div>
      <div>
        <dt className="text-[9px] uppercase tracking-[1.2px] text-home-gold">Market value</dt>
        <dd className="mt-1 text-home-text">
          {marketValue == null ? '—' : formatCurrency(marketValue)}
        </dd>
      </div>
      <div className="col-span-2 sm:col-span-4">
        <dt className="text-[9px] uppercase tracking-[1.2px] text-home-gold">Total P&amp;L</dt>
        <dd className={`mt-1 ${pnlClassName}`}>
          {position.pnl == null ? '—' : formatSignedCurrency(position.pnl)}
        </dd>
      </div>
    </dl>
  )
}

export function PortfolioPage() {
  const portfolio = usePortfolio()
  const positions = usePositions()
  const closePosition = useClosePosition()
  const [confirmingId, setConfirmingId] = useState<string | null>(null)

  if (portfolio.isLoading || positions.isLoading) {
    return (
      <main className="min-h-screen bg-home-background px-6 py-10 font-home-sans text-home-muted">
        <p className="mx-auto max-w-[1296px] text-center">Loading portfolio…</p>
      </main>
    )
  }

  if (portfolio.isError || positions.isError) {
    return (
      <main className="min-h-screen bg-home-background px-6 py-10 font-home-sans text-home-text">
        <p className="mx-auto max-w-[1296px] rounded-[6px] border border-home-border bg-home-surface p-6 text-center text-home-muted" role="alert">
          Could not load portfolio — the price feed may be down. Try again shortly.
        </p>
      </main>
    )
  }

  const allPositions = positions.data ?? []
  const openPositions = allPositions.filter((position) => position.status === 'open')
  const allTimePnl = getTotalPnl(allPositions)
  const openExposure = getOpenExposure(openPositions)
  const allocation = getAllocation(openPositions)
  const history = portfolio.data?.history ?? []
  const latestPoint = history.at(-1)
  const pnlClassName =
    allTimePnl == null
      ? 'text-home-text'
      : allTimePnl >= 0
        ? 'text-[#9dc3ab]'
        : 'text-[#e3a29b]'

  function close(positionId: string) {
    closePosition.mutate(positionId, {
      onSuccess: () => setConfirmingId(null),
    })
  }

  return (
    <main className="min-h-screen bg-home-background font-home-sans text-home-text">
      <div className="mx-auto w-full max-w-[1296px] px-6 pb-8 pt-10 min-[1344px]:px-0 min-[1200px]:pt-12">
        <section aria-labelledby="portfolio-title">
          <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <p className="text-[10px] leading-[1.5] tracking-[1.7px] text-home-gold">
                02 / SEE THE BIGGER PICTURE
              </p>
      <h1
                id="portfolio-title"
                className="mt-5 font-display text-[46px] leading-[1.08] text-home-text sm:text-[56px] lg:text-[66px]"
              >
                Your Portfolio.
              </h1>
              <p className="mt-5 max-w-3xl text-[14px] leading-[1.5] text-home-muted sm:text-[16px]">
                A clear view of what you hold, how it’s performing, and where you’re exposed.
              </p>
            </div>
            <span className="inline-flex h-[35px] w-[202px] shrink-0 items-center self-start rounded-[6px] border border-home-border bg-[#211b2b] px-[15px] text-[10px] tracking-[1.7px] text-home-gold sm:mt-[17px]">
              <span aria-hidden="true" className="mr-2">✦</span>
              PAPER TRADING
            </span>
          </div>

          <div className="mt-9 grid gap-4 sm:grid-cols-2 xl:grid-cols-4 xl:gap-6">
            <MetricCard
              label="Portfolio value"
              value={formatCurrency(portfolio.data?.value ?? 0)}
              detail="Open position value + realized P&amp;L"
            />
            <MetricCard
              label="All-time P&amp;L"
              value={allTimePnl == null ? '—' : formatSignedCurrency(allTimePnl)}
              detail="Realized and unrealized position P&amp;L"
              valueClassName={pnlClassName}
            />
            <MetricCard
              label="Open positions"
              value={String(openPositions.length)}
              detail="Positions currently open"
            />
            <MetricCard
              label="Open exposure"
              value={openExposure == null ? '—' : formatCurrency(openExposure)}
              detail={
                openExposure == null
                  ? 'Some market prices are unavailable'
                  : 'At the latest market prices'
              }
            />
          </div>
        </section>

        <div className="mt-6 grid gap-6 xl:grid-cols-[1.89fr_1fr]">
          <section className="min-h-[273px] rounded-[6px] border border-home-border bg-home-surface px-5 pb-5 pt-5 sm:px-[25px] sm:pb-[18px] sm:pt-[18px]" aria-labelledby="performance-title">
            <div className="flex items-center justify-between gap-4 border-b border-home-border pb-10">
              <h2 id="performance-title" className="font-display text-[26px] leading-[1.1] sm:text-[29px]">
                Your celestial journey
              </h2>
              <span className="shrink-0 text-[10px] tracking-[1.7px] text-home-gold">ALL TIME</span>
            </div>
            {history.length > 1 ? (
              <div className="h-[163px] w-full" role="img" aria-label="Portfolio value over time">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={history} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
                    <CartesianGrid vertical={false} stroke="#352c40" />
                    <XAxis
                      dataKey="taken_at"
                      axisLine={false}
                      tickLine={false}
                      tick={{ fill: '#a49bab', fontSize: 10 }}
                      tickMargin={10}
                      minTickGap={24}
                      tickFormatter={(value: string) => formatSnapshotTick(value, history)}
                    />
                    <YAxis
                      axisLine={false}
                      tickLine={false}
                      tick={{ fill: '#a49bab', fontSize: 10 }}
                      tickFormatter={(value: number) => COMPACT_CURRENCY.format(value)}
                      domain={['auto', 'auto']}
                      width={54}
                    />
                    <Tooltip
                      labelFormatter={(value) => new Date(String(value)).toLocaleString()}
                      formatter={(value) => [formatCurrency(Number(value)), 'Portfolio value']}
                      contentStyle={{
                        backgroundColor: '#15111d',
                        border: '1px solid #352c40',
                        borderRadius: '6px',
                        color: '#eee8df',
                        fontSize: '12px',
                      }}
                      labelStyle={{ color: '#a49bab' }}
                    />
                    <Line
                      type="monotone"
                      dataKey="value"
                      stroke="#cfb884"
                      strokeWidth={2}
                      dot={false}
                      activeDot={{ r: 4, fill: '#cfb884', strokeWidth: 0 }}
                    />
                    {latestPoint && (
                      <ReferenceDot
                        x={latestPoint.taken_at}
                        y={latestPoint.value}
                        r={3}
                        fill="#cfb884"
                        stroke="#15111d"
                        strokeWidth={1}
                      />
                    )}
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <p className="flex h-[163px] items-center justify-center px-4 text-center text-[13px] text-home-muted">
                Not enough portfolio history yet — snapshots build as your positions change.
              </p>
            )}
          </section>

          <section className="min-h-[273px] rounded-[6px] border border-home-border bg-home-surface px-5 pb-5 pt-5 sm:px-[25px] sm:pb-[18px] sm:pt-[18px]" aria-labelledby="allocation-title">
            <div className="flex items-center justify-between gap-3">
              <h2 id="allocation-title" className="font-display text-[26px] leading-[1.1] sm:text-[29px]">
                Your Positions
              </h2>
            </div>
            {allocation.items.length > 0 ? (
              <div className="mt-[26px] max-h-[185px] space-y-[18px] overflow-y-auto pr-1">
                {allocation.items.map((item) => (
                  <div key={item.symbol} className="grid grid-cols-[56px_minmax(0,1fr)_52px] items-center gap-3 text-[11px]">
                    <span className="truncate text-home-text" title={item.symbol}>{item.symbol}</span>
                    <div
                      className="h-1 overflow-hidden rounded-full bg-[#2b2335]"
                      role="meter"
                      aria-label={`${item.symbol} share of open exposure`}
                      aria-valuemin={0}
                      aria-valuemax={100}
                      aria-valuenow={Math.round(item.percentage)}
                    >
                      <div
                        className="h-full rounded-full bg-home-gold"
                        style={{ width: `${item.percentage}%` }}
                      />
                    </div>
                    <span className="text-right text-home-muted">{item.percentage.toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="flex min-h-[185px] items-center justify-center px-4 text-center text-[13px] text-home-muted">
                Open positions will appear here as your portfolio grows.
              </p>
            )}
            {allocation.hasUnavailableQuote && allocation.items.length > 0 && (
              <p className="mt-2 text-[10px] text-home-muted">Some prices are unavailable; allocation may be incomplete.</p>
            )}
          </section>
        </div>

        <section className="mt-6 rounded-[6px] border border-home-border bg-home-surface px-5 pb-5 pt-5 sm:px-[25px] sm:pb-[18px] sm:pt-[18px]" aria-labelledby="holdings-title">
          <div className="mb-4 flex items-center justify-between gap-4">
            <h2 id="holdings-title" className="font-display text-[26px] leading-[1.1] sm:text-[29px]">
              Your holdings
            </h2>
            <span className="shrink-0 text-[9px] uppercase tracking-[1.1px] text-home-muted sm:text-[10px]">
              {openPositions.length} open {openPositions.length === 1 ? 'position' : 'positions'}
            </span>
          </div>

          {closePosition.isError && (
            <p className="mb-4 text-[12px] text-[#e3a29b]" role="alert">
              Could not close the position. Try again shortly.
            </p>
          )}

          {openPositions.length === 0 ? (
            <p className="border-t border-home-border py-6 text-center text-[13px] text-home-muted">
              No open positions yet. Your holdings will appear here.
            </p>
          ) : (
            <>
              <div className="hidden overflow-x-auto xl:block">
                <table className="w-full min-w-[960px] table-fixed text-left">
                  <colgroup>
                    <col className="w-[25%]" />
                    <col className="w-[10%]" />
                    <col className="w-[13%]" />
                    <col className="w-[13%]" />
                    <col className="w-[15%]" />
                    <col className="w-[14%]" />
                    <col className="w-[10%]" />
                  </colgroup>
                  <thead>
                    <tr className="border-b border-home-border text-[9px] uppercase tracking-[1.4px] text-home-gold">
                      <th scope="col" className="py-2.5 pr-3 font-normal">Asset</th>
                      <th scope="col" className="py-2.5 pr-3 font-normal">Shares</th>
                      <th scope="col" className="py-2.5 pr-3 font-normal">Avg. cost</th>
                      <th scope="col" className="py-2.5 pr-3 font-normal">Last price</th>
                      <th scope="col" className="py-2.5 pr-3 font-normal">Market value</th>
                      <th scope="col" className="py-2.5 pr-3 font-normal">Total P&amp;L</th>
                      <th scope="col" className="py-2.5 text-right font-normal">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {openPositions.map((position) => {
                      const marketValue = positionMarketValue(position)
                      const positionPnlClass =
                        position.pnl == null
                          ? 'text-home-muted'
                          : position.pnl >= 0
                            ? 'text-[#9dc3ab]'
                            : 'text-[#e3a29b]'

                      return (
                        <tr key={position.id} className="border-b border-home-border/70 last:border-b-0">
                          <td className="py-1.5 pr-3"><PositionName position={position} /></td>
                          <td className="py-1.5 pr-3 text-[12px] text-home-text">{formatQuantity(position.quantity)}</td>
                          <td className="py-1.5 pr-3 text-[12px] text-home-text">{formatCurrency(position.entry_price)}</td>
                          <td className="py-1.5 pr-3 text-[12px] text-home-text">
                            {position.current_price == null ? '—' : formatCurrency(position.current_price)}
                          </td>
                          <td className="py-1.5 pr-3 text-[12px] text-home-text">
                            {marketValue == null ? '—' : formatCurrency(marketValue)}
                          </td>
                          <td className={`py-1.5 pr-3 text-[12px] ${positionPnlClass}`}>
                            {position.pnl == null ? '—' : formatSignedCurrency(position.pnl)}
                          </td>
                          <td className="py-1.5 text-right">
                            <PositionActions
                              position={position}
                              confirming={confirmingId === position.id}
                              disabled={closePosition.isPending}
                              onBegin={() => {
                                closePosition.reset()
                                setConfirmingId(position.id)
                              }}
                              onConfirm={() => close(position.id)}
                              onCancel={() => setConfirmingId(null)}
                            />
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>

              <ul className="space-y-3 xl:hidden">
                {openPositions.map((position) => (
                  <li key={position.id} className="rounded-[4px] border border-home-border/80 p-4">
                    <div className="flex items-start justify-between gap-3">
                      <PositionName position={position} />
                      <PositionActions
                        position={position}
                        confirming={confirmingId === position.id}
                        disabled={closePosition.isPending}
                        onBegin={() => {
                          closePosition.reset()
                          setConfirmingId(position.id)
                        }}
                        onConfirm={() => close(position.id)}
                        onCancel={() => setConfirmingId(null)}
                      />
                    </div>
                    <div className="mt-4 border-t border-home-border/70 pt-4">
                      <HoldingDetails position={position} />
                    </div>
                  </li>
                ))}
              </ul>
            </>
          )}
        </section>

        <footer className="mt-7 border-t border-home-border pt-5 text-[10px] leading-[1.5] text-home-muted sm:flex sm:items-start sm:justify-between sm:gap-6">
          <p className="shrink-0">© {new Date().getFullYear()} Tarot Trader <span className="mx-2">/</span> PAPER TRADING</p>
          <p className="mt-2 sm:mt-0">For exploration, not financial advice. Trading involves risk.</p>
        </footer>
      </div>
    </main>
  )
}
