import re
from urllib.parse import urlparse, urldefrag, urljoin
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from collections import defaultdict
import pickle

uniqueURLs = []
wordCount = defaultdict(int) # make dictionary with words found in each page without stop words
visitedURLs = []
icsSubdomains = defaultdict(int) # {subdomain : count}
longest_page_url = "" # stores longest page (by text content)
longest_page_length = 0

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))




def scraper(url, resp):
    links = extract_next_links(url, resp)

    #part D, exporting our global variables for processing to report with pickle
    # wb to open and write to binary pkl file
    with open('report.pkl', 'wb') as file:
        pickle.dump([uniqueURLs, wordCount, visitedURLs, longest_page_url, longest_page_length, icsSubdomains], file)

    return [link for link in links if is_valid(link)]
    

def tokenize(clean_text: str) -> list:
    # finds all the words in the page
    token_list = []
    wordfinder = re.compile(r"([A-Za-z\d]+)") # regex equation accepts all alphabetic chars and digits in the text file
    words = wordfinder.findall(clean_text) # finds all matches in the line, can take longer depending on line size which means it runs on O(N) time, however, should be quicker than using against entire file
    
    # we're not considering words 2 characters or less (tokenization)
    for word in words:
        if (len(word) > 2):
            token_list.append(word.lower()) # appends each word found in the matches and lowercases it to a list
    
    return token_list

def extract_next_links(url, resp) -> list:
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    
    
    # get link and parse
    temp_link = urlparse(url)
    
    # initialize list for next urls
    found_urls  = list()
    
    # gets url without fragment
    # http://sli.ics.uci.edu/Pubs/Abstracts#_tkde10
    current_url = urldefrag(url)[0]
    
    # used later for finding subdomains from ics.uci.edu
    url_base = temp_link.scheme + "://" + temp_link.netloc


    # catching beautiful soup exception if it comes up
    try:
        # if link status is valid
        if 200 <= resp.status < 300:
            soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
            # if content obtained not None
            if (resp.raw_response.content is not None):
                # finds all links and appends it to list
                for link in soup.find_all('a'):
                    found_urls.append(link.get('href'))
        else:
            return list()
    except Exception as e:
        return list()



    #https://www.geeksforgeeks.org/remove-all-style-scripts-and-html-tags-using-beautifulsoup/
    #this loops through the html data and removes all html markup
    for data in soup(['style', 'script']):
        #removes tags
        data.decompose()
    
    # avoiding crawling the website if it has low information value (determined by a threshold of some small number)
    if len(list(soup.stripped_strings)) < 100: 
        return list()
    
    global longest_page_length, longest_page_url
    # for report -- stores page with most words
    if len(list(soup.stripped_strings)) > longest_page_length:
        longest_page_length = len(list(soup.stripped_strings))
        longest_page_url = url
    
    clean_text = (' '.join(soup.stripped_strings))
    

    # goes through text and tokenizes each one
    token_list = tokenize(clean_text.lower()) 

    # checking if we already visited site, and if so ending loop
    # this should stop code if there are no further links to crawl
    
    if temp_link in visitedURLs:
        return list()
    # checks if url is a unique URL and makes sure it is off ics.uci.edu domain
    elif current_url not in uniqueURLs:
        if re.match(r".*\.ics\.uci\.edu", url_base):
            sub_link = str(temp_link.netloc)
            if sub_link != "www.ics.uci.edu" and sub_link != "ics.uci.edu":
                if "www." in sub_link:
                    sub_link = sub_link.replace("www.", "") # removes www. so that all sites are uniform and counted
                # adding in https so it doesn't count http/https separately
                icsSubdomains["https://" + sub_link] += 1 # adds subdomain to dictionary
        uniqueURLs.append(current_url)
    # otherwise, we add the url to the visited URLs 
    if temp_link not in visitedURLs:
        visitedURLs.append(temp_link)


    # count words except those in stopwords and add to dict
    for word in token_list:
        if word not in stop_words:
            wordCount[word] += 1

    return found_urls

def is_valid(url) -> bool:
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        # matches given domains
        if not re.match(
            r".*\.(ics\.uci\.edu"
            + r"|cs\.uci\.edu"
            + r"|informatics\.uci\.edu"
            + r"|stat\.uci\.edu)", parsed.netloc.lower()):
            return False

        # https://support.archive-it.org/hc/en-us/articles/208824546-Archiving-Wix-sites
        # block wix websites which can be traps
        if re.match(r"^.*/[^/]{300,}$", parsed.path.lower()) or re.match(r"^.*calendar.*$", parsed.netloc.lower()) or re.match(r"/pdf/", parsed.path.lower()):
            return False
        
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1|wix|blur_|calendar" # block wix, blur_, calendar sites which are traps
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())


    except TypeError:
        print ("TypeError for ", parsed)
        raise

