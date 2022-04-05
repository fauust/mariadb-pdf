from scripts.generate_html import generate_html
from scripts.generate_pdf import generate_pdf
from scripts.debug_csv import debug_csv
from scripts.ReadPDF.getpdfdata import get_pdf_data
from scripts.notifications import notify

from scripts.edit_cover_pages import edit_covers
from scripts.funcs import get_main_config, get_time, format_time, set_logging, create_temp


def main():
    #config and start time 
    start_time = get_time()
    config = get_main_config()

    #debug
    print()
    set_logging()
    create_temp()
    edit_covers()

    #get header data
    html = generate_html(filename = "headers.html", config = config, mark_headers=True)
    generate_pdf(content = html, filename = "headers.pdf", config = config, mark_pages=True)
    header_data = get_pdf_data("headers.pdf", config)

    #write final html and pdf
    html = generate_html(filename = config["output_html"], config = config, header_data = header_data)
    generate_pdf(content = html, filename = config["output_pdf"], config = config)

    #csv debug
    debug_csv(config["input_csv"])


    #print time
    formatted_time = format_time(startstring = "Total Time Taken: ", time = get_time() - start_time)
    
    
    print(f"Total Time Taken: {formatted_time}")
    if config["notify"]: notify(formatted_time)

if __name__ == "__main__":
    main()