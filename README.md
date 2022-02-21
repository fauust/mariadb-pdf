# MariaDB Pdf-Creator


## WORK IN PROGRESS

 MariaDB Pdf-Creator looks through a list of mariaDB urls and extracts information into a pdf

## Usage
    uses urls.csv as a base for pdf creation
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

##