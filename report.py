import pickle

#loading our variables for processing into report with pickle
with open('report.pkl', 'rb') as file:
    uniqueURLs, wordCount, visitedURLs, longest_page_url, longest_page_length, icsSubdomains = pickle.load(file)

with open('report.txt', 'w') as report:
    report.write("Report:\n")
    # count unique pages
    report.write("\n>>>Unique Pages Found: " + str(len(uniqueURLs)) + "\n")
    # writes longest page and its length
    report.write("\n>>>Longest Page (by Word Count): " + longest_page_url + " (" + str(longest_page_length) + " words)" + "\n")
    
    # writes out most common words by sorting by count, then name
    report.write("\n>>>50 Most Common Words:\n")
    count = 0
    for key,value in sorted(wordCount.items(), key=lambda x:(-x[1], x)):
        if count < 50:
            report.write(f"{key} = {value}\n")
        else:
            break
        count += 1

    # counts and writes all subdomains ordered alphabetically by key and # of unique pages in each domain
    report.write("\n>>>" + str(len(icsSubdomains)) + " Subdomains Found:\n")
    for key,value in sorted(icsSubdomains.items()):
        report.write(key + ", " + str(value) + "\n")
