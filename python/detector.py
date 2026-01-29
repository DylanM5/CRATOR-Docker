"""
CRATOR Detection

Provides detection functions for identifying security mechanisms that block automated crawlers on dark web sites.

Link Validity Check (Paper Section III-C):
    URL reachability check involves sending a request to the URL or onion link using the HTTP or HTTPS protocol,
    and checking the response status code returned by the server. A response status code of 200 indicates that
    the URL is reachable and the server has successfully returned the content of the page. On the other hand,
    a status code of 404 indicates that the page is not found, while a status code of 503 indicates that the
    server is temporarily unavailable.
    
    If the crawler determines that a URL is not reachable, it marks the URL as broken or invalid, and removes it from
    the crawling queue. This helps to prevent unnecessary requests to unreachable URLs, which can slow down the
    crawling process and waste system resources.

    In addition, the crawler may also check if the URL is a duplicate or a mirror of another page, and avoid crawling
    such pages to prevent duplication of content.

Captcha Detection (Paper Section III-E):
    Detects captcha challenges by analyzing page structure.

Reference: https://arxiv.org/html/2405.06356v1
"""
from bs4 import BeautifulSoup
import requests
import logging

logger = logging.getLogger("CRATOR")


def captcha_detector(url, response):
    logger.debug(f"DETECTOR - Captcha detector")
    soup = BeautifulSoup(response.text, "html.parser")
    captchas = soup.find_all("img", src=lambda x: "captcha" in x.lower())

    if captchas:
        logger.debug(f"DETECTOR - Captcha detector - Captcha word found in url -> {url}")
        return True

    #if captchas and anomalous_redirection(url, response):
    #    if anomalous_redirection(url, response):
    #        logger.debug(f"DETECTOR - Captcha detector - Captcha word and anomalous redirect found in url -> {url}")
    #    return True

    return False


def anomalous_redirection(url_request, webpage):
    try:
        if any(response.status_code == 302 for response in webpage.history) and webpage.url != url_request:
            return True
        return False
    except Exception as e:
        logger.error(f"DETECTOR - Anomalous redirection - {str(e)}")
        return True


def login_redirection(webpage, loginpage=None):
    """
    Check if in the webpage history there is a redirect (status code 302) and if the url of that page is the login page.
    :param webpage: the webpage to analyze, containing the response history, from the request until the final output.
    :param loginpage: the loginpage, used as validator.
    :return: True, if the function detects a redirect to a loginpage in the webpage history. False otherwise.
    """
    if not loginpage:
        logger.debug("DETECTOR - No login page defined")
        return False
    try:
        webpage.history.reverse()
        for response in webpage.history:
            if response.status_code == 302 and response.url == loginpage.url:
                return True
    except Exception as e:
        logger.error(f"DETECTOR - Login redirection - {str(e)}")
        return False

    return False


def compare_page_contents(web_page_1, web_page_2):
    """
    Check if different request responses have the same htnl content.
    :param web_page_1: :class requests.Response containing info crawled from an url.
    :param web_page_2: :class requests.Response containing info crawled from an url.
    :return: True if the page content is the same, False otherwise.
    """

    if not web_page_1 or not web_page_2:
        return False

    if not all(isinstance(web_page, requests.Response) for web_page in [web_page_1, web_page_2]):
        raise TypeError("The type of each value of the list must be :class requests.Response.")

    soup1 = BeautifulSoup(web_page_1.content, "html.parser")
    content1 = soup1.find('body').text

    soup2 = BeautifulSoup(web_page_2.content, "html.parser")
    content2 = soup2.find('body').text

    if content1 == content2:
        return True

    return False