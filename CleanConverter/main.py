import json
import time
import logging
#used python files
import used.depth_to_numbers as depth
from used.check_errors import check_errors
from used.funcs import _format_time
#config

with open("config.json", "r") as file:
    config = json.loads(file.read())

#conditional modules

if config["alert_on_pdf"] or config["alert_on_html"]: from used.notifications import notify_pdf, notify_html
if config["write_to_pdf"]: from used.generate_pdf import write_to_pdf
if config["new_html"]: from used.generate_html import make_html, write_to_html, read_html


#functions
def main():
    filepath = depth.modify_csv(config["input_csv"])
    if config["logging"]:
        logging.getLogger("requests").setLevel(logging.WARNING)
        check_errors(config["input_csv"])
    if config["new_html"]:
        start_time = time.perf_counter()

        html, request_time = make_html(config, filepath)
        write_to_html(html)

        total_time_taken = time.perf_counter() - start_time
        generation_time = total_time_taken - request_time

        if config["alert_on_html"]: notify_html(request_time, generation_time)
        print(f"html generation took {_format_time(generation_time)}")
        if request_time > 0: print(f"html get requests took {_format_time(total_time_taken - generation_time)}")
    else:
        html = read_html()
    #write to pdf
    if config["write_to_pdf"]:
        start_time = time.perf_counter()
        write_to_pdf(html, config)

        time_taken = time.perf_counter() - start_time
        print(f"pdf generation took {_format_time(time_taken)}")
        if config["alert_on_pdf"]:
            notify_pdf(time_taken)



main()
