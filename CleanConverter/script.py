#imports
import requests
from bs4 import BeautifulSoup

import sys
import json
import time
import re
import os
import csv

#config
with open("config.json", "r") as file:
    config = json.loads(file.read())


#functions
def main():
    if not config["read_off_output"]:
        html = make_html()
    else:
        path = os.path.join("output", config["output_html"])
        with open(path, "r", encoding = "utf-8") as file:
            html = file.read()
    if config["write_to_html"]:
        write_to_html(html)
    if config["write_to_pdf"]:
        write_to_pdf(html)
def make_html():
    full_html = ""
    rows = _get_rows()
    last_requested = stripped = 0
    for index, row in enumerate(rows):
        if row["Include"] == "": continue
        include = int(row["Include"])
        
        if include == 0:
            continue
        elif include == 2:
            add = row["Header"]
            full_html += f'\n<h1 class="col-md-8">{add}</h1>\n'
        elif include == 3:
            url = row["URL"]
            name = _get_name(url)
            add = row["Header"]
            full_html += f'\n<h1 class="col-md-1"><a href="#{name}">{add}</a></h1>\n'
        elif include == 1:
            if stripped > 0 and stripped % 50 == 0:
                print(f"stripped {stripped}")
            time_since = time.perf_counter() - last_requested
            if config["min_sleep_time"] - time_since > 0:
                time.sleep(config["min_sleep_time"] - time_since)

            existing_files = os.listdir("html")
            url = row["URL"]
            name = _get_name(url)
            filename = name + ".html"
            if filename not in existing_files or config["request_existing_files"]:
                print(f"requesting {name}")
                _request_and_write(url, name)
                last_requested = time.perf_counter()

            html = _get_html_file(filename, existing_files)


            html = _strip(html, name, row)
            html = _convert_links(html, name)
            full_html += html
        #to keep sameline 
        sys.stdout.write(f"\rrun through {index + 1} rows")
        sys.stdout.flush()
    sys.stdout.write("\n")#to clear for next line
    boiler, plate = _get_boilerplate()
    return boiler + full_html + plate

def _strip(html, name, row):
    def remove(content, *args, **kwargs): #helper method
        tag = content.find(*args, **kwargs)
        if tag != None:
            tag.decompose()
    
    #load into html parser
    soup = BeautifulSoup(html, features = "html.parser")
    soup.prettify()

    #find main content
    content = soup.find("section", {"id": "content"})
    #content.attrs["style"] = "margin-top:3cm;"
    content.h1.attrs["id"] = name

    #change h1 to have version
    content.h1.string = row["Header"] + " " + content.h1.text


    remove(content, "div", {"id": "content_disclaimer"})
    remove(content, "div", {"id": "comments"})
    remove(content, "h2", text = "Comments")
    remove(content, "div", {"id": "subscribe"})
    remove(content, "div", {"class": "simple_section_nav"})
    
    
    text = str(content)
    text = text.replace('class="product_title"', "")

    return text


def _get_html_file(filename, existing_files):
    path = os.path.join("html", filename)
    with open(path, "r", encoding="utf-8") as file:
        contents = file.read()
    
    return contents
def _request_and_write(url, filename):
    print("requesting url")
    text = requests.get(url).text
    print("writing to filename")
    path = os.path.join("html", filename)
    with open(path, "w", encoding = "utf-8") as file:
        file.write(text)

def _convert_links(html, unique_id):
    #make absolute
    #html = re.sub('href="/kb/en', 'href="' + config["base_url"] + "/kb/en", html)
    html = html.replace('href="/kb/en', 'href="' + config["base_url"] + "/kb/en")
    #make id's unique
    find_pattern = r'"#[\w-]+"' #changing this means changes string = string[1:]
    hash_tags = re.findall(find_pattern, html)
    for string in hash_tags:
        string = string[2:][:-1]
        find = f'"{string}"'
        replacement = f'"{unique_id}{string}"'
        html = html.replace(find, replacement)

        find = f'"#{string}"'
        replacement = f'"#{unique_id}{string}"'
        html = html.replace(find, replacement)

    html = _make_internal(html)
    html = _make_single_internals(html)

    return html

def _make_internal(html):
    urls = _get_rows()
    for row in urls:
        if row["URL"] != "":
            url = row["URL"]
            name = _get_name(url)
            html = html.replace(url, "#" + name)
    return html

def _make_single_internals(html):
    pattern = r'(href ?= ?")(#[\w-]+)#([\w-]+)'
    html = re.sub(pattern, r"\1\2\3", html)
    return html
def _get_rows():
    with open(config["input_csv"]) as file:
        contents = list(csv.DictReader(file))

    if config["number_of_rows"] > 0:
        contents = contents[:config["number_of_rows"]]

    return contents

def _get_name(url):
    lru = ""
    for c in url:
        lru = c + lru
    name = re.match(r"/[\w-]+/", lru)[0]
    output = ""
    for c in name[1:]:
        output = c + output
    #print(output[1:])
    return output[1:]



def _get_boilerplate():
    with open("boilerplate.html", "r") as file:
        boilerplate = file.readlines()
    
    boiler = "".join(boilerplate[:-2])
    plate = "".join(boilerplate[-2:])

    boiler = _add_css(boiler)
    return boiler, plate

def _add_css(string):
    url = config["base_url"] + "/kb/static/css/main.9a0d7dcebefd.css"
    line = f'<link rel="stylesheet" href="{url}" type="text/css">'

    string = re.sub("css-link", line, string)
    return string

def write_to_pdf(html):
    """WORK IN PROGRESS"""

    #check to see if wkhtmltopdf is in the directory
    for filename in os.listdir():
        if filename.find("wkhtmltopdf") != -1: break
    else: raise OSError("wkhtmltopdf is not in the correct directory")


    import pdfkit
    path_to_exe = "wkhtmltopdf.exe"
    pdf_config = pdfkit.configuration(wkhtmltopdf=path_to_exe)
    options = {
        'margin-bottom': '1cm', 
        'margin-top': '1cm',
        'footer-line': '',
        'page-size': 'Letter',
        'footer-right': '[page]/[topage]',
     }

    print("\nmaking_pdf")

    pdf_file = config["output_pdf"]

    path = os.path.join("output", pdf_file)
    try:
        pdfkit.from_string(html, path, configuration = pdf_config, options = options)
    except OSError:
        pass
    print(f"pdf written to {path}")

def write_to_html(html):
    path = os.path.join("output", config["output_html"])
    print(f"html written to {path}")
    with open(path, "w", encoding = "utf-8") as file:
        file.write(html)


main()