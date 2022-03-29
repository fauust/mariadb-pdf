import re
import time
def clean_string(contents):
    string = ""
    for char in contents:
        if char.isalnum() or char in [" ", "\n", ".", "/"]:
            string += char

    return string

def seperate_pages(contents):
    matches = re.finditer(r"(\d+)/(\d+)(PAGE)", contents)
    pagenums = [match for match in matches]
    last_index = 0
    pages = []
    for match in pagenums:
        pagenum, max_num, _ = match.groups()
        index = match.end(0)
        #index = contents.index(f"\n({pagenum}/{max_num})(PAGE)").groups()[0]
        page_contents = contents[last_index: index]
        pages.append((page_contents, pagenum))
        last_index = index
    return pages

def assign_headers(pages):
    all_headers = []
    for content, pagenum in pages:
        #print(len(content), pagenum)
        headers = re.findall(r"H3Dr([\d.\w ]+)", content)
        headers = [(header, pagenum) for header in headers]
        all_headers += headers
    
    #print(all_headers)
    return all_headers