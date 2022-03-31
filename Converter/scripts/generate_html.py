import os
import time
import requests
import sys
import re

from datetime import date
from bs4 import BeautifulSoup

from scripts.funcs import read_csv, strip_name, new_page, format_time
from scripts.generate_contents import create_main_contents
from scripts.edit_cover_page import edit_cover_page


def generate_html(filename, config, mark_headers = False, header_data = None):
    #time info
    print("generating html")
    start_time = time.perf_counter()
    #get_full_html
    html, contents_data, urls, total_request_time = get_full_html(config, mark_headers)
    html = modify_full_html(html, contents_data, urls, config, header_data)

    path = os.path.join("output", filename)
    with open(path, "w", encoding="utf-8") as file:
        file.write(html)
    #print time info
    print(f"html written to {path}")

    total_time = time.perf_counter() - start_time
    generation_time = format_time(total_time - total_request_time)
    request_time = format_time(total_request_time)

    if total_request_time > 2:
        print("html get requests took {request_time}")
    print(f"html generation took {generation_time}")
    return html

def get_full_html(config, mark_headers):
    #variables
    rows = read_csv(config)
    urls = [row["URL"] for row in rows if row["Include"] != "0"]
    total_request_time = 0
    last_requested = time.perf_counter()
    contents_data = []
    existing_files = os.listdir("scraped_html")
    
    full_html = ""
    for index, row in enumerate(rows):
        if row["Include"] in ['0', '']: continue # skip unecessary rows
        elif row["Include"] in ['2', '3']:
            insert_text = row["Depth"].strip() + " " + row["Header"].strip()
            #if row["URL"] != "":
            name = strip_name(row["URL"])
            contents_data.append( (insert_text, name, row["Depth"]) )
            if mark_headers:
                insert_text = "H3Dr" + insert_text[-4:]
            #insert to html
            insert_id    = f'id="{name}"'
            insert_class = 'class="col-md-8"'
            insert_style = '"'

            if row["Include"] == "2":
                header_tag = f'\n<h1 {insert_class} {insert_id} {insert_style}>{insert_text}</h1>\n'
            else:
                header_tag = f'\n<h1 {insert_class} {insert_style}>{insert_text}</h1>\n'
            
            full_html += header_tag
        
        elif row["Include"] == "1":
            name = strip_name(row["URL"])
            filename = name + ".html"

            #request
            if filename not in existing_files or config["request_existing_files"]:
                if not config["request_existing_files"]: existing_files.append(filename) #do not do duplicate requests (might be unnecessary)
                sretime = time.perf_counter()
                do_request(row["URL"], name, last_requested, config["min_sleep_time"])
                total_request_time += time.perf_counter() - sretime
                last_requested = time.perf_counter()
            #read and modify single html file
            html = read_html_file(filename)
            html, header = strip_html(html, name, row, config, mark_headers)
            contents_data.append( (header, name, row["Depth"]) )

            html = convert_links(html, name, urls)

            #add full html
            full_html += html
        sys.stdout.write(f"\rrun through {index + 1}/{len(rows)} rows")
        sys.stdout.flush()
    print("\n") #to clear for 2 lines
    
    return full_html, contents_data, urls, total_request_time

def modify_full_html(html, contents_data, urls, config, header_data):

    #contents
    if config["add_contents"]:
        contents = create_main_contents(contents_data, header_data)
        html = contents + html

    #flatten subcontents
    html = flatten_subcontents(html)

    #add extra information
    boiler, plate = get_boilerplate()
    cover_page, second_page = get_title_pages()
    second_page = make_internal(second_page, urls)

    #merge into final html
    full_html = boiler + cover_page + second_page + html + plate
    if config["colour_external_links"]:
        full_html = colour_external_links(full_html, config)

    return full_html

