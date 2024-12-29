import urllib.request
from urllib.request import urlopen
import re
from collections import defaultdict
import csv


def run_kicks():  
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
    with open("entire_summary.csv", "w", newline='') as csvfile:
        csv_writer = csv.writer(csvfile)

        csv_writer.writerow(["Program created by kenobi_luke (Vecto__), 2024. This document adheres to the CC-BY-NC-ND copyright licence. Unauthorised sharing of this program is not allowed."])
        csv_writer.writerow(["The use of this document for explicit malicious intent is not allowed."])
        csv_writer.writerow("")
        csv_writer.writerow("")

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


def run_warns():
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
    with open("entire_summary.csv", "a", newline='') as csvfile:
        csv_writer = csv.writer(csvfile)

        csv_writer.writerow("")
        csv_writer.writerow("")

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

run_kicks()
run_warns()