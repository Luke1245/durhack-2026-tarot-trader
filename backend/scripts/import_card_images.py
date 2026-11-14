"""Convert Rider–Waite card scans to WebP and backfill tarot_cards.image_path.

Matches files to database cards by normalized name:
- Majors:  "00_Fool.jpg"        <-> "The Fool"          (NN_ prefix + optional "the ")
- Minors:  "Wands01.jpg"        <-> "Ace of Wands"      (suit + rank number; Pents = Pentacles)

Usage:
    uv run python scripts/import_card_images.py /Users/user/Desktop/rider-waite/720px
"""

import asyncio
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image

OUT_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "public" / "cards"
SIZE = (300, 500)

RANKS = {
    "01": "ace", "02": "two", "03": "three", "04": "four", "05": "five",
    "06": "six", "07": "seven", "08": "eight", "09": "nine", "10": "ten",
    "11": "page", "12": "knight", "13": "queen", "14": "king",
}


def normalize_card_name(name: str) -> str:
    """'The Fool' -> 'fool', 'Ace of Wands' -> 'ace_of_wands'."""
    n = name.lower().removeprefix("the ")
    return n.replace(" ", "_")


def file_stem_to_key(stem: str) -> str | None:
    """'00_Fool' -> 'fool', 'Wands01' -> 'ace_of_wands', 'Cover' -> None."""
    if m := re.fullmatch(r"\d{2}_(.+)", stem):
        return m.group(1).lower()
    if m := re.fullmatch(r"(Wands|Cups|Swords|Pents|Pentacles)(\d{2})", stem):
        suit = "pentacles" if m.group(1) == "Pents" else m.group(1).lower()
        return f"{RANKS[m.group(2)]}_of_{suit}"
    return None


def slugify(name: str) -> str:
    return name.lower().replace(" ", "-")


def convert(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as img:
        img = img.convert("RGB").resize(SIZE, Image.LANCZOS)
        img.save(dest, "WEBP", quality=80)


async def main(source_dir: Path) -> None:
    from sqlalchemy import select

    from app.db import SessionLocal
    from app.models import TarotCard

    sources: dict[str, Path] = {}
    for f in source_dir.iterdir():
        if key := file_stem_to_key(f.stem):
            sources[key] = f
    if len(sources) != 78:
        raise SystemExit(f"expected 78 source cards, found {len(sources)} in {source_dir}")

    async with SessionLocal() as session:
        cards = (await session.scalars(select(TarotCard))).all()
        if len(cards) != 78:
            raise SystemExit(f"tarot_cards has {len(cards)} rows; seed 78 first")
        updated = 0
        for card in cards:
            key = normalize_card_name(card.name)
            src = sources.get(key)
            if src is None:
                print(f"!! no source file for {card.name!r} (key {key!r})")
                continue
            slug = slugify(card.name)
            convert(src, OUT_DIR / f"{slug}.webp")
            card.image_path = f"/cards/{slug}.webp"
            updated += 1
        await session.commit()
    print(f"converted {updated} cards -> {OUT_DIR} at {SIZE[0]}x{SIZE[1]} webp")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    asyncio.run(main(Path(sys.argv[1])))
