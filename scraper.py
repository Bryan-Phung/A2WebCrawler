import re
from tabnanny import check
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from urllib.robotparser import robotparse
from collections import Counter
import math

WHITELISTED_DOMAINS = [".ics.uci.edu/",
                       ".cs.uci.edu/",
                       ".informatics.uci.edu/",
                       ".stat.uci.edu/",
                       "//cs.uci.edu/",
                       "//informatics.uci.edu/",
                       "//stat.uci.edu/",
                       "//today.uci.edu/department/information_computer_sciences"]

robots = dict()
uniqueURL = set()               #A set to see which urls have been IDENTIFIED
largestWordCountURL = 0         #Find the page with the highest URL count
subDomainURLs = dict()          #Find all the subdomains from each URLS 
tokenMap = dict()               #Find the 50 top most used words in all the websites


def scraper(url: str, resp: utils.response.Response) -> list[str]:
    # print("URL" , url)

    #1. Check for status of the website with resp.status (200-299)
    if 200 <= resp.status <= 299 and resp.status != 204:
        #2. Handle all the declaration such as an anchor(#), etc
        url = defragmentURL(url)
        #3. Add to a list or set the uniquePages
        uniqueURL.add(url)

        #4. Get the subdomains of the pages to the site
        # print(getSubdomain(url))

    #5. unsure more reading needed

    links = extractNextLinks(url, resp)
    
    return [link for link in links if isValid(link)]

def dotProduct(dict1, dict2):
    """ calculate the dot product of the givem two dictionaries
    args:
        dict1(dict): key is the word in str, value is the frequency of the word in int
        dict2(dict): key is the word in str, value is the frequency of the word in int
    return:
        sum(float): the dot product result in float
    """
    productSum = 0.0
    for key in dict1.keys():
        if key in dict2.keys():
            productSum += (dict1[key] * dict2[key])
    return productSum

def page_similarity(text1: str, text2: str):
    """ calculate the page similarity score
    args: 
        text1(str): str of the first page content
        text2(str): str of the second page content
    return:
        score(float): the score of the similarity between these two pages
    """
    # split page into words
    text1_word = list(); text2_word = list()
    for word in text1.split():
        if not word.isalnum():
            prunedWord = ("".join(filter(str.isalnum, word))).lower()
            if len(prunedWord) > 0:
                text1_word.append(prunedWord)
        else:
            if len(word) > 0:
                text1_word.append(word.lower())
    for word in text2.split():
        if not word.isalnum():
            prunedWord = ("".join(filter(str.isalnum, word))).lower()
            if len(prunedWord) > 0:
                text2_word.append(prunedWord)
        else:
            if len(word) > 0:
                text2_word.append(word.lower())
    
    # count the word frequencies
    text1_frequency, text2_frequency = Counter(text1_word), Counter(text2_word)
    
    
    # returns the angle in radians 
    numerator = dotProduct(text1_frequency, text2_frequency)
    denominator = math.sqrt(dotProduct(text1_frequency, text1_frequency)*dotProduct(text2_frequency, text2_frequency))

    return math.acos(numerator / denominator)

def extractNextLinks(url: str, resp: utils.response.Response) -> list[str]:
    # https://www.crummy.com/software/BeautifulSoup/bs4/doc/
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    
    # regex = r"https?://[^\s]+"
    # hyperlinks = re.findall(regex, resp.raw_response.content)
    links = list()
    soup = BeautifulSoup(resp.raw_response.content, "html.parser")

    # Gets all links found in the page whose href attribute starts with http or https
    for link in soup.findAll('a', attrs={"href": re.compile("^http://|^https://")}):
        links.append(link.get("href"))

    return links


"""
Might be unnecessary when trying to get all the subdomains as extractNextLinks should work?
"""
# def getSubdomain(url: str, subDomain = "ics.uci.edu", protocol = "http://") -> str:
#     #https://docs.python.org/3/library/urllib.parse.html
#     parsedURL = urlparse(url)
#     if subDomain in parsedURL.netloc:
#         sb = parsedURL.netloc.split(".")
#         if "www" in parsedURL.netloc:
#             return protocol + sb[1] + "." + subDomain + "/"
#         return protocol + sb[0] + "." + subDomain + "/"
#     return None


def defragmentURL(url):
    #Remove fragment from a url
    fragIndex = url.find("#")
    if fragIndex > 0:
        url = url[:(fragIndex-1 if url[fragIndex-1] == "/" else fragIndex)]
    elif url[-1] == "/":
        url = url[:-1]
    return url


def isValid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    
    try:
        parsed = urlparse(url)
        #Handle the calendar
        #Handle the navgiation pages
        if parsed.scheme not in set(["http", "https"]):
            return False

        if url in uniqueURL or checkNetLoc(url):
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
def checkNetLoc(url: str, urlNetloc: str) -> bool:
    check = False
    
    #Checks if it is in the whitelisted_domain
    for domain in WHITELISTED_DOMAINS:
        if domain in url:
            check = True
    if not check:
        return False
    
    #Checks if it obeys the robots request
    if urlNetloc not in robots:
        robotCheck(url)
    if urlNetloc in robots and not robots[urlNetloc](url):  #Refers to the robots dictionary created that it's True or False (False meaning that it's disallowed from the robots.txt)
        return False
    return True


def robotCheck(url: str) -> None:
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
    

def isCalendar(url: str) -> bool:
    return url.match("r^.*calendar.*&")