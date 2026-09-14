import zipfile
import urllib.error
import urllib.request
from pathlib import Path

from services.exceptions import FeedError
import xml.etree.ElementTree as ET


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
