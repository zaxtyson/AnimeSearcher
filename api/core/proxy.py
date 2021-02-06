from quart import Response

from api.core.helper import HtmlParseHelper

__all__ = ["RequestProxy"]


class RequestProxy(HtmlParseHelper):

    async def make_response(self, url: str) -> Response:
        """代理访问远程请求"""
        await self.init_session()
        resp = await self.get(url, allow_redirects=True)
        if not resp or resp.status != 200:
            return Response("resource maybe not available", status=404)
        data = await resp.read()
        resp_headers = {
            "Server": "API-Proxy",
            "Content-Type": resp.content_type
        }
        return Response(data, headers=resp_headers, status=200)

    async def close(self):
        await self.close_session()
