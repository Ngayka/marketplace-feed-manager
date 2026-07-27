from pathlib import Path

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import PlainTextResponse

from services.feed_service import (
    AUTOMATIC_XML_PATH,
    MANUAL_XLSX_PATH,
    FeedError,
    save_manual_feed,
)

import logging

logger = logging.getLogger(__name__)


BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"

app = FastAPI(
    title="Feed Manager",
    description="Керування XML та XLSX-фідами для Prom.ua",
)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.exception(
        "Непередбачена помилка під час запиту %s",
        request.url,
    )

    return PlainTextResponse(
        "Internal Server Error",
        status_code=500,
    )


def build_page_context(
    request: Request,
    message: str | None = None,
    error: str | None = None,
) -> dict:
    return {
        "request": request,
        "message": message,
        "error": error,

        "automatic_feed_url": str(
            request.url_for("automatic_xml_feed")
        ),
        "manual_feed_url": str(
            request.url_for("manual_xlsx_feed")
        ),

        "automatic_feed_exists": AUTOMATIC_XML_PATH.exists(),
        "manual_feed_exists": MANUAL_XLSX_PATH.exists(),

        "automatic_feed_size": (
            AUTOMATIC_XML_PATH.stat().st_size
            if AUTOMATIC_XML_PATH.exists()
            else None
        ),
        "manual_feed_size": (
            MANUAL_XLSX_PATH.stat().st_size
            if MANUAL_XLSX_PATH.exists()
            else None
        ),
    }


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=build_page_context(request),
    )


@app.post("/admin/manual-feed", response_class=HTMLResponse)
async def upload_manual_feed(
    request: Request,
    file: UploadFile = File(...),
):
    filename = file.filename or ""

    if not filename.lower().endswith(".xlsx"):
        await file.close()

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context=build_page_context(
                request,
                error="Оберіть файл із розширенням .xlsx.",
            ),
            status_code=400,
        )

    try:
        save_manual_feed(file.file)

    except FeedError as error:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context=build_page_context(
                request,
                error=str(error),
            ),
            status_code=400,
        )

    except Exception as error:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context=build_page_context(
                request,
                error=f"Не вдалося зберегти файл: {error}",
            ),
            status_code=500,
        )

    finally:
        await file.close()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=build_page_context(
            request,
            message=(
                "XLSX-файл успішно завантажено. "
                "Постійне посилання залишилося незмінним."
            ),
        ),
    )


@app.get("/feeds/automatic.xml",
         name="automatic_xml_feed")
def automatic_feed():
    if not AUTOMATIC_XML_PATH.exists():
        return HTMLResponse(
            content="Автоматичний XML ще не сформовано.",
            status_code=404,
        )

    return FileResponse(
        path=AUTOMATIC_XML_PATH,
        media_type="application/xml",
        filename="automatic_feed.xml",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
        },
    )


@app.get("/feeds/manual.xlsx",
         name="manual_xlsx_feed")
def manual_xlsx_feed():
    if not MANUAL_XLSX_PATH.exists():
        return HTMLResponse(
            content="Ручний XLSX-файл ще не завантажено.",
            status_code=404,
        )

    return FileResponse(
        path=MANUAL_XLSX_PATH,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        filename="manual_feed.xlsx",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
        },
    )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "automatic_feed_exists": AUTOMATIC_XML_PATH.exists(),
        "manual_feed_exists": MANUAL_XLSX_PATH.exists(),
    }
