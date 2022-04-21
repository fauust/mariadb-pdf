import pdfkit
import os
import json
import time

from scripts.funcs import format_time

def generate_pdf(content, filename, config, mark_pages=False):
    if not config["new_pdf"]:
        return
    print("making_pdf")
    start_time = time.perf_counter()

    with open(os.path.join("config", "wkhtmltopdf.json")) as file:
        pdf_options = json.loads(file.read())
    if mark_pages: pdf_options["footer-right"] += "PAGE"

    pdf_config = pdfkit.configuration(wkhtmltopdf = config["path_to_app"])
    path = os.path.join("output", filename)
    #for easy call

    cover = os.path.join("static_HTML", "cover.html")

    pdfcall = lambda content, path, wk_config, pdf_options: pdfkit.from_string(content, path, configuration = wk_config, options = pdf_options)
    args = content, path, pdf_config, pdf_options
    if config["catch-OSError"]:
        try:
            pdfcall(*args)
        except OSError: pass
    else: pdfcall(*args)

    print(f"pdf written to {path}")
    #time info
    time_taken = time.perf_counter() - start_time
    formatted_time = format_time(time_taken)
    print(f"pdf generation took {formatted_time}\n")
