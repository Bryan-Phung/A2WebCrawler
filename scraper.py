import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from urllib.robotparser import robotparse

WHITELISTED_DOMAINS = [".ics.uci.edu/",
                       ".cs.uci.edu/",
                       ".informatics.uci.edu/",
                       ".stat.uci.edu/"]

robots = dict()

def scraper(url, resp):
    # print("URL" , url)
    uniqueURL = set()

    #1. Check for status of the website with resp.status (200-299)
    if 200 <= resp.status <= 299 and resp.status != 204:
        #2. Handle all the declaration such as an anchor(#), etc
        url = defragmentURL(url)
        #3. Add to a list or set the uniquePages
        uniqueURL.add(url)

        #4. Get the subdomains of the pages to the site
        print(getSubdomain(url))

    #5. unsure more reading needed

    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    return list()

def getSubdomain(url: str, subDomain = "ics.uci.edu", protocol = "http://") -> str:
    #https://docs.python.org/3/library/urllib.parse.html
    parsedURL = urlparse(url)
    if subDomain in parsedURL.netloc:
        sb = parsedURL.netloc.split(".")
        if "www" in parsedURL.netloc:
            return protocol + sb[1] + "." + subDomain + "/"
        return protocol + sb[0] + "." + subDomain + "/"
    return None

def defragmentURL(url):
    #Remove fragment from a url
    fragIndex = url.find("#")
    if fragIndex > 0:
        url = url[:(fragIndex-1 if url[fragIndex-1] == "/" else fragIndex)]
    elif url[-1] == "/":
        url = url[:-1]
    return url

def is_valid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        #Handle the calendar
        #Handle the navgiation pages
        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

# Given the params of the url, urlNetloc
# return true if it is a valid domain and the url is allowed
# return false if it has been explored already or the robot.txt does not want us exploring the web pages
def checkNetLoc(url : str, urlNetloc: str) -> bool:
    # for dom in
    if urlNetloc not in robots:
        robotCheck(url)
    if urlNetloc in robots and not robots[urlNetloc](url):
        return False
    return True

def robotCheck(url : str) -> None:
    url = urlparse(url)
    robot = robotparse()
    robot.set_url(url.scheme + "://" + url.netloc + "/robots.txt")

    try:
        robot.read()
        robots[url.netloc] = crawlAble
    except:
        print("Failed to read")

    def crawlAble(url_with_path: str):
        return robot.can_fetch('*', url_with_path)