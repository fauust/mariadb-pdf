import re

def _get_name(url):
    lru = ""
    for c in url:
        lru = c + lru
    name = re.match(r"/[\w-]+/", lru)[0]
    output = ""
    for c in name[1:]:
        output = c + output
    #print(output[1:])
    return output[1:]