# Marketplace Feed Manager

**Last updated:** 26.11.2026

Added brand filtering to the VIATEC feed and introduced a separate filtered
Trinity XML feed, available at `GET /feeds/trinity.xml`.

A FastAPI-based service for aggregating, processing, and publishing
product feeds for online marketplaces.

The application automatically downloads product data from multiple
supplier XML feeds, merges it into a single marketplace-compatible feed,
and provides a permanent URL for accessing the generated file.

It also supports manual product feed generation from an uploaded XLSX
file.

## Features

-   Automatic download of multiple supplier XML feeds
-   XML feed aggregation into a single product catalog
-   Brand filtering with separate exclusion lists for VIATEC and Trinity
-   Product data normalization and transformation
-   Generation of marketplace-compatible XML feeds
-   Permanent public URLs for generated feeds
-   Manual XLSX file upload
-   XLSX-to-XML conversion
-   Simple web interface for feed management
-   Error handling for unavailable or invalid supplier feeds
-   Asynchronous request processing with FastAPI
-   Easy integration with Prom.ua and other marketplaces

## How It Works

### Automatic VIATEC feed generation

``` text
Supplier XML feeds
        ↓
Download and parse XML files
        ↓
Normalize product data
        ↓
Merge products into one catalog
        ↓
Exclude products from listed brands
        ↓
Generate the final XML feed
        ↓
Publish the feed using a permanent URL
```

### Brand filtering and Trinity feed generation

| Feed | Excluded brands |
| --- | --- |
| VIATEC | MikroTik, TP-Link |
| Trinity | MikroTik, TP-Link, Hikvision, Dahua, Imou |

Both filters look for brand names anywhere in the XML fields `vendor`,
`name`, and `name_ua`, ignoring case. The filters recognize `TP-Link`,
`TP Link`, and `TPLink` as variants of the same brand.

VIATEC filtering runs after the supplier feeds are merged. The Trinity
generator downloads its source XML from the URL configured in
`TRINITY_PROM_FEED` and saves the filtered result to
`feeds/trinity_feed.xml`. If filtering leaves no products, the update fails
before replacing the existing file.

Run `python update_automatic_feed.py` to refresh both feeds. The web
interface shows each feed's availability and, when the file exists, its size,
last update time, and permanent URL.

### Manual feed generation

``` text
XLSX file
    ↓
Upload through the web interface
    ↓
Validate and process product data
    ↓
Generate XML feed
    ↓
Publish the result using a permanent URL
```

## Tech Stack

-   Python
-   FastAPI
-   Uvicorn
-   Jinja2
-   XML
-   XLSX
-   HTML/CSS
-   Pydantic

## Project Structure

``` text
marketplace-feed-manager/
│
├── app/
│   ├── api/
│   ├── core/
│   ├── services/
│   ├── templates/
│   ├── static/
│   └── main.py
│
├── feeds/
├── uploads/
├── tests/
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation

### Clone the repository

``` bash
git clone https://github.com/Ngayka/marketplace-feed-manager.git
cd marketplace-feed-manager
```

### Create a virtual environment

Windows:

``` bash
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

``` bash
pip install -r requirements.txt
```

## Running

``` bash
uvicorn app.main:app --reload
```

Application:

``` text
http://127.0.0.1:8000
```

Swagger:

``` text
http://127.0.0.1:8000/docs
```

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/` | Open the web interface |
| POST | `/admin/manual-feed` | Upload the manual XLSX feed |
| GET | `/feeds/automatic.xml` | Download the VIATEC XML feed |
| GET | `/feeds/trinity.xml` | Download the filtered Trinity XML feed. Returns `404` if the file has yet to be generated |
| GET | `/feeds/manual.xlsx` | Download the manual XLSX feed |
| GET | `/health` | Check service status and feed availability |
| GET | `/docs` | Open Swagger documentation |

## Future Improvements

-   Celery + Redis
-   Scheduled updates
-   Database support
-   User authentication
-   Docker & Docker Compose
-   Nginx deployment
-   Feed history
-   Telegram notifications

## Author

**Nataliia**

Python Backend Developer

GitHub: https://github.com/Ngayka
