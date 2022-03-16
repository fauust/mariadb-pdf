import re

def _get_name(url):
    lru = ""
    for c in url:
        lru = c + lru
    name = re.match(r"/[\w-]+/", lru)[0]
    output = ""
    for c in name[1:]:
        output = c + output
    return output[1:]

# def _format_time(s):
#     h = m = 0
#     if s > 3600:
#         h = s // 3600
#         s = s % 3600
#     if s > 60:
#         m = s // 60
#         s = s % 60
    
#     return (h, m, s) if h > 0 else (m, s) if m > 0 else (s)

_format_time = lambda s: f"{int(s // 3600)}h, {int((s % 3600) // 60)}m" if s >= 3600 else f"{int(s // 60)}m, {int(s % 60)}s" if s >= 60 else f"{round(s, 3)}s"