from bs4 import BeautifulSoup
import requests
from splinter import Browser
import pymongo
import pandas as pd


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    browser = init_browser()

    # Set URL's
    news_url= "https://mars.nasa.gov/news/"
    img_url= "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    fact_url= "https://space-facts.com/mars/"
    usgs_url= "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"

    # Retrieve page with the browser module
    browser.visit(news_url)

    html = browser.html

    soup = BeautifulSoup(html, 'html.parser')

    # Create a variable to store the scraped article title and paragraph description
    news_title = soup.find_all('div', class_='content_title')[1].text
    news_p = soup.find_all('div', class_='article_teaser_body')[0].text

    # Retrieve page with the browser module
    browser.visit(img_url)

    # Click the Full Image link
    browser.click_link_by_partial_text("FULL IMAGE")

    # Click the more info link
    browser.click_link_by_partial_text("more info")

    # Get browser info into beautiful soup
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    image_url = soup.find('figure', class_='lede').a['href']
    featured_image_url = f'https://www.jpl.nasa.gov{image_url}'

    # Use pandas to scrape the table containing Mars facts
    facts_tbl = pd.read_html(fact_url)

    # Create a data frame from the first table
    mars_df = facts_tbl[0]

    # Add Column names
    mars_df.columns=['Description','Mars']

    # Set the index to the description
    mars_df.set_index('Description', inplace=True)

    # Use pandas to convert to a HTML table
    mars_facts = mars_df.to_html('table.html')

    # Retrieve page with the browser module
    browser.visit(usgs_url)

    html = browser.html

    soup = BeautifulSoup(html, 'html.parser')

    hemisphere_image_url = []

    urls = soup.find('div', class_='collapsible results')
    hemispheres = urls.find_all('div', class_='item')

    for hemisphere in hemispheres:
        title =  hemisphere.find('h3').text
        title = title.replace(' Enhanced', '')
        
        link = 'https://astrogeology.usgs.gov/' + hemisphere.find('a')['href']
        
        browser.visit(link)
        html = browser.html
        img_soup = BeautifulSoup(html, 'html.parser')
        
        img_url = img_soup.find('div', class_='downloads').a['href']

        hemisphere_image_url.append({'title': title, 'img_url': img_url})

    mars_data = {
        'news_title': news_title,
        'news_p': news_p,
        'featured_image_url': featured_image_url,
        'mars_facts': mars_facts,
        'hemisphere_image_urls': hemisphere_image_url
    }

    return mars_data