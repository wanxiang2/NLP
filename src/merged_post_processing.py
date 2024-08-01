import os
import re
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
import pandas as pd

# When this main function is called, it iteratively looks for all folders that start with 'US' in the current directory, goes into those folders, 
# reads the .txt file within the folder, then goes back to the original directory you started from. After it is done for all the text files, 
# it will create a single pickle file for all of them. Call this file after you are done collecting your text data from the Google Patents Details API 
# by calling the NLPScript.py file and need to generate one single pickle file for all the text files you've created.

# This code will create one pickle file to put in an NER model from all the text files. postprocessing.py creates a pickle file for each
# patent text file.

def main():
    current_dir = os.getcwd()

    regex = re.compile(r'US*')

    # List all folders in the current directory
    all_folders = os.listdir(current_dir)

    # Filter for folders that are patent folders, which all start with 'US' 
    patent_folders = [patent_folder for patent_folder in all_folders if regex.match(patent_folder) and os.path.isdir(patent_folder)]

    tokenized_sentences = []
    tokenized_labels = []

    for patent_directory in patent_folders:
        dir_path = os.path.join(current_dir, patent_directory)
        
        os.chdir(dir_path)

        print("\nUsing the text file to create a pickle file called " + patent_directory + ".pkl for Natural Language Processing...")
                    
        # Reads from the .txt file that you created. Then, first split the text by sentences using NLTK, then
        # split those sentences into words and punctuation using NLTK. After that, it adds everything to
        # a Pandas DataFrame and saves it as a pickle file.
        with open(patent_directory + '.txt', 'r', encoding='utf-8') as read_file:
            content = read_file.read()
            sentences_list = sent_tokenize(content)
            
            for sentence in sentences_list:
                 tokenized_sentences.append(word_tokenize(sentence))
                 tokenized_labels.append(['O' for label_index in range(len(tokenized_sentences[-1]))])                    

        os.chdir(current_dir)

    data_frame = pd.DataFrame({
                 'Word': tokenized_sentences,
                 'Label': tokenized_labels
                 })

    data_frame.to_pickle('merged_patents_picklefile.pkl')
    print(data_frame.head(100))

    print("\nDone.\n")


    return 0
                  

if __name__ == "__main__":
    main()



