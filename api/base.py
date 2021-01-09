import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, TypeVar, Callable, Optional, Dict

import requests
from flask import request, Response
from lxml import etree
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from zhconv import convert

from api.logger import logger
from api.models import AnimeDetailInfo, AnimeMetaInfo, Video, DanmakuMetaInfo, DanmakuCollection

__all__ = ["HtmlParseHelper", "VideoHandler", "BaseEngine", "DanmakuEngine"]


class HtmlParseHelper(object):
    """辅助引擎处理网页提取数据的类"""

    _headers = {
        "User-Agent": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }
    disable_warnings(InsecureRequestWarning)  # 全局禁用 SSL 警告

    @staticmethod
    def head(url: str, params=None, allow_redirects=True, **kwargs) -> requests.Response:
        """封装 HEAD 方法, 默认开启 302 重定向, 用于获取目标直链"""
        try:
            logger.debug(f"url: {url}, params: {params}, allow_redirects: {allow_redirects}")
            kwargs.setdefault("timeout", 10)
            kwargs.setdefault("headers", HtmlParseHelper._headers)
            return requests.head(url, params=params, verify=False, allow_redirects=allow_redirects, **kwargs)
        except requests.Timeout as e:
            logger.warning(e)
            return requests.Response()
        except requests.RequestException as e:
            logger.exception(e)
            return requests.Response()

    @staticmethod
    def get(url: str, params=None, html_encoding="utf-8", **kwargs) -> requests.Response:
        """封装 GET 方法, 默认网页编码为 utf-8"""
        try:
            logger.debug(f"url: {url}, params: {params}")
            kwargs.setdefault("timeout", 5)
            kwargs.setdefault("headers", HtmlParseHelper._headers)
            ret = requests.get(url, params, verify=False, **kwargs)
            ret.encoding = html_encoding  # 有些网页仍然使用 gb2312/gb18030 之类的编码, 需要单独设置
            return ret
        except requests.Timeout as e:
            logger.warning(e)
            return requests.Response()
        except requests.RequestException as e:
            logger.exception(e)
            return requests.Response()

    @staticmethod
    def post(url: str, data=None, html_encoding="utf-8", **kwargs) -> requests.Response:
        """"封装 POST 方法, 默认网页编码为 utf-8"""
        try:
            logger.debug(f"url: {url}, data: {data}")
            kwargs.setdefault("timeout", 5)
            kwargs.setdefault("headers", HtmlParseHelper._headers)
            ret = requests.post(url, data, verify=False, **kwargs)
            ret.encoding = html_encoding
            return ret
        except requests.Timeout as e:
            logger.warning(e)
            return requests.Response()
        except requests.RequestException as e:
            logger.exception(e)
            return requests.Response()

    @staticmethod
    def xpath(html: str, xpath: str) -> Optional[etree.Element]:
        """支持 xpath 方便处理网页"""
        if not html:
            return None
        try:
            return etree.HTML(html).xpath(xpath)
        except etree.XPathError:
            return None

    T = TypeVar("T")  # 提交任务的返回类型

    @staticmethod
    def submit_tasks(task_list: List[Tuple[Callable[..., T], Tuple, Dict]]) -> List[T]:
        """线程池, 解析多个网页时可以使用, 加快解析速度
        @task_list 任务列表, 每一个 task 都是元组:  (待调用的函数, 参数列表, 关键字参数列表), 示例
                    (function, (arg1, arg2), {"kwarg1":"value"})
                    (function, (arg1, ), {})
        """
        executor = ThreadPoolExecutor()
        all_task = []
        result = []
        for fn, args, kwargs in task_list:
            all_task.append(executor.submit(fn, *args, **kwargs))
        for task in as_completed(all_task):
            ret = task.result()
            if ret is not None:
                result.append(ret)
        return result


class BaseEngine(HtmlParseHelper):
    """基础引擎类, 用户自定义引擎应该继承此类"""

    def search(self, keyword: str) -> List[AnimeMetaInfo]:
        """搜索番剧, 返回番剧摘要信息的列表"""
        pass

    def get_detail(self, detail_page_url: str) -> AnimeDetailInfo:
        """处理一部番剧的详情页面, 解析视频播放列表, 返回详情信息"""
        pass

    def _search(self, keyword: str) -> List[AnimeMetaInfo]:
        """引擎管理器负责调用, 捕获异常"""
        try:
            return self.search(keyword)
        except Exception as e:
            logger.exception(e)
            return []

    def _get_detail(self, detail_page_url: str) -> AnimeDetailInfo:
        """引擎管理器负责调用, 捕获异常"""
        try:
            return self.get_detail(detail_page_url)
        except Exception as e:
            logger.exception(e)
            return AnimeDetailInfo()


class DanmakuEngine(HtmlParseHelper):
    """弹幕库引擎基类, 用户自定义的引擎应该继承它"""

    def convert_to_zh(self, text: str):
        """将繁体弹幕转换为简体"""
        return convert(text, "zh-cn")

    def convert_to_tw(self, text: str):
        """简体转繁体"""
        return convert(text, "zh-tw")

    def search(self, keyword: str) -> List[DanmakuMetaInfo]:
        """搜索相关番剧, 返回指向番剧详情页的信息"""
        pass

    def get_detail(self, play_page_url: str) -> DanmakuCollection:
        """处理一部番剧的播放页面, 解析所有视频的弹幕 id 信息"""
        pass

    def get_danmaku(self, cid: str) -> Dict:
        """提供弹幕的 id, 解析出弹幕的内容, 并处理成 DPlayer 支持的格式"""
        pass

    def _search(self, keyword: str) -> List[DanmakuMetaInfo]:
        """引擎管理器负责调用, 捕获异常"""
        try:
            return self.search(keyword)
        except Exception as e:
            logger.exception(e)
            return []

    def _get_detail(self, play_page_url: str) -> DanmakuCollection:
        """引擎管理器负责调用, 捕获异常"""
        try:
            return self.get_detail(play_page_url)
        except Exception as e:
            logger.exception(e)
            return DanmakuCollection()

    def _get_danmaku(self, cid: str) -> Dict:
        """引擎管理器负责调用, 捕获异常"""
        try:
            return self.get_danmaku(cid)
        except Exception as e:
            logger.exception(e)
            return {}


