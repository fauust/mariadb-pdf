import re
import os
import json
import time
import logging
import csv

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

def set_logging():
    logging.getLogger("requests").setLevel(logging.ERROR)
    logging.getLogger('pdfminer').setLevel(logging.ERROR)


#def func
get_time = time.perf_counter
new_page = '<div style = "page-break-after:always;"></div>\n'