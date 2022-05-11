import sys
import re
from collections import Counter
import math

#https://www.ranks.nl/stopwords
STOP_WORDS = set(['a', 'about', 'above', 'after', 'again', 'against', 'all', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are',
                  'aren\'t', 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can\'t', 'cannot', 'could', 'couldn\'t', 'did',
                  'didn\'t', 'do', 'does', 'doesn\'t', 'doing', 'don\'t', 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', 'hadn\'t', 'has', 'hasn\'t', 'have',
                  'haven\'t', 'having', 'he', 'he\'d', 'he\'ll', 'he\'s', 'her', 'here', 'here\'s', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'how\'s', 'i', 'i\'d', 'i\'ll',
                  'i\'m', 'i\'ve', 'if', 'in', 'into', 'is', 'isn\'t', 'it', 'it\'s', 'its', 'itself', 'let\'s', 'me', 'more', 'most', 'musntn\'t', 'my', 'myself', 'no', 'nor', 'not',
                  'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'shan\'t', 'she', 'she\'d', 'she\'ll', 'she\'s',
                  'should', 'shouldn\'t', 'so', 'some', 'such', 'than', 'that', 'that\'s', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'there\'s', 'these', 'they',
                  'they\'d', 'they\'ll', 'they\'re', 'they\'ve', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'wasn\'t', 'we', 'we\d', 'we\'ll', 'we\'re', 'we\'ve',
                  'were', 'weren\'t', 'what', 'what\'s', 'when', 'when\'s','where', 'where\'s', 'which', 'while', 'who', 'who\'s', 'whom', 'why', 'why\'s', 'with', 'won\'t', 'would',
                  'wouldn\'t', 'you', 'you\'d', 'you\'ll', 'you\'re', 'you\'ve', 'your', 'yours', 'yourself', 'yourselves'])

"""
For the function, tokenize, it runs in polynomial-time O(n^2) as it takes one loop to iterate the characters of the documents, and one statement to check the information
Each check is runnning in O(1) time, which adds up to the function only being O(n^3).
In addition, there is space complexity of O(n) as it could contain all the words from the input.
"""
def tokenize(information: str) -> (list, int):
    """
    Given the information from the URL, read in the information and parse each token to the tokenMap.
    Return the LSTOFTOKENS, # of words on the website
    """
    lst = list()
    word = ""
    allWords = 0
    for c in information:
        """
        A token to me is identified as being able to remove all the special characters or non-alphanumeric characters and then adding them together as one string.
        Allows also for escape characters such as can't, you're (BUT NOT STOP_WORDS)
        """
        # temp = "".join(s for s in line.lower() if s.isalnum())
        if c.isalnum() or c == "\'":
            word += c
        else:
            if len(word) > 2 and word.lower() not in STOP_WORDS:
                allWords+=1
                lst.append(word.lower())
            word = ""
    return lst, allWords

"""
Allows to get all the information from the website, and tokenize the information into a list then, it could build the simHash
return the list
"""
def get_features(information: str) -> list:
    lst = list()
    word = ""
    for c in information:
        """
        A token to me is identified as being able to remove all the special characters or non-alphanumeric characters and then adding them together as one string.
        Allows also for escape characters such as can't, you're (BUT NOT STOP_WORDS)
        """
        if c.isalnum() or c == "\'":
            word += c
        else:
            if len(word) > 2 and word.lower() not in STOP_WORDS:
                lst.append(word.lower())
            word = ""
    return lst


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
    #https://www.geeksforgeeks.org/measuring-the-document-similarity-in-python/
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