class VideoHandler(HtmlParseHelper):
    """视频解析类, 用于处理视频的真实 url、推断视频格式、视频数据修复等功能
    代理访问视频数据流并返回响应给客户端, 以此绕过服务器的防盗链
    如果 Video 没有设置 handler, 则默认使用本 Handler"""

    def __init__(self, video: Video):
        self._raw_url = video.raw_url  # 视频的原始链接, 可能只是些参数信息, 需要进一步处理
        self._real_url = video.real_url  # 解析出来的视频直链
        self._video_format = ""  # 解析出来的视频格式
        self._chunk_size = 1024 * 512  # 代理访问时每次读取的数据流大小 bytes
        self._proxy_headers = {}  # 代理访问使用的 headers

    def get_raw_url(self) -> str:
        """自定义 Handler 类通过本方法获取视频的原始链接信息"""
        return self._raw_url

    def get_real_url(self) -> str:
        """获取视频真实链接, 如果提取的视频 url 不是直链, 应该重写本方法"""
        return self._raw_url

    def get_cached_real_url(self):
        """获取视频直链, 如果有缓存的话, 使用缓存的值"""
        if self._real_url:  # 缓存解析完成的直链, 防止重复解析
            logger.debug(f"Using cached real url: {self._real_url}")
            return self._real_url
        return self.get_real_url()

    def set_proxy_headers(self) -> Dict:
        """设置代理访问使用的请求头, 如果服务器存在防盗链, 可以尝试重写本方法
        返回空值时使用默认 headers
        """
        return {}

    def _set_proxy_headers(self):
        self._proxy_headers = self.set_proxy_headers()
        if not self._proxy_headers:
            self._proxy_headers = {
                "User-Agent": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
            }

    def _get_stream_from_server(self, byte_start=0, byte_end=None) -> Tuple[Optional[dict], Optional[iter]]:
        """从服务器读取视频数据流, 可指定数据流起始、结束的字节位置
        返回服务器响应头信息和视频数据流迭代器"""
        self._set_proxy_headers()  # 请求数据前设置 headers
        if not byte_end:
            self._proxy_headers["Range"] = f"bytes={byte_start}-"
        else:
            self._proxy_headers["Range"] = f"bytes={byte_start}-{byte_end}"
        try:
            real_url = self.get_cached_real_url()
            resp = requests.get(real_url, stream=True, headers=self._proxy_headers, verify=False)
            return resp.headers, resp.iter_content(self._chunk_size)
        except requests.RequestException:
            return None, None

    def _get_stream_with_range(self):
        """按客户端请求头设置的 Range 范围获取视频流"""
        byte_start = 0
        range_header = request.headers.get("Range", None)
        logger.info(f"Client header: Range={range_header}")
        if range_header:
            result = re.search(r"(\d+)-\d*", range_header)
            if result:
                byte_start = int(result.group(1))  # 客户端要求的视频流起始位置
        return self._get_stream_from_server(byte_start)

    def detect_video_format(self) -> str:
        """判断视频真正的格式, url 可能没有视频后缀"""
        # 尝试从 url 提取后缀
        url = self.get_cached_real_url()
        try:
            ext = url.split("?")[0].split(".")[-1].lower()
            if ext in ["mp4", "flv"]:
                return ext
            if ext == "m3u8":
                return "hls"
        except (IndexError, AttributeError):
            pass

        # 视频的元数据中包含了视频的格式信息, 在视频开头寻找十六进制标识符推断视频格式
        format_hex = {
            "mp4": ["69736F6D", "70617663", "6D703432", "4D50454734", "4C617666"],
            "flv": ["464C56"],
            "hls": ["4558544D3355"]
        }

        _, data_iter = self._get_stream_from_server(0, 512)
        if not data_iter:
            logger.warning("Could not get video stream from server")
            return "unknown"

        logger.debug("Detecting video format from binary stream")
        video_meta = next(data_iter).hex().upper()
        for format_, hex_list in format_hex.items():
            for hex_sign in hex_list:
                if hex_sign in video_meta:
                    logger.debug(f"Video format: {format_}")
                    return format_
        logger.error("Could not detect video format from stream")
        logger.debug("Video raw binary stream (512byte):")
        logger.debug(video_meta)
        return "unknown"

    def make_response(self) -> requests.Response:
        """读取远程的视频流，并伪装成本地的响应返回给客户端"""
        header, data_iter = self._get_stream_with_range()
        if not data_iter:
            return Response("error", status=500)

        if not self._video_format:
            self._video_format = self.detect_video_format()

        if self._video_format == "hls":
            resp = Response("M3U8 Video is no need to use proxy", status=200)  # m3u8 无需代理
        elif self._video_format == "mp4":
            resp = Response(data_iter, status=206)  # 状态码需设置为 206, 否则无法拖动进度条
            resp.content_range = header.get("Content-Range", None)  # 将服务器的响应头的信息作为代理的响应头
            resp.content_type = header.get("Content-Type", None)
        else:
            resp = Response(data_iter, status=200)
            resp.content_range = header.get("Content-Range", None)
            resp.content_type = header.get("Content-Type", None)

        # 返回响应给客户端
        return resp
