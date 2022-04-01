# MariaDB Server Knowledge Base

## Usage

- uses a csv containing urls and other info as a base for pdf creation
- Run Script.py, change settings for creation in the config.json
- (Requires Converter/temp to be created)

## Dependencies:

### Python Version: 

- python 3.6 and above

### modules:

- bs4
- pdfkit (if "write_to_pdf" is true)
- plyer (if "notify" is true)
- pdfminer.six (if "toc_pagenumbers" is true)

### Applications:

- if "write_to_pdf" is true:
- You need to have wkhtmltopdf in the "path_to_app" set in the config


## Config

### Main Config

```yaml
"request_existing_files": bool #indicates whether or not to re-request all html files

"new_html": bool #indicates whether to re-use the previous output html file for pdf generation or to create a new one

"write_to_pdf": bool #indicates whether or not to process and write a new pdf file

"input_csv": string #which csv file to read from

"output_html": string #name of output html file

"output_pdf": string #name of output html file

"number_of_rows": int #number of rows to look through from the csv, -1 to do all rows

"add_contents": bool # whether or not to add a main contents page

"add_body" # adds the body of the pdf (everything excluding the contents)

"edit_cover_image": bool # edit the cover for this month's date

"read_pdf": bool #TEMPORARY - indicates whether or not to read the pdf for header info and rewrite the txt

"toc_pagenumbers": bool # whether or not to add pagenumbers to the TOC

"logging": bool # whether or not to store csv issues in the issues.log file in output

"space_above_webpage": string # amount of space above each new webpage

"page-break-length": int #the number of characters in each webpages syntax block is greater than this int, it will start the webpage on a new page in the pdf

"page-break": bool #whether or not to use page-break-length

"remove_background_media": bool # removes the file icons in some pages

"notify": bool # sends a little popup upon completion

"mark_external_links": bool # puts a little icon next to each external link (Currently stuck to "true")

"colour_external_links": bool # whether or not to alter the colour of external links

"external_link_colour": string # modifies the external link colour

"flatten_internal_contents": bool #whether or not to push each page's internal contents to the left (false sometimes leads to text overlap)

"min_sleep_time": int #minimum number of seconds to wait between each get request

"catch-OSError": bool #indicates whether or not to catch the error raised by pdf (currently always raises an error)

"parser": string # library to use for Bs4

"path_to_exe": string #the path to the wkhtmltopdf application
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
"page-size": string 
"footer-font-size": int
"margin-top": string # margin-top for each page of the pdf
"margin-bottom": string # margin-bottom for each page of the pdf
"margin-right": string # margin-right for each page of the pdf
"margin-left": string # margin-left for each page of the pdf
"zoom": int
"footer-right": string #places text at footer-right of each page (can use [page] to indicate current page and [topage] to indicate total pages)
"encoding": string
"footer-line": "" #leave empty for a line above the margin-bottom
"disable-javascript": bool
"enable-local-file-access": bool # for using Cover.jpg