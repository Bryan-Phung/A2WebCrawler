import sys
import re

#https://www.ranks.nl/stopwords
STOP_WORDS = set('a', 'about', 'above', 'after', 'again', 'against', 'all', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are',
                 'aren\'t', 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can\'t', 'cannot', 'could', 'couldn\'t', 'did',
                 'didn\'t', 'do', 'does', 'doesn\'t', 'doing', 'don\'t', 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', 'hadn\'t', 'has', 'hasn\'t', 'have',
                 'haven\'t', 'having', 'he', 'he\'d', 'he\'ll', 'he\'s', 'her', 'here', 'here\'s', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'how\'s', 'i', 'i\'d', 'i\'ll',
                 'i\'m', 'i\'ve', 'if', 'in', 'into', 'is', 'isn\'t', 'it', 'it\'s', 'its', 'itself', 'let\'s', 'me', 'more', 'most', 'musntn\'t', 'my', 'myself', 'no', 'nor', 'not',
                 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'shan\'t', 'she', 'she\'d', 'she\'ll', 'she\'s', 
                 'should', 'shouldn\'t', 'so', 'some', 'such', 'than', 'that', 'that\'s', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'there\'s', 'these', 'they', 
                 'they\'d', 'they\'ll', 'they\'re', 'they\'ve', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'wasn\'t', 'we', 'we\d', 'we\'ll', 'we\'re', 'we\'ve',
                 'were', 'weren\'t', 'what', 'what\'s', 'when', 'when\'s','where', 'where\'s', 'which', 'while', 'who', 'who\'s', 'whom', 'why', 'why\'s', 'with', 'won\'t', 'would',
                 'wouldn\'t', 'you', 'you\'d', 'you\'ll', 'you\'re', 'you\'ve', 'your', 'yours', 'yourself', 'yourselves')
                 
"""
For the function, tokenize, it runs in polynomial-time O(n^3) as it takes one loop to iterate take the lines of the words, and another loop to iterate through
each string and then lastly a loop to iterate through each character if it matches an alphanumeric character or number.
Each check is runnning in O(1) time, which adds up to the function only being O(n^3).
In addition, there is space complexity of O(n) as it could contain all the words from the input.
"""
def tokenize(information: str, tokenMap: dict[str]) -> list:
    """
    Given the information from the URL, read in the information and parse each token to the tokenMap.
    Return the dict follow by the amount of tokens in the file
    """
    lst = list()
    
    with open(TextFilePath, 'r', encoding = 'utf8') as file:
        for line in file:
            templst = line.split()
            for line in templst:
                """
                A token to me is identified as being able to remove all the special characters or non-alphanumeric characters and then adding them together as one string.
                For example, if "can't" is found in my parser, its token will be saved as "cant". 
                """
                # temp = "".join(s for s in line.lower() if s.isalnum())
                temp = re.sub('[^A-Za-z/d]', '', line.lower())
                """
                Check if the string is not blank before adding it to the string as " " are not classified as tokens.
                """
                if temp:
                    lst.append(temp)
    return lst

"""
computeWord runs in O(n) time given that it's iterating through each word from the list and does not add up when checking in the words is in the dct since that runs in only O(1) time.
Space Compexity would be O(n) as it will grow to have the tokens of the word.
"""
def computeWord(tokenList: list) -> map:
    dct = dict()
    """
    Given a list of all the tokens, count all the occurences of all the words
    Return the unsorted dictionary that contains the Key as the token and the Value as the occurences.
    """
    for w in tokenList:
        if w not in dct and not dct.update({w : 1}):
            """
            Since the word does not exist, count as 1, else add 1 to the words
            """
            dct[w] = 1
        else:
            dct[w] += 1
    return dct
