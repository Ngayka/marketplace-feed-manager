from pathlib import Path
import xml.etree.ElementTree as ET

from services.exceptions import FeedError


def update_prom_by_availability(
    available_xml_path: Path,
    automatic_xml_path: Path,
) -> None:
    available_tree = ET.parse(available_xml_path)
    available_root = available_tree.getroot()

    prom_tree = ET.parse(automatic_xml_path)
    prom_root = prom_tree.getroot()

    if available_root.tag != "sitedata":
        raise FeedError(
            "У available XML кореневий елемент не <sitedata>."
        )

    products = available_root.find("products")
    if products is None:
        raise FeedError(
            "У available XML не знайдено <products>."
        )

    shop = prom_root.find("shop")
    if shop is None:
        raise FeedError(
            "У Prom XML не знайдено <shop>."
        )

    offers = shop.find("offers")
    if offers is None:
        raise FeedError(
            "У Prom XML не знайдено <offers>."
        )

    availability = {
        product.findtext("code").strip(): product.findtext("stock")
        for product in products
        if product.findtext("code")
    }

    for offer in list(offers):
        barcode = offer.findtext("barcode")

        if not barcode:
            continue

        barcode = barcode.strip()
        stock = availability.get(barcode)

        if stock == "few":
            stock_quantity = offer.find("stock_quantity")

            if stock_quantity is None:
                stock_quantity = ET.SubElement(
                    offer,
                    "stock_quantity",
                )

            stock_quantity.text = "5"

        elif stock == "yes":
            stock_quantity = offer.find("stock_quantity")

            if stock_quantity is not None:
                offer.remove(stock_quantity)

        else:
            offers.remove(offer)

    prom_tree.write(
        automatic_xml_path,
        encoding="utf-8",
        xml_declaration=True,
    )