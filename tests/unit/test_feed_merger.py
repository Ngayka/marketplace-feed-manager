from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

from services import feed_service
from services.feed_service import FeedError


FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def load_xml(filename: str) -> ET.Element:
    """
    Загружает XML-фикстуру и возвращает корневой элемент.
    """
    return ET.parse(FIXTURES_DIR / filename).getroot()


def get_offers(xml_path: Path) -> list[ET.Element]:
    """
    Возвращает все элементы <offer> из сохранённого XML.
    """
    root = ET.parse(xml_path).getroot()

    return root.findall("./shop/offers/offer")


def test_merge_automatic_feeds_combines_all_offers(
    monkeypatch,
    tmp_path,
):
    """
    В каждой фикстуре находится по три товара.

    После объединения трёх XML должно быть девять товаров.
    """

    roots = [
        load_xml("viatec_video.xml"),
        load_xml("viatec_network.xml"),
        load_xml("viatec_intercom.xml"),
    ]

    def fake_download_xml(url: str) -> ET.Element:
        return roots.pop(0)

    output_path = tmp_path / "automatic_feed.xml"

    monkeypatch.setattr(
        feed_service,
        "download_xml",
        fake_download_xml,
    )
    monkeypatch.setattr(
        feed_service,
        "AUTOMATIC_XML_PATH",
        output_path,
    )
    monkeypatch.setattr(
        feed_service,
        "FEEDS_DIR",
        tmp_path,
    )

    result = feed_service.merge_automatic_feeds()

    offers = get_offers(result)

    assert result == output_path
    assert output_path.exists()
    assert len(offers) == 9


def test_merge_contains_offers_from_every_feed(
    monkeypatch,
    tmp_path,
):
    roots = [
        load_xml("viatec_video.xml"),
        load_xml("viatec_network.xml"),
        load_xml("viatec_intercom.xml"),
    ]

    def fake_download_xml(url: str) -> ET.Element:
        return roots.pop(0)

    output_path = tmp_path / "automatic_feed.xml"

    monkeypatch.setattr(
        feed_service,
        "download_xml",
        fake_download_xml,
    )
    monkeypatch.setattr(
        feed_service,
        "AUTOMATIC_XML_PATH",
        output_path,
    )
    monkeypatch.setattr(
        feed_service,
        "FEEDS_DIR",
        tmp_path,
    )

    result = feed_service.merge_automatic_feeds()

    offers = get_offers(result)

    offer_ids = {
        offer.attrib["id"]
        for offer in offers
    }

    assert "100001" in offer_ids
    assert "101083" in offer_ids
    assert "100056" in offer_ids


def test_merge_preserves_available_attribute(
    monkeypatch,
    tmp_path,
):
    roots = [
        load_xml("viatec_video.xml"),
        load_xml("viatec_network.xml"),
        load_xml("viatec_intercom.xml"),
    ]

    def fake_download_xml(url: str) -> ET.Element:
        return roots.pop(0)

    output_path = tmp_path / "automatic_feed.xml"

    monkeypatch.setattr(
        feed_service,
        "download_xml",
        fake_download_xml,
    )
    monkeypatch.setattr(
        feed_service,
        "AUTOMATIC_XML_PATH",
        output_path,
    )
    monkeypatch.setattr(
        feed_service,
        "FEEDS_DIR",
        tmp_path,
    )

    result = feed_service.merge_automatic_feeds()

    offers_by_id = {
        offer.attrib["id"]: offer
        for offer in get_offers(result)
    }

    assert offers_by_id["100001"].attrib["available"] == "false"
    assert offers_by_id["100002"].attrib["available"] == "true"


def test_merge_preserves_offer_without_price(
    monkeypatch,
    tmp_path,
):
    roots = [
        load_xml("viatec_video.xml"),
        load_xml("viatec_network.xml"),
        load_xml("viatec_intercom.xml"),
    ]

    def fake_download_xml(url: str) -> ET.Element:
        return roots.pop(0)

    output_path = tmp_path / "automatic_feed.xml"

    monkeypatch.setattr(
        feed_service,
        "download_xml",
        fake_download_xml,
    )
    monkeypatch.setattr(
        feed_service,
        "AUTOMATIC_XML_PATH",
        output_path,
    )
    monkeypatch.setattr(
        feed_service,
        "FEEDS_DIR",
        tmp_path,
    )

    result = feed_service.merge_automatic_feeds()

    offers_by_id = {
        offer.attrib["id"]: offer
        for offer in get_offers(result)
    }

    offer = offers_by_id["100001"]

    assert offer.findtext("name") == (
        "VD-920B Відеокамера купольна чорно-біла"
    )
    assert offer.find("price") is None
    assert offer.find("currencyId") is None


