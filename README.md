# MariaDB Pdf-Creator

## Usage
    uses a csv containing urls and other info as a base for pdf creation
    Run Script.py, change settings for creation in the config.json

## Dependencies:
### Python Version: 
    python 3.6 and above

### modules:
    bs4
    pdfkit (if "write_to_pdf" is true)

### Applications:
    if "write_to_pdf" is true:
    You need to have wkhtmltopdf in your local directory

## Config Options:

- "request_html_files": bool - indicates whether or not to re-request all html files

- "new_html": bool - indicates whether to re-use the previous output html file for pdf generation or to create a new one

- "write_to_pdf": bool - indicates whether or not to process and write a new pdf file

- "input_csv": string - which csv file to read from

- "output_html": string - name of output html file

- "output_pdf": string - name of output html file

- "number_of_rows": int - number of rows to look through from the csv, -1 to do all rows

- flatten_internal_contents": bool - whether or not to push each page's internal contents to the left (false sometimes leads to text overlap)

- "min_sleep_time": int - minimum number of seconds to wait between each get request

- "catch-OSError": bool - indicates whether or not to catch the error raised by pdf (currently always raises an error)

- "page-break": bool - indicates whether or not to end the page before each new pdf file (probably sucks with the new headers - haven't tested)

- "css-link": string - if you want to specify css link (leave blank for it to find and fill in automatically)

- "path_to_exe": string - the path to the wkhtmltopdf application

- "options": object - the flags to give to wkhtmltopdf

