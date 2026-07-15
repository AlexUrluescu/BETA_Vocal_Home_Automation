import urllib.request
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

class internet_checker():

    def check_internet_connection(self) -> bool:
        url: str = "http://www.google.com"
        timeout: int = 5
        try:
            urllib.request.urlopen(url, timeout=timeout)
            return True
        except urllib.request.URLError:
            return False
