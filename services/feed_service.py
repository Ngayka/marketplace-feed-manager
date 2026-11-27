import shutil
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import BinaryIO
from dotenv import load_dotenv

from feed_config import (MANUAL_XLSX_PATH,
                         FEEDS_DIR,
                         AUTOMATIC_FEED_URLS,
                         AUTOMATIC_XML_PATH,
                         AVAILABLE_XML_PATH,
                         EXCLUDED_BRANDS)
from feed_utils import validate_xlsx, download_xml
from services.exceptions import FeedError
from services.get_availabale_code import update_prom_by_availability
from services.merge_available_products import merge_available_products_feeds

load_dotenv()

def save_manual_feed(uploaded_file: BinaryIO) -> Path:
    """
    Зберігає вручну завантажений XLSX-файл.

    Новий файл спочатку зберігається тимчасово.
    Старий файл замінюється лише після успішної перевірки.
    """

    temporary_path = FEEDS_DIR / "safetyhouse_feed.tmp.xlsx"

    try:
        with temporary_path.open("wb") as destination:
            shutil.copyfileobj(uploaded_file, destination)

        validate_xlsx(temporary_path)

        temporary_path.replace(MANUAL_XLSX_PATH)

        return MANUAL_XLSX_PATH

    except FeedError:
        temporary_path.unlink(missing_ok=True)
        raise

    except Exception as error:
        temporary_path.unlink(missing_ok=True)

        raise FeedError(
            f"Не вдалося зберегти XLSX-файл: {error}"
        ) from error


def merge_prom_feeds() -> Path:
    """
    Завантажує XML-фіди Viatec, об'єднує товари,
    виключає товари за назвами брендів та зберігає
    результат у feeds/automatic_feed.xml.
    """

    roots = [
        download_xml(url)
        for url in AUTOMATIC_FEED_URLS
    ]

    first_root = roots[0]
    first_root.set(
        "date",
        datetime.now().strftime("%Y-%m-%d %H:%M"),
    )

    first_shop = first_root.find("shop")

    seen_barcodes = set()
    if first_shop is None:
        raise FeedError(
            "У першому XML не знайдено елемент <shop>."
        )
    first_categories = first_shop.find("categories")
    if first_categories is None:
        raise FeedError("У першом XML не знайдено елемент <category>")
    seen_categories_ids = {category.get("id")
                           for category in first_categories.findall("category")}

    first_offers = first_shop.find("offers")

    if first_offers is None:
        raise FeedError(
            "У першому XML не знайдено елемент <offers>."
        )
    for offer in first_offers:
        barcode = offer.find("barcode")

        if barcode is None or barcode.text is None:
            raise FeedError("Для товару не знайдений артикул")

        barcode_value = barcode.text.strip()
        seen_barcodes.add(barcode_value)

    for root in roots[1:]:
        shop = root.find("shop")

        if shop is None:
            raise FeedError(
                "В одному із XML не знайдено елемент <shop>."
            )
        categories = shop.find("categories")
        if categories is not None:
            for category in categories.findall("category"):
                category_id = category.get("id")

                if category_id not in seen_categories_ids:
                    seen_categories_ids.add(category_id)
                    first_categories.append(category)

        offers = shop.find("offers")

        if offers is None:
            raise FeedError(
                "В одному із XML не знайдено елемент <offers>."
            )

        for offer in list(offers):
            barcode = offer.find("barcode")
            if barcode is None or barcode.text is None:
                raise FeedError("Для товару не знайдений артикул")
            barcode_value = barcode.text.strip()
            if barcode_value in seen_barcodes:
                continue
            seen_barcodes.add(barcode_value)
            first_offers.append(offer)

    for offer in first_offers.findall("offer"):
        fields = (
            (offer.findtext("vendor") or "").casefold(),
            (offer.findtext("name") or "").casefold(),
            (offer.findtext("name_ua") or "").casefold(),
        )

        if any(
                brand in field
                for brand in EXCLUDED_BRANDS
                for field in fields
        ):
            first_offers.remove(offer)

    for offer in first_offers:
        price = offer.find("price")
        currency_id = offer.find("currencyId")

        if price is None or currency_id is None:
            offer.set("available", "false")

    temporary_path = FEEDS_DIR / "viatec_feed.tmp.xml"

    try:
        tree = ET.ElementTree(first_root)

        tree.write(
            temporary_path,
            encoding="utf-8",
            xml_declaration=True,
        )

        temporary_path.replace(AUTOMATIC_XML_PATH)

    except OSError as error:
        temporary_path.unlink(missing_ok=True)

        raise FeedError(
            f"Не вдалося зберегти автоматичний XML-фід: {error}"
        ) from error

    update_prom_by_availability(
        AVAILABLE_XML_PATH,
        AUTOMATIC_XML_PATH,
    )

    return AUTOMATIC_XML_PATH


if __name__ == "__main__":
    merge_available_products_feeds()
    path = merge_prom_feeds()
    print(f"Файл сохранён: {path}")