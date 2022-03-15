import requests
from bs4 import BeautifulSoup

from datetime import date
import sys
import json
import time
import re
import os
import csv


import used.depth_to_numbers as depth
from used.check_errors import check_errors
from used.generate_contents import create_main_contents, new_page
from used.funcs import _get_name
import logging
logging.getLogger("requests").setLevel(logging.WARNING)
#check_errors
check_errors()
#config
with open("config.json", "r") as file:
    config = json.loads(file.read())

if config["alert_on_pdf"] or config["alert_on_html"]:
    import used.notifications as notify

#call modify_csv
filepath = depth.modify_csv(config["input_csv"])

#declare vars
base_url = "https://mariadb.com"
parser = "html5lib"

boilerplate_filepath = os.path.join("used", "boilerplate.html")
starter_page_filepath = os.path.join("used", "starter_page.html")


#functions


def main():
    #get html
    #long lambda for formatting time
    format_time = lambda s: f"{int(s // 3600)}h, {int((s % 3600) // 60)}m" if s >= 3600 else f"{int(s // 60)}m, {int(s % 60)}s" if s >= 60 else f"{round(s, 3)}s"
    if config["new_html"]:
        html = make_html()
        write_to_html(html)
    else:
        html = read_html()
    
    #write to pdf
    if config["write_to_pdf"]:
        start_time = time.perf_counter()
        write_to_pdf(html)
        time_taken = time.perf_counter() - start_time
        print(f"pdf generation took {format_time(time_taken)}")
        if config["alert_on_pdf"]:
            notify.notify_pdf(time_taken)
def make_html():
    total_time = time.perf_counter()
    total_request_time = 0
    full_html = ""
    rows = _get_rows()
    last_requested = 0
    existing_files = os.listdir("html")

    list_of_ids = []
    for index, row in enumerate(rows):
        if row["Include"] == "": continue
        include = int(row["Include"])
        if include == 0:
            continue
        elif include in [2, 3]:
            url = row["URL"]
            add = row["Header"]
            if config["add_depth"]: add = row["Depth"] + " " + add
            if url != "":
                name = _get_name(row["URL"])
                added_id = f' id="{name}"'
                list_of_ids.append((add, name, row["Depth"]))
            
            if config["add_body"]:
                if include == 2:
                    header_tag = f'\n<h1 class="col-md-8" style="margin-top:0px"{added_id}>{add}</h1>\n'
                else: # include == 3:
                    header_tag = f'\n<h1 class="col-md-8"><a href="#{name}">{add}</a></h1>\n'
                full_html += header_tag
        elif include == 1:
            url = row["URL"]
            name = _get_name(url)
            filename = name + ".html"
            if filename not in existing_files or config["request_existing_files"]:
                time_since = time.perf_counter() - last_requested
                if config["min_sleep_time"] - time_since > 0:
                    print("\nsleeping for " + str(config["min_sleep_time"] - time_since))
                    time.sleep(config["min_sleep_time"] - time_since)
                    total_request_time += 10
                print(f"\nrequesting {name}")
                last_requested = time.perf_counter()
                _request_and_write(url, filename)
            #read full html
            html = _get_html_file(filename)
            html, header = _strip(html, name, row)
            list_of_ids.append((header, name, row["Depth"]))
            if config["add_body"]:
                html = _convert_links(html, name, rows)
                if config["page-break"]:
                    page_break = '\n<div style = "display:block; clear:both; page-break-after:always;"></div>\n'
                    html += page_break
                full_html += html
        #to keep sameline 
        sys.stdout.write(f"\rrun through {index + 1}/{len(rows)} rows")
        sys.stdout.flush()
    print("\n")#clear for 2 new lines

    #contents
    print("making contents")
    if config["add_contents"]:
        full_html = create_main_contents(list_of_ids) + full_html

    
    #final fixes
    print("final fixes")
    if config["flatten_internal_contents"]:
        full_html = _edit_contents(full_html)

    boiler, plate = _get_boilerplate()
    starter_page = _get_starter_page()
    page = boiler + starter_page + full_html + plate
    if config["prettify_html"]:
        page = _prettify_html(page)
    
    total_time_taken = time.perf_counter() - total_time
    format_time = lambda s: f"{int(s // 3600)}h, {int((s % 3600) // 60)}m" if s >= 3600 else f"{int(s // 60)}m, {int(s % 60)}s" if s >= 60 else f"{round(s, 3)}s"
    generation_time = total_time_taken - total_request_time
    print(f"html generation took {format_time(generation_time)}")
    if config["alert_on_html"]:
        notify.notify_html(total_request_time, generation_time)
    if total_request_time > 0:
        print(f"html get requests took {format_time(total_time_taken - generation_time)}")
    return page
