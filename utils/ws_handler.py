import asyncio
import json
from asyncio import Lock
from logging import Handler, LogRecord

from sanic.server.websockets.impl import WebsocketImplProtocol

__all__ = ["ws_log_handler"]


class WebsocketHandler(Handler):

    def __init__(self):
        super().__init__()
        self._lock = Lock()
        self._users = set()

    def emit(self, record: LogRecord) -> None:
        asyncio.create_task(self.broadcast(record))

    async def register(self, ws: WebsocketImplProtocol):
        # print(f"Register {ws}")
        async with self._lock:
            if ws not in self._users:
                self._users.add(ws)

    async def unregister(self, ws: WebsocketImplProtocol):
        # print(f"Unregister {ws}")
        async with self._lock:
            if ws in self._users:
                self._users.remove(ws)

    async def broadcast(self, record: LogRecord):
        for u in self._users:
            text = json.dumps({
                "level": record.levelname,
                "datetime": record.asctime,
                "filename": record.filename,
                "lineno": record.lineno,
                "message": record.message
            }, ensure_ascii=False)
            await u.send(text)


# global handler
ws_log_handler = WebsocketHandler()
