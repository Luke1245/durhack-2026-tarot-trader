import { useState } from 'react'
import { Menu as MenuPrimitive } from '@base-ui/react/menu'
import { LogOut, Menu, UserRound, X } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

export type AppPage = 'home' | 'draw' | 'portfolio'

type AppHeaderProps = {
  currentPage: AppPage
  userName: string
  logoutPending: boolean
  onNavigate: (page: AppPage) => void
  onLogout: () => void
}

const NAV_ITEMS: { page: AppPage; label: string; className: string }[] = [
  { page: 'home', label: 'Home', className: 'w-[76px]' },
  { page: 'draw', label: 'Pick Trade', className: 'w-[107px]' },
  { page: 'portfolio', label: 'View Portfolio', className: 'w-[139px]' },
]

export function AppHeader({
  currentPage,
  userName,
  logoutPending,
  onNavigate,
  onLogout,
}: AppHeaderProps) {
  const [mobileOpen, setMobileOpen] = useState(false)

  function navigate(page: AppPage) {
    setMobileOpen(false)
    onNavigate(page)
  }

  function logout() {
    setMobileOpen(false)
    onLogout()
  }

  return (
    <header className="relative bg-home-background font-home-sans text-home-text">
      <div className="mx-auto flex h-20 max-w-[1440px] items-center px-6 min-[1200px]:h-[100px] min-[1200px]:px-8 min-[1440px]:px-[72px]">
        <button
          type="button"
          onClick={() => navigate('home')}
          className="flex shrink-0 items-center text-left outline-none focus-visible:ring-2 focus-visible:ring-home-gold/60 min-[1200px]:w-[300px] min-[1440px]:w-[405px]"
          aria-label="Tarot Trader home"
        >
          <span className="w-[30px] text-[24px] leading-[1.6] text-home-gold min-[1200px]:text-[28px]">
            ✦
          </span>
          <span className="ml-2 whitespace-nowrap font-display text-[22px] leading-[1.04] tracking-[2px] min-[1200px]:ml-[10px] min-[1200px]:text-[29px] min-[1200px]:tracking-[2.4px]">
            TAROT TRADER
          </span>
        </button>

        <nav
          aria-label="Primary navigation"
          className="ml-[clamp(24px,3.68vw,53px)] hidden items-start gap-[clamp(12px,1.67vw,24px)] min-[1200px]:flex"
        >
          {NAV_ITEMS.map((item) => (
            <button
              key={item.page}
              type="button"
              onClick={() => navigate(item.page)}
              aria-current={currentPage === item.page ? 'page' : undefined}
              className={cn(
                'relative h-[52px] shrink-0 text-left text-[14px] outline-none focus-visible:ring-2 focus-visible:ring-home-gold/60',
                item.className,
              )}
            >
              <span
                className={cn(
                  'absolute left-[10px] top-[15px] whitespace-nowrap leading-[18px]',
                  currentPage === item.page ? 'text-home-gold' : 'text-home-muted hover:text-home-text',
                )}
              >
                {item.label}
              </span>
              {currentPage === item.page && (
                <span className="absolute bottom-0 left-[3px] right-[17px] h-px bg-home-gold" />
              )}
            </button>
          ))}
        </nav>

        <div className="ml-auto hidden items-center gap-3 min-[1200px]:flex">
          <AccountMenu userName={userName} logoutPending={logoutPending} onLogout={logout} />
          <Button
            variant="outline"
            onClick={() => navigate('draw')}
            className="relative h-[54px] w-[198px] rounded-[3px] border-home-border bg-transparent p-0 text-left text-[14px] font-normal text-home-text hover:bg-home-surface hover:text-home-text"
          >
            <span className="absolute left-[20px] top-[13px] leading-[1.6]">Pick a trade&nbsp;&nbsp;↗</span>
          </Button>
        </div>

        <button
          type="button"
          className="ml-auto inline-flex size-10 items-center justify-center rounded-[3px] border border-home-border text-home-gold outline-none focus-visible:ring-2 focus-visible:ring-home-gold/60 min-[1200px]:hidden"
          aria-label={mobileOpen ? 'Close navigation menu' : 'Open navigation menu'}
          aria-expanded={mobileOpen}
          aria-controls="mobile-navigation"
          onClick={() => setMobileOpen((open) => !open)}
        >
          {mobileOpen ? <X className="size-5" /> : <Menu className="size-5" />}
        </button>
      </div>

      <div className="pointer-events-none absolute inset-x-6 bottom-0 h-px bg-home-border min-[1200px]:left-8 min-[1200px]:right-8 min-[1440px]:left-[72px] min-[1440px]:right-[72px]" />

      {mobileOpen && (
        <nav
          id="mobile-navigation"
          aria-label="Mobile navigation"
          className="absolute inset-x-0 top-full z-50 border-b border-home-border bg-home-background px-6 py-5 shadow-2xl min-[1200px]:hidden"
        >
          <div className="mx-auto flex max-w-[1440px] flex-col gap-1">
            {NAV_ITEMS.map((item) => (
              <button
                key={item.page}
                type="button"
                onClick={() => navigate(item.page)}
                aria-current={currentPage === item.page ? 'page' : undefined}
                className={cn(
                  'flex min-h-11 items-center justify-between border-b border-home-border/60 py-2 text-left text-[14px]',
                  currentPage === item.page ? 'text-home-gold' : 'text-home-muted',
                )}
              >
                {item.label}
                {currentPage === item.page && <span aria-hidden="true">✦</span>}
              </button>
            ))}
            <Button
              onClick={() => navigate('draw')}
              className="mt-4 h-[54px] rounded-[3px] bg-home-gold text-[14px] text-home-background hover:bg-home-gold/85"
            >
              Pick a trade&nbsp;&nbsp;↗
            </Button>
            <div className="mt-4 flex items-center justify-between gap-4 border-t border-home-border pt-4">
              <span className="truncate text-[13px] text-home-muted">{userName}</span>
              <Button
                variant="ghost"
                size="sm"
                disabled={logoutPending}
                onClick={logout}
                className="text-home-muted hover:bg-home-surface hover:text-home-text"
              >
                <LogOut aria-hidden="true" />
                {logoutPending ? 'Logging out…' : 'Log out'}
              </Button>
            </div>
          </div>
        </nav>
      )}
    </header>
  )
}

