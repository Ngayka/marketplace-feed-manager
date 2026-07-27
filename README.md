# Marketplace Feed Manager

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

### Automatic feed generation

``` text
Supplier XML feeds
        ↓
Download and parse XML files
        ↓
Normalize product data
        ↓
Merge products into one catalog
        ↓
Generate the final XML feed
        ↓
Publish the feed using a permanent URL
```

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

  Method   Endpoint                    Description
  -------- --------------------------- -------------------------
  GET      /                           Open web interface
  POST     /feeds/generate             Generate automatic feed
  POST     /feeds/upload               Upload XLSX
  GET      /feeds/automatic_feed.xml   Download automatic feed
  GET      /feeds/manual_feed.xml      Download manual feed
  GET      /docs                       Swagger documentation

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
