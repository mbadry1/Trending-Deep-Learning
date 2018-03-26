# Imports
import numpy as np
import pandas as pd
from github import Github
from terminaltables import AsciiTable
from terminaltables import GithubFlavoredMarkdownTable
import pickle
import codecs
import urllib.parse as urlparse  # For url parsing
from datetime import datetime, timedelta
from IPython.display import clear_output

# Functions

def get_last_stargazers_page_number(stargazers):
    """
    stargazers: List of stargazers output of pygithub package
    """
    url = stargazers._getLastPageUrl()
    if url is None:
        return 0
    page_num = int(urlparse.parse_qs(urlparse.urlparse(url).query)['page'][0])
    return page_num


def get_stars_count_in_last_days(rep, days, print_user=True):
    """
    rep: Object of github repository which was made by pygithub package
    days: int, number of last days to get the count at.
    """
    last_stargazers_page_num = get_last_stargazers_page_number(rep.get_stargazers())
    if print_user:
        print("Number of stargazzers:",last_stargazers_page_num)
    
    last_day = True
    total_count = 0
    for page_num in range(last_stargazers_page_num-1, -1, -1):
        stargazers = rep.get_stargazers_with_dates().get_page(page_num)[::-1]
        for star in stargazers:
            if datetime.now() - star.starred_at < timedelta(days=days):
                total_count += 1
                if print_user:
                    print(star.starred_at, star.user)
                    # print(star)
            else:
                last_day = False
                break

        if not last_day:
            break
    return total_count


def pandas_table_to_nested_list(df):
    """
    Converts pandas table df to nested list
    """
    table_data = [["" for x in range(df.shape[1])] for y in range(df.shape[0]+1)]
    
    # Columns names
    for i in range(df.shape[1]):
        table_data[0][i] = df.columns[i]
        
    for i in range(df.shape[0]):
        for j in range(df.shape[1]):
            table_data[i+1][j] = df.iat[i, j]
    
    return table_data
	
	
# Github object
username = ""
password = ""
g = Github(username, password)

# Settings
query = 'deep-learning OR CNN OR RNN OR "convolutional neural network" OR "recurrent neural network"'
number_of_reps_to_present = 100
number_of_reps_to_check = 1000
days_to_check = 1
biggest_stars_number = 50000              # Because of github limitations!
names_of_props = ["Name", "Description", "Language", "Stars Today", "Total Stars"]
github_server_link = "https://github.com/"
last_tables_file_name = 'last_table_data.pickle'
md_file_name = 'readme.md'
# Symbols
new_symbol = ":new:"
up_symbol = ":arrow_up:"
down_symbol = ":arrow_down:"
same_symbol = ":heavy_minus_sign:"

# Main query
df = pd.DataFrame(columns=names_of_props)
df_count = 0
seach_query = g.search_repositories(query, sort="stars", order="desc")
results = []
for index, rep in enumerate(seach_query):
    
    # print(rep.full_name)
    
    clear_output()
    print(index)
    
    if rep.stargazers_count > biggest_stars_number:
        continue
    
    link = github_server_link + rep.full_name
    starts_count = get_stars_count_in_last_days(rep, days_to_check, print_user=False)
    
    lst = []
    lst.append("[{}]({})".format(rep.name, link))
    lst.append(rep.description)
    lst.append(rep.language)
    lst.append(starts_count)
    lst.append(rep.stargazers_count)
    
    df.loc[df_count] = lst
    df_count += 1
    
    if(index > number_of_reps_to_check-2):
        break
        
# Sorting
df = df.sort_values(by=["Stars Today"], ascending=False)

# Slicing
df = df.iloc[0:number_of_reps_to_present]

# Inserting pos column
df.insert(0, "Pos1", list(range(1, number_of_reps_to_present+1)))

table_data = pandas_table_to_nested_list(df)

# Generating the ascii table
table = GithubFlavoredMarkdownTable(table_data)
table_str = table.table

# Wrting the md file
with codecs.open(md_file_name, "w", "utf-8") as f:
    f.write(table_str)