import requests
import re
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import pandas as pd

election_response = requests.get(url='http://historical.elections.virginia.gov/elections/search/year_from:1924/year_to:2016/office_id:1/stage:General')
soup = BeautifulSoup(election_response.text, 'html.parser')
links = []
years = []
#prepare IDs and extract years
for tag in soup.find_all('tr', class_="election_item"):
    if tag.attrs['id'].startswith('election-id-'):
        links.append(tag.attrs['id'])
    year = tag.find_next('td').text
    years.append(year)
ids = []
#extract IDs
for each in links:
    pattern = re.compile('\d+')
    matches = pattern.findall(each)
    #convert list objects to integers
    for i in matches:
        matches2 = int(tuple(matches)[0])
        ids.append(matches2)
df = pd.DataFrame({'Years' : years, 'IDs': ids})
df.to_csv('election_ids.csv')
election_ids = pd.read_csv('election_ids.csv')
base = 'http://historical.elections.virginia.gov'
dfs = []
for row in election_ids.iterrows():
    link = row[1]['IDs']
    year = row[1]['Years']
    year2 = str(year)
    link2 = str(link)
    part1 = ('/elections/download/')
    part2 = ('/precints_include:0/')
    link3 = (base + part1 + link2 + part2)
    dfs.append(pd.read_csv(link3))
    for df in dfs:
        d = pd.DataFrame(df)
        d.to_csv(year2+'.csv', index=False)
test = pd.read_csv('1924.csv')
election_ids = pd.read_csv('election_ids.csv')
rp = pd.DataFrame()
for year in election_ids['Years']:
    data = pd.read_csv(str(year)+'.csv')
    #the republican candidate is always in the 5th column
    republican = data[data.columns[4]]
    republican = republican[1:]
    republican = republican.str.replace(',','').astype(int)
    data['Republican'] = republican
    total = data['Total Votes Cast']
    total = total[1:]
    total = total.str.replace(',','').astype(int)
    data['Total'] = total
    grouped = data.groupby('County/City')
    sums = grouped[['Republican', 'Total']].sum()
    #sums.columns = ['Republican Votes', 'Total Votes']
    sums['R_Share'] = sums['Republican']/sums['Total']
    sums['Year'] = year
    sums2 = sums.drop(['Republican', 'Total'], axis=1)
    rp = pd.concat([rp, sums2])
rp.to_csv('republican_shares.csv')
republican = pd.read_csv('republican_shares.csv')
important = republican.loc[republican['County/City'].isin(['Accomack County', 'Amelia County', 'Amherst County', 'Alleghany County'])]
grouped = important.groupby('County/City')
for name, group in grouped:
    plt.plot(group['Year'], group['R_Share'], label=name)
    plt.legend()
    plt.title('Republican Share over Time')
    plt.xlabel('Year')
    plt.ylabel('Republican Share')
plt.savefig('r_share.jpg')
