# 1. Web Scraping:

# Import all the required libraries.

# Install the webdriver for Chrome
from selenium import webdriver
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup
import requests

import pandas as pd
import numpy as np

import time

# Creating driver session for chrome browser
driver = webdriver.Chrome()

# Visit the url
driver.get('https://www.justwatch.com/')

def get_details_of_content(url):
    '''This function takes any content movie or tv show in the form of url.
       It returns the data (title, year, genre, rating, streaming, url) in the form of tuple.'''
    response = requests.get(url)
    html = response.text
    
    soup = BeautifulSoup(html, 'html.parser')
    
    movie = soup.find(class_='title-block')
    title = movie.h1.string
    year = int( movie.span.string.strip()[1:-1] )
    
    # Getting Stream platform lists
    stream_platforms = soup.find(class_='buybox-row stream')
    if stream_platforms is not None:
        # Finding platform name of streams
        streams = []
        for i in stream_platforms.find_all('img'):
            name = i.attrs.get('alt')
            streams.append(name)
        streaming = ",".join(streams)
    else:
        # If streaming platform is not present then leave blank
        streaming = np.nan
    
    movie_info = soup.find('div',{'class':'title-info title-info'})
    
    for i in movie_info.find_all(class_='detail-infos'):
        if i.h3.string == 'Rating':
            # Get the Rating of the content.
            rating = float(i.find_all('span')[-1].string.strip()[:3])    
        
        elif i.h3.string == 'Genres':
            try:
                # Get the Genre of the content.
                genre = i.div.string.strip() 
            except:
                # If genre is not present then we can put Nan
                genre = np.nan
        
    
    try:
        # if rating is not present then it executes except block.
        rating
    except UnboundLocalError:
        # If rating of the content is not present then put NaN.
        rating = np.nan
    
    return (title, year, genre, rating, streaming, url)

# Find "Popular" text and click on it.
time.sleep(3)
popular = driver.find_element(by=By.LINK_TEXT, value="Popular")
popular.click()

# Go to movies section by clicking on "Movies"
time.sleep(3)
movies = driver.find_element(by=By.LINK_TEXT, value="Movies")
movies.click()

# Scrolling down using JavaScript code to extract more movies details.
for i in range(4):
    # Scroll page vertically by 10000 pixels.
    driver.execute_script('window.scrollBy(0,10000)')
    
    # Giving extra time to reload contents.
    time.sleep(3)

# Base url of the site.
base_url = 'https://www.justwatch.com'

# List of column names want to scrape data.
column_names = ['Title', 'Release Year', 'Genre', 'IMDB Rating', 'Streaming Platform', 'Page URL']

# Getting HTML content of current page.
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Getting all anchor tags from "div" tag of class='title-list-grid' under "Movies".
movies = soup.find('div',{'class': 'title-list-grid'}).find_all('a')

movies_urls = []
for movie in movies:
    # Get the ralative url of current movie
    href = movie.attrs.get('href')
    
    # Get the absolute url by combining base_url and relative url.
    movie_url = base_url + href
    
    # Store absolute url of the movie in a list.
    movies_urls.append(movie_url)


# Store Movies data in the list.
movies_data = []
for url in movies_urls:
    
    # get the required data for current url by calling the function.
    try:
        data = get_details_of_content(url)
        
        # Add Movie data in movies_data list
        movies_data.append(data)
    except:
        print('Invalid URL')

# Create a DataFrame from movies data and column_names
movies_df = pd.DataFrame(movies_data, columns=column_names)

## TV Shows Data Extraction

# Scrolling UP using JavaScript code to go on Top of the screen.
for i in range(4):
    # Scroll page UP vertically by 10000 pixels.
    driver.execute_script('window.scrollBy(0,-10000)')
    
    # Giving extra time to reload contents.
    time.sleep(3)

# Go to movies section by clicking on "TV Shows"
time.sleep(3)
tv_shows = driver.find_element(by=By.LINK_TEXT, value="TV Shows")
tv_shows.click()

# Scrolling down using JavaScript code to extract more TV Shows details.
for i in range(5):
    # Scroll page UP vertically by 10000 pixels.
    driver.execute_script('window.scrollBy(0,10000)')
    
    # Giving extra time to reload contents.
    time.sleep(3)

# Getting HTML content of current page.
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Getting all anchor tags from "div" tag of class='title-list-grid' Under "TV Shows".
tv_shows = soup.find('div',{'class': 'title-list-grid'}).find_all('a')
tv_show_urls = []
for show in tv_shows:
    # Get the rative url of current movie
    href = show.attrs.get('href')
    
    # Get the absolute url by combining base_url and relative url.
    show_url = base_url + href
    
    # Store absolute url of the movie in a list.
    tv_show_urls.append(show_url)


# Store TV Shows data in the list.
tv_shows_data = []
for url in tv_show_urls:
    try:
        # get the required data for current url by calling the function.
        tv_shows = get_details_of_content(url)

        # Add TV Shows data in tv_shows_data list
        tv_shows_data.append(tv_shows)
    except:
        print('Invalid URL')

# Create a DataFrame from movies data and column_names
tv_shows_df = pd.DataFrame(tv_shows_data, columns=column_names)

# 2. Data Filtering & Analysis

