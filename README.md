# US Patents Scraper

This repo can extract US patent data, text, and images based on a query you provide. Everything extracted is saved in the current directory.
It uses the Google Patents API and the Google Patents Details API.

You'll need to create a Serpapi account (https://serpapi.com/google-patents-api) and get an API key.

To extract patents, run this on the terminal:
python3 NLPScript.py "your query" flags

You can use -l flag for only JSON data, -t flag for only text, or -f flag for only images. If you don't add any flags, it will download everything.

After you get all the text files, you can run postprocessing.py or merged_post_processing.py to create pickle files from all the text files and use them in an NER model.
postprocessing.py creates a pickle file for each patent text file and merged_post_processing.py creates one single pickle file for all the patent text files.

# Data For DeBERTa Pretraining

The download_harvard_data.py file is used to download another patents dataset that can be used to pretrain deBERTa.