def strip_html(html, name, row, config, mark_headers):
    def remove(content, *args, **kwargs): #helper method
        tag = content.find(*args, **kwargs)
        if tag != None:
            tag.decompose()

    def remove_all(content, *args, **kwargs):
        tags = content.find_all(*args, **kwargs)
        for tag in tags:
            if tag != None:
                tag.decompose()
        
    soup = BeautifulSoup(html, features = config["parser"])
    #find main content
    content = soup.find("section", {"id": "content"})
    content.h1.attrs["id"] = name #identify this page
    
    string = row["Depth"] + " " + content.h1.text
    header = string
    if mark_headers:
        string = "H3Dr" + string[:-4]
    content.h1.string = string

    text = ""
    if config["add_body"]:
        remove(content, "div", {"id": "content_disclaimer"})
        remove(content, "div", {"id": "comments"})
        remove(content, "h2", text = "Comments")
        remove(content, "div", {"id": "subscribe"})
        remove(content, "div", {"class": "simple_section_nav"})

        if config["remove_media_background"]:
            remove_all(content, "div", {"class": "print-background"})
    
        text = str(content)
        text = text.replace('class="product_title"', "")
        
        #text = text.replace('<h2 class="anchored_heading"', '<h2 class="anchored_heading" style="margin-top: 0;"')

        #puts a gap above each header
        text = text.replace('<h1 ', f'<h1 style="margin-top: {config["space_above_webpage"]};" ')


        if config["page-break"]: 
            length = config["page-break-length"]
            page_break = '\n<div style = "display:block; clear:both; page-break-after:always;"></div>\n'
            text = re.sub(r"<h3>Contents</h3>", "<h3>Contents</h3>" + page_break, text)

            if length == -1:
                text += page_break
            else: #add a page break if length of text in syntax is longer that set in config
                syntax = content.find("h2", text = "Syntax")
                if syntax != None:
                    block = content.find("pre", {"class": "fixed"})
                    if block != None:
                        if len(block.text.strip()) >= config["page-break-length"]:
                            text = page_break + text
            
    return text, header

def convert_links(html, name, urls):
    #make absolute
    base_url = "https://mariadb.com"
    html = html.replace('href="/', 'href="' + base_url + "/")
    html = html.replace('src="/', 'src="' + base_url + "/")
    #call other link conversions
    html = make_unique(html, name)
    html = make_internal(html, urls)
    return html

def make_unique(html, name):
    """Makes all ids in a page unique to that page"""
    internal_refs = re.findall(r'"#[\w-]+"', html) #find all internal references
    #refs = []
    for ref in set(internal_refs):
        #if ref in refs:
        #    continue
        #refs.append(ref)
        ref = ref[2:][:-1]
        if ref != name: #to prevent doubling h1 ids if that id is linked to
            find = f'id="{ref}"' #
            replacement = f'id="{name}{ref}"'
            html = html.replace(find, replacement)

            find = f'href="#{ref}"'
            replacement = f'href="#{name}{ref}"'
            html = html.replace(find, replacement)
    return html

def make_internal(html, urls):
    """Makes all absolute links internal if they are contained within the csv"""
    html = html.replace('/+quest', '+quest')
    html = html.replace('/+attach', '+attach')
    for url in urls:
        if url != "":
            name = strip_name(url)
            html = html.replace('href="'+ url, 'href="#' + name)
    
    html = html.replace('+quest', '/+quest')
    html = html.replace('+attach', '+/attach')

    #remove duplicates hashes for previously external links carrying internal links
    pattern = r'(href ?= ?")(#[\w-]+)#([\w-]+)'
    html = re.sub(pattern, r"\1\2\3", html)
    return html

def colour_external_links(html, config):
    colour = config["external_link_colour"]
    output = html.replace('href="http', f'style="color: {colour};" href="http')
    return output


def flatten_subcontents(html):
    find = '<div class="table_of_contents'
    replace = '<div style="float: none;" class="table_of_contents'
    html = html.replace(find, replace)
    return html

def do_request(url, name, last_requested, min_sleep_time):
    filename = name + ".html"
    time_since = time.perf_counter() - last_requested
    if time_since > min_sleep_time:
        sleep_time = min_sleep_time - time_since
        print(f'sleeping for {sleep_time}')
        time.sleep(sleep_time)

    print(f"\nrequesting {name}")
    text = requests.get(url).text
    print(f"writing to {filename}")
    path = os.path.join("scraped_html", filename)
    with open(path, "w", encoding = "utf-8") as file:
        file.write(text)

def read_html_file(filename):
    path = os.path.join("scraped_html", filename)
    with open(path, "r", encoding="utf-8") as file:
        contents = file.read()
    
    return contents

def get_boilerplate():
    with open(os.path.join("static_HTML", "boilerplate.html"), "r") as file:
        boilerplate = file.readlines()
    
    boiler = "".join(boilerplate[:-2])
    plate = "".join(boilerplate[-2:])

    return boiler, plate

def get_cover_image():
    image_path = os.path.join(os.getcwd(), "temp", "Cover.jpg")
    string = f'<img style="margin-top: 250;" src="{image_path}">'
    return string

def get_title_pages():
    edit_cover_page()
    #with open(os.path.join("static_HTML", "cover_page.html"), encoding = "utf-8") as file:
    #    cover_page = file.read() + new_page
    cover_page = get_cover_image() + new_page
    with open(os.path.join("static_HTML", "second_page.html"), encoding="utf-8") as file:
        second_page = file.read() + new_page
    
    generated_time = str(date.today())
    second_page = second_page.replace("[generated_time]", generated_time)

    return cover_page, second_page