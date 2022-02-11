from requests import Session
from requests_futures.sessions import FuturesSession
from bs4 import BeautifulSoup
import pdfkit
import time
import os
import re



class Converter():
    base_url = "https://mariadb.com"
    filename = "script.html"
    def __init__(self, urls, css = True):
        self.urls = urls
        self.css = css
        self.files = []
        self.direct = "script_html"
        if self.css:
            self.output = "script_css"
        else:
            self.output = "script_nocss"
    
    def get_html(self):
        #create sessions
        session = FuturesSession()

        #get sessions
        sessions = [session.get(url) for url in self.urls]

        #wait for sessions to finish

        #create a list of running sessions
        running_sessions = list(sessions)


        while running_sessions != []: # while there are still running sessions
            for s in running_sessions: # iterate through them
                if s._state != "RUNNING": # and check if they are running
                    running_sessions.remove(s) # remove if they are completed
        
        all_text = []
        for s in sessions:
            session_text = s.result().text
            all_text.append(session_text)
        
        self.html = all_text

    def strip(self):
        #little helper function for later
        def remove(content, *args, **kwargs): 
            tag = content.find(*args, **kwargs)
            tag.decompose()
        for index, code in enumerate(self.html):
            #make and clean up html structure
            soup = BeautifulSoup(code, features = "lxml")
            soup.prettify()

            #find the relevant information
            content = soup.find("section", {"id": "content"})
            
            #remove unwanted information
            remove(content, "div", {"id": "content_disclaimer"})
            remove(content, "div", {"id": "comments"})
            remove(content, "h2", text = "Comments")
            remove(content, "div", {"id": "subscribe"})

            remove(content, "div", {"class": "simple_section_nav"})
            remove(content, "h2", {"id": "see-also"})


            tags = content.findAll("ul")
            for i in tags: i.decompose()

            link = soup.find("link", {"rel": "stylesheet"})
            for child in link.findChildren():
                child.decompose()
            if not self.css:
                link = ""
            self.html[index] = str(link) + str(content)

    def absolute_links(self):
        for index, string in enumerate(self.html):
            self.html[index] = re.sub('href="/', 'href="' + self.base_url + "/", string)



    def write_to_file(self):
        for index, h in enumerate(self.html):
            filename = str(index) + ".html"
            path = os.path.join(self.direct, filename)
            self.files.append(path)
            with open(path, "w", encoding = "utf-8") as file:
                file.write(h)


    def write_to_pdf(self):
        path_to_exe = "C:\\Program Files\\wkhtmltopdf\\bin\wkhtmltopdf.exe"
        config = pdfkit.configuration(wkhtmltopdf=path_to_exe)
        print("making_pdf")
        new_file = pdfkit.from_file(self.files, self.output + ".pdf", configuration = config)
        #with open(self.files, "w") as file:
        #    file.write(text)
        print("finished")


urls = ["https://mariadb.com/kb/en/select/", "https://mariadb.com/kb/en/limit/",
        "https://mariadb.com/kb/en/order-by/", "https://mariadb.com/kb/en/union/"]

#urls = ["https://mariadb.com/kb/en/select/"]

converter = Converter(urls)
converter.get_html()
converter.strip()
converter.absolute_links()
converter.write_to_file()
converter.write_to_pdf()