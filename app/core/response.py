from datetime import datetime, timezone

from fastapi.responses import JSONResponse

from app.core.request_context import get_request_id


def _meta(meta: dict | None = None) -> dict:
    payload = {
        "requestId": get_request_id() or None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if meta:
        payload.update(meta)
    return payload


def ok(data=None, meta=None, status_code: int = 200):
    return JSONResponse(
        status_code=status_code,
        content={
            "data": data,
            "error": None,
            "meta": _meta(meta),
        },
    )


def fail(code: str, message: str, details=None, status_code: int = 400, meta=None):
    return JSONResponse(
        status_code=status_code,
        content={
            "data": None,
            "error": {
                "code": code,
                "message": message,
                "details": details,
            },
            "meta": _meta(meta),
        },
    )
