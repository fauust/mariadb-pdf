import json
import os
import csv
import logging
import re
if __name__ == "__main__":
    from funcs import _get_name
else:
    from used.funcs import _get_name
logging.basicConfig(filename=os.path.join("used", "issues.log"), level=logging.DEBUG, filemode="w")

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
                logging.debug(f'({str_line}) Duplicate Include 1 for: {name}')
                did_log = True
            elif includes.count("1") == 0 and includes.count("3") > 0:
                logging.debug(f'({str_line}) Missing Include 1 for: {name}')
                did_log = True
            if includes.count("1") > 0 and includes.count("2") > 0:
                logging.debug(f'({str_line}) Include 2 with Include 1: {name}')
                did_log = True
        return did_log

    def add_to_includes(self, row, num):
        name = "No-URL"
        if row["URL"] != "":
            name = _get_name(row["URL"])
        
        if name not in self.includes:
            self.includes[name] = []
        self.includes[name].append((row["Include"], num))

def check_errors(input_csv):
    did_log = False
    include_checker = IncludeChecker()
    with open(input_csv) as file:
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

    did_log = include_checker.assert_include()#keeps did_log True
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

def missing_url(row, num):
    if row["URL"] == "":
        logging.debug(f"({num}) Missing Url")
        return True
    return False
        

if __name__ == "__main__":
    check_errors()