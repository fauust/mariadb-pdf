new_page = '<div style = "page-break-after:always;"></div>\n'
import os
import json
with open(os.path.join("used", "contents.json")) as file:
    config = json.loads(file.read())
BODY = config["Body"]
HEADER = config["Header"]


class content_counter():
    prev_depth = 0
    header_style = f'font-size: {HEADER["font_size"]}px; text-align: center; margin-bottom: {HEADER["margin-bottom"]}px; float: none; clear: right;'
    li_style = "margin-top: 0px; margin-bottom: 0px; list-style-type: none; clear: right;"
    content = ""
    scaling_levels = {}
    def __init__(self, header_txt, body_font, margin_left, font_scaling):
        self.body_font = body_font
        self.margin_left = margin_left
        self.font_scaling = font_scaling

        self.header = f'\n<h1 class="col-md-8" style="{self.header_style}">{header_txt}</h1>\n'
        self.a_style ="color: #333333; text-decoration: none; font-size: {rep}px;"
    
    def add_content(self, header, name, depth, no_children, max_children):
        """nests li elements based on depth and adds that element to content"""
        if depth > self.prev_depth:
            self.content += f'<ol style="margin-left: {self.margin_left}em;">'
        elif depth < self.prev_depth:
            self.content += "</ol>"*(self.prev_depth-depth)
        self.prev_depth = depth
        if depth not in self.scaling_levels:
            self.scaling_levels[depth] = 1 * (1 + self.font_scaling / 1) ** (depth - 1)
        scaling = self.scaling_levels[depth]
        new_font_size = self.body_font# * scaling
        a_style = self.a_style.replace("{rep}", str(round(new_font_size, 1)))
        text = f"{header}"

        if depth == 1:
            text = "Chapter " + text
            a_style += f" font-weight: bold"
        #boldness = int(700 * (no_children/max_children))
        #a_style += f" font-weight: {boldness};"
        self.content += f'<li style="{self.li_style}"><a href="#{name}" style="{a_style}">{text}</a></li>\n'
    
    def get_contents(self, depth):
        "finishes html and return contents"
        return self.header + self.content + ("</ol>"*depth)
    
def create_main_contents(ids):
    main = content_counter(
        header_txt = HEADER["table"], body_font = BODY["table_font_size"], margin_left=BODY["table_indent"]-2.5, font_scaling = BODY["table_scaling"])
    chapters = content_counter(
        header_txt = HEADER["chapters"], body_font = BODY["chapter_font_size"], margin_left=BODY["chapter_indent"]-2.5, font_scaling = BODY["chapter_scaling"])
    
    #lambda function to get depth int from Fstr
    get_depth = lambda depth_str: depth_str.count(".") + 1 if depth_str != "" else 0
    #main loop going through each id and giving the information to the counter
    arr = [(header, name, get_depth(depth_str)) for header, name, depth_str in ids]
    max_children = max([depth_of_children(index, arr) for index, _ in enumerate(arr)])
    for index, (header, name, depth) in enumerate(arr):
        main.add_content(header, name, depth, depth_of_children(index, arr), max_children)
        range_of_depths = [1, 2]
        if depth in range_of_depths:
            chapters.add_content(header, name, depth, depth_of_children(index, arr), max_children)
    
    #print(content_counter.scaling_levels)
    return chapters.get_contents(depth) + new_page + main.get_contents(depth) + new_page

def depth_of_children(sindex, arr):
    count = 0
    prev_depth = 0
    base = arr[sindex][2]
    for index, (_, _, depth) in enumerate(arr[sindex:]):
        if depth < prev_depth:
            break
        elif depth > prev_depth:
            count += 1
            prev_depth = depth

    return count
def find_max_depth(ids, depth_func):
    """highly inefficient mess"""
    highest_depth = 0
    for _, _, depth_str in ids:
        if len(depth_str) <  highest_depth * 2 - 1: #can't be higher
            continue
        depth = depth_func(depth_str)
        if depth > highest_depth:
            highest_depth = depth
    
    return highest_depth