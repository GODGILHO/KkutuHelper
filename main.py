from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
import word_db
import re
from random import randint
from threading import Thread
from json import load
from time import sleep

down_url = 'https://chromedriver.chromium.org/downloads'

longdb = word_db.DB('resources\\kklong.txt')
db = word_db.DB('resources\\kkutu.txt')

with open('resources\\config.json', 'r') as f:
    config = load(f)

driver = webdriver.Chrome('resources\\chromedriver.exe')
driver.get('https://kkutu.co.kr/')
driver.maximize_window()
print('driver ready')

print('log in')
while driver.current_url != 'https://kkutu.co.kr/o/game?server=0':
    continue

addr_inputbox = '//*[@id="GameBox"]/div/div[3]'  # block -> my turn, none -> other's turn
inputbox = driver.find_element_by_xpath(addr_inputbox)
print('inputbox hooked - {}'.format(addr_inputbox))

addr_place = '//*[@id="AABox"]/h5'
place = driver.find_element_by_xpath(addr_place)  # place to print text
print('place hooked - {}'.format(addr_place))

addr_first_char = '//*[@id="GameBox"]/div/div[1]/div[6]/div/div[1]'
first_char = driver.find_element_by_xpath(addr_first_char)
print('FirstChar hooked - {}'.format(addr_first_char))

addr_chat = '//*[@id="ChatBox"]/div[1]/input[1]'
chat = driver.find_element_by_xpath(addr_chat)
print('ChatBox hooked - {}'.format(addr_chat))

word = ''
word_exceptions = []
perma_word_exceptions = []

print('Declaring worker')
running = False


class Worker(Thread):
    def run(self):
        global running, word_exceptions, perma_word_exceptions
        if inputbox.get_attribute('style') != 'display: block;':
            running = False
            print('worker end')
            return

        if word == '':
            running = False
            print('worker end because of blank word')
            return

        for i in list(word):
            sleep(randint(config['auto_config']['key_delay'][0], config['auto_config']['key_delay'][1]) / 1000)
            chat.send_keys(i)

        sleep(randint(config['auto_config']['return_delay'][0], config['auto_config']['return_delay'][0]) / 1000)
        chat.send_keys(Keys.RETURN)
        sleep(0.1)

        if not config['auto_exception']:
            running = False
            print('worker end because of auto exception')
            return

        if inputbox.get_attribute('style') == 'display: block;':
            print('added permanent exception {}'.format(word))
            word_exceptions.append(word)
            perma_word_exceptions.append(word)
        else:
            print('passing exception')

        running = False
        print('worker done.')


print('start game')
while inputbox.get_attribute('style') != 'display: block;':
    continue

addr_word_history = '//*[@id="GameBox"]/div/div[1]/div[9]/div'
word_history = driver.find_element_by_xpath(addr_word_history)
print('word history hooked - {}'.format(addr_word_history))
addr_latest_word = '//*[@id="GameBox"]/div/div[1]/div[9]/div/div[1]'
print('latest word hooked - {}'.format(addr_latest_word))

twoum_rule = re.compile('.\(.\)')
str_in_html = re.compile('>[가-힣]*<')

while True:
    try:
        latest_word = driver.find_element_by_xpath(addr_latest_word)
    except NoSuchElementException:
        latest_word = None
    except StaleElementReferenceException:
        latest_word = None
    if word_history.text == '':  # restarted
        if word_exceptions or word_exceptions == perma_word_exceptions:
            print('exception initialized')
        word_exceptions = []
        for i in perma_word_exceptions:
            word_exceptions.append(i)
    else:
        if latest_word is not None:
            try:
                txt = str_in_html.findall(latest_word.get_attribute('outerHTML'))[0][1:-1]
            except StaleElementReferenceException:
                txt = ''
            if txt not in word_exceptions and txt != '':
                print('exception added: {}'.format(txt))
                word_exceptions.append(txt)
    if inputbox.get_attribute('style') == 'display: block;':
        search_txt = first_char.text
        if twoum_rule.match(first_char.text):
            search_txt = [list(first_char.text)[0], list(first_char.text)[2]]
        word = longdb.get_longest_of(search_txt, word_exceptions)
        if word == '':
            word = db.get_longest_of(search_txt, word_exceptions)
        if config['enabled_auto']:
            if not running and word is not False:
                running = True
                print('new instance of worker')
                worker = Worker(name='worker')
                print('starting new worker')
                worker.start()
        driver.execute_script('$("#AABox").html("<h5 class=\'product-title\'>{}</h5>")'.format(word))