def test_merge_handles_empty_additional_feeds(
    monkeypatch,
    tmp_path,
):
    roots = [
        load_xml("viatec_video.xml"),
        load_xml("empty_feed.xml"),
        load_xml("empty_feed.xml"),
    ]

    def fake_download_xml(url: str) -> ET.Element:
        return roots.pop(0)

    output_path = tmp_path / "automatic_feed.xml"

    monkeypatch.setattr(
        feed_service,
        "download_xml",
        fake_download_xml,
    )
    monkeypatch.setattr(
        feed_service,
        "AUTOMATIC_XML_PATH",
        output_path,
    )
    monkeypatch.setattr(
        feed_service,
        "FEEDS_DIR",
        tmp_path,
    )

    result = feed_service.merge_automatic_feeds()

    offers = get_offers(result)

    assert len(offers) == 3


def test_merge_creates_valid_xml(
    monkeypatch,
    tmp_path,
):
    roots = [
        load_xml("viatec_video.xml"),
        load_xml("viatec_network.xml"),
        load_xml("viatec_intercom.xml"),
    ]

    def fake_download_xml(url: str) -> ET.Element:
        return roots.pop(0)

    output_path = tmp_path / "automatic_feed.xml"

    monkeypatch.setattr(
        feed_service,
        "download_xml",
        fake_download_xml,
    )
    monkeypatch.setattr(
        feed_service,
        "AUTOMATIC_XML_PATH",
        output_path,
    )
    monkeypatch.setattr(
        feed_service,
        "FEEDS_DIR",
        tmp_path,
    )

    result = feed_service.merge_automatic_feeds()

    root = ET.parse(result).getroot()

    assert root.tag == "yml_catalog"
    assert root.find("shop") is not None
    assert root.find("./shop/offers") is not None


def test_merge_raises_error_when_first_feed_has_no_shop(
    monkeypatch,
    tmp_path,
):
    invalid_root = ET.fromstring(
        """
        <yml_catalog>
            <offers />
        </yml_catalog>
        """
    )

    roots = [
        invalid_root,
        load_xml("viatec_network.xml"),
        load_xml("viatec_intercom.xml"),
    ]

    def fake_download_xml(url: str) -> ET.Element:
        return roots.pop(0)

    monkeypatch.setattr(
        feed_service,
        "download_xml",
        fake_download_xml,
    )
    monkeypatch.setattr(
        feed_service,
        "AUTOMATIC_XML_PATH",
        tmp_path / "automatic_feed.xml",
    )
    monkeypatch.setattr(
        feed_service,
        "FEEDS_DIR",
        tmp_path,
    )

    with pytest.raises(
        FeedError,
        match="У першому XML не знайдено елемент <shop>",
    ):
        feed_service.merge_automatic_feeds()


def test_merge_raises_error_when_first_feed_has_no_offers(
    monkeypatch,
    tmp_path,
):
    invalid_root = ET.fromstring(
        """
        <yml_catalog>
            <shop>
                <name>VIATEC</name>
            </shop>
        </yml_catalog>
        """
    )

    roots = [
        invalid_root,
        load_xml("viatec_network.xml"),
        load_xml("viatec_intercom.xml"),
    ]

    def fake_download_xml(url: str) -> ET.Element:
        return roots.pop(0)

    monkeypatch.setattr(
        feed_service,
        "download_xml",
        fake_download_xml,
    )
    monkeypatch.setattr(
        feed_service,
        "AUTOMATIC_XML_PATH",
        tmp_path / "automatic_feed.xml",
    )
    monkeypatch.setattr(
        feed_service,
        "FEEDS_DIR",
        tmp_path,
    )

    with pytest.raises(
        FeedError,
        match="У першому XML не знайдено елемент <offers>",
    ):
        feed_service.merge_automatic_feeds()
