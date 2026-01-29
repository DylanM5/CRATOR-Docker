"""
CRATOR FileSaver

File saving for downloaded web pages.

Architecture (Paper Section III-A):
    After the verification of link and cookie validity, the crawling process starts by downloading the
    first link along with all internal links, which are links sharing the same domain as the initial link,
    such as https://en.wikipedia.org/wiki/IOT and https://en.wikipedia.org/wiki/Crawler, both having the
    domain en.wikipedia.org. For each link, the crawler extracts and saves the webpage content locally and
    checks if there are other internal links to put in the download queue. The connection module makes use
    of proxy settings to establish a connection with onion links, cookies to bypass security checks, and
    random user-agent to avoid being identified as a bot. This process keeps running until it reaches a
    certain exit condition, such as a preset crawling time or a maximum number of links crawled.

Reference: https://arxiv.org/html/2405.06356v1
"""
import threading
import time
import os
import hashlib
from collections import deque
from concurrent.futures import ThreadPoolExecutor

# Local imports
import utils.fileutils as file_utils


class FileSaver:
    def __init__(self, save_path, n_threads=1):
        self.n_threads = n_threads
        self.save_path = save_path

        self.queue = deque()
        self.lock = threading.Lock()
        self.running = True

    def enqueue(self, web_page, index_node):
        self.queue.append((web_page, index_node))

    def stop(self):
        self.running = False

    def start(self):
        threading.Thread(target=self.save, daemon=True).start()

    def save(self):
        with ThreadPoolExecutor(max_workers=self.n_threads) as executor:
            while self.running:
                if not self.queue:
                    time.sleep(0.1)
                    continue

                with self.lock:
                    while self.queue:
                        web_page, index_node = self.queue.popleft()
                        file_name = str(index_node) + ".html"
                        dir = os.path.join(self.save_path, file_name)

                        executor.submit(file_utils.save_file, web_page.text, dir)
                        time.sleep(0.1)
