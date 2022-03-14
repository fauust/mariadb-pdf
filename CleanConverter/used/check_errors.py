import json
import os
import csv
import logging
import re
if __name__ == "__main__":
    from funcs import _get_name
else:
    from used.funcs import _get_name
logging.basicConfig(filename=os.path.join("used", "issues.log"), encoding='utf-8', level=logging.DEBUG, filemode="w")

with open("config.json") as file:
    config = json.loads(file.read())

def check_errors():
    did_log = False
    with open(config["input_csv"]) as file:
        reader = csv.DictReader(file)
        rows = list(reader)
    
    for index, row in enumerate(rows):
        line_num = index + 2
        if row["Include"].strip() == "0" or row["Include"].strip() == "":
            continue
        did_log = depth_missing(row, line_num) or did_log #keeps did_log True
        did_log = missing_headers(row, line_num) or did_log #keeps did_log True
    if did_log:
        print(f"issues logged to issues.log")

def depth_missing(row, num):
    if row["Depth"].strip() == "":
        if row["URL"] != "":
            name = _get_name(row["URL"])
        else:
            name = "placeholder"
        logging.debug(f"({num}) Depth missing for: {name}")
        return True
    return False

def headers_have_depth(row, num):
    pass

def missing_headers(row, num):
    if int(row["Include"]) not in [2, 3]:
        return False
    header = re.sub(r"[\.\d]", "", row["Header"])
    if header.strip() == "":
        if row["URL"] != "":
            name = _get_name(row["URL"])
        else:
            name = "placeholder"
        logging.debug(f"({num}) Missing Header for: {name}")
        return True
    return False
if __name__ == "__main__":
    check_errors()