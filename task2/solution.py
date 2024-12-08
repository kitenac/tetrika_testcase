import re
import html
import urllib
import asyncio
import unittest
from collections import defaultdict
from typing import Annotated

import aiohttp


'''почему-то url криво новый находит:

каждый раз один и тот же матч из регекса и ондобавлякется и растёт до бесконецчности
- на конце '#mv-pages' - в середине нет что странно!
- т.е. он мусор какой-то добавляет 
- мб нужно не первый матч брать
'''


class AnimalsParser:

    def __init__(self, url=None, RATELIMIT_sec: Annotated[float|int, 'responce timeout in seconds']=None):
        self.url = url or 'https://ru.wikipedia.org/wiki/Категория:Животные_по_алфавиту' # url to 1-st page

        '''
        wikipedia ratelimit for anonymus - 500 requests/hour
        https://api.wikimedia.org/wiki/Rate_limits
        '''
        self.RATELIMIT_sec = RATELIMIT_sec or 1/10

        self.counts = defaultdict(int) # default value = 0,  {letter: count_times} dictionary - how many animals are there that have particular letter at the beginning of it`s name`


    def count_animals(self, html_resp: str) -> None:
        '''
        updating animals-count dictionary attribute with new wiki`s table-page 
        (new table-page can have 1 or more main letters) 
        
        [TODO | RAM optimization] due table`s alredy sorted we can reduce RAM usage by writing total count of animals when we see new main letter
        - but it requires some additional handlings and adds complicity + for given task it works just fine
        '''

        # using lazy/not greedy find (*?) - due we don`t need global scope
        # re.DOTALL - flag to unignore \n in str
        table_block = re.search(r'"mw-category mw-category-columns"(.*?)</div></div></div>', html_resp, re.DOTALL).group(1) # блоки-таблицы из слов начинающихся на одну букву - они расположены тут 
        #print(f'block: {table_block}')
        tables: list[str, str] = re.findall(r'<h3>(.*?)</h3>(.*?)</ul>', table_block, re.DOTALL) # заглавная буква и сами слова на эту букву
        #print(f'tables: {tables}')

        for main_letter, names_table in tables:
            self.counts[main_letter] += names_table.count('<li>')

           
    
    # traverse all pages
    async def main(self):
        page = 1        
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.url) as response:
                        html_resp = await response.text()
                        #print(f'resp: {html_resp}')
                        self.count_animals(html_resp)  # update counts

                        # search link to next page
                        regex = re.search(r'Предыдущая.*<a href="(.*)".*>Следующая страница', html_resp)
                        next_page = html.unescape(regex.group(1)) #  get 1-st group (shorten url - wiki stores linkes as such) and escape html-encoded chracters, ex: '&amp' --> '&' 
                        self.url = f'https://ru.wikipedia.org{next_page}'  # add baseurl (wiki stores links as shortened urls)
                        
                        print(f'- got page #{page}\n next url: {urllib.parse.unquote(self.url)}') # urllib.parse.unquote(self.url)
                        page += 1
                        await asyncio.sleep(self.RATELIMIT_sec) # we don`t want to be banned :)

            except AttributeError as e:
                print(f'ended animal collecting - no more data: {e}: \n - at page #{page-1}, latest url: {self.url}')
                print(f'counts: {self.counts}')
                # write csv table of counts
                with open('beasts.csv', 'w') as fl:
                    for letter, count in self.counts.items():
                        fl.write(f'{letter},{count}\n')

                break




