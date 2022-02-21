import csv
import pprint

pp = pprint.PrettyPrinter(indent=2)
pprint = pp.pprint

def is_valid(row):
    
    return row["URL"] != "" and row["Include"] == 1

with open("kb_urls.csv") as file:
    reader = list(csv.DictReader(file))
    

    urls = [row["URL"] for row in reader if is_valid(row)]

    pprint(urls)