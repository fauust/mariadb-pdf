#imports
import requests
from requests_futures.sessions import FuturesSession
from bs4 import BeautifulSoup

import json
import time
import re
import csv
import os

#config
with open("config.json", "r") as file:
    config = json.loads(file.read())

if config["write_to_pdf"]:
    import pdfkit

stripped_html_dir = "stripped_html"
full_html_dir = "full_html"
#functions
def get_urls():
    """returns a list containing all the urls located in 'urls.csv' """
    print("getting urls...")
    with open("urls.csv") as file:
        urls = file.read().split(',')
    return urls


def write_urls_to_html(urls):
    print("sending requests")
    session = FuturesSession()
    sent_requests = []
    for url in urls:
        request  = session.get(url)
        sent_requests.append(request)
    print("waiting for requests")
    while sent_requests != []:
        time.sleep(0.1)
        for index, request in enumerate(sent_requests):
            if request in busy_requests and request._state != "RUNNING":
                filename = f"temp({index}).html"
                path = os.path.join(full_html_dir, filename)

                content = request.result().text
                with open(path, "w", encoding = "utf-8") as file:
                    file.write(content)
                busy_requests.remove(request)


def modify_html_files():
    files = os.listdir(full_html_dir)
    print("stripping files")
    for filename in files:
        path = os.path.join(full_html_dir, filename)
        with open(path, "r", encoding = "utf-8") as file:
            html = file.read()
        
        html = _strip(html)
        html = _absolute_links(html)
        html = _convert_links(html, filename)


        path = os.path.join(stripped_html_dir, filename)
        with open(path, "w") as file:
            file.write(html)

def merge_html_files():
    print("merging files")
    files = os.listdir("stripped_html")

    boiler, plate = _get_boilerplate()
    output_file = config["output_name"] + ".html"
    with open(output_file, "w") as file:
        file.write(boiler)

    for filename in files:
        path = os.path.join(stripped_html_dir, filename)
        with open(path, "r", encoding = "utf-8") as file:
            html = file.read()
        
        with open(output_file, "a", encoding = "utf-8") as file:
            file.write(html)

    with open(output_file, "a", encoding = "utf-8") as file:
        file.write(plate)
        

def write_to_pdf():
    path_to_exe = "wkhtmltopdf.exe"
    pdf_config = pdfkit.configuration(wkhtmltopdf=path_to_exe)
    print("making_pdf")

    html_file = config["output_name"] + ".html"
    pdf_file = config["output_name"] + ".pdf"
    with open(html_file, "r") as file:
        html = file.read()
    pdfkit.from_string(html, pdf_file, configuration = pdf_config)
    print("finished")

def _strip(html):
    def remove(content, *args, **kwargs): #helper method
        tag = content.find(*args, **kwargs)
        tag.decompose()
    
    #load into html parser
    soup = BeautifulSoup(html, features = "html.parser")
    soup.prettify()

    #find main content
    content = soup.find("section", {"id": "content"})
    #remove unwanted information
    remove(content, "div", {"id": "content_disclaimer"})
    remove(content, "div", {"id": "comments"})
    remove(content, "h2", text = "Comments")
    remove(content, "div", {"id": "subscribe"})

    remove(content, "div", {"class": "simple_section_nav"})

    
    #remove(content, "h2", {"id": "see-also"})

    #tags = content.findAll("ul")
    #for i in tags: i.decompose()

    #link = soup.find("link", {"rel": "stylesheet"})
    #for child in link.findChildren():
    #    child.decompose()

    return str(content)

def _absolute_links(html):
    html = re.sub('href="/', 'href="' + config["base_url"] + "/", html)
    return html


def _convert_links(html, filename):
    num = int(re.search("\d", filename)[0])
    replacement = chr(num + 97) + "_"
    #print(replacement)
    find_pattern = '#\w+'
    hash_tags = re.findall(find_pattern, html)
    tag_list = ""
    for tag in hash_tags:
        tag = tag[1:]
        tag_list += f"{tag}|"
    tag_list = tag_list[:-1]
    pattern = f"({tag_list})"
    html = re.sub(pattern, replacement + r"\1", html)

    return html

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


if __name__ == "__main__":
    if config["from_urls"]:
        urls = get_urls()
        write_urls_to_html(urls)
    modify_html_files()
    merge_html_files()
    if config["write_to_pdf"]:
        write_to_pdf()