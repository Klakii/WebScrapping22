from urllib import request
import bs4 as bs
import ssl
import re
import pandas as pd
import numpy as np
import sqlite3

# If True, scraper stops after visiting 100 pages
limit = True

# Set up the counter
j = 0

# Database in which scraped data is stored
conn = sqlite3.connect('database.db')

# First, the link for each team is found
url = 'https://www.plusliga.pl/statsTeams/tournament_1/all.html'
context = ssl._create_unverified_context()
html = request.urlopen(url, context=context)
bst = bs.BeautifulSoup(html.read(), 'html.parser')
tags = bst.find_all('div', {'class':re.compile('thumbnail player team-logo')})

links_teams = []
links_teams = ['https://www.plusliga.pl' + tag.find('a')['href'] for tag in tags]


# Then, for each team we find the link to results after each season
links_teams_seasons = {}
for i, link_ in enumerate(links_teams):
    html2 = request.urlopen(link_, context=context)
    bst2 = bs.BeautifulSoup(html2.read(), 'html.parser')
    tags2 = bst2.find_all('a', {'href':re.compile('/statsTeams/tournament.*')})
    links_teams_seasons[i] = ['https://www.plusliga.pl' + tag['href'] for tag in tags2]


# Finally, we extract data out of each link
for i, links in links_teams_seasons.items():
    for link in links:

        if limit and j >= 100:
            break

        html3 = request.urlopen(link, context=context)
        bst3 = bs.BeautifulSoup(html3.read(), 'html.parser')
        table = pd.read_html(str(bst3.find('table', {'class':re.compile('rs-standings-table stats-table table table-bordered table-hover table-condensed table-striped responsive double-responsive')})))[0]

        # Save data to sql database
        team_name = bst3.find('h1', {'class':re.compile('hidden-xs')}).text
        season_nr = bst3.select('#teams-stats-selector > div > button > span:nth-child(1)')[1].text
        table['Season'] = season_nr
        table.to_sql(team_name, conn, if_exists='append', index=False)

        # Increase the counter
        j += 1

