from dataclasses import dataclass
from typing import Callable
from selenium.webdriver.remote.webdriver import WebDriver


@dataclass
class Request:
    domains: list | None = None
    url: str
    district: str | None = None
    script: str | None = None
    cookies: dict | None = None
    wait_until: Callable | None = None
    wait_time: int = 10
    screenshot: bool = False
    getjson: bool = False
    driver: WebDriver | None = None
    skip_download: bool = False
    recycle: bool = False
    params: dict = {}
