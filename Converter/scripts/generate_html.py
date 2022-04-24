import os
import time
import requests
import sys
import re

from datetime import date
from bs4 import BeautifulSoup

from scripts.funcs import read_csv, strip_name, new_page, format_time, get_date
from scripts.generate_contents import create_main_contents

from scripts.waiter import Waiter

WAITER = Waiter(10)

def generate_html(filename, config, mark_headers = False, header_data = None):
    if not config["new_html"]:
        fpath = os.path.join("output", config["output_html"])
        with open(fpath, encoding="utf-8") as file:
            html = file.read()
        return html

    #time info
    print("generating html")
    start_time = time.perf_counter()
    #get_full_html
    html, contents_data, urls, slugs, total_request_time = get_full_html(config, mark_headers)
    html = modify_full_html(html, contents_data, urls, slugs, config, header_data)

    path = os.path.join("output", filename)
    with open(path, "w", encoding="utf-8") as file:
        file.write(html)
    #print time info
    print(f"html written to {path}")

    total_time = time.perf_counter() - start_time
    generation_time = format_time(total_time - total_request_time)
    request_time = format_time(total_request_time)

    if total_request_time > 2:
        print(f"html get requests took {request_time}")
    print(f"html generation took {generation_time}\n")
    return html

def get_full_html(config, mark_headers):
    #variables
    rows = read_csv(config)
    #urls = [row["URL"] for row in rows if row["Include"] != "0"]
    urls, slugs = get_urls_and_slugs(rows) # TODO
    total_request_time = 0
    contents_data = []
    existing_files = os.listdir("scraped_html")
    
    full_html = ""
    for index, row in enumerate(rows):
        if row["Include"] in ['0', '']: pass # skip unecessary rows
        elif row["Include"] in ['2', '3']:

            insert_text = row["Depth"].strip() + " " + row["Header"].strip()
            #if row["URL"] != "":
            name = strip_name(row["URL"])
            replace = f"rep-{name}-rep"
            contents_data.append( (insert_text, name, row["Depth"]) )
            if mark_headers:
                insert_text = insert_text[4:]
                insert_text = "H3Dr" + insert_text.strip()
            #insert to html
            insert_id    = f'id="{name}"'
            insert_class = 'class="col-md-8"'
            insert_style = ''

            if row["Include"] == "2":
                header_tag = f'\n<h1 {insert_class} {insert_id} {insert_style}>{insert_text}</h1>\n'
            else:
                link_tag = f'<a href="#{name}">{insert_text}</a>'
                header_tag = f'<h1 {insert_class} {insert_style}>{link_tag}</h1>\n'
                #header_tag = header_tag
            
            full_html += header_tag
        
        elif row["Include"] == "1":
            name = strip_name(row["URL"])
            filename = name + ".html"

            #request
            if filename not in existing_files:
                existing_files.append(filename) #do not do duplicate requests (might be unnecessary)
                sretime = time.perf_counter()
                do_request(row["URL"], name, config["min_sleep_time"])
                total_request_time += time.perf_counter() - sretime
            #read and modify single html file
            html = read_html_file(filename)
            html, header = strip_html(html, name, row, config, mark_headers)
            contents_data.append( (header, name, row["Depth"]) )

            html = absolute_links(html)
            html = make_unique(html, name)

            #add full html
            full_html += html
        sys.stdout.write(f"\rrun through {index + 1}/{len(rows)} rows")
        sys.stdout.flush()
    print() #to clear for 2 lines
    
    return full_html, contents_data, urls, slugs, total_request_time

def set_headings():
    pass

def modify_full_html(html, contents_data, urls, slugs, config, header_data):
    #contents
    
    print("merging html")

    html = make_internal(html, urls, slugs)
    if config["add_contents"]:
        contents = create_main_contents(contents_data, header_data)
        html = contents + html

    #flatten subcontents
    html = flatten_subcontents(html)

    #add extra information
    boiler, plate = get_boilerplate()
    cover_page, second_page = get_title_pages(config)
    second_page = make_internal(second_page, urls, slugs)

    #merge into final html
    full_html = boiler + cover_page + second_page + html + plate
    if config["colour_external_links"]:
        full_html = colour_external_links(full_html, config)
    log_external_links(full_html)
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
        string = "H3Dr" + string.strip()[4:]
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

def absolute_links(html):
    """makes page links absolute"""
    base_url = "https://mariadb.com"
    html = html.replace('href="/', 'href="' + base_url + "/")
    html = html.replace('src="/', 'src="' + base_url + "/")
    return html

def make_unique(html, name):
    """Makes all ids in a page unique to that page"""
    internal_ids = re.findall(r'id="[\w-]+"', html) #find all internal references

    for ref in internal_ids:
        ref = ref[4:][:-1]
        if ref != name: #to prevent doubling h1 ids if that id is linked to
            find = f'id="{ref}"' #
            replacement = f'id="{name}{ref}"'
            html = html.replace(find, replacement)

            find = f'href="#{ref}"'
            replacement = f'href="#{name}{ref}"'
            html = html.replace(find, replacement)
    
    return html


def make_internal(html, urls, slugs):
    """Makes all absolute links internal if they are contained within the csv"""
    html = html.replace('/+quest', '+quest')
    html = html.replace('/+attach', '+attach')
    base_url = "https://mariadb.com/kb/en/"
    for index, url in enumerate(urls):
        if url == "":
            continue
        name = strip_name(url)
        html = html.replace('href="'+ url, 'href="#' + name)

        for slug in slugs[index]:
            if slug == "": continue
            slug = base_url + slug + "/"
            html = html.replace('href="'+ slug, 'href="#' + name)

    html = html.replace('+quest', '/+quest')
    html = html.replace('+attach', '+/attach')

    #remove duplicates hashes for previously external links carrying internal links
    pattern = r'(href ?= ?")(#[\w-]+)#([\w-]+)'
    html = re.sub(pattern, r"\1\2\3", html)
    return html

def colour_external_links(html, config) -> str:
    colour = config["external_link_colour"]
    output = html.replace('href="http', f'style="color: {colour};" href="http')
    return output

def log_external_links(full_html):
    links = full_html

def get_urls_and_slugs(rows) -> tuple:
    urls = []
    slugs = []
    for row in rows:
        if row["URL"] != "":
            urls.append(row["URL"])
            dup_slugs = row["Duplicate slugs"]
            slugs.append( dup_slugs.split(";") )
    
    return urls, slugs

def flatten_subcontents(html) -> str:
    find = '<div class="table_of_contents'
    replace = '<div style="float: none;" class="table_of_contents'
    html = html.replace(find, replace)
    return html

def do_request(url, name, min_sleep_time):
    print()
    filename = name + ".html"
    WAITER.wait(True)

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
    date = get_date()
    image_path = os.path.join(os.getcwd(), "cover_images", f"{date}.png")
    string = f'<img src="{image_path}">' + new_page

    with open(os.path.join("static_HTML", "cover.html"), "w", encoding="utf-8") as file:
        file.write(string)

    #string = "<div>hi</div>"+new_page
    return string

def get_title_pages(config):
    cover_page = get_cover_image()
    with open(os.path.join("static_HTML", "second_page.html"), encoding="utf-8") as file:
        second_page = file.read() + new_page
    
    generated_time = str(date.today())
    second_page = second_page.replace("[generated_time]", generated_time)

    return cover_page, second_page