from pathlib import Path
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

from feed_utils import download_xml
from feed_config import AVAILABLE_FEED_URLS, AVAILABLE_XML_PATH
from services import FEEDS_DIR
from services.exceptions import FeedError


load_dotenv()

def merge_available_products_feeds() -> Path:
    """
    Об'єднує XML-фіди Viatec з товарами в наявності.

    Товари ідентифікуються за <code>.
    Дублікати не додаються.
    """

    roots = [
        download_xml(url)
        for url in AVAILABLE_FEED_URLS
    ]

    first_root = roots[0]

    if first_root.tag != "sitedata":
        raise FeedError(
            "У першому XML кореневий елемент не <sitedata>."
        )

    first_sitedata = first_root

    first_products = first_sitedata.find("products")

    if first_products is None:
        raise FeedError(
            "У першому XML не знайдено елемент <products>."
        )

    seen_codes = set()

    for product in first_products:
        code = product.find("code")

        if code is None or not code.text:
            raise FeedError(
                "Для товару не знайдений артикул <code>."
            )

        seen_codes.add(code.text.strip())

    for root in roots[1:]:
        if root.tag != "sitedata":
            raise FeedError(
                "В одному із XML кореневий елемент не <sitedata>."
            )

        sitedata = root

        products = sitedata.find("products")

        if products is None:
            raise FeedError(
                "В одному із XML не знайдено елемент <products>."
            )

        for product in list(products):
            code = product.find("code")

            if code is None or not code.text:
                raise FeedError(
                    "Для товару не знайдений артикул <code>."
                )

            code_value = code.text.strip()

            if code_value in seen_codes:
                continue

            seen_codes.add(code_value)
            first_products.append(product)
    temporary_path = FEEDS_DIR / "viatec_available.tmp.xml"

    try:
        tree = ET.ElementTree(first_root)

        tree.write(
            temporary_path,
            encoding="utf-8",
            xml_declaration=True,
        )

        temporary_path.replace(AVAILABLE_XML_PATH)

    except OSError as error:
        temporary_path.unlink(missing_ok=True)

        raise FeedError(
            f"Не вдалося зберегти XML-фід: {error}"
        ) from error

    return AVAILABLE_XML_PATH