from enum import unique
import re
import math
from tabnanny import check
from urllib.parse import urlparse
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from urllib import robotparser
from collections import Counter, defaultdict
from tokenizer import tokenize, get_features
from simhash import Simhash, SimhashIndex


WHITELISTED_DOMAINS = [".ics.uci.edu/",
                       ".cs.uci.edu/",
                       ".informatics.uci.edu/",
                       ".stat.uci.edu/",
                       "//cs.uci.edu/",
                       "//informatics.uci.edu/",
                       "//stat.uci.edu/",
                       "//today.uci.edu/department/information_computer_sciences"]

BLACKLISTED_DOMAINS = ["https://wics.ics.uci.edu/events/",
                       "https://www.ics.uci.edu/~eppstein/pix/",
                       "https://evoke.ics.uci.edu/qs-personal-data-landscapes-poster/",
                       "https://evoke.ics.uci.edu/health-data-exploration-report-published/",
                       "https://evoke.ics.uci.edu/hollowing-i-in-the-authorship-of-letters-a-note-on-flusser-and-surveillance/"
                       ]

BLACKLISTED_PATHWAYS = ["calendar", "event", "commit/", "blob/", "raw/", "blame/", "tree/", "/graphs/"]

HIGHINFO = 3000
robots = dict()
uniqueURL = set()               #A set to see which urls have been IDENTIFIED
largestWordCountURL = 0         #Find the page with the highest URL count
subDomainURLs = defaultdict(int)          #Find all the subdomains from each URL
tokenMap = Counter()               #Find the 50 top most used words in all the websites
simHash = SimhashIndex([], k = 0) #Starting with the key = 0, and empty [], get the [key: URL, ]
simHashKey = 1
periodCt = 0


def printStats():
    with open("report.txt", "w") as f:
        f.write("--------------- CS 121 Report ---------------\n")
        f.write("Team Members of: Geo Li(82784712), Ryan Luong(27248658), Bryan Phung(12937958)\n")
        f.write("Number of unique URLs: "+ str(len(uniqueURL)) + "\n")
        f.write("Number of subdomains: "+ str(len(subDomainURLs)) + "\n")
        f.write("Largest word count: "+ str(largestWordCountURL) + "\n")
        f.write("Top 50 words: "+ str(tokenMap.most_common(50))+ "\n")
        f.write("(Domain, # of Subdomains): "+ str([(key, subDomainURLs[key]) for key in subDomainURLs]) + "\n")


def readInfo():
    global uniqueURL, subDomainURLs, tokenMap, largestWordCountURL
    try:
        with open("robots.txt", "r") as file:
            lst = eval(file.read())
            for line in lst:
                robotCheck("http://" + line)
        with open("uniqueURL.txt", "r") as file:
            uniqueURL = eval(file.read())
        with open("subDomainURLs.txt", "r") as file:
            dct = dict(eval(file.read()))
            subDomainURLs = defaultdict(int, dct)
        with open("tokenMap.txt", "r") as file:
            tokenMap = Counter(eval(file.read()))
        with open("largestNumberURL.txt", "r") as file:
            largestWordCountURL = int(eval(file.read()))
    except FileNotFoundError as e:
        print(e)

def saveInfoToText():
    with open("robots.txt", "w") as file:
        file.write(str(list(robots.keys())))
    with open("uniqueURL.txt", "w") as file:
        file.write(str(uniqueURL))
    with open("subDomainURLs.txt", "w") as file:
        file.write(str(dict(subDomainURLs)))
    with open("tokenMap.txt", "w") as file:
        file.write(str(tokenMap))
    with open("largestNumberURL.txt", "w") as file:
        file.write(str(largestWordCountURL))

def scraper(url: str, resp):
    #1. Check for status of the website with resp.status (200-299)
    urlLinks = []
    global periodCt
    periodCt += 1
    # print("Isvalid not correct? : ", isValid("https://www.linkedin.com/company/uci-institute-for-future-health"))
    if 200 == resp.status <= 299 and resp.status != 204 and resp.raw_response and len(resp.raw_response.content) > HIGHINFO:
        #2. Handle all the declaration such as an anchor(#), etc
        url = defragmentURL(url)
        subDomain = checkSubDomain(url)
        if subDomain:
            subDomainURLs[subDomain] += 1
        # url = removeQuery(url)
        #3. Add to a list or set the uniquePages
        if processWebsiteText(resp):
            uniqueURL.add(url)

        longestURLCheck(resp)
        #4. Get the subdomains of the pages to the site
        # print(getSubdomain(url))

        links = extractNextLinks(url, resp)
        urlLinks = list(set(link for link in links if isValid(link)))
    elif resp.status >= 600:
        print("600-errors Failed to open the website URL: ", url)

    if periodCt % 10 == 0:
        saveInfoToText()
        # print("URLLinks: " + str(urlLinks))
    return urlLinks


