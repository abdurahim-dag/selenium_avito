from spider import Spider
from sites import Sites, Xpaths
from settings import Settings

spider = Spider(Settings(), Sites(), Xpaths())
spider.start_requests()