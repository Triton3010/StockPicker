#import necessary modules
import csv
from math import sqrt
import datetime
from dateutil.parser import parse

#Levenshtein Distance Ratio to measure similarity between two texts
def similarity_check(text1, text2, ratio_calc=True):
	rows = len(text1)+1
	cols = len(text2)+1
	distance = [[0 for col in range(cols)] for row in range(rows)]

	for i in range(1, rows):
		for k in range(1,cols):
			distance[i][0] = i
			distance[0][k] = k

	for col in range(1, cols):
		for row in range(1, rows):
			if text1[row-1] == text2[col-1]:
				cost = 0 
			else:
				
				if ratio_calc == True:
					cost = 2
				else:
					cost = 1
			distance[row][col] = min(distance[row-1][col] + 1,      # Cost of deletions
								 distance[row][col-1] + 1,          # Cost of insertions
								 distance[row-1][col-1] + cost)     # Cost of substitutions
	if ratio_calc == True:
		Ratio = ((len(text1)+len(text2)) - distance[row][col]) / (len(text1)+len(text2))
		return Ratio
	else:
		return "The strings are {} edits away".format(distance[row][col])

#get all stock names present in data
def get_stocknames():
	stock_names = set()
	with open('./data.csv','rt') as f:
		data = csv.reader(f)
		for index, row in enumerate(data):
			if(index == 0):
				continue

			stock_names.add(row[0])
	return list(stock_names)

stock_names = get_stocknames()

flag=True

while(flag):

	try:

		stock = str(input("Welcome Agent! Which stock you need to process? : "))

		#check if stock name exists in the data
		if stock not in stock_names:
			for each_stock in stock_names:
				if similarity_check(stock, each_stock) > 0.75:
					response = str(input((f"Oops! Did you mean {each_stock} y or n :-")))
					if response == 'y':
						stock = each_stock
						break

		data_list = []
		with open('./data.csv','rt') as f:
			data = csv.reader(f)
			for index, row in enumerate(data):

				if(index == 0):
					continue

				if(row[0]==stock):
					data_dict = {}
					data_dict['date'] = datetime.datetime.strptime(row[1], '%d-%b-%y')
					data_dict['price'] = float(row[2])
					data_list.append(data_dict)

		start_date = parse(str(input("From which date you want to start : ")))
		end_date = parse(str(input("Till which date you want to analyze : ")))

		formatted_data = []

		#filter data according to starting and ending date
		for item in data_list:
			if start_date <= item['date'] <= end_date:
				formatted_data.append(item)

		#if no such data exists between the two dates, exit
		if len(formatted_data) == 0:
			print('No data exist for these dates')
			continue

		#sort data based on date - O(nlogn)
		formatted_data.sort(key = lambda x:x['date']) 

		prices = [item['price'] for item in formatted_data]

		#format float values to two decimal precision
		def format(value):
			return float("{0:.2f}".format(value))

		#get all metrics about the price and profit - O(n)
		def profits(price_data):
			result = 0
			std = 0
			buy_index = sell_index = 0
			minsofar = next(iter(prices))

			for index, price in enumerate(price_data):
				if minsofar < min(minsofar, price):
					buy_index = index
				minsofar = min(minsofar, price)
				if result < max(result, price - minsofar):
					sell_index = index

				result = max(result, price - minsofar)

			mean = sum(price_data)/len(price_data)
			std = sqrt(sum((x - mean)**2 for x in price_data) / len(price_data))

			return format(result), buy_index, sell_index, format(mean), format(std)

		result, buy, sell, mean, std = profits(prices)

		print(f"Mean - {mean} , STD - {std} , Buy date - {formatted_data[buy]['date']} , Sell date - {formatted_data[sell]['date']} , Profit - {100*result}")

		response = str(input('Do you want to continue? (y or n) : ')).lower()

		flag = False if response == 'n' else True

	except:
		print('Invalid data format input')
		

