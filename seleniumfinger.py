import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

driver = webdriver.Firefox(executable_path = '/home/pi/Desktop/kantinian/geckodriver')
driver.get("https://facebook.com")

elem = driver.find_element_by_id("email")
elem.clear()
elem.send_keys("pycon")

time.sleep(60)
driver.quit()