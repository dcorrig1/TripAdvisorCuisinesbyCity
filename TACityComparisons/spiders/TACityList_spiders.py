from scrapy import Spider, Request
from TACityComparisons.items import TAcitycomparisonsItem
import re
import ast

#Check all these indents
class TripSpider(Spider):

    name = 'TripList_Spider'
    allowed_urls = ['https://www.tripadvisor.com']
    #Define the list of URLs we could potentially scrape. I generated a list of all cities covered in the US, but settled on analyzing only the top 60.
    start_urls = ["https://www.tripadvisor.com/Restaurants-g191-United_States.html#LOCATION_LIST"] + ["https://www.tripadvisor.com/Restaurants-g191-oa" + str(20*i) + "-United_States.html#LOCATION_LIST" for i in range(1, 1000)]

    def parse(self, response):
        # Define the list of specific city urls we will need to scrape (the info from these urls will contain all of the data to scrape). The only unique things contained on this first page are the city rank and TripAdvisor code, which we will import to later parse functions.
        IndividualCityUrls = []

        #This if/else statement distinguishes between the very first page (the else statement), and the subsequent pages (the if statement), which have different xpaths for the city links:
        if response.xpath("//div[@id='LOCATION_LIST']/ul/li[1]/a/@href"):

            #List of rows, each containing a link to the corresponding city
            rows = response.xpath("//div[@id='LOCATION_LIST']/ul/li")

            #Text of the range of ranks contained on this specific page. We will use this, plus the index from "rows," to calculate the city rank
            PageRange = response.xpath("//div[@id='LOCATION_LIST']/div[@class='deckTools']/div[@class='pagination']/span/span/text()").extract_first()

            #Highest rank contained on this page, determined by subbing out everything after the first dash on the rank range of the page
            StartRange = re.sub("-.*", "", PageRange)

            #Remove commas from the "StartRange" for ranks higher than 1,000
            StartRangeNoComma = re.sub(",", "", StartRange)

            #For each row, we can find the link to the city page (Link), CityRank, and TripAdvisor's code for that city (CityCode)
            for i in range(0, 20):
                #Script to the links from subsequent page: (link to city)
                Link = rows[i].xpath("./a/@href").extract_first()
                IndividualCityUrls.append(Link)
            
                #Determine the individual city rank based on the StartRange determined earlier
                CityRank = int(StartRangeNoComma) + i
            
                #This will isolate the "city code" for the given city
                CityCode = re.sub("-.*", "", re.sub(".*Restaurants-", "", Link))


        #This is almost the exact same thing as the if statment (which covers all pages except the first). But this else statement covers the very first page of most popular cities (rank 1-20), whose ranks are displayed next to the city name and have a different xpath.
        else:

            #We have 5 columns and 4 rows on this page, and need to use a for loop to scrape each of these
            rows = response.xpath("//div[@id='BROAD_GRID']/div/div[@class='geos_row']")
            for i in range(0, 5):
                columns = rows[i].xpath("./div[@class='geo_wrap']")
                for j in range (0, 4):

                    #Script to the links from the first page: (city rank)
                    CityRank = int(columns[j].xpath("./div[@class='geo_entry']/div[@class='geo_info']/div[@class='geo_rank']/text()").extract_first())
                
                    #Script to the links from the first page: (link to city)
                    Link = columns[j].xpath("./div[@class='geo_entry']/div[@class='geo_info']/div[@class='geo_name']/a/@href").extract_first()
                    IndividualCityUrls.append(Link)

                    #Script to find the actual city code from the first page:
                    CityCode = re.sub("-.*", "", re.sub(".*Restaurants-", "", Link))

        #Now, we have a list of City Ranks, City Links, and City Code for the top 20,000 cities. Pass this info into a subsequent function, parse_city_page:
        # ***For this project, I have settled on only the top 60 cities
        for url in IndividualCityUrls[:60]:
            yield Request(url=url, callback=self.parse_city_page, meta={'CityRank': CityRank, 'CityCode': CityCode})

    def parse_city_page(self, response):
        CityRank = response.meta('CityRank')
        CityCode = response.meta('CityCode')

        #Each restaurant is in a div subtag with a "data-index" attribute. Only restaurant entries have this, so use it to scrape the list of restaurant xpaths.
        rows = response.xpath("//div[@id='EATERY_SEARCH_RESULTS']/div[@data-index]")
              
                #For each city page, determine the number of total following pages (there are only 30 restaurants per page per city, so top cities have multiple following pages). 
                LastPage = response.xpath("//div[@class='pageNumbers']/a[last()]/text()").extract_first()
                #Convert LastPage to an integer (you need this if statement because, if there are no extra pages, LastPage will be a NoneType object with no int function)
                if LastPage is not None:
                    LastPage = int(LastPage)
                    #Since we have follwing pages containing additional restaurants, we need to generate a list of those pages and a function to scrape those (parse_following_pages)
                    SecondPageURLRelative = response.xpath("//div[@class='pageNumbers']/a[1]/@href").extract_first()
                    SecondPageURL = "https://www.tripadvisor.com" + SecondPageURLRelative
                    CityFollowingURLList = [SecondPageURL] + [re.sub("oa30", "oa" + str(30*i), SecondPageURL) for i in range(2, LastPage)]

                #Scrape data common to every restaurant located in this city:
                CityName = response.xpath("//div[@data-placement-name='trip_planner_breadcrumbs']/ul/li[last()-1]/a/span/text()").extract_first()
                RegionName = response.xpath("//div[@data-placement-name='trip_planner_breadcrumbs']/ul/li/a[contains(@onclick, 'Region')]/span/text()").extract_first()
                StateName = response.xpath("//div[@data-placement-name='trip_planner_breadcrumbs']/ul/li/a[contains(@onclick, ' 2')]/span/text()").extract_first()
                CountryName = response.xpath("//div[@data-placement-name='trip_planner_breadcrumbs']/ul/li/a[contains(@onclick, ' 1')]/span/text()").extract_first()                

                #Scrape information for the first page of restaurants (the first 30 restaurants):
                for row in rows:
                    #Restaurant Name and url link (with newlines trimmed off the sides)
                    RestaurantName = row.xpath("./div[2]/div[1]/div[@class='title']/a/text()").extract_first()
                    RestaurantName = RestaurantName[1:][:-1]
                    RestaurantLink = row.xpath("./div[2]/div[1]/div[@class='title']/a/@href").extract_first()

                    #TripAdvisor AvgRating and Price (with additional text trimmed off the right edge):
                    AvgRating = row.xpath("./div[2]/div[1]/div[@class='rating rebrand']/span[1]/@alt").extract_first()
                    AvgRating = AvgRating[:-13]
                    Price = row.xpath("./div[2]/div[1]/div[@class='cuisines']/span[@class='item price']/text()").extract_first()

                    #Code to determine the cuisines list (there is an actual list of cuisines (CuisinesList) and an overall restaurant type (RestaurantCategory), determined by trimming the "RankBlurb"). We then combine these to get the final CuisinesList
                    RankBlurb = row.xpath("./div[2]/div[1]/div[@class='popIndexBlock']/div/text()").extract_first()
                    CuisinesList = row.xpath("./div[2]/div[1]/div[@class='cuisines']/*[@class='item cuisine']/text()").extract()
                    RestaurantCategoryList = ['Restaurants', 'Dessert', 'Coffee & Tea', 'Bakeries', 'Bars & Pubs']
                    for i in RestaurantCategoryList:
                        if RankBlurb.find(i) != -1:
                            RestaurantCategory = [i]
                    #(in some cases, there is no base cuisines list, so we need this if/else statement)
                    if CuisinesList is not None:
                        CuisinesList.extend(RestaurantCategory)
                    else:
                        CuisinesList = RestaurantCategory

                    #Number of Reviews for this restaurant
                    NumReviews = row.xpath("./div[2]/div[1]/div[@class='rating rebrand']/span[2]/a/text()").extract_first()
                    NumReviews = NumReviews[1:][:-9]

                    #In some cases, even using ?geobroaden=false, some restaurants from outside a city get put on a page. In this case, they have an extra blurb located at this xpath, and we can use this to generate a True/False statement and eliminate them.
                    OutofCity = row.xpath("./div[2]/div[1]/div[@class='title']/span/text()").extract_first()
                    IsOutofCity = OutofCity is not None                    

                    #Import overall values taken from the top of the page
                    CityName = CityName
                    StateName = StateName
                    RegionName = RegionName
                    CountryName = CountryName
                    CityCode = CityCode
                    CityRank = CityRank

                    #Yield a Scrapy item for each restaurant located on the first page
                    item = TAcitycomparisonsItem()
                    item['CityCode'] = CityCode
                    item['CityName'] = CityName
                    item['StateName'] = StateName
                    item['RegionName'] = RegionName
                    item['CountryName'] = CountryName
                    #We will generate a pipeline to remove items in which IsOutofCity is True
                    item['IsOutofCity'] = IsOutofCity
                    item['NumReviews'] = NumReviews
                    item['Price'] = Price
                    item['CuisinesList'] = CuisinesList
                    item['AvgRating'] = AvgRating
                    item['RestaurantName'] = RestaurantName
                    item['RestaurantLink'] = RestaurantLink
                    item['RankBlurb'] = RankBlurb
                    item['CityRank'] = CityRank

                    yield item

                #If there are mutiple pages in this city (true of all the top 60 cities since they have many restaurants), we need to then parse the "following" pages
                if LastPage is not None:
                    for url in CityFollowingURLList:
                        yield Request(url=url, callback=self.parse_following_pages, meta={'CityRank': CityRank, 'CityCode': CityCode, 'CountryName': CountryName, 'RegionName': RegionName, 'StateName': StateName, 'CityName': CityName})

            def parse_following_pages(self, response):
                CityName = response.meta['CityName']
                StateName = response.meta['StateName']
                CityCode = response.meta['CityCode']
                RegionName = response.meta['RegionName']
                CountryName = response.meta['CountryName']
                CityRank = response.meta['CityRank']

                #The scraping processes for restaurant entries on following pages is actually identical to that on the front page
                rows = response.xpath("//div[@id='EATERY_SEARCH_RESULTS']/div[@data-index]")

                for row in rows:
                    #Restaurant Name and url link (with newlines trimmed off the sides)
                    RestaurantName = row.xpath("./div[2]/div[1]/div[@class='title']/a/text()").extract_first()
                    RestaurantName = RestaurantName[1:][:-1]
                    RestaurantLink = row.xpath("./div[2]/div[1]/div[@class='title']/a/@href").extract_first()

                    #TripAdvisor AvgRating and Price (with additional text trimmed off the right edge):
                    AvgRating = row.xpath("./div[2]/div[1]/div[@class='rating rebrand']/span[1]/@alt").extract_first()
                    AvgRating = AvgRating[:-13]
                    Price = row.xpath("./div[2]/div[1]/div[@class='cuisines']/span[@class='item price']/text()").extract_first()

                    #Code to determine the cuisines list (there is an actual list of cuisines (CuisinesList) and an overall restaurant type (RestaurantCategory), determined by trimming the "RankBlurb"). We then combine these to get the final CuisinesList
                    RankBlurb = row.xpath("./div[2]/div[1]/div[@class='popIndexBlock']/div/text()").extract_first()
                    CuisinesList = row.xpath("./div[2]/div[1]/div[@class='cuisines']/*[@class='item cuisine']/text()").extract()
                    RestaurantCategoryList = ['Restaurants', 'Dessert', 'Coffee & Tea', 'Bakeries', 'Bars & Pubs']
                    for i in RestaurantCategoryList:
                        if RankBlurb.find(i) != -1:
                            RestaurantCategory = [i]
                    #(in some cases, there is no base cuisines list, so we need this if/else statement)
                    if CuisinesList is not None:
                        CuisinesList.extend(RestaurantCategory)
                    else:
                        CuisinesList = RestaurantCategory

                    #Number of Reviews for this restaurant
                    NumReviews = row.xpath("./div[2]/div[1]/div[@class='rating rebrand']/span[2]/a/text()").extract_first()
                    NumReviews = NumReviews[1:][:-9]

                    #In some cases, even using ?geobroaden=false, some restaurants from outside a city get put on a page. In this case, they have an extra blurb located at this xpath, and we can use this to generate a True/False statement and eliminate them.
                    OutofCity = row.xpath("./div[2]/div[1]/div[@class='title']/span/text()").extract_first()
                    IsOutofCity = OutofCity is not None                    

                    #Import overall values taken from the top of the page
                    CityName = CityName
                    StateName = StateName
                    RegionName = RegionName
                    CountryName = CountryName
                    CityCode = CityCode
                    CityRank = CityRank

                    #Yield a Scrapy item for each restaurant located on the first page
                    item = TAcitycomparisonsItem()
                    item['CityCode'] = CityCode
                    item['CityName'] = CityName
                    item['StateName'] = StateName
                    item['RegionName'] = RegionName
                    item['CountryName'] = CountryName
                    #We will generate a pipeline to remove items in which IsOutofCity is True
                    item['IsOutofCity'] = IsOutofCity
                    item['NumReviews'] = NumReviews
                    item['Price'] = Price
                    item['CuisinesList'] = CuisinesList
                    item['AvgRating'] = AvgRating
                    item['RestaurantName'] = RestaurantName
                    item['RestaurantLink'] = RestaurantLink
                    item['RankBlurb'] = RankBlurb
                    item['CityRank'] = CityRank

                    yield item

