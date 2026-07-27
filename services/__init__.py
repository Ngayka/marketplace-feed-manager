from pathlib import Path
from typing import BinaryIO
import shutil
import xml.etree.ElementTree as ET

import requests


BASE_DIR = Path(__file__).resolve().parent.parent
FEEDS_DIR = BASE_DIR / "feeds"

AUTOMATIC_FEED_PATH = FEEDS_DIR / "automatic_feed.xml"
MANUAL_FEED_PATH = FEEDS_DIR / "manual_feed.xml"

FEEDS_DIR.mkdir(parents=True, exist_ok=True)


XML_SOURCE_URLS = [
    # Сюди вставимо твої реальні посилання постачальників.
    # Наприклад:
    # "https://example.com/feed1.xml",
    # "https://example.com/feed2.xml",
]


class FeedError(Exception):
    """Помилка під час оброблення XML-фіду."""


def validate_xml(file_path: Path) -> None:
    """
    Перевіряє, що файл є коректним XML.
    """

    try:
        ET.parse(file_path)
    except ET.ParseError as error:
        raise FeedError(f"Файл не є коректним XML: {error}") from error


def save_manual_feed(uploaded_file: BinaryIO) -> Path:
    """
    Зберігає вручну завантажений XML.

    Спочатку файл записується як тимчасовий.
    Поточний XML замінюється лише після успішної перевірки.
    """

    temporary_path = FEEDS_DIR / "manual_feed.tmp"

    try:
        with temporary_path.open("wb") as destination:
            shutil.copyfileobj(uploaded_file, destination)

        if not temporary_path.exists() or temporary_path.stat().st_size == 0:
            raise FeedError("Завантажений файл порожній.")

        validate_xml(temporary_path)

        temporary_path.replace(MANUAL_FEED_PATH)

        return MANUAL_FEED_PATH

    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


def download_xml(url: str) -> bytes:
    """
    Завантажує XML за URL.
    """

    try:
        response = requests.get(
            url,
            timeout=120,
            headers={
                "User-Agent": "Marketplace-XML-Feed-Manager/1.0",
            },
        )
        response.raise_for_status()

    except requests.RequestException as error:
        raise FeedError(
            f"Не вдалося завантажити XML: {url}. Помилка: {error}"
        ) from error

    if not response.content:
        raise FeedError(f"Отримано порожню відповідь: {url}")

    return response.content


def merge_automatic_feeds() -> Path:
    """
    Завантажує XML-фіди постачальників та створює один спільний файл.
    """

    if not XML_SOURCE_URLS:
        raise FeedError(
            "Не задано жодного XML-посилання в XML_SOURCE_URLS."
        )

    merged_root = None
    successfully_loaded = 0

    for url in XML_SOURCE_URLS:
        print(f"Завантаження: {url}")

        try:
            xml_content = download_xml(url)
            source_root = ET.fromstring(xml_content)

        except (FeedError, ET.ParseError) as error:
            print(f"Помилка: {error}")
            continue

        if merged_root is None:
            merged_root = ET.Element(source_root.tag, source_root.attrib)

        for child in source_root:
            merged_root.append(child)

        successfully_loaded += 1
        print(f"Успішно: {url}")

    if merged_root is None or successfully_loaded == 0:
        raise FeedError(
            "Не вдалося завантажити жодного коректного XML."
        )

    temporary_path = FEEDS_DIR / "automatic_feed.tmp"

    try:
        tree = ET.ElementTree(merged_root)

        tree.write(
            temporary_path,
            encoding="utf-8",
            xml_declaration=True,
        )

        validate_xml(temporary_path)

        temporary_path.replace(AUTOMATIC_FEED_PATH)

    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise

    print(f"Файл збережено: {AUTOMATIC_FEED_PATH}")
    print(f"Оброблено джерел: {successfully_loaded}")

    return AUTOMATIC_FEED_PATH
