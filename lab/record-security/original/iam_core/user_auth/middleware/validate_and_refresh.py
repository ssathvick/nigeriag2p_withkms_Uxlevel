from fastapi import Request
from openg2p_fastapi_common.errors.base_exception import BaseAppException
from openg2p_fastapi_common.errors.http_exceptions import UnauthorizedError
from starlette.middleware.base import BaseHTTPMiddleware

from iam_core.schemas import AuthPrincipal

from ..decorators import endpoint_requires_token, endpoint_requires_user
from ..enums import AuthCookieName, cookie_name, RequestStateKey
from ..errors import ExpiredTokenError
from ..helpers.cookie_helper import clear_auth_cookies, set_auth_cookies
from ..helpers.error_response_helper import user_auth_error_response
from ..helpers.auth_user_helper import auth_principal_from_credentials, build_logged_in_user
from ..helpers.route_helper import match_route
from ..helpers.token_helper import (
    REFRESH_FAILED_MESSAGE,
    SESSION_INVALIDATED_MESSAGE,
    access_token_and_id_token_from_request,
    validate_request_token,
)


class ValidateAndRefreshTokenMiddleware(BaseHTTPMiddleware):
    """Validate and refresh tokens, then set ``request.state.auth``.

    Register before ResolvePermissionMiddleware. All token work happens here.
    """

    def __init__(
        self,
        app,
        *,
        state_key: str | RequestStateKey = RequestStateKey.AUTH,
        user_state_key: str | RequestStateKey = RequestStateKey.USER,
    ):
        super().__init__(app)
        self._state_key = str(state_key)
        self._user_state_key = str(user_state_key)

    def _apply_refreshed_tokens_to_request(self, request: Request, token_response: dict) -> None:
        """Patch request headers/cookies so downstream handlers see the new tokens."""
        access_token = token_response["access_token"]
        cookies = dict(request.cookies)
        cookies[cookie_name(AuthCookieName.ACCESS_TOKEN)] = access_token
        id_token = token_response.get("id_token")
        if id_token:
            cookies[cookie_name(AuthCookieName.ID_TOKEN)] = id_token

        cookie_header = "; ".join(f"{k}={v}" for k, v in cookies.items())
        headers = [
            (k, v) for k, v in request.scope["headers"] if k.lower() not in (b"cookie", b"authorization")
        ]
        headers.append((b"authorization", f"Bearer {access_token}".encode("latin-1")))
        headers.append((b"cookie", cookie_header.encode("latin-1")))
        request.scope["headers"] = headers
        # Starlette caches parsed headers/cookies; bust so the handler reads the refreshed values.
        if hasattr(request, "_cookies"):
            delattr(request, "_cookies")
        if hasattr(request, "_headers"):
            delattr(request, "_headers")

    async def _refresh_access_token(self, request: Request) -> dict | None:
        from iam_core.services import AuthService

        # Session cookie holds OIDC sid; refresh tokens are looked up server-side by that id.
        session_id = request.cookies.get(cookie_name(AuthCookieName.SESSION))
        auth_service = AuthService.get_component() or AuthService()
        return await auth_service.refresh_access_token(session_id)

    def _ensure_refresh_session_active(self, request: Request) -> None:
        """Reject requests when the browser session no longer has stored refresh state."""
        session_id = request.cookies.get(cookie_name(AuthCookieName.SESSION))
        if not session_id:
            return

        from iam_core.services import AuthService

        auth_service = AuthService.get_component() or AuthService()
        if not auth_service.has_active_refresh_session(session_id):
            raise UnauthorizedError(message=SESSION_INVALIDATED_MESSAGE)

    async def _authenticate_with_refresh(self, request: Request) -> tuple[AuthPrincipal, dict | None]:
        """Validate tokens; on expiry, refresh via session cookie and re-validate."""
        self._ensure_refresh_session_active(request)
        access_token, id_token = access_token_and_id_token_from_request(request)
        if not access_token:
            raise UnauthorizedError()

        refreshed_tokens: dict | None = None
        try:
            credentials = await validate_request_token(
                request,
                jwt_token=access_token,
                jwt_id_token=id_token,
            )
        except ExpiredTokenError:
            refreshed_tokens = await self._refresh_access_token(request)
            if not refreshed_tokens:
                raise UnauthorizedError(message=REFRESH_FAILED_MESSAGE) from None
            credentials = await validate_request_token(
                request,
                jwt_token=refreshed_tokens["access_token"],
                jwt_id_token=refreshed_tokens.get("id_token"),
            )

        return auth_principal_from_credentials(credentials), refreshed_tokens

    def _attach_refresh_cookies(self, response, refreshed_tokens: dict | None) -> None:
        """Write new token cookies on the response; session cookie is left unchanged."""
        if refreshed_tokens:
            set_auth_cookies(response, refreshed_tokens)

    async def dispatch(self, request: Request, call_next):
        # Skip auth for unmarked routes; protected routes get state.auth (and optionally state.user).
        try:
            matched_route = match_route(request)
            if matched_route is None:
                return await call_next(request)

            endpoint = getattr(matched_route, "endpoint", None)
            if not endpoint_requires_token(endpoint):
                return await call_next(request)

            request.scope["route"] = matched_route

            principal, refreshed_tokens = await self._authenticate_with_refresh(request)
            setattr(request.state, self._state_key, principal)
            if refreshed_tokens:
                self._apply_refreshed_tokens_to_request(request, refreshed_tokens)

            if endpoint_requires_user(endpoint):
                user = await build_logged_in_user(principal)
                setattr(request.state, self._user_state_key, user)

            response = await call_next(request)
            self._attach_refresh_cookies(response, refreshed_tokens)
            return response
        except BaseAppException as exc:
            response = user_auth_error_response(request, exc)
            if isinstance(exc, UnauthorizedError) and exc.message in (
                REFRESH_FAILED_MESSAGE,
                SESSION_INVALIDATED_MESSAGE,
            ):
                clear_auth_cookies(response)
            return response
