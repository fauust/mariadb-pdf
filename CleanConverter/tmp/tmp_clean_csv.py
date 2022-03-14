import csv
import re


with open("kb_urls.csv") as file:
    reader = csv.DictReader(file)
    rows = list(reader)
    fd = reader.fieldnames

for row in rows:
    row["Header"] = re.sub("[\.\d]", "", row["Header"]).strip()


with open("kb_urls.csv", "w", newline = "") as file:
    writer = csv.DictWriter(file, fieldnames = fd)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

