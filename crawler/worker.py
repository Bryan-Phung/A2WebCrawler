from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
from bs4 import BeautifulSoup
from tokenizer import tokenize
import os
import scraper
import time


class Worker(Thread):

    contentFileName = "contentFile.txt"          #File that stores crawling web content
    urlFileName = "urlFile.txt"                  #File that stores crawling web url

    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests from scraper.py"
        super().__init__(daemon=True)

    # https://stackoverflow.com/questions/52787585/how-to-efficiently-read-a-large-file-with-a-custom-newline-character-using-pytho
    def splitLines(self, file, newline, chunk_size = 4096*4096):
        # split the contentFile into pages based on the special parser
        tail = ""
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                if tail:
                    yield tail
                break
            lines = (tail + chunk).split(newline)
            tail = lines.pop(0)
            if lines:
                yield tail
                tail = lines.pop()
                yield from lines


    def run(self):
        # open the file with the mode "append and read"
        # contentFile = open(self.contentFileName, "a+")
        urlFile = open(self.urlFileName, "a+")
        # evaluate the content file if there is one (e.g. the server crashes and you need to start from the mid way)
        try:
            # there is something already
            if not self.frontier.save:
                os.remove(self.contentFileName)
                file = open(self.contentFileName, "w")
            else:
                # read from the content text file
                file = open(self.contentFileName, "a+")
                for chunk in self.splitLines(file, "\n--zhuoyul4--\n"):
                    if chunk: # ignore blank lines
                        # add the tokenizer into simhash dataset
                        scraper.similarCheck(chunk)
        except FileNotFoundError:
            pass


        while True:
            # return the content and url as string so they can be put into the file
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                scraper.printStats()
                break
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            ################################
            urlFile.write(tbd_url + "\n")
            # we should split the file based on "\n--zhuoyul4--\n"
            if resp.raw_response:
                soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
                text = soup.get_text()
                file.write(text + "\n--zhuoyul4--\n")
            ################################
            scraped_urls = scraper.scraper(tbd_url, resp)
            if scraped_urls:
                for scraped_url in scraped_urls:
                    self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)



        file.close()
        urlFile.close()

