import os
import glob
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


def scrape_img(index):
	global link, extension
	index = str(index)

	url = 'http://archillect.com/' + index
	print(('Scraping ' + url + ''))

	r = requests.get(url)
	tree = html.fromstring(r.content)

	try:
		link = tree.xpath('//*[@id="ii"]/@src')[0]
		ext_index = link.rfind(".", 0)
		extension = link[ext_index:]
		if not os.path.isfile('img/' + index + extension):
			print(('Saving ' + index))
			save_img(link, index, extension)
		return 1

	except IOError:
		print('Saving...')
		save_img(link, index, extension)
		return 1

	except IndexError:
		return 0


def save_img(link, filename, extension):
	img = requests.get(link)

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
