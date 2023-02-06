import re
from urllib.parse import urlparse, urldefrag, urljoin
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from collections import defaultdict
import pickle

uniqueURLs = [] # list for unique urls
wordCount = defaultdict(int) # make dictionary with words found in each page without stop words
visitedURLs = [] # list for counting visited urls
icsSubdomains = defaultdict(int) # {subdomain : count}
longest_page_url = "" # stores longest page (by text content)
longest_page_length = 0 # stores longest page's length

nltk.download('stopwords')
stop_words = set(stopwords.words('english')) # create variable with english stopwords


def scraper(url, resp):
    links = extract_next_links(url, resp) # grab next links into list

    # 4.
    with open('report.pkl', 'wb') as file: # export global variables with pickle 
        pickle.dump([uniqueURLs, wordCount, visitedURLs, longest_page_url, longest_page_length, icsSubdomains], file)

    return [link for link in links if is_valid(link)] # return valid links
    

def tokenize(clean_text: str) -> list:
    # from assignment one of group member 48261700
    token_list = []
    wordfinder = re.compile(r"([A-Za-z\d]+)") # regex equation to accept alphabetic chars and digits in the text file
    words = wordfinder.findall(clean_text) # finds matches in the line, can take longer depending on line size which means it runs on O(N) time, however, should be quicker than using against entire file
    
    for word in words:
        if (len(word) > 2): # only accepting words with at least 3 characters (tokenization)
            token_list.append(word.lower()) # append each word found and lowercase it to a list
    
    return token_list

def extract_next_links(url, resp) -> list:
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    # resp.raw_response.url: the url, again
    # resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    
    temp_link = urlparse(url) # get and parse link
    found_urls  = list() # initialize list for next urls
    current_url = urldefrag(url)[0] # get url without fragment
    
    url_base = temp_link.scheme + "://" + temp_link.netloc # used later for finding subdomains from ics.uci.edu

    try: # catch beautiful soup exception if it comes up
        if 200 <= resp.status < 300: # if link status is valid
            soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
            
            if (resp.raw_response.content is not None): # if content obtained not None
                
                for link in soup.find_all('a'): # finds all links and appends it to list
                    if '#' in link:
                        link = link.split('#', 1)[0] # defrag here in case line 67 does not work
                    found_urls.append(link.get('href'))
        else:
            return list()
    except Exception:
        return list()


    # https://www.geeksforgeeks.org/remove-all-style-scripts-and-html-tags-using-beautifulsoup/
    for data in soup(['style', 'script']): # remove all html markup
        data.decompose() # remove tags
    
    clean_text = (' '.join(soup.stripped_strings))

    token_list = tokenize(clean_text.lower()) # goes through text and tokenizes each one
    
    if len(token_list) < 5: # avoiding low information value pages
        return list()
    
    global longest_page_length, longest_page_url
    if len(token_list) > longest_page_length: # for report -- stores page with most words
        longest_page_length = len(token_list)
        longest_page_url = url

    if current_url.lower() in visitedURLs: # end loop if site already visited, thus stopping code if no more links to crawl
        return list()
    elif current_url.lower() not in uniqueURLs: # checks if url is a unique URL and makes sure it is off ics.uci.edu domain
        if re.match(r".*\.ics\.uci\.edu", url_base):
            sub_link = str(temp_link.netloc)
            if sub_link != "www.ics.uci.edu" and sub_link != "ics.uci.edu":
                if "www." in sub_link:
                    sub_link = sub_link.replace("www.", "") # removes www. so that all sites are uniform and counted
                icsSubdomains["https://" + sub_link.lower()] += 1 # adding in https so it doesn't count http/https separately & add to dictionary
        uniqueURLs.append(current_url)
    if current_url.lower() not in visitedURLs: # otherwise, we add the url to the visited URLs 
        visitedURLs.append(current_url.lower())

    for word in token_list: # count words except those in stopwords and add to dict
        if word not in stop_words:
            wordCount[word] += 1

    return found_urls

def is_valid(url) -> bool:
    # decide whether to crawl this url or not. 
    # if you decide to crawl it, return True; otherwise return False.
    # there are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        if not re.match( # matches given domains
            r".*\.(ics\.uci\.edu"
            + r"|cs\.uci\.edu"
            + r"|informatics\.uci\.edu"
            + r"|stat\.uci\.edu)", parsed.netloc.lower()):
            return False

        # https://support.archive-it.org/hc/en-us/articles/208824546-Archiving-Wix-sites
        # block wix websites which can be traps
        # blocks share, comments, action since they lead to the same page 
        if re.match(r"^.*/[^/]{300,}$", parsed.path.lower()) or "pdf" in url or "share=" in url or "#comment" in url or "#respond" in url or "action=" in url:
            return False
        
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|bib|ppsx" # block ppsx, word powerpoint, and bib
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1|wix|blur_" # block wix, blur_ sites which are traps
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())


    except TypeError:
        print ("TypeError for ", parsed)
        raise
