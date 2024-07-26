import os
import re
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
import pandas as pd

# When this main function is called, it iteratively looks for all folders that start with 'US' in the current directory, goes into those folders, 
# reads the .txt file within the folder and generates a pickle file that will be named the patent id of the patent + '.pkl', 
# then goes back to the orginal directory you started from. Call this file after you are done collecting your text data from the 
# Google Patents Details API by calling the NLPScript.py file and need to get the pickle files from the text files again for whatever reason.
# The getPickleFiles() function will be automatically called when you call the NLPScript.py file to get the .txt files!
def main():
    current_dir = os.getcwd()

    regex = re.compile(r'US*')

    # List all folders in the current directory
    all_folders = os.listdir(current_dir)

    # Filter for folders that are patent folders, which all start with 'US' 
    patent_folders = [patent_folder for patent_folder in all_folders if regex.match(patent_folder) and os.path.isdir(patent_folder)]

    for patent_directory in patent_folders:
        dir_path = os.path.join(current_dir, patent_directory)
        
        os.chdir(dir_path)

        getPickleFiles(patent_directory)

        os.chdir(current_dir)

    return 0


def getPickleFiles(patent_directory):
    
        print("\nUsing the text file to create a pickle file called " + patent_directory + ".pkl for Natural Language Processing...")
                    
        # Reads from the .txt file that you created. Then, first split the text by sentences using NLTK, then
        # split those sentences into words and punctuation using NLTK. After that, it adds everything to
        # a Pandas DataFrame and saves it as a pickle file.
        with open(patent_directory + '.txt', 'r', encoding='utf-8') as read_file:
            content = read_file.read()
            sentences_list = sent_tokenize(content)
                        
            tokenized_sentences = []
            tokenized_labels = []
            for sentence in sentences_list:
                 tokenized_sentences.append(word_tokenize(sentence))
                 tokenized_labels.append(['O' for label_index in range(len(tokenized_sentences[-1]))])                    

            data_frame = pd.DataFrame({
                 'Word': tokenized_sentences,
                 'Label': tokenized_labels
                 })
            data_frame.to_pickle(patent_directory + '.pkl')
            print(data_frame.head(100))

        print("\nDone.\n")

                    

if __name__ == "__main__":
    main()
