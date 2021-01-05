from bs4 import BeautifulSoup
from bs4 import Comment
from pathlib import Path
import os

doc_template = """
    <html>
        <head>
            <title> SURF analysis </title>
        </head>

        <body>
            <div class="meta-source">
                <h1 class="source"></h1>
            </div>
        </body>
    </html>
"""

plot_template = """
    <div>
        <h3 id='title'></h3>
        <h4 id='metric'> Metric: </h4>
        <p id='meta-data'>File name: </p>
        <img/>
        <p id='explanation'></p>
    </div>
"""

TOOL_PATH = Path(os.path.abspath(__file__)).parent

class GeneratePage:
    def __init__(self, source): # 'source' is used to make the html doc in disk,mem,cpu
        self.source = source
        self.source_file_path = os.path.join(str(TOOL_PATH) + "/html_pages/", source + "_page.html")
        f = open(self.source_file_path, 'r')
        file_contents = f.read()

        self.doc_bs4 = BeautifulSoup(file_contents, "html.parser") # Get doc from .html file template
        self.plot_template_bs4 = BeautifulSoup(plot_template, "html.parser")

    def add_plot(self, file):

        pass

    def save_file(self, file):
        pass

    def write_to_file(self, file_bs4):
        """
        file is a type of beautifulsoup html parser
        return: written source_file
        """
        source_file = open(self.source_file_path, "w")

        source_file.write(str(file_bs4.prettify())) # unicode also can be used
        source_file.close()

    def launch(self, title, savefig_title, *args):
        metric = args[0] if args is not None else exit(1)
        
        plot_div = self.plot_template_bs4.div

        path_to_plot = os.path.join(str(TOOL_PATH) + "/plots/", savefig_title + ".pdf")


        plot_div.find(id="title").append(title)
        plot_div.find(id='metric').append(metric)
        plot_div.find(id="meta-data").append(savefig_title)
        plot_div.img['src'] = path_to_plot

        self.doc_bs4.body.append(plot_div)  # Append plot to main doc

        # Write the template to an html file
        self.write_to_file(self.doc_bs4)