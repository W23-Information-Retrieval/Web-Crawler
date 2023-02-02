import pickle

#loading our variables for processing into report with pickle
with open('report.pkl', 'rb') as file:
    uniqueURLs, wordCount, visitedURLs, longest_page_url, longest_page_length, icsSubdomains = pickle.load(file)

with open('report.txt', 'w') as report:
    report.write("Report:\n")
    #count visitedURLs?
    report.write("\n>>>Unique Pages Found: " + str(len(uniqueURLs)) + "\n")

    report.write("\n>>>Longest Page (by Word Count): " + longest_page_url + " (" + str(longest_page_length) + " words)" + "\n")
    #process wordCount
    

    report.write("\n>>>50 Most Common Words:\n")
    # for key,value in wordCount.items():
    #     # if count < 50:
    #     report.write(key + value + "\n")
    count = 0
    for key,value in sorted(wordCount.items(), key=lambda x:(-x[1], x)):
        if count < 50:
            report.write(f"{key} = {value}\n")
        else:
            break
        count += 1

    #count uniqueURLs? then submit list ordered alphabetically and # of unique pages in each domain
    report.write("\n>>>Subdomains Found:\n")
    for key,value in sorted(icsSubdomains.items()):
        report.write(key + ", " + str(value) + "\n")