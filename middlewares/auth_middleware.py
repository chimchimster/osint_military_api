import json

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Message

from database import get_auth_key_hash


class AuthMiddleware(BaseHTTPMiddleware):

    def __init__(self, app):
        super().__init__(app)

    async def set_body(self, request: Request):
        receive_ = await request._receive()

        async def receive() -> Message:
            return receive_

        request._receive = receive

    async def dispatch(self, request: Request, call_next):

        await self.set_body(request)

        req_auth_key_hash = request.headers.get('authorization')

        json_body = await request.json()

        moderator_id = json_body.get('user_id')

        auth_key_hash = await get_auth_key_hash(moderator_id)

        if req_auth_key_hash != auth_key_hash:
            raise HTTPException(status_code=401, detail='Не авторизован.')

        return await call_next(request)