function AccountMenu({
  userName,
  logoutPending,
  onLogout,
}: Pick<AppHeaderProps, 'userName' | 'logoutPending' | 'onLogout'>) {
  return (
    <MenuPrimitive.Root>
      <MenuPrimitive.Trigger
        aria-label={`Account menu for ${userName}`}
        className="inline-flex size-9 items-center justify-center rounded-full border border-home-border text-home-gold outline-none transition-colors hover:bg-home-surface focus-visible:ring-2 focus-visible:ring-home-gold/60"
      >
        <UserRound className="size-4" aria-hidden="true" />
      </MenuPrimitive.Trigger>
      <MenuPrimitive.Portal>
        <MenuPrimitive.Positioner align="end" sideOffset={8} className="z-50">
          <MenuPrimitive.Popup className="min-w-52 rounded-[3px] border border-home-border bg-home-surface p-1.5 font-home-sans text-home-text shadow-2xl outline-none">
            <div className="border-b border-home-border px-3 py-2.5">
              <p className="text-[10px] uppercase tracking-[1.4px] text-home-gold">Signed in as</p>
              <p className="mt-1 truncate text-[13px] text-home-muted">{userName}</p>
            </div>
            <MenuPrimitive.Item
              disabled={logoutPending}
              onClick={onLogout}
              className="mt-1 flex cursor-pointer items-center gap-2 rounded-[2px] px-3 py-2.5 text-[13px] text-home-muted outline-none data-[highlighted]:bg-home-border/60 data-[highlighted]:text-home-text data-[disabled]:cursor-wait data-[disabled]:opacity-60"
            >
              <LogOut className="size-4" aria-hidden="true" />
              {logoutPending ? 'Logging out…' : 'Log out'}
            </MenuPrimitive.Item>
          </MenuPrimitive.Popup>
        </MenuPrimitive.Positioner>
      </MenuPrimitive.Portal>
    </MenuPrimitive.Root>
  )
}
