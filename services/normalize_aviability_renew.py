import xml.etree.ElementTree as ET


def normalize_availability(product):
    stock = product.findtext("stock")

    if stock == "few":
        stock_quantity = product.find("stock_quantity")

        if stock_quantity is None:
            stock_quantity = ET.SubElement(
                product,
                "stock_quantity",
            )

        stock_quantity.text = "5"