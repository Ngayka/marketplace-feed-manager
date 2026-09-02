import xml.etree.ElementTree as ET


def normalize_availability(offer):
    status_param = offer.find("./param[@name='Наявність']")

    if status_param is None or not status_param.text:
        return

    status = status_param.text.strip()

    if status in {"У резерві", "Передзамовлення"} or status.startswith(
        "Очікується"
    ):
        offer.set("available", "false")

    elif status == "Закінчується":
        offer.set("available", "true")

        stock_quantity = offer.find("stock_quantity")

        if stock_quantity is None:
            stock_quantity = ET.SubElement(
                offer,
                "stock_quantity",
            )

        stock_quantity.text = "9"
