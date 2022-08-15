import os
import csv 
import re


from scripts.funcs import strip_name
from scripts.depth_to_numbers import modify_csv

def debug(text):
    with open("csv_debug.log", "a", encoding="utf-8") as outfile:
        outfile.write(text + "\n") 

def empty_log():
    with open("csv_debug.log", "w") as outfile:
        outfile.write("")


class IncludeChecker():
    def __init__(self):
        self.includes = {}
        self.line_nums = []

    def assert_include(self):
        did_log = False
        for name, array in self.includes.items():
            includes = [a for a, b in array]
            line_nums = [str(b) for a, b in array]
            str_line = ",".join(line_nums)
            if includes.count("1") > 1:
                debug(f'({str_line}) Duplicate Include 1 for: {name}')
                did_log = True
            elif includes.count("1") == 0 and includes.count("3") > 0:
                debug(f'({str_line}) Missing Include 1 for: {name}')
                did_log = True
            if includes.count("1") > 0 and includes.count("2") > 0:
                debug(f'({str_line}) Include 2 with Include 1: {name}')
                did_log = True

        return did_log

    def add_to_includes(self, row, num):
        name = "No-URL"
        if row["URL"] != "":
            name = f'"{strip_name(row["URL"])}"'
        
        if name not in self.includes:
            self.includes[name] = []
        self.includes[name].append((row["Include"], num))

def debug_csv(filepath, config):
    if not config["debug_csv"]:
        return
    did_log = False
    include_checker = IncludeChecker()
    with open(filepath) as file:
        reader = csv.DictReader(file)
        rows = list(reader)
    for index, row in enumerate(rows):
        line_num = index + 2
        if row["Include"].strip() == "0" or row["Include"].strip() == "":
            continue
        did_log = depth_missing(row, line_num) or did_log #keeps did_log True
        did_log = missing_headers(row, line_num) or did_log #keeps did_log True
        did_log = missing_url(row, line_num) or did_log #keeps did_log True

        include_checker.add_to_includes(row, line_num)

    did_log = include_checker.assert_include() or did_log#keeps did_log True
    if did_log:
        print(f"issues logged to csv_debug.log")


def correct_license(row, linenum):
    if row["Include"] in ["0", "2", "3"] or row["URL"].strip() == "":
        return False

    correct_licenses = ["GPLv2 fill_help_tables.sql", "CC BY-SA / Gnu FDL", "GPLv2", ""]
    #correct_licenses = [""]
    #sys.stdout.write(f"\rrun through {linenum + 1} rows")
    #sys.stdout.flush()

    name = strip_name(row["URL"])
    filename = f'{name}.html'
    filepath = os.path.join("scraped_html", filename)

    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read()

    license  = find_license(content)

    if license not in correct_licenses:
        debug(f'({linenum}) Incorrect License ("{license}") for {name}')
        return True
    return False

def find_license(html):
    index = html.find("License")

    after_license = html[index:] # find position of license

    a_tag_start = after_license.find("<a")
    a_tag_end = after_license.find("</a>")
    a_tag = after_license[a_tag_start:a_tag_end]

    end_of_styling = a_tag.find(">")
    a = a_tag[end_of_styling+1:]

    return a

def depth_missing(row, num):
    if row["Depth"].strip() == "":
        if row["URL"] != "":
            name = f'"{strip_name(row["URL"])}"'
        else:
            name = "placeholder"
        debug(f"({num}) Depth missing for: {name}")
        return True
    return False

def missing_headers(row, num):
    if int(row["Include"]) not in [2, 3]:
        return False
    header = re.sub(r"[\.\d]", "", row["Header"])
    if header.strip() == "":
        if row["URL"] != "":
            name = strip_name(row["URL"])
        else:
            name = "placeholder"
        debug(f"({num}) Missing Header for: {name}")
        return True
    return False

def missing_url(row, num):
    if row["URL"] == "":
        debug(f"({num}) Missing Url")
        return True
    return False