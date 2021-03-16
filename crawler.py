from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from time import sleep
import os

class Crawler:
    def __init__(self, url):
        path = os.environ.get('chromedriver_path')
        self.driver = webdriver.Chrome(executable_path=path)
        self.driver.get(url)

    def crawl(self, html):
        return BeautifulSoup(html, 'html.parser')

    def fb_login(self, driver):
        sleep(1)
        fb = driver.find_element_by_xpath('//span[.="Facebook"]')
        fb.click()
        sleep(2)
        base_window = driver.window_handles[0]
        fb_login_window = driver.window_handles[1]
        driver.switch_to.window(fb_login_window)
        sleep(1)
        consent = driver.find_element_by_css_selector('button[title="Alle akzeptieren"]')
        consent.click()
        sleep(1)
        email = driver.find_element_by_xpath('//*[@id="email"]')
        password = driver.find_element_by_xpath('//*[@id="pass"]')

        email.send_keys(os.environ.get('fb_mail'))
        password.send_keys(os.environ.get('fb_pw'))
        password.send_keys(Keys.ENTER)

        driver.switch_to.window(base_window)
