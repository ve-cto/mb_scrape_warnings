import urllib.request
from urllib.request import urlopen
import re
from collections import defaultdict
import csv

# Base URL for the kicks pages
base_url = "https://punishments.mindbuzz.com.au/kicks.php?page="

# Header to mimic a browser request
header = {'User-Agent': 'Mozilla/5.0'}

# Regular expression pattern to extract necessary details from the HTML
pattern_3 = ('<a href="info.php\\?type=kick&id=(\\d+)">'
             '<div class=\'avatar-name\' align=\'center\'><img class=\'avatar noselect\' src=\'[^\']+\'/>'
             '<br class=\'noselect\'>(.*?)</div></a></td><td>'
             '<a href="info.php\\?type=kick&id=\\d+"><div class=\'avatar-name\' align=\'center\'><img class=\'avatar noselect\' src=\'[^\']+\'/>'
             '<br class=\'noselect\'>(.*?)</div></a></td><td>'
             '<a href="info.php\\?type=kick&id=\\d+">(.*?)</a></td><td>'
             '<a href="info.php\\?type=kick&id=\\d+">(.*?)</a></td>')

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
        id, who_was_kicked, kicked_by, reason, time = match
        formatted_output.append({
            "ID": id,
            "Who was kicked": who_was_kicked,
            "Kicked by": kicked_by,
            "Reason": reason,
            "Time": time
        })
    return formatted_output

# Clear all kicks data
all_kicks = []

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
    
    # Format the reasons and add to the all_kicks list
    all_kicks.extend(format_output(reasons_with_ids))
    # Increase the page number to fetch the next page
    page_number += 1

# Tally kicks given and received
kicks_given = defaultdict(int)
kicks_received = defaultdict(int)

# Update the tally counts
for kick in all_kicks:
    kicks_given[kick["Kicked by"]] += 1
    kicks_received[kick["Who was kicked"]] += 1

# Create and write to the CSV file
with open("kicks_summary.csv", "w", newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    
    # Write the tally of kicks given and received
    csv_writer.writerow(["Player", "Number of kicks given", "Number of kicks received"])
    for player in set(kicks_given.keys()).union(set(kicks_received.keys())):
        csv_writer.writerow([player, kicks_given[player], kicks_received[player]])
    
    csv_writer.writerow([])
    csv_writer.writerow(["ID", "Who was kicked", "Kicked by", "Reason", "Time"])
    
    # Write the list of all kicks
    for item in all_kicks:
        csv_writer.writerow([
            item["ID"],
            item["Who was kicked"],
            item["Kicked by"],
            item["Reason"],
            item["Time"]
        ])

print("Data has been written to kicks_summary.csv")
print("if you see this it means that the code didn't error out... good job!")
