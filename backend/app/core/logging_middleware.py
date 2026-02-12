import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("incube.requests")

MAX_REQUEST_BODY_LOG_LENGTH = 1000

# Methods that typically carry a request body
BODY_METHODS = {"POST", "PUT", "PATCH"}

# Paths to skip logging (e.g. health checks to avoid noise)
SKIP_PATHS = {"/api/health"}


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs request/response details and timing for every HTTP call."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in SKIP_PATHS:
            return await call_next(request)

        request_id = getattr(request.state, "request_id", "unknown")
        start_time = time.monotonic()

        # --- Log the incoming request ---
        request_body = await self._get_request_body(request)
        self._log_request(request, request_id, request_body)

        # --- Call the next middleware / route handler ---
        response: Response | None = None
        error_detail: str | None = None
        try:
            response = await call_next(request)
        except Exception as exc:
            elapsed_ms = (time.monotonic() - start_time) * 1000
            error_detail = f"{type(exc).__name__}: {exc}"
            logger.error(
                "[%s] UNHANDLED EXCEPTION | %s %s | %.1fms | %s",
                request_id,
                request.method,
                request.url.path,
                elapsed_ms,
                error_detail,
            )
            raise

        elapsed_ms = (time.monotonic() - start_time) * 1000

        # --- Read response body for error responses ---
        response_body: str | None = None
        if response.status_code >= 400:
            response_body = await self._get_response_body(response)

        self._log_response(request, response, request_id, elapsed_ms, response_body)

        return response

    async def _get_request_body(self, request: Request) -> str | None:
        """Read and return the request body for methods that carry one."""
        if request.method not in BODY_METHODS:
            return None
        try:
            body_bytes = await request.body()
            if not body_bytes:
                return None
            body_str = body_bytes.decode("utf-8", errors="replace")
            if len(body_str) > MAX_REQUEST_BODY_LOG_LENGTH:
                return body_str[:MAX_REQUEST_BODY_LOG_LENGTH] + f"... [truncated, total {len(body_str)} chars]"
            return body_str
        except Exception:
            return "[error reading body]"

    async def _get_response_body(self, response: Response) -> str | None:
        """Read the full response body from a StreamingResponse for error logging."""
        try:
            body_parts: list[bytes] = []
            async for chunk in response.body_iterator:  # type: ignore[union-attr]
                if isinstance(chunk, str):
                    body_parts.append(chunk.encode("utf-8"))
                else:
                    body_parts.append(chunk)

            full_body = b"".join(body_parts)

            # Rebuild the body iterator so the client still receives the response
            async def replay_body():
                yield full_body

            response.body_iterator = replay_body()  # type: ignore[assignment]

            return full_body.decode("utf-8", errors="replace")
        except Exception:
            return "[error reading response body]"

    def _log_request(self, request: Request, request_id: str, body: str | None) -> None:
        has_auth = "Authorization" in request.headers
        query = str(request.url.query) if request.url.query else None

        parts = [
            f"[{request_id}] REQUEST  | {request.method} {request.url.path}",
        ]
        if query:
            parts.append(f"  query_params={query}")
        parts.append(f"  auth={'present' if has_auth else 'absent'}")
        if body is not None:
            parts.append(f"  body={body}")

        logger.info("\n".join(parts))

    def _log_response(
        self,
        request: Request,
        response: Response,
        request_id: str,
        elapsed_ms: float,
        response_body: str | None,
    ) -> None:
        status = response.status_code
        level = logging.WARNING if 400 <= status < 500 else logging.ERROR if status >= 500 else logging.INFO

        parts = [
            f"[{request_id}] RESPONSE | {request.method} {request.url.path} | {status} | {elapsed_ms:.1f}ms",
        ]
        if response_body is not None:
            parts.append(f"  response_body={response_body}")

        logger.log(level, "\n".join(parts))