def longestURLCheck(resp):
    global largestWordCountURL, tokenMap
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    text = soup.get_text()
    wordList, numOfWords = tokenize(text)
    if numOfWords > largestWordCountURL:
        largestWordCountURL = numOfWords
    tokenMap.update(Counter(wordList))


def extractNextLinks(url: str, resp):
    # https://www.crummy.com/software/BeautifulSoup/bs4/doc/
    # https://www.geeksforgeeks.org/beautifulsoup-scraping-link-from-html/
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    links = list()
    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    # Gets all links found in the page whose href attribute starts with http or https
    for link in soup.findAll('a'):
        path = link.get('href')
        if not path:
            continue

        path = removeQuery(defragmentURL(path.strip()))

        if path and re.match(r"^https://|^http://", path):
            links.append(path)
        elif path and path.startswith("/"):
            links.append(urljoin(url, path))

    return links


"""
Might be unnecessary when trying to get all the subdomains as extractNextLinks should work?
"""
def checkSubDomain(url: str, subDomain = "ics.uci.edu", protocol = "http://") -> str:
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
    # <scheme>://<netloc>/<path>;<params>?<query>#<fragment>
    fragIndex = url.find("#")
    # If there exist
    if fragIndex > 0:
        url = url[:(fragIndex-1 if url[fragIndex-1] == "/" else fragIndex)]
    elif url and url[-1] == "/":
        url = url[:-1]
    return url

def removeQuery(url):
    #Remove query from a url
    queryIndex = url.find("?")
    if queryIndex > 0:
        url = url[:(queryIndex-1 if url[queryIndex-1] == "/" else queryIndex)]
        # url = url[:(index-1 if url[index-1] == "/" else index)]
    elif url and url[-1] == "/":
        url = url[:-1]
    return url

def pathSimlarToURLS(url):
    parsed = urlparse(url)
    ct = 0
    for website in uniqueURL:
        if parsed.path in website:
            ct+=1
        if ct > 5:
            # print("Return false")
            return False
    return True

def isValid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    if url is None or url == "":
        return False
    try:
        parsed = urlparse(url)

        #Handle the calendar
        #Handle the navgiation pages
        if parsed.scheme not in set(["http", "https"]):
            return False

        if url in uniqueURL or not checkNetLoc(url, parsed.netloc) or not pathSimlarToURLS(url):
            return False

        for path in BLACKLISTED_PATHWAYS:
            if path in parsed.path:
                return False

        # print(parsed)
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|html"
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
def checkNetLoc(url: str, urlNetloc: str) -> bool:
    check = False

    #Checks if it is in the whitelisted_domain
    for domain in WHITELISTED_DOMAINS:
        if domain in url:
            check = True
    if not check:
        return False

    for domain in BLACKLISTED_DOMAINS:
        if domain in url:
            return False


    #Checks if it obeys the robots request
    if urlNetloc not in robots:
        robotCheck(url)
    if urlNetloc in robots and not robots[urlNetloc](url):  #Refers to the robots dictionary created that it's True or False (False meaning that it's disallowed from the robots.txt)
        return False
    return True


def robotCheck(url: str) -> None:
    #https://docs.python.org/3/library/urllib.robotparser.html
    def crawlAble(url_with_path: str):
        return robot.can_fetch('*', url_with_path)

    url = urlparse(url)
    # print(url)
    robot = robotparser.RobotFileParser()
    robot.set_url(url.scheme + "://" + url.netloc + "/robots.txt")
    # print(url.scheme + "://" + url.netloc + "/robots.txt")
    try:
        robot.read()
        robots[url.netloc] = crawlAble
    except:
        print("Failed to read the robot.txt of URL: ", url.scheme + "://" + url.netloc + "/robots.txt")

""""
@Params: url (str), resp (Response.Entity)
Grabs the information using the response content and calls similarCheck to see if it contains the information from a previous website
Returns true if the process can be process, if it cannot be process, return false (Do not try to parse the information)
"""
def processWebsiteText(resp):
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    text = soup.get_text()

    if similarCheck(text):
        return False
    return True

"""
@Params: url (str), info (str of body text from the website)
Return if there is similars, if not then return False and add to the simHash function
"""
def similarCheck(info : str) -> bool:
    """
    get_features from tokenize.py returns a list of all the tokens
    Simhash creates an entity of simhash and allows to compare with our simHashIndex
    """
    global simHashKey
    features = Counter.most_common(Counter(get_features(info)))
    features = [k[0] for k in features]
    fingerPrint = Simhash(features)
    if simHash.get_near_dups(fingerPrint):
        return True
    else:
        simHash.add(str(simHashKey), fingerPrint)
        simHashKey+=1
        return False
    
