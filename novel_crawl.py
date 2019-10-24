import asyncio
import aiohttp
import time
import random
import requests
from contextlib import contextmanager
from aiohttp import web
from aiohttp import ClientSession
from bs4 import BeautifulSoup
import os


class Fetch(Exception):

    def __init__(self, number):
        self.number = number


class Novel:

    def __init__(self, concur_req, path, category='lightnovel'):
        self.semaphore = asyncio.Semaphore(concur_req)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
        }
        self.base_url = 'https://www.x23qb.com/{}/'.format(category)
        self.file_dir = path
        self.category = category
        self.url_list = []

    async def get_one_page(self, url):
        async with ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    return await response.text(encoding='gb18030', errors='ignore')
                elif response.status == 404:
                    raise web.HTTPNotFound() from None
                else:
                    raise aiohttp.errors.HttpProcessingError(
                        code=response.status,
                        message=response.reason,
                        headers=response.headers
                    ) from None

    async def get_novels(self, url):
        novel_number = url.split('/')[-2]
        try:
            async with self.semaphore:
                response = await self.get_one_page(url)
                await asyncio.sleep(3)
        except Exception as e:
            raise Fetch(novel_number) from e
        else:
            soup = BeautifulSoup(response, 'lxml')
            title = soup.find(name='div', attrs={'class': 'd_title'}).h1.string
            author = soup.find(name='span', attrs={'class': 'p_author'}).a.string
            chapters = soup.find(attrs={'id': 'chapterList'}).find_all('a')
            chapters_list = ['https://www.x23qb.com' + chapter.attrs['href'] for chapter in chapters]
            loop = asyncio.get_event_loop()
            loop.run_in_executor(None, self.get_charpters, chapters_list, title, author)

    def get_charpters(self, url_list, title, author):
        file = open('{}/{}--{}.txt'.format(self.file_dir, title, author), 'w', encoding='utf-8')
        for url in url_list:
            try:
                response = requests.get(url, headers=self.headers)
                if response.status_code == 200:
                    text = response.content.decode('gb18030')
                    text = text.replace('&nbsp;', ' ')
                    text = text.replace('<br/>', ' ')
                    soup = BeautifulSoup(text, 'lxml')
                    chapter_title = soup.find('h1').string
                    content = soup.find(attrs={'id': 'TextContent'}).contents[6]
                    print('获取章节{}'.format(url))
                    file.write(chapter_title + '\n')
                    file.write(content.string + '\n\n')
                else:
                    print('本章节获取失败')
            except requests.ConnectionError as e:
                print('error {}'.format(e.args))
            time.sleep(3)
        file.close()

    async def get_number_list(self, page_number):
        url = '{}{}/'.format(self.base_url, page_number)
        try:
            async with self.semaphore:
                response = await self.get_one_page(url)
                await asyncio.sleep(random.random())
        except Exception as e:
            raise Fetch(page_number) from e
        soup = BeautifulSoup(response, 'lxml')
        parses = soup.find(name='div', attrs={'id': 'sitebox'}).find_all('dt')
        url_list = [parse.a.attrs['href'] for parse in parses]
        self.url_list.extend(url_list)

    @staticmethod
    def write_url_to_file(url_list):
        with open('urls.txt', 'w') as f:
            f.write(str(url_list))

    @staticmethod
    def read_url_from_file():
        with open('urls.txt', 'r') as f:
            return eval(f.read())
	
	@contextmanager
    def get_many(self):
        res = requests.get(self.base_url, headers=self.headers).content.decode('gb18030', 'ignore')
        num = BeautifulSoup(res, 'lxml').find(attrs={'class': 'pagelink'}).span.string
        num = num.split('/')[-1]
        num = int(num)
        self.loop = asyncio.get_event_loop()
        urls = [self.get_number_list(i) for i in range(1, num+1)]
        wait_urls = asyncio.wait(urls)
        counts = self.loop.run_until_complete(wait_urls)
        self.write_url_to_file(self.url_list)

    def download_many(self):
        url_list = self.read_url_from_file()
        no = [self.get_novels(url) for url in url_list]
        wait_no = asyncio.wait(no)
        counts = self.loop.run_until_complete(wait_no)
        if counts == 0:
            loop_2.close()


if __name__ == '__main__':
    if not os.path.exists('novels'):
        os.mkdir('novels')
    novel = Novel(concur_req=5, path='novels', category='lightnovel')
    with novel.get_many():
		novel.download_many()





