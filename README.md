# TripAdvisor Cuisines by City - David Corrigan
This is a web scraping project (Scrapy) in which I scraped data from 130,000 restaurants in the top 60 US cities to look for differences in the quantity and quality of different cuisines available in each city

## Rationale
As part of the NYC Data Science bootcamp, I devised a web scraping project. I saw a wealth of data presented on www.tripadvisor.com and thought it would be a great place to scrape some meaningful data.

I wanted to gather information on a macro, geographical scale. To this end, I searched Tripadvisor and found the location (https://www.tripadvisor.com/Restaurants-g191-United_States.html#LOCATION_LIST) where they display the top cities (in order), with links to their restaurant pages. Following pages list every city in America, in descinding order.

## Web Scraping
I used these pages, combined with Scrapy, to scrape basic data on 130,000 restaurants located in the top 60 American cities, according to Tripadvisor.com.  The Scrapy scripts are located in the TACityComparisons folder, with actual Spider found inside the spiders subfolder. In the root folder are the scrapy.cfg executable file, the PRX.txt file, which was used to set up Proxy IP addresses, and most importantly, the TACityInfo1to60.jsonl JSON Lines file, which contains raw line-by-line text of the scraped data.

## Data Cleanup and Analysis files
In the DataCleanup subfolder is the Cleanup and Processing iPython notebook, in which I imported the JSONL file, converted that information into a Pandas dataframe, and then cleaned up and eliminated some of the columns. I also eliminated certain cities (suburbs and other abnormal locations such as Oahu, which was on the list along with Honolulu), paring the number of cities down to 50. I ultimately made two distinct but essential files: A "collapsed" dataframe, in which all cuisines for each restaurant are contained in a list form (each restaurant is one line), and an "expanded" dataframe in which the cuisines lists were expanded, allowing for each line to represent only one cuisine (great for visualization and cuisine analysis). The downside of this dataframe, of course, is that one restaurant is now contained over multiple lines. The specific analysis desired leads to the choise of dataframe ("Collapsed" or "Expanded") used for analysis.

## Data Analysis files
In the DataAnalysis subfolder, you will find the CuisineAnalysis iPython notebook, in which data was analyzed and visualized using MatPlotLib. Notably, this analysis allows an investigator to choose a city and see the distribution of cuisines in that city (both in terms of quantity of restaurants and quality of reviews). Conversely, we can also choose a cuisine, and see how that cuisine is represented (again in quality or quantity) throughout the top 50 US cities.

I also transferred this data to R, and did some visualization using ggplot2, specifically co-visualization of cuisine quantity (represented by bar size) and quality (by bar color) together on one graph.

## Presentation files
Finally, in the root directory there are Presentation PPT and PDF files, which gives a presentable overview of the work done for this project.

