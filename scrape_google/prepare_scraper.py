import os

def create_folder(output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

def read_keywords(keywords_from_file):
    with open(keywords_from_file) as file:
        kw_list = file.readlines()
        kw_list = [line.rstrip() for line in kw_list]
    print(kw_list)
    return kw_list

