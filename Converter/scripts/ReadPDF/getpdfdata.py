import time
import os

from scripts.ReadPDF.readpdf import get_text
from scripts.ReadPDF.fromtxt import clean_string, seperate_pages, assign_headers
from scripts.funcs import format_time

ospath = os.path.join


def get_pdf_data(pdfname, config):
    start_time = time.perf_counter()
    pdfpath = os.path.join("output", pdfname)
    print("getting pdf data for", pdfpath)
    #write txt
    if config["toc_pagenumbers"]:
        text = get_text(pdfpath)
        text = clean_string(text)
        with open(ospath("temp", "raw.txt"), "w", encoding="utf-8") as file: file.write(text)
    else:
        with open(ospath("temp", "raw.txt"), "r", encoding="utf-8") as file:
            text = file.read()

    pages = seperate_pages(text)
    headers = assign_headers(pages)

    with open(ospath("temp", "headers.txt"), "w", encoding="utf-8") as file:
        file.write("\n".join(header+pagenum for header, pagenum in headers))
    #time info
    time_taken = time.perf_counter() - start_time
    formatted_time = format_time(time_taken)
    print(f"pdf reading took {formatted_time}\n")
    return headers

if __name__ == "__main__":
    filepath = ospath("output", "Headers.pdf")
    get_pdf_data(filepath)
