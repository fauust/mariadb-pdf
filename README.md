# MariaDB Server Knowledge Base

## Usage

- uses a csv containing urls and other info as a base for pdf creation
- Run main.py, change settings for creation in the config.json
- (Requires Converter/temp to be created)

## Dependencies:

### Python 3.9+ (below are untested)

### Modules:

- requests
- bs4
- html5lib
- pdfkit (if "new_pdf" is true)
- plyer (if "notify" is true)
- pdfminer.six (if "toc_pagenumbers" is true)

### Applications:

- if "new_pdf" is true:
- You need to have wkhtmltopdf in the "path_to_app" set in the config


## Config

### Main Config

```yaml
"redownload_all_files": #deletes all existing files in scraped_html to be re-requested

"redownload_files": bool #deletes all filenames/urls in re-download.txt to be re-requested

"new_html": bool #creates a new output html for pdf conversion

"new_pdf": bool #processes and writes a new pdf file

"toc_pagenumbers": bool #adds pagenumbers to the TOC

"check_slugs": bool #checks alternate slugs based on csv information

"debug_csv": bool #debugs the csv and logs to csv_debug.log

"notify": bool #sets up an alert upon final completion

"page-break": bool #sets up page breaks based on Syntax block sizes (WIP)

"mark_external_links": bool #places an icon next to external links

"colour_external_links": bool #colours external links

"add_contents": bool #creates the TOC

"add_body": #creates the main pdf body 

"flatten_internal_contents": bool #flattens each pages contents to prevent text overlap

"remove_media_background": bool #removes specific images like folder icons for categories

"catch-OSError": bool #catches the OSError raised by wkhtmltopdf if sent

"input_csv": string #filename for input csv

"output_html": string #filename for output html

"output_pdf": string #filename for output pdf

"number_of_rows": int #number of rows to read from the csv (-1 for all)

"page-break-length": #length of Syntax Block at which new pages are added

"min_sleep_time": int #minimum number of seconds between each GET request

"space_above_webpage": string #space above each page (untested)

"external_link_colour": string  #colour for external links

"parser": string #html parser for bs4

"path_to_app": string #path to wkhtmltopdf (leave empty for automatic location)
```

### Contents Config

```yaml
"Body" {
    "chapter_font_size": int,
    "table_font_size": int,
    "chapter_indent": float,
    "table_indent": float,
    "font_colour": string
}
"Header" {
    "font_size": int,
    "table": string,
    "chapters": string,
    "margin-bottom": int
}
```

### Wkhtmltopdf.json

```yaml
"DPI": int # affects quality of text rendering and filesize

"page-size": string #page size (eg. A4)

"footer-font-size": int #size for page numbers

"margin-top": string # margin-top for each page of the pdf

"margin-bottom": string # margin-bottom for each page of the pdf

"margin-right": string # margin-right for each page of the pdf

"margin-left": string # margin-left for each page of the pdf

"zoom": float #zoom level

"footer-right": string #places text at footer-right of each page (can use [page] to indicate current page and [topage] to indicate total pages)

"encoding": string #encoding format

"footer-line": "" #leave empty for a line above the margin-bottom

"quiet": "" #leave empty for quiet pdf generation

"disable-javascript": bool #disables javascript

"enable-local-file-access": bool #for using the cover image
```
# The Scraper

The scraper is for finding what needs to be added to the csv.

It currently operates in a seperate directory resulting in duplicate files.