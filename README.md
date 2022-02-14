# MariaDB Pdf-Creator


## WORK IN PROGRESS

 MariaDB Pdf-Creator looks through a list of mariaDB urls and extracts information into a pdf


## Usage

    Run Script.py, change settings for creation in the config.json

## Dependecies:
### Python Version: 
    python 3.6 and above

### modules:
    requests_futures
    bs4
    pdfkit (if "write_to_pdf" is true)

### Applications:
    if "write_to_pdf" is true:
    You need to have wkhtmltopdf in your local directory

### Plans:
    I want to not use wkhtmltopdf due to os dependency,
    I need to set external links that link to a page inside of the pdf to reference that part of the pdf.
    I need to modify every id and reference to said id to be specific to each page
    I want to add better comments and cleaner code
    