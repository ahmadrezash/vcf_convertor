import os
import sys
import pandas as pd


def create_file_list():
    '''
        inputs: none
        outputs: a list of all .vcf files within the current directory
    '''
    file_list = []
    for word in os.listdir():
        if ".vcf" in word:
            file_list.append(word)

    return file_list


def clean_entry(field):
    g = field.replace('\n', '')
    g = g.replace(';;', ';')
    g = g.replace(';', ' ')
    g = g.replace('=0D=0A=', '')
    return g


def read_vcf(file):
    contact_list = []
    '''
        inputs: file path with .vcf files
        outputs: a dictionary form of the .vcf file
    '''
    with open(file, 'r') as f:
        lines = [l.split(':') for l in f]  # if not l.startswith('#')]
        tup_lin = [tuple(li) for li in lines]
        dt = {}

        for d in tup_lin:
            if len(d) == 2:
                dt.update({d[0]: clean_entry(d[1])})
                if d[0] == "END":
                    contact_list.append(dt)
                    dt = {}

        return contact_list


from unidecode import unidecode


def convert_persian_to_english(persian_string):
    english_string = unidecode(str(persian_string)).replace(" ", "").replace("+98", "0").replace("nan", "")
    return english_string


def clean_name(item):
    return item.replace("مشتری لالی پاپ", "")


def create_df(file_list):
    '''
        inputs: list of files to add to Dataframe
        outputs: dataframe of the vcf files
    '''
    # d_list = [read_vcf(item) for item in file_list]
    d_list = read_vcf(file_list[0])
    db = pd.DataFrame(d_list)
    tel_col = list(filter(lambda i: "TEL" in i, db.columns))
    db = db[['FN;CHARSET=UTF-8', *tel_col]]
    db = db[db['FN;CHARSET=UTF-8'].str.contains("لالی")]
    db["tel"] = db[tel_col].apply(edit, axis=1)
    # db.drop(['BEGIN', 'END', 'X-MS-OL-DEFAULT-POSTAL-ADDRESS', 'VERSION'], axis=1, inplace=True)
    db.rename(columns={'FN;CHARSET=UTF-8': "name"}, inplace=True)
    db = db[["name", "tel"]]
    db["tel"] = db["tel"].apply(convert_persian_to_english)
    db['name'] = db['name'].apply(clean_name)
    db.reset_index(inplace=True, drop=True)
    return db


def edit(row):
    for item in row:
        if item:
            try:
                if not any(char.isdigit() for char in str(item)):
                    continue
                return item
            except:
                # print(item)
                return ""


# fn = sys.argv[1]
fn = "finall"

file_list = create_file_list()
df = create_df(file_list)
print()
df.to_csv('{}1.csv'.format(fn))
