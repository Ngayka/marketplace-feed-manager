import os
from pathlib import Path
from typing import BinaryIO
from dotenv import load_dotenv
import shutil
import zipfile
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()
FEEDS_DIR = BASE_DIR / "feeds"

AUTOMATIC_XML_PATH = FEEDS_DIR / "automatic_feed.xml"
MANUAL_XLSX_PATH = FEEDS_DIR / "manual_feed.xlsx"

FEEDS_DIR.mkdir(parents=True, exist_ok=True)


AUTOMATIC_FEED_URLS = [
    os.environ["VIATEC_FEED_1"],
    os.environ["VIATEC_FEED_2"],
    os.environ["VIATEC_FEED_3"],
    os.environ["VIATEC_FEED_4"],
]


class FeedError(Exception):
    """Помилка під час оброблення фіда."""


def validate_xlsx(file_path: Path) -> None:
    """
    Перевіряє, що файл є коректним XLSX-документом.

    XLSX технічно є ZIP-архівом із внутрішніми XML-файлами.
    """

    if not file_path.exists():
        raise FeedError("Завантажений файл не знайдено.")

    if file_path.stat().st_size == 0:
        raise FeedError("Завантажений файл порожній.")

    if not zipfile.is_zipfile(file_path):
        raise FeedError(
            "Файл не є коректним XLSX-документом."
        )

    try:
        with zipfile.ZipFile(file_path, "r") as archive:
            filenames = set(archive.namelist())

            required_files = {
                "[Content_Types].xml",
                "xl/workbook.xml",
            }

            missing_files = required_files - filenames

            if missing_files:
                raise FeedError(
                    "Файл не має коректної структури XLSX."
                )

            damaged_file = archive.testzip()

            if damaged_file is not None:
                raise FeedError(
                    f"XLSX-файл пошкоджений: {damaged_file}"
                )

    except zipfile.BadZipFile as error:
        raise FeedError(
            "Не вдалося прочитати XLSX-файл."
        ) from error


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


def download_xml(url: str) -> ET.Element:
    """
    Завантажує XML за URL та повертає кореневий елемент.
    """

    try:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0",
            },
        )

        with urllib.request.urlopen(
            request,
            timeout=60,
        ) as response:
            content = response.read()

    except urllib.error.HTTPError as error:
        raise FeedError(
            f"Сервер повернув помилку {error.code} для URL: {url}"
        ) from error

    except urllib.error.URLError as error:
        raise FeedError(
            f"Не вдалося завантажити XML за URL {url}: "
            f"{error.reason}"
        ) from error

    except TimeoutError as error:
        raise FeedError(
            f"Перевищено час очікування для URL: {url}"
        ) from error

    try:
        return ET.fromstring(content)

    except ET.ParseError as error:
        raise FeedError(
            f"За URL отримано некоректний XML: {url}. "
            f"Помилка: {error}"
        ) from error


def merge_automatic_feeds() -> Path:
    """
    Завантажує три XML-фіди Viatec, об'єднує товари
    та зберігає результат у feeds/automatic_feed.xml.
    """

    roots = [
        download_xml(url)
        for url in AUTOMATIC_FEED_URLS
    ]

    first_root = roots[0]

    first_shop = first_root.find("shop")

    if first_shop is None:
        raise FeedError(
            "У першому XML не знайдено елемент <shop>."
        )

    first_offers = first_shop.find("offers")

    if first_offers is None:
        raise FeedError(
            "У першому XML не знайдено елемент <offers>."
        )

    for root in roots[1:]:
        shop = root.find("shop")

        if shop is None:
            raise FeedError(
                "В одному із XML не знайдено елемент <shop>."
            )

        offers = shop.find("offers")

        if offers is None:
            raise FeedError(
                "В одному із XML не знайдено елемент <offers>."
            )

        for offer in list(offers):
            first_offers.append(offer)

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

    return AUTOMATIC_XML_PATH