def _strip(html, name, row):
    def remove(content, *args, **kwargs): #helper method
        tag = content.find(*args, **kwargs)
        if tag != None:
            tag.decompose()
    
    #load into html parser


    soup = BeautifulSoup(html, features = parser)
    soup.prettify()

    #find main content
    content = soup.find("section", {"id": "content"})
    #content.attrs["style"] = "margin-top:3cm;"
    content.h1.attrs["id"] = name
    #change h1 to have version
    depth = ""
    if config["add_depth"]:
        depth = row["Depth"]
    content.h1.string = depth + " " + content.h1.text

    text = ""
    if config["add_body"]:

        remove(content, "div", {"id": "content_disclaimer"})
        remove(content, "div", {"id": "comments"})
        remove(content, "h2", text = "Comments")
        remove(content, "div", {"id": "subscribe"})
        remove(content, "div", {"class": "simple_section_nav"})
        
    
        text = str(content)
        text = text.replace('class="product_title"', "")
    return text, content.h1.text


def _get_html_file(filename):
    path = os.path.join("html", filename)
    with open(path, "r", encoding="utf-8") as file:
        contents = file.read()
    

    #set css link if not yet set
    if config["css-link"] == "":
        match = re.search(r'[^"]+\.css', contents)
        if match != None:
            link = match[0]
            config["css-link"] = link

    return contents
def _request_and_write(url, filename):
    text = requests.get(url).text
    print(f"writing to {filename}")
    path = os.path.join("html", filename)
    with open(path, "w", encoding = "utf-8") as file:
        file.write(text)

def _convert_links(html, unique_id, urls):
    #make absolute
    html = html.replace('href="/kb/en', 'href="' + base_url + "/kb/en")
    html = html.replace('src="/kb/en', 'src="' + base_url + "/kb/en")
    #make id's unique
    find_pattern = r'"#[\w-]+"' #changing this means changes string = string[1:]
    hash_tags = re.findall(find_pattern, html)
    strings = []
    for string in hash_tags:
        if string in strings:
            continue
        strings.append(string)
        string = string[2:][:-1]
        if string != unique_id: #to prevent doubling h1 ids if that id is linked to
            find = f'id="{string}"'
            replacement = f'id="{unique_id}{string}"'
            html = html.replace(find, replacement)

            find = f'href="#{string}"'
            replacement = f'href="#{unique_id}{string}"'
            html = html.replace(find, replacement)
    html = _make_internal(html, urls)
    html = _make_single_internals(html)

    return html

def _make_internal(html, urls):
    completed = []
    html = html.replace('/+quest', '+quest')
    html = html.replace('/+attach', '+attach')
    for row in urls: 
        url = row["URL"]
        if url != "" and row["Include"] not in ["0", "2"] and url not in completed:
            name = _get_name(url)
            html = html.replace('href="'+ url, 'href="#' + name)
            #html = html.replace('href="#' + name + "+questions", 'href="'+ url + "+questions")
            completed.append(url)
    html = html.replace('+quest', '/+quest')
    html = html.replace('+attach', '+/attach')
    return html

def _make_single_internals(html):
    pattern = r'(href ?= ?")(#[\w-]+)#([\w-]+)'
    html = re.sub(pattern, r"\1\2\3", html)
    return html

def _get_starter_page():
    with open(starter_page_filepath, encoding = "utf-8") as file:
        html = file.read()

    generated_time = str(date.today())
    html = html.replace("[generated_time]", generated_time)
    return html + new_page

def _edit_contents(html):
    find = '<div class="table_of_contents'
    replace = '<div style="float: none;" class="table_of_contents'
    html = html.replace(find, replace)
    return html

def _get_rows():
    with open(filepath) as file:
        contents = list(csv.DictReader(file))
    if config["number_of_rows"] > 0:
        contents = contents[:config["number_of_rows"]]
    return contents



def _get_boilerplate():
    with open(boilerplate_filepath, "r") as file:
        boilerplate = file.readlines()
    
    boiler = "".join(boilerplate[:-2])
    plate = "".join(boilerplate[-2:])

    boiler = _add_css(boiler)
    return boiler, plate

def _add_css(string):
    css_link = config["css-link"]
    index = css_link.find("https")
    if index == -1:
        config["css-link"] = base_url + css_link
    url = config["css-link"]
    line = f'<link rel="stylesheet" href="{url}" type="text/css">'

    string = re.sub("css-link", line, string)
    return string

def _prettify_html(html):
    print("prettifying html")

    return html

def write_to_pdf(html):
    import pdfkit
    print("\nmaking_pdf")

    pdf_config = pdfkit.configuration(wkhtmltopdf = config["path_to_app"])
    pdf_file = config["output_pdf"]
    path = os.path.join("output", pdf_file)
    
    #affect quality
    config["options"]["DPI"] = int(config["options"]["DPI"] * config["quality"])


    #for easy call
    pdfcall = lambda html, path, wk_config, pdf_options: pdfkit.from_string(html, path, configuration = wk_config, options = pdf_options)
    args = html, path, pdf_config, config["options"]
    if config["catch-OSError"]:
        try:
            pdfcall(*args)
        except OSError: pass
    else: pdfcall(*args)

    print(f"pdf written to {path}")

def write_to_html(html):
    path = os.path.join("output", config["output_html"])
    print(f"html written to {path}")
    with open(path, "w", encoding = "utf-8") as file:
        file.write(html)

def read_html():
    path = os.path.join("output", config["output_html"])
    with open(path, "r", encoding = "utf-8") as file:
        html = file.read()
    return html
main()
