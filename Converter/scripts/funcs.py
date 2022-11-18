import re
import os
import json
import time
import csv

from datetime import date

def strip_name(url):
    lru = ""
    for c in url:
        lru = c + lru
    try: 
        name = re.match(r"/[\w-]+/", lru)[0]
    except TypeError:
        print(f"Missing url")
        name = ""
    output = ""
    for c in name[1:]:
        output = c + output
    return output[1:]


def format_time(time, startstring = ""):
    """TEMPORARY SOLUTION"""
    s = time
    return f"{int(s // 3600)}h, {int((s % 3600) // 60)}m" if s >= 3600 else f"{int(s // 60)}m, {int(s % 60)}s" if s >= 60 else f"{round(s, 3)}s"


def get_main_config():
    with open(os.path.join("config", "main.json")) as file:
        content = json.loads(file.read())
    return content

def read_csv(config):
    with open(os.path.join("temp", "m_" + config["input_csv"])) as file:
        contents = list(csv.DictReader(file))
    if config["number_of_rows"] > 0:
        contents = contents[:config["number_of_rows"]]
    return [row for row in contents if row["URL"] != ""]

def get_date(tformat = "%Y-%m"):
    today = date.today()
    string = today.strftime(tformat)

    return string

def delete_redownloads(config):
    with open("re-download.txt") as file:
        urls = [url.replace("\n", "") for url in file.readlines()]
    
    urls = list(set(urls))
    existing_files = os.listdir("scraped_html")

    #count deleted files for debug
    num_deleted = 0

    if config["redownload_all_files"]:
        for filename in existing_files:
            os.remove(os.path.join("scraped_html", filename))
            num_deleted += 1
    else:
        for filename in urls:
            
             #turn url into filename
            if filename.startswith("https"): filename = strip_name(filename) + ".html"
            else: filename = filename + ".html"
            #delete file
            
            if filename in existing_files:
                os.remove(os.path.join("scraped_html", filename))
                num_deleted += 1

    #debug delete num_deleted
    if num_deleted > 0: print(f"deleted {num_deleted} files")

    return
get_time = time.perf_counter
new_page = '<div style = "page-break-after:always;"></div>\n'