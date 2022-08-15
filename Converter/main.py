from scripts.generate_html import generate_html
from scripts.generate_pdf import generate_pdf
from scripts.debug_csv import debug_csv, empty_log
from scripts.ReadPDF.getpdfdata import get_pdf_data
from scripts.notifications import notify

from scripts.depth_to_numbers import modify_csv
from scripts.funcs import get_main_config, get_time, format_time, create_temp, delete_redownloads

def main():
    #config and start time 
    start_time = get_time()
    config = get_main_config()
    filepath = modify_csv(config["input_csv"])

    #reset files
    empty_log()
    create_temp()
    delete_redownloads(config)

    #full runthrough
    if config["toc_pagenumbers"] and config["add_body"] and config["add_contents"] and config["new_pdf"]:
        #get header data
        html = generate_html(filename = "headers.html", config = config, mark_headers=True, log_ext=True)
        generate_pdf(content = html, filename = "headers.pdf", config = config, mark_pages=True)
        header_data = get_pdf_data("headers.pdf", config)

        #write final html and pdf
        html = generate_html(filename = config["output_html"], config = config, header_data = header_data)
        generate_pdf(content = html, filename = config["output_pdf"], config = config)
    #cheap runthrough (no page numbers)
    else:
        html = generate_html(filename = config["output_html"], config = config, log_ext=True)
        generate_pdf(content = html, filename = config["output_pdf"], config = config)

    #csv debug
    debug_csv(filepath, config)

    #print time
    formatted_time = format_time(startstring = "Total Time Taken: ", time = get_time() - start_time)    
    print(f"Total Time Taken: {formatted_time}")
    if config["notify"]: notify(formatted_time)

if __name__ == "__main__":
    print()
    main()