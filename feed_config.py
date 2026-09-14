import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)

FEEDS_DIR = BASE_DIR / "feeds"

AUTOMATIC_XML_PATH = FEEDS_DIR / "automatic_feed.xml"
MANUAL_XLSX_PATH = FEEDS_DIR / "manual_feed.xlsx"
AVAILABLE_XML_PATH = FEEDS_DIR / "available_feed.xml"

FEEDS_DIR.mkdir(parents=True, exist_ok=True)


AUTOMATIC_FEED_URLS = [
    os.environ["VIATEC_PROM_FEED_1"],
    os.environ["VIATEC_PROM_FEED_2"],
    os.environ["VIATEC_PROM_FEED_3"],
    # os.environ["VIATEC_FEED_4"],
]

AVAILABLE_FEED_URLS = [
    os.environ["VIATEC_AVAILABLE_FEED_1"],
    os.environ["VIATEC_AVAILABLE_FEED_2"],
    os.environ["VIATEC_AVAILABLE_FEED_3"],
    # os.environ["VIATEC_FEED_4"],
]
