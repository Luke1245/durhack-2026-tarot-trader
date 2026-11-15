"""The Advice: turn a drawn spread into side (long/short) + asset + narratives.

Primary: Google Gemini (structured JSON output). Fallback (spec Q8): dataset
yes/no majority vote with reversed-flip, random asset, template narratives —
the draw must never hard-fail on a model or quota error.
"""

import asyncio
import logging
import random
import re
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field

from ..config import get_settings
from ..models import SPREAD_POSITIONS, Asset, TarotCard
from .news import NewsItem

logger = logging.getLogger("tarot-trader.advice")

ADVICE_TIMEOUT_SECONDS = 30

ADVICE_PROMPT = """You are a tarot-trading oracle. A user drew three tarot cards
(past, present, future). Based on the cards' meanings and orientations:

1. Decide a sentiment: does the spread predict the chosen asset's price will
   RISE (long) or FALL (short)?
2. Use the cards as the market mood and headlines as real-world context.
   Jointly choose one tradeable asset and, when relevant, the exact headline
   that best connects to that asset and the spread.
3. If no supplied headline is relevant, set event_headline to null and choose
   the asset that best fits the spread.
4. Write a one-paragraph reasoning connecting the three cards to the asset and
   the selected event when one exists.
5. For each card, write a short narrative relating it to the asset's price:
   past = the asset's recent history, present = its current situation,
   future = where it is heading.

Be decisive: always pick exactly one side and one asset. Never invent a
headline; event_headline must exactly match a supplied headline or be null.

Drawn cards:
{cards}

Tradeable assets:
{assets}

Recent headlines:
{headlines}"""


@dataclass
class Advice:
    side: Literal["long", "short"]
    asset: Asset | None  # None only when no assets are seeded at all
    reasoning: str
    narratives: dict[str, str]  # spread position -> hover narrative
    event_headline: str | None = None
    event_url: str | None = None

class _CardAdvice(BaseModel):
    position: Literal["past", "present", "future"]
    narrative: str


class _GeminiAdvice(BaseModel):
    """Schema sent to Gemini as structured output."""

    side: Literal["long", "short"]
    asset_symbol: str = Field(description="Symbol from the provided tradeable list")
    event_headline: str | None = Field(
        default=None,
        description="Exact headline from the recent headlines list, or null",
    )
    reasoning: str
    cards: list[_CardAdvice] = Field(min_length=3, max_length=3)


async def get_advice(
    drawn: list[tuple[TarotCard, str, bool]],
    assets: list[Asset],
    news_items: list[NewsItem] | None = None,
) -> Advice:
    """Never raises: any Gemini failure degrades to the deterministic fallback."""
    try:
        return await asyncio.wait_for(
            _gemini_advice(drawn, assets, news_items or []),
            timeout=ADVICE_TIMEOUT_SECONDS,
        )
    except Exception:
        logger.exception("Gemini advice failed; using deterministic fallback")
        return _fallback_advice(drawn, assets, news_items or [])

async def _gemini_advice(
    drawn: list[tuple[TarotCard, str, bool]],
    assets: list[Asset],
    news_items: list[NewsItem],
) -> Advice:
    from google import genai
    from google.genai import types

    key = get_settings().gemini_api_key
    if not key:
        raise RuntimeError("GEMINI_API_KEY not configured")
    if not assets:
        raise RuntimeError("no assets seeded")

    cards_text = "\n".join(
        f"- {card.name} ({position}{', reversed' if rev else ''}): "
        f"{card.reversed_ if rev else card.upright}"
        for card, position, rev in drawn
    )
    assets_text = "\n".join(f"- {a.symbol}: {a.name}" for a in assets)
    headlines_text = "\n".join(f"- {item.headline}" for item in news_items)
    if not headlines_text:
        headlines_text = "- None available."

    client = genai.Client(api_key=key)
    response = await client.aio.models.generate_content(
        model="gemini-3.8-flash",
        contents=ADVICE_PROMPT.format(
            cards=cards_text,
            assets=assets_text,
            headlines=headlines_text,
        ),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=_GeminiAdvice,
            max_output_tokens=1024,
        ),
    )
    raw = _GeminiAdvice.model_validate_json(response.text)

    # map narratives by position (never positionally — Gemini may reorder)
    narratives = {c.position: c.narrative for c in raw.cards}
    if set(narratives) != set(SPREAD_POSITIONS):
        raise RuntimeError(f"Gemini returned positions {sorted(narratives)}")

    symbol = raw.asset_symbol.strip().upper()
    asset = next((a for a in assets if a.symbol == symbol), None)
    if asset is None:
        raise RuntimeError(f"Gemini chose unknown asset {symbol!r}")

    event = next(
        (item for item in news_items if item.headline == raw.event_headline),
        None,
    )
    reasoning = raw.reasoning.strip()
    if event and event.headline.casefold() not in reasoning.casefold():
        reasoning = (
            f'{reasoning} The spread is interpreted in light of "{event.headline}".'
        ).strip()
    return Advice(
        side=raw.side,
        asset=asset,
        reasoning=reasoning,
        narratives=narratives,
        event_headline=event.headline if event else None,
        event_url=event.url if event else None,
    )


def _fallback_advice(
    drawn: list[tuple[TarotCard, str, bool]],
    assets: list[Asset],
    news_items: list[NewsItem],
) -> Advice:
    score = 0
    for card, _position, rev in drawn:
        verdict = (card.yes_no or "").lower()
        if rev:
            verdict = {"yes": "no", "no": "yes"}.get(verdict, verdict)
        if verdict == "yes":
            score += 1
        elif verdict == "no":
            score -= 1
    side = "long" if score > 0 else "short" if score < 0 else random.choice(["long", "short"])

    event = next(
        (
            (asset, item)
            for item in news_items
            for asset in assets
            if _headline_matches(item.headline, asset)
        ),
        None,
    )
    if event:
        asset = event[0]
        event_headline = event[1].headline
        event_url = event[1].url
    else:
        asset = random.choice(assets) if assets else None
        event_headline = None
        event_url = None
    symbol = asset.symbol if asset else "the market"

    phrases = {
        "past": f"what {symbol} has been through",
        "present": f"the situation {symbol} is in right now",
        "future": f"where {symbol} is heading",
    }
    narratives = {
        position: (
            f"{card.name} ({position}{', reversed' if rev else ''}): "
            f"{card.reversed_ if rev else card.upright}. "
            f"In this spread for {symbol}, this reflects {phrases[position]}."
        )
        for card, position, rev in drawn
    }
    direction = "upward" if side == "long" else "downward"
    reasoning = (
        f"Taken together, the spread tilts {direction} for {symbol}. "
        f"The cards counsel {side}."
    )
    if event_headline:
        reasoning += f' The asset was selected in light of "{event_headline}".'
    return Advice(
        side=side,
        asset=asset,
        reasoning=reasoning,
        narratives=narratives,
        event_headline=event_headline,
        event_url=event_url,
    )


def _headline_matches(headline: str, asset: Asset) -> bool:
    text = headline.casefold()
    terms = (asset.symbol, (asset.name.split() or [""])[0])
    return any(
        term and re.search(rf"\b{re.escape(term.casefold())}\b", text)
        for term in terms
    )
