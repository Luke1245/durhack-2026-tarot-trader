# Glossary

Domain vocabulary for Tarot Trader. Terms are defined by the domain, not the implementation.

- **Tarot Card**: One of the 78 fixed reference cards (22 Major Arcana, 56 Minor Arcana). Carries upright/reversed/love/career meanings, a yes/no verdict, element and zodiac associations. Read-only reference data; identical for all users.
- **Reading**: A tarot spread a user has drawn, tied to a question. A reading is made of drawn cards — each draw records which card, its spread position, and whether it was reversed — plus a generated interpretation. Drawn cards are recorded by reference to the Tarot Card reference data, never copied.
- **Spread**: The fixed three-card layout of every reading: **past**, **present**, **future**, in that order. Deliberately not generalized — other layouts (single-card, Celtic Cross) are out of scope, so spread positions are a closed set, not free text.
- **Position**: A paper-trade the user has opened on an asset. Never real money: the app's internal ledger. Characterised by direction (side), quantity, entry price, and lifecycle timestamps. May reference the Reading that motivated it.
- **Side**: The direction of a position — **long** (profit if price rises) or **short** (profit if price falls). Not an options contract type; the project deliberately avoids options vocabulary (no calls, puts, strikes, expiries).
- **Asset**: A tradeable instrument — a stock (e.g. AAPL) or a cryptocurrency (e.g. BTC). Identified by a display symbol; priced by an external market-data feed (Finnhub) under its own provider symbol. Stocks trade during market hours; crypto trades 24/7, which is why the draw can be scoped to a market: all, stocks, or crypto.
- **Paper Trading**: All positions exist only inside this app. Entry and exit are recorded at prices fetched from a market-data API at that moment; PnL is computed, no funds move. There is no cash balance: amounts are unconstrained and portfolio value is the sum of open position values plus realized PnL.
- **Advice**: The trade recommendation derived from a Reading: a direction (long or short) and a chosen Asset, produced by AI sentiment analysis of the drawn cards. The user may accept the advice (opening a Position referencing the Reading) or decline it (the Reading is still kept).