### Filter movies based on specific criteria:

# First five records of Movies data
print(movies_df.head())

# Check shape of data.
print(movies_df.shape)

# Check for null values
print(movies_df.isnull().sum())

# So we can just drop movies with No Rating.
movies_df.dropna(subset=['IMDB Rating'], inplace=True)

# Get the current year from current date
current_date = pd.to_datetime('today').date()
current_year = current_date.year

# Only include movies and TV shows released in the last 2 years (from the current date)
filtered_df_movies = movies_df[ (current_year - movies_df['Release Year'])<=2 ]

# Only include movies and TV shows with an IMDb rating of 7 or higher.
filtered_df_movies = filtered_df_movies[ filtered_df_movies['IMDB Rating']>=7 ]

print(filtered_df_movies.head())


## Filter TV shows based on specific criteria:

# First five records of TV shows data.
print(tv_shows_df.head())

# Check shape of data.
print(tv_shows_df.shape)

# Check for null values
print(tv_shows_df.isnull().sum())

# So we can just drop movies with No Rating.
tv_shows_df.dropna(subset=['IMDB Rating'], inplace=True)


# Only include movies and TV shows released in the last 2 years (from the current date)
filtered_df_tv_shows = tv_shows_df[ (current_year - tv_shows_df['Release Year'])<=2 ]

# Only include movies and TV shows with an IMDb rating of 7 or higher.
filtered_df_tv_shows = filtered_df_tv_shows[ filtered_df_tv_shows['IMDB Rating']>=7 ]

print(filtered_df_tv_shows.head())


## Data Analysis on Movies Data

# Calculate the average IMDb rating for the scraped movies
average_imdb_rating_movies = filtered_df_movies['IMDB Rating'].mean()
print("Average IMDB Rating For Movies : ", round(average_imdb_rating_movies,2) )

# Split the genres into individual genres
filtered_df_movies['Genre'] = filtered_df_movies['Genre'].str.split(',')

# Create a list of all unique genres
all_genres_movies = [genre.strip() for genre_list in filtered_df_movies['Genre'].dropna() for genre in genre_list]

# Count the occurrences of each genre
genre_counts_movies = pd.Series(all_genres_movies).value_counts()

# Get the top 5 genres
top_5_genres_movies = genre_counts_movies.head(5)
print("Top 5 Genres of movies:\n", top_5_genres_movies)

## Data Analysis On TV Shows Data

# Calculate the average IMDb rating for the scraped TV Shows
average_imdb_rating_tv_shows = filtered_df_tv_shows['IMDB Rating'].mean()
print("Average IMDB Rating For Movies : ", round(average_imdb_rating_tv_shows, 2))

# Split the genres into individual genres
filtered_df_tv_shows['Genre'] = filtered_df_tv_shows['Genre'].str.split(',')

# Create a list of all unique genres
all_genres_tv_shows = [genre.strip() for genre_list in filtered_df_tv_shows['Genre'].dropna() for genre in genre_list]

# Count the occurrences of each genre
genre_counts_tv_shows = pd.Series(all_genres_tv_shows).value_counts()

# Get the top 5 genres
top_5_genres_tv_shows = genre_counts_tv_shows.head(5)
print("Top 5 Genres of Tv Shows:\n",top_5_genres_tv_shows)

## Determine the streaming service with the most significant number of offerings for movies

# Split the Streaming Platforms into individual Streaming Platform
filtered_df_movies['Streaming Platform'] = filtered_df_movies['Streaming Platform'].str.split(',')

# We have some NaN values in Streaming Platform so we are just droping them.
# Create a list of all unique Streaming Platform
all_streaming_latforms_movies = [platform for platforms in filtered_df_movies['Streaming Platform'].dropna() for platform in platforms]
# all_streaming_latforms_movies

# Count the occurrences of each genre
streaming_latforms_counts_movies = pd.Series(all_streaming_latforms_movies).value_counts()

# Top 1 Streaming Platform.
print("\nTop 1 Sreaming Platform for Movies : ", streaming_latforms_counts_movies.head(1))

## Determine the streaming service with the most significant number of offerings for TV Shows

# Split the Streaming Platforms into individual Streaming Platform
filtered_df_tv_shows['Streaming Platform'] = filtered_df_tv_shows['Streaming Platform'].str.split(',')

# We have some NaN values in Streaming Platform so we are just droping them.
# Create a list of all unique Streaming Platform
all_streaming_latforms_tv_shows = [platform for platforms in filtered_df_tv_shows['Streaming Platform'].dropna() for platform in platforms]
# all_streaming_latforms_tv_shows

# Count the occurrences of each genre
streaming_latforms_counts_tv_shows = pd.Series(all_streaming_latforms_tv_shows).value_counts()

# Top 1 Streaming Platform.
print("\nTop 1 Sreaming Platform for TV Shows : ", streaming_latforms_counts_tv_shows.head(1))


# 3. Data Export

# Store Filter Movies Data In CSV File.
filtered_df_movies.to_csv('Movies_Data.csv', index=False)

# Store Filter TV Shows Data In CSV File.
filtered_df_tv_shows.to_csv('TV_Shows_Data.csv', index=False)

# Close the driver session.
driver.quit()