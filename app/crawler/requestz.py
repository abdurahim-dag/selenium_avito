class Requestz:
    def __init__(self,
      url: str,
      domains: list = None,
      district: str = None,
      cookies=None,
      script=None,
      wait_until=None,
      wait_time=10,
      screenshot=False,
      getjson=False,
      driver=None,
      skip_download=False,
      recycle=False,
    ):
      self.domains = domains
      self.url = url
      self.district = district
      self.script = script
      self.cookies = cookies
      self.wait_until = wait_until
      self.wait_time = wait_time
      self.screenshot = screenshot
      self.getjson = getjson
      self.driver = driver
      self.skip_download = skip_download
      self.recycle = recycle
      self.params = {}


    def __del__(self):
        if self.driver:
          self.driver.quit()
          self.driver = None