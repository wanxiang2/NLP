import requests
from serpapi import GoogleSearch
import subprocess
import os
import re
import argparse
from bs4 import BeautifulSoup
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
import pandas as pd

import my_secrets
import postprocessing

# Google Patents API Documentation:
# https://serpapi.com/google-patents-api
#
# Google Patents Details API Documentation:
# https://serpapi.com/google-patents-details-api
#
# This program will save all patents about food packaging products from the US Patents Office in its own folder that 
# will be named after its Patent ID using Google Patents API. All these patent directories will be downloaded to the 
# current directory in your computer. Each patent folder will contain a JSON file (which holds JSON data on the patent 
# such as title, id, URL to the PDF, and URLs to figures), a text file that contains all the text from the patent 
# document, and all patent images belonging to that patent (if any). The program will get the text files by using the
# Google Patents Details API, which will be queried for each patent that you need to extract text to a .txt file for.

def main():
    # Sets up command line arguments and flag options.
    parser = argparse.ArgumentParser(description="Contains the query and any flags to specify if you only want the log file, text, or figures.")
    parser.add_argument('query', help='You must pass an argument for what query you would like to make.')        
    
    parser.add_argument('-l', '--log', action='store_true', help='Use -l (--log) flag to only download the log files, which contains the JSON data for each patent.')
    parser.add_argument('-t', '--text', action='store_true', help='Use -t (--text) flag to only download the text files extracted from the patent PDFs.')
    parser.add_argument('-f', '--figures', action='store_true', help='Use -f (--figures) flag to only download the images from each patent if there are any.')

    arguments = parser.parse_args()
    query = arguments.query

    flags = set()
    if arguments.log:
        flags.add('-l')
    if arguments.text:
        flags.add('-t')
    if arguments.figures:
        flags.add('-f')

    if not (arguments.log or arguments.text or arguments.figures):
        flags.add('-l')
        flags.add('-t')
        flags.add('-f')

    page_returned = True
    page_count = 1

    # This loop will call the helper function print_page and print all pages of data.
    while(page_returned):
        page_returned = print_page(page_count, query, flags)
        page_count += 1

    return 0

def print_page(page_number, my_query, my_flags):
    # This makes a connection with the Google Patents API and gets back patent data in the form of a Python dictionary.
    url = "https://serpapi.com/search?engine=google_patents"
    params = {
        "engine": "google_patents",
        "q": my_query,
        "api_key": my_secrets.API_KEY,
        "country": "US",
        "language": "ENGLISH",
        "page": page_number,
        "num": 100,
        "type": "PATENT"
    }

    search = GoogleSearch(params)
    data = search.get_dict()

    value = data.get('organic_results', None)
    if value == None:
        return False
    
    # Looping through each patent in the organic_results of each page and filters the data for title, patent_id, 
    # a snippet of the text, a URL to the PDF, and URLs for any images for each patent
    for patent in value:
        patent_dict = {}
        title = patent.get('title', None)
        patent_id = patent.get('patent_id', None)
        publication_date = patent.get('publication_date', None)
        snippet = patent.get('snippet', None)
        pdf = patent.get('pdf', None)
        figures = patent.get('figures', None)

        patent_dict['title'] = title
        patent_dict['patent_id'] = patent_id
        patent_dict['publication_date'] = publication_date 
        patent_dict['snippet'] = snippet
        patent_dict['pdf'] = pdf
        patent_dict['figures'] = figures

        # Creates a new directory for each patent with the patent id as its name, then enter into that directory. 
        # If a folder with the same name already exists it will do nothing.
        # Then it will write the data in patent_dict into a file ending in .json.
        patent_directory = ""
        if patent_id != None:
            # Filters out directories in the patent_id string, leaving only the Patent ID.
            patent_directory = re.search(r'US[A-Z0-9]+', patent_id)
            if patent_directory != None:
                patent_directory = patent_directory.group()

            else:
                print("\n\n*****Error! The patent id was not what was expected!*****\n\n")
                continue

            if ('-l' not in my_flags) and ('-t' not in my_flags) and (figures == None):
                continue
            else:
                print("\nCreating directory for patent id " + patent_directory + "...")
                os.makedirs(patent_directory, exist_ok=True)
                os.chdir(patent_directory)
                print("Done.\n")

            if '-l' in my_flags:
                print("\nWriting data to " + patent_directory + ".json log file...")
                log_file = open(patent_directory + '.json', 'w')
                log_file.write(str(patent_dict))
                log_file.close()
                print("Done.\n")

            if '-t' in my_flags:
                print("\nWriting text to " + patent_directory + ".txt text file...")

                # Uses the Google Patents Details API and the Patent IDs received from the Google Patents API to 
                # get the full text of each patent in the form of an html webpage. Then Beautiful Soup is used
                # to convert it to writeable text.
                details_url = "https://serpapi.com/search?engine=google_patents_details"
                details_params = {
                    "engine": "google_patents_details",
                    "patent_id": patent_id,
                    "api_key": my_secrets.API_KEY
                }

                details_search = GoogleSearch(details_params)
                details_data = details_search.get_dict()

                description_link = details_data.get('description_link', None)
                if description_link != None:
                    html = requests.get(description_link)
                    html.encoding = 'utf-8'
                    html_text = html.text

                    soup = BeautifulSoup(html_text, 'html.parser')

                    target_paragraphs = soup.find_all(attrs={"class": "description-paragraph"})
                    target_text = [paragraph.get_text() for paragraph in target_paragraphs]
                    
                    # Write the text to a .txt file. Writes a line space for each paragraph in the .txt.
                    with open(patent_directory + '.txt', 'w', encoding='utf-8') as file:
                        for text in target_text:
                            for line in text.splitlines():
                                file.write(line)        
                            file.write("\n\n")          

                    print("\nDone.\n")

                    # This calls the getPickleFiles() function in the postprocessing.py file to read the .txt file that was
                    # just created and generate a pickle file named the patent id + '.pkl'.
                    pickle_result = postprocessing.getPickleFiles(patent_directory)

                else:
                    print("\n*****Error! You've ran out of search credits!*****\n")
        
        # This code will download all the images that any patent documents have to the current directory that you 
        # are on. Since it uses the Linux curl command, it might not work if you are not using a Linux OS.
        if (figures != None) and ('-f' in my_flags):
            print("\nDownloading all images for patent id " + patent_directory + " into directory...\n")
            for figure in figures:
                figure_url = figure['full']
                curl_cmd = ["curl", "-O", figure_url]
                subprocess.run(curl_cmd)    
            print("\nDone.\n")

        # Exit back to its parent directory so the next patent can have its own folder.
        if patent_id != None:
            os.chdir('..')        

    return True

if __name__ == "__main__":
    main()



