import os
import json

from scripts.funcs import new_page

with open(os.path.join("config", "contents.json")) as file:
    config = json.loads(file.read())
BODY = config["Body"]
HEADER = config["Header"]


class content_counter():
    header_style = f'font-size: {HEADER["font_size"]}px; text-align: center; margin-bottom: {HEADER["margin-bottom"]}px; float: none; clear: right;'
    li_style = "margin-top: 0px; margin-bottom: 0px; list-style-type: none; clear: right;"
    content = ""
    def __init__(self, header_txt, body_font, margin_left, font_colour="#333333"):
        self.prev_depth = 0
        self.body_font = body_font
        self.margin_left = margin_left

        self.header = f'\n<h1 class="col-md-8" style="{self.header_style}">{header_txt}</h1>\n'
        self.a_style =f"color: {font_colour}; text-decoration: none;" "font-size: {rep}px;"
    
    def add_content(self, header, name, depth, header_data):
        """nests li elements based on depth and adds that element to content"""
        if depth > self.prev_depth:
            self.content += f'<ol style="margin-left: {self.margin_left}em;">'
        elif depth < self.prev_depth:
            self.content += "</ol>"*(self.prev_depth-depth)
        
        a_style = self.a_style.replace("{rep}", str(round(self.body_font, 1)))
        text = f"{header}"

        ba_style = a_style
        if depth == 1:
            text = "Chapter " + text
            ba_style += f" font-weight: bold;"
        pgnum_style = a_style + " float: right; background: #fff"
        if header_data != None:
            the_header, page_num = header_data
        else: page_num = "x"

        self.content += f"""
            <li style="{self.li_style}">
                <div class="pdfhorizontal_dotted_line">
                    <span><a href="#{name}" style="{ba_style}">{text.strip()}</a></span>
                    <a href="#{name}" style="{pgnum_style}">{page_num}</a>
                </div>
            </li>
                """
        self.prev_depth = depth
    def get_contents(self, depth):
        "finishes html and return contents"
        return self.header + self.content + ("</ol>"*depth)
    
def create_main_contents(ids, header_data = None):
    main = content_counter(
        header_txt = HEADER["table"],
        body_font = BODY["table_font_size"],
        margin_left=BODY["table_indent"]-2.5,
        font_colour = BODY["font_colour"])
    chapters = content_counter(
        header_txt = HEADER["chapters"],
        body_font = BODY["chapter_font_size"],
        margin_left=BODY["chapter_indent"]-2.5,
        font_colour = BODY["font_colour"])
    
    #lambda function to get depth int from Fstr
    get_depth = lambda depth_str: depth_str.count(".") + 1 if depth_str != "" else 0
    #main loop going through each id and giving the information to the counter
    arr = [(header, name, get_depth(depth_str)) for header, name, depth_str in ids]
    if header_data != None:
        print(f"length of header_data {len(header_data)}")
    for index, (header, name, depth) in enumerate(arr):
        i_header = None
        if header_data != None:
            if index < len(header_data):
                i_header = header_data[index]


        main.add_content(header, name, depth, header_data = i_header)
        range_of_depths = [1, 2]
        if depth in range_of_depths:
            chapters.add_content(header, name, depth, header_data = i_header)
    

    return chapters.get_contents(depth) + new_page + main.get_contents(depth) + new_page

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