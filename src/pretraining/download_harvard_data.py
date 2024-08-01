from datasets import load_dataset
import os
import json

# Harvard USPTO Dataset Documentation:
# https://huggingface.co/datasets/HUPD/hupd
#
# This program will download text from patents in the Harvard USPTO dataset as .txt files into the current directory.
# The user must specify the range of dates that the patents were published. After that all patents in the Harvard
# USPTO dataset that falls within that range of dates will be downloaded.
#
# We will use this to pre-train the deBERTa model so that it can get better at reading patents.

def main():
    train_start_date = input("What patent date do you want to start at for the train data? YYYY-MM-DD : ")
    train_end_date = input("What patent date do you want to end at for the train data? YYYY-MM-DD : ")
    validation_start_date = input("What patent date do you want to start at for the validation data? YYYY-MM-DD : ")
    validation_end_date = input("What patent date do you want to start at for the validation data? YYYY-MM-DD : ")

    # Load the dataset
    dataset = load_dataset("HUPD/hupd", 
        name='all',
        data_files="https://huggingface.co/datasets/HUPD/hupd/blob/main/hupd_metadata_2022-02-22.feather", 
        icpr_label=None,
        force_extract=True,
        train_filing_start_date=train_start_date,
        train_filing_end_date=train_end_date,
        val_filing_start_date=validation_start_date,
        val_filing_end_date=validation_end_date,
    )

    # The dataset is split into 'train' and 'validation' sets
    train_data = dataset['train']
    validation_data = dataset['validation']

    # Save train data
    save_patent_text(train_data, 'hupd_train')

    # Save validation data
    save_patent_text(validation_data, 'hupd_validation')

    return 0



# Once the dataset is downloaded into cache, this method will write the text data for each patent into
# .txt files and save them into the current directory that you are in.
def save_patent_text(split_data, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for patent in split_data:
        filename = patent['patent_number'] + '.txt'
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(patent['title'] + '\n\n')
            f.write(patent['abstract'] + '\n\n')
            f.write(patent['claims'] + '\n\n')
            f.write(patent['background'] + '\n\n')
            f.write(patent['summary'] + '\n\n')
            f.write(patent['description'])


if __name__ == "__main__":
    main()












