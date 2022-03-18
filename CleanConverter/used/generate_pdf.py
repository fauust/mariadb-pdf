import pdfkit
import os
import json

def write_to_pdf(html, config):
    print("\nmaking_pdf")
    with open(os.path.join("used", "wkhtmltopdf.json")) as file:
        pdf_options = json.loads(file.read())

    pdf_config = pdfkit.configuration(wkhtmltopdf = config["path_to_app"])
    pdf_file = config["output_pdf"]
    path = os.path.join("output", pdf_file)
    #for easy call
    pdfcall = lambda html, path, wk_config, pdf_options: pdfkit.from_string(html, path, configuration = wk_config, options = pdf_options)
    args = html, path, pdf_config, pdf_options
    if config["catch-OSError"]:
        try:
            pdfcall(*args)
        except OSError: pass
    else: pdfcall(*args)

    print(f"pdf written to {path}")
