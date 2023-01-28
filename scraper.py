import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from collections import defaultdict

uniqueURL = []
wordCount = {}

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
# make dictionary with words found in each page without stop words
word_count = defaultdict(int)

def scraper(url, resp):
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
    
    
    #get link and parse
    temp_link = urlparse(url)
    
    #initialize list for next urls
    found_url  = list()
    
    #initialize start domain and format link
    start_domain = temp_link.netloc + temp_link.path.rstrip('/')

    # catching beautiful soup exception if it comes up
    try:
        soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    except Exception as e:
        print(e)
        return found_url

    # read and format content using regex
    text_content = re.findall(r'[a-z]{2,}', soup.text.lower())
    
    # if content obtained not None
    if (resp.raw_response.content is not None):
        # add check for duplicate or similar links
        for link in soup.find_all('a'):
            #make sure to add defragment part/format link
            found_url.append(link.get('href'))

    # checking if we are at start domain, and if so ending loop
    # # this should stop code if there are no further links to crawl
    # # otherwise, we add the url to the list and save the size of its 
    # # content so we can traverse it later
    # if start_domain in uniqueURL:
    #     return found_url
    # elif start_domain not in uniqueURL and len(text_content) > 0:
    #     uniqueURL[start_domain] = len(text_content)

    # # count words except those in stopwords and add to dict
    # for word in text_content:
    #     if word not in stop_words:
    #         word_count[word] += 1

    return found_url

def is_valid(url):
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