# Test part
markup = '''
Предыдущая страница</a>) (<a href="/w/index.php?title=%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%96%D0%B8%D0%B2%D0%BE%D1%82%D0%BD%D1%8B%D0%B5_%D0%BF%D0%BE_%D0%B0%D0%BB%D1%84%D0%B0%D0%B2%D0%B8%D1%82%D1%83&amp;pagefrom=%D0%91%D0%B0%D1%80%D1%81%D1%83%D0%BA#mw-pages" title="Категория:Животные по алфавиту">Следующая страница</a>)<div lang="ru" dir="ltr" class="mw-content-ltr"><div class="mw-category mw-category-columns"><div class="mw-category-group"><h3>А</h3>
<ul><li><a href="/wiki/%D0%90%D1%84%D1%80%D0%B8%D0%BA%D0%B0%D0%BD%D1%81%D0%BA%D0%B8%D0%B5_%D1%82%D1%80%D0%BE%D0%B3%D0%BE%D0%BD%D1%8B" title="Африканские трогоны">Африканские трогоны</a></li>
<li><a href="/wiki/%D0%90%D1%84%D1%80%D0%B8%D0%BA%D0%B0%D0%BD%D1%81%D0%BA%D0%B8%D0%B5_%D1%83%D0%B7%D0%BA%D0%BE%D1%80%D0%BE%D1%82%D1%8B" title="Африканские узкороты">Африканские узкороты</a></li>
<li><a href="/wiki/%D0%90%D1%84%D1%80%D0%B8%D0%BA%D0%B0%D0%BD%D1%81%D0%BA%D0%B8%D0%B5_%D1%87%D0%B5%D1%85%D0%BE%D0%BD%D0%B8" title="Африканские чехони">Африканские чехони</a></li>
<li><a href="/wiki/%D0%90%D1%84%D1%80%D0%B8%D0%BA%D0%B0%D0%BD%D1%81%D0%BA%D0%B8%D0%B5_%D1%8F%D0%B8%D1%87%D0%BD%D1%8B%D0%B5_%D0%B7%D0%BC%D0%B5%D0%B8" title="Африканские яичные змеи">Африканские яичные змеи</a></li>
<li><a href="/wiki/%D0%90%D1%84%D1%80%D0%B8%D0%BA%D0%B0%D0%BD%D1%81%D0%BA%D0%B8%D0%B9_%D0%B0%D0%B2%D1%81%D1%82%D1%80%D0%B0%D0%BB%D0%BE%D0%BF%D0%B8%D1%82%D0%B5%D0%BA" title="Африканский австралопитек">Африканский австралопитек</a></li>
</ul></div><div class="mw-category-group"><h3>Б</h3>
<ul><li><a href="/wiki/%D0%91%D0%B0%D0%B1%D0%B0%D0%BA%D0%BE%D1%82%D0%B8%D0%B8" title="Бабакотии">Бабакотии</a></li>
<li><a href="/wiki/%D0%91%D0%B0%D0%B1%D0%B0%D0%BA%D1%81_%D0%9A%D0%BE%D0%B7%D0%BB%D0%BE%D0%B2%D0%B0" title="Бабакс Козлова">Бабакс Козлова</a></li>
<li><a href="/wiki/%D0%91%D0%B0%D0%B1%D0%B0%D0%BA%D1%81%D1%8B" title="Бабаксы">Бабаксы</a></li>
<li><a href="/wiki/%D0%91%D0%B0%D0%B1%D0%B1%D0%BB%D0%B5%D1%80-%D0%BA%D0%B0%D0%BF%D1%83%D1%86%D0%B8%D0%BD" title="Бабблер-капуцин">Бабблер-капуцин</a></li>
</ul></div></div></div>
'''

class TestParser(unittest.TestCase):
    def __init__(self, methodName: str = "runTest"):
        super().__init__(methodName)
        self.testparser = AnimalsParser() # add parser for testing purposes
        self.maxDiff = None # need to see more info on failed tests

    def test_find_next_page(self):
        # часть из кода main, отвечающая за поиск ссылки на след. страницу 
        regex = re.search(r'Предыдущая.*<a href="(.*?)".*>Следующая страница', markup)
        next_page = regex.group(1)
        print(f'next_page: {next_page}\n\n')
        self.assertEqual(next_page, '/w/index.php?title=%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%96%D0%B8%D0%B2%D0%BE%D1%82%D0%BD%D1%8B%D0%B5_%D0%BF%D0%BE_%D0%B0%D0%BB%D1%84%D0%B0%D0%B2%D0%B8%D1%82%D1%83&amp;pagefrom=%D0%91%D0%B0%D1%80%D1%81%D1%83%D0%BA#mw-pages')


    def test_count_animals(self):
        self.testparser.count_animals(markup)
        self.assertEqual(self.testparser.counts, {'А': 5, 'Б': 4}) 



if __name__ == '__main__':
    # само задание
    parser = AnimalsParser()
    asyncio.run(parser.main())

    # тесты:
    unittest.main()
