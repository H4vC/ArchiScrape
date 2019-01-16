import os, glob
import requests
import time
import os.path
from lxml import html
import configparser
import concurrent.futures
import sys

config = configparser.ConfigParser()
config.read('./config.cfg')

archillectIndex = int(config['DEFAULT']['lastIndex'])
# minWidth = ''
# minHeight = ''
maxIndex = 0

jobs = [0]

def getIndex():	
	url = 'http://archillect.com/'

	r = requests.get(url)

	tree = html.fromstring(r.content)
	
	global maxIndex

	maxIndex = int(tree.xpath("//div[@id='container']/a[1]/div[@class='item']/div[@class='overlay']")[0].text)

	return 0

getIndex()

jobs = [i+archillectIndex for i in range(maxIndex - archillectIndex+1)]


print("Scraping Until " + str(maxIndex))

if not os.path.exists('img'):
	os.makedirs('img')

# initialize browser for parsing

def scrape_img(index):
	global link, extension
	index = str(index)

	url = 'http://archillect.com/' + index
	print(('Scraping ' + url + ''))

	r = requests.get(url)
	tree = html.fromstring(r.content)

	try:
		link = tree.xpath('//*[@id="ii"]/@src')[0]  # [0]: retrieves the first element matching the criteria
		ext_index = link.rfind(".", 0)  # search backwards looking for the first "."
		extension = link[ext_index:]  # retrieves the file extension
		if not os.path.isfile('img/' + index + extension):
			print(('Saving ' + index))
			save_img(link, index, extension)
		# open('img/' + index + extension, 'r')  # raises FileNotFoundError exception if the file is doesn't exist
		return 1

	except IOError:
		print('Saving...')
		save_img(link, index, extension)
		return 1

	except IndexError:
		# print('[ERR] Looks like '+index+' is missing.')
		return 0


def save_img(link, filename, extension):
	img = requests.get(link)  # load the image to memory

	file_img = open('img/' + filename + extension, 'wb')
	file_img.write(img.content)
	file_img.close()


def erase_file(filename):
	try:
		path = glob.glob('img/' + str(filename) + '.*')[0]
		os.remove(path)
	except:
		pass


while True:

	if (archillectIndex < maxIndex):
		with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
			executor.map(scrape_img, jobs)
			executor.shutdown(wait=True)
			archillectIndex = jobs[-1]

	else:
		config['DEFAULT']['lastIndex'] = str(archillectIndex)
		config['DEFAULT']['maxIndex'] = str(maxIndex)
		config.write(open('./config.cfg', 'w'))
		print('Last scraped ' + str(archillectIndex))
		print('Quiting in 3s...')
		time.sleep(3)
		break
