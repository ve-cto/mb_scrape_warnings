import urllib.request
from urllib.request import urlopen
import re
from collections import defaultdict
import csv

base_url = "https://punishments.mindbuzz.com.au/warnings.php?page="

header = {'User-Agent': 'Mozilla/5.0'}
pattern_3 = '<a href="info.php\?type=warn&id=(\d+)">(.*?)</a></td><td>'

# open and decode the webpage
def fetch_page(url):
    req = urllib.request.Request(url=url, headers=header)
    print("opening...")
    page = urlopen(req)
    print("opened!")
    bytes = page.read()
    raw_html = bytes.decode("utf-8")
    print("decoded")
    return raw_html


# retrieve the dehta (but remove all html goop {<>})
def get_reason(raw_html):
    match_results = re.findall(pattern_3, raw_html, re.IGNORECASE)
    reasons_with_ids = [(match[0], re.sub("<.*?>", "", match[1])) for match in match_results]
    return reasons_with_ids

# fooorrrmmmatttt
def format_output(reasons_with_ids):
    formatted_output = []
    for i in range(0, len(reasons_with_ids), 4):
        id = reasons_with_ids[i][0]
        who_was_warned = reasons_with_ids[i][1]
        warned_by = reasons_with_ids[i+1][1]
        reason = reasons_with_ids[i+2][1]
        time = reasons_with_ids[i+3][1]
        expired = "yes" if "(Expired)" in time else "no"
        time = time.replace(" (Expired)", "")
        formatted_output.append({
            "ID": id,
            "Who was warned": who_was_warned,
            "Warned by": warned_by,
            "Reason": reason,
            "Time": time,
            "Expired?": expired
        })
    return formatted_output

# clear all warnings
all_warnings = []

# start doing stuff!
page_number = 1
while True:
    # increment the URL by 1 and fetch
    url = base_url + str(page_number)
    raw_html = fetch_page(url)
    
    # extract the reasons
    reasons_with_ids = get_reason(raw_html)
    if not reasons_with_ids: # if none, stop
        break
    
    # format 
    all_warnings.extend(format_output(reasons_with_ids))
    # increase URL number
    page_number += 1

# tally warnings
warns_given = defaultdict(int)
warns_received = defaultdict(int)


for warning in all_warnings:
    warns_given[warning["Warned by"]] += 1
    warns_received[warning["Who was warned"]] += 1

# create and write to the csv file
with open("warnings_summary.csv", "w", newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    
    # tally all the warnings
    csv_writer.writerow(["Player", "Number of warns given", "Number of warns received"])
    for player in set(warns_given.keys()).union(set(warns_received.keys())):
        csv_writer.writerow([player, warns_given[player], warns_received[player]])
    
    csv_writer.writerow([])
    csv_writer.writerow(["ID", "Who was warned", "Warned by", "Reason", "Time", "Expired?"])
    
    # do the list of all the warnings
    for item in all_warnings:
        csv_writer.writerow([
            item["ID"],
            item["Who was warned"],
            item["Warned by"],
            item["Reason"],
            item["Time"],
            item["Expired?"]
        ])

print("data written :]")
print("if you see this it means that the code didn't error out... good job!")
