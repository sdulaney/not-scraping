from lxml import html
import unicodecsv as csv
import requests
from exceptions import ValueError
from time import sleep
import re
import argparse

def parse(url):
	response = requests.get(url).text
	parser = html.fromstring(response)
	print "Parsing the page"
	listing = parser.xpath("//li[@class='regular-search-result']")
	total_results = parser.xpath("//span[@class='pagination-results-window']//text()")
	scraped_datas=[]
	for results in listing:
		raw_position = results.xpath(".//span[@class='indexed-biz-name']/text()")
		raw_name = results.xpath(".//span[@class='indexed-biz-name']/a//text()")
		raw_ratings = results.xpath(".//div[contains(@class,'rating-large')]//@title")
		raw_review_count = results.xpath(".//span[contains(@class,'review-count')]//text()")
		raw_price_range = results.xpath(".//span[contains(@class,'price-range')]//text()")
		category_list = results.xpath(".//span[contains(@class,'category-str-list')]//a//text()")
		raw_address = results.xpath(".//address//text()")
		is_reservation_available = results.xpath(".//span[contains(@class,'reservation')]")
		is_accept_pickup = results.xpath(".//span[contains(@class,'order')]")
		url = "https://www.yelp.com"+results.xpath(".//span[@class='indexed-biz-name']/a/@href")[0]

		name = ''.join(raw_name).strip()
		position = ''.join(raw_position).replace('.','')
		cleaned_reviews = ''.join(raw_review_count).strip()
		reviews =  re.sub("\D+","",cleaned_reviews)
		categories = ','.join(category_list)
		cleaned_ratings = ''.join(raw_ratings).strip()
		if raw_ratings:
			ratings = re.findall("\d+[.,]?\d+",cleaned_ratings)[0]
		else:
			ratings = 0
		price_range = len(''.join(raw_price_range)) if raw_price_range else 0
		address  = ' '.join(' '.join(raw_address).split())
		reservation_available = True if is_reservation_available else False
		accept_pickup = True if is_accept_pickup else False
		data={
				'business_name':name,
				'rank':position,
				'review_count':reviews,
				'categories':categories,
				'rating':ratings,
				'address':address,
				'reservation_available':reservation_available,
				'accept_pickup':accept_pickup,
				'price_range':price_range,
				'url':url
		}
		scraped_datas.append(data)
	return scraped_datas

if __name__=="__main__":
	argparser = argparse.ArgumentParser()
	argparser.add_argument('place',help = 'Location/ Address/ zip code')
	search_query_help = """Available search queries are:\n
							Restaurants,\n
							Breakfast & Brunch,\n
							Coffee & Tea,\n
							Delivery,
							Reservations"""
	argparser.add_argument('search_query',help = search_query_help)
	args = argparser.parse_args()
	place = args.place
	search_query = args.search_query
	yelp_url  = "https://www.yelp.com/search?find_desc=%s&find_loc=%s"%(search_query,place)
	print "Retrieving :",yelp_url
	scraped_data = parse(yelp_url)
	print "Writing data to output file"
	with open("scraped_yelp_results_for_%s.csv"%(place),"w") as fp:
		fieldnames= ['business_name','rank','review_count','categories','rating','address','reservation_available','accept_pickup','price_range','url']
		writer = csv.DictWriter(fp,fieldnames=fieldnames)
		writer.writeheader()
		for data in scraped_data:
			writer.writerow(data)
