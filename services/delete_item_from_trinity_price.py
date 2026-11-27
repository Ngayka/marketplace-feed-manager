import xml.etree.ElementTree as ET
from pathlib import Path

from feed_config import (
    FEEDS_DIR,
    TRINITY_PROM_FEED,
    TRINITY_XML_PATH,
    EXCLUDED_BRANDS_TRINITY,
)
from feed_utils import download_xml
from services.exceptions import FeedError


def filter_trinity_feed() -> Path:
    """
    Завантажує XML-фід Trinity, виключає товари
    за назвами брендів та зберігає результат.
    """
    if not TRINITY_PROM_FEED:
        raise FeedError("Не задано URL XML-фіду Trinity.")

    root = download_xml(TRINITY_PROM_FEED)

    offers = root.find("offers")

    if offers is None:
        raise FeedError(
            "У XML Trinity не знайдено елемент <offers>."
        )

    initial_count = len(offers.findall("offer"))
    removed_count = 0

    for offer in offers.findall("offer"):
        fields = (
            (offer.findtext("vendor") or "").casefold(),
            (offer.findtext("name") or "").casefold(),
            (offer.findtext("name_ua") or "").casefold(),
        )

        if any(
            brand in field
            for brand in EXCLUDED_BRANDS_TRINITY
            for field in fields
        ):
            offers.remove(offer)
            removed_count += 1

    remaining_count = initial_count - removed_count

    if remaining_count == 0:
        raise FeedError("XML-фід Trinity не містить товарів.")

    temporary_path = FEEDS_DIR / "trinity_feed.tmp.xml"

    try:
        tree = ET.ElementTree(root)

        tree.write(
            temporary_path,
            encoding="utf-8",
            xml_declaration=True,
        )

        temporary_path.replace(TRINITY_XML_PATH)

    except OSError as error:
        temporary_path.unlink(missing_ok=True)

        raise FeedError(
            f"Не вдалося зберегти XML-фід Trinity: {error}"
        ) from error

    print(f"Trinity: всього товарів — {initial_count}")
    print(f"Trinity: видалено — {removed_count}")
    print(f"Trinity: залишилось — {remaining_count}")

    return TRINITY_XML_PATH


if __name__ == "__main__":
    path = filter_trinity_feed()
    print(f"Файл збережено: {path}")