"""Import the Deckaura 78-card tarot dataset into tarot_cards.

Idempotent: upserts by card name. Usage:

    uv run python scripts/import_cards.py <dataset.json>

The Zenodo record (https://zenodo.org/records/19475329) ships CSV/JSONL/JSON;
export any of them to a JSON array of card objects and pass the path.
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Key in dataset file -> (model attribute, transform)
FIELD_MAP: dict[str, tuple[str, object]] = {
    "name": ("name", str),
    "arcana": ("arcana", lambda v: str(v).lower()),
    "suit": ("suit", str),
    "rank": ("rank", str),
    "upright": ("upright", str),
    "reversed": ("reversed_", str),
    "love": ("love", str),
    "career": ("career", str),
    "yes_no": ("yes_no", str),
    "element": ("element", str),
    "zodiac": ("zodiac", str),
    "guide_url": ("guide_url", str),
    # image_path is not in the dataset; set it manually after adding images.
}

REQUIRED = {"name", "arcana", "upright", "reversed", "love", "career", "yes_no"}


def load_cards(path: Path) -> list[dict]:
    data = json.loads(path.read_text())
    if isinstance(data, dict):  # some exports wrap the array under a key
        data = next((v for v in data.values() if isinstance(v, list)), [])
    if not isinstance(data, list):
        raise SystemExit(f"{path} does not contain a JSON array of cards")
    return data


async def main(path: Path) -> None:
    from sqlalchemy import select

    from app.db import Base, SessionLocal, engine
    from app.models import TarotCard

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    raw_cards = load_cards(path)
    imported = 0
    async with SessionLocal() as session:
        existing = {
            c.name.lower(): c
            for c in (await session.scalars(select(TarotCard))).all()
        }
        for raw in raw_cards:
            attrs: dict = {}
            for key, (attr, transform) in FIELD_MAP.items():
                if raw.get(key) is not None:
                    attrs[attr] = transform(raw[key])
            missing = {k for k in REQUIRED if raw.get(k) is None}
            if missing:
                raise SystemExit(f"card {raw.get('name', '?')!r} missing fields: {missing}")
            card = existing.get(attrs["name"].lower())
            if card is None:
                session.add(TarotCard(**attrs))
                imported += 1
            else:
                for attr, value in attrs.items():
                    setattr(card, attr, value)
        await session.commit()
    print(f"imported {imported} new cards, updated {len(raw_cards) - imported}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    asyncio.run(main(Path(sys.argv[1])))
