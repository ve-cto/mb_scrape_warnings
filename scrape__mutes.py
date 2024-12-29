import urllib.request
from urllib.request import urlopen
import re
from collections import defaultdict
import csv

# Base URL for the mutes pages
base_url = "https://punishments.mindbuzz.com.au/mutes.php?page="

# Header to mimic a browser request
header = {'User-Agent': 'Mozilla/5.0'}

# Regular expression pattern to extract necessary details from the HTML
pattern_3 = ('<a href="info.php\\?type=mute&id=(\\d+)">'
             '<div class=\'avatar-name\' align=\'center\'><img class=\'avatar noselect\' src=\'[^\']+\'/>'
             '<br class=\'noselect\'>(.*?)</div></a></td><td>'
             '<a href="info.php\\?type=mute&id=\\d+"><div class=\'avatar-name\' align=\'center\'><img class=\'avatar noselect\' src=\'[^\']+\'/>'
             '<br class=\'noselect\'>(.*?)</div></a></td><td>'
             '<a href="info.php\\?type=mute&id=\\d+">(.*?)</a></td><td>'
             '<a href="info.php\\?type=mute&id=\\d+">(.*?)</a></td>')

# Open and decode the webpage
def fetch_page(url):
    req = urllib.request.Request(url=url, headers=header)
    print("opening...")
    page = urlopen(req)
    print("opened!")
    bytes = page.read()
    raw_html = bytes.decode("utf-8")
    print("decoded")
    return raw_html

# Retrieve the data and remove all HTML tags
def get_reason(raw_html):
    match_results = re.findall(pattern_3, raw_html, re.IGNORECASE)
    reasons_with_ids = [(match[0], match[1], match[2], match[3], match[4]) for match in match_results]
    return reasons_with_ids

# Format the extracted data into a structured format
def format_output(reasons_with_ids):
    formatted_output = []
    for match in reasons_with_ids:
        id, who_was_muted, muted_by, reason, time = match
        formatted_output.append({
            "ID": id,
            "Who was muted": who_was_muted,
            "muted by": muted_by,
            "Reason": reason,
            "Time": time
        })
    return formatted_output

# Clear all mutes data
all_mutes = []

# Start processing pages
page_number = 1
while True:
    # Increment the URL by 1 and fetch the page
    url = base_url + str(page_number)
    raw_html = fetch_page(url)
    
    # Extract the reasons
    reasons_with_ids = get_reason(raw_html)
    if not reasons_with_ids:  # If no data is found, stop the loop
        break
    
    # Format the reasons and add to the all_mutes list
    all_mutes.extend(format_output(reasons_with_ids))
    # Increase the page number to fetch the next page
    page_number += 1

# Tally mutes given and received
mutes_given = defaultdict(int)
mutes_received = defaultdict(int)

# Update the tally counts
for mute in all_mutes:
    mutes_given[mute["muted by"]] += 1
    mutes_received[mute["Who was muted"]] += 1

# Create and write to the CSV file
with open("mutes_summary.csv", "w", newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    
    # Write the tally of mutes given and received
    csv_writer.writerow(["Player", "Number of mutes given", "Number of mutes received"])
    for player in set(mutes_given.keys()).union(set(mutes_received.keys())):
        csv_writer.writerow([player, mutes_given[player], mutes_received[player]])
    
    csv_writer.writerow([])
    csv_writer.writerow(["ID", "Who was muted", "muted by", "Reason", "Time"])
    
    # Write the list of all mutes
    for item in all_mutes:
        csv_writer.writerow([
            item["ID"],
            item["Who was muted"],
            item["muted by"],
            item["Reason"],
            item["Time"]
        ])

print("Data has been written to mutes_summary.csv")

print("if you see this it means that the code didn't error out... good job!")
