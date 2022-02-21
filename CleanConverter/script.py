#imports
import requests
from bs4 import BeautifulSoup

import json
import time
import re
import os

#config
with open("config.json", "r") as file:
    config = json.loads(file.read())


#functions
def main():
    if config["from_urls"]:
        request_html()
    
    #html = merge_and_split()
    with open('output.html', encoding = "utf-8") as file:
        html = file.read()
    if config["write_to_html"]:
        write_to_html(html)
    if config["write_to_pdf"]:
        write_to_pdf(html)


#sub functions
def request_html():
    urls = _get_urls()
    sleep_duration = 0
    existing_files = os.listdir("html")
    for index, url in enumerate(urls):
        name = _get_name(url)
        filename = f"{name}.html"
        if not config["request_existing_files"] and filename in existing_files:
            continue
        if sleep_duration > 0:
            print(f"sleeping for {sleep_duration}")
            time.sleep(sleep_duration)
        print()

        start_time = time.perf_counter()
        print(f"sending_request for {name} ({index+1}/{len(urls)})")
        request = requests.get(url)
        print(f"request took {time.perf_counter() - start_time}")
        path = os.path.join('html', filename)
        print(f"writing to {path}")
        with open(path, "w", encoding = "utf-8") as file:
            file.write(request.text)
        
        
        time_took = time.perf_counter() - start_time
        sleep_duration = config["min_sleep_time"] - time_took

def merge_and_split():
    urls = _get_urls()
    filenames = [_get_name(url) for url in urls] 

    html = ""
    print("stripping files")
    for index, name in enumerate(filenames):
        if index % 50 == 0 and index != 0:
            print(f"stripped {index} files")
        path = os.path.join("html", f"{name}.html")
        with open(path, "r", encoding = "utf-8") as file:
            content = file.read()

            content = _strip(content, name)
            content = _convert_links(content, name)

            html += content
    print(f"stripped all {len(filenames)} files")
    boiler, plate = _get_boilerplate()
    return boiler + html + plate

def write_to_html(html):
    output = config["output_html"]
    with open(output, "w", encoding = "utf-8") as file:
        file.write(html)
    print(f"written to {output}")


def write_to_pdf(html):
    """WORK IN PROGRESS"""
    import pdfkit
    path_to_exe = "wkhtmltopdf.exe"
    pdf_config = pdfkit.configuration(wkhtmltopdf=path_to_exe)
    options = { 
      'margin-bottom': '0.75in', 
      'footer-right': '[page] of [topage]',
     }  

    print("\nmaking_pdf")

    pdf_file = config["output_pdf"]
    pdfkit.from_string(html, pdf_file, configuration = pdf_config)
    print("finished")

#sub sub functions
def _strip(html, unique_id):
    def remove(content, *args, **kwargs): #helper method
        tag = content.find(*args, **kwargs)
        if tag != None:
            tag.decompose()
    
    #load into html parser
    soup = BeautifulSoup(html, features = "html.parser")
    soup.prettify()

    #find main content
    content = soup.find("section", {"id": "content"})
    content.h1.attrs["id"] = unique_id
    remove(content, "div", {"id": "content_disclaimer"})
    remove(content, "div", {"id": "comments"})
    remove(content, "h2", text = "Comments")
    remove(content, "div", {"id": "subscribe"})
    remove(content, "div", {"class": "simple_section_nav"})
    return str(content)


def _convert_links(html, unique_id):
    #make absolute
    html = re.sub('href="/kb/en', 'href="' + config["base_url"] + "/kb/en", html)

    #make id's unique
    find_pattern = r"#[\w-]+"
    hash_tags = re.findall(find_pattern, html)
    for string in hash_tags:
        string = string[1:]
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
    urls = _get_urls()
    for url in urls:
        reference = _get_name(url)
        html = html.replace(url, "#" + reference)
    
    return html

def _make_single_internals(html):
    pattern = r'(href ?= ?")(#[\w-]+)#([\w-]+)'
    html = re.sub(pattern, "\1\2", html)
    return html
def _get_name(url):
    lru = ""
    for c in url:
        lru = c + lru
    name = re.match(r"/[\w-]+/", lru)[0]
    output = ""
    for c in name[1:]:
        output = c + output
    return output[1:]


def _get_urls():
    with open("urls.csv") as file:
        urls = file.read().replace("\n", "").split(",")
    do_while = True
    for url in urls:
        if "/" not in url:
            urls.remove(url)
    return urls

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
#call main
main()