from os.path import dirname as get_path
from os.path import basename as get_name
from urllib.parse import urlparse

__all__ = ["get_path", "get_host", "get_name"]


def get_host(url: str) -> str:
    p = urlparse(url)
    return p.scheme + "://" + p.netloc


if __name__ == '__main__':
    url1 = "https://www.example.com/foo/bar/abc.txt?key=value#xx"
    assert get_host(url1) == "https://www.example.com"
    assert get_path(url1) == "https://www.example.com/foo/bar"

    url2 = "https://www.example.com/foo/bar/abc/"
    assert get_host(url2) == "https://www.example.com"
    assert get_path(url2) == "https://www.example.com/foo/bar/abc"
