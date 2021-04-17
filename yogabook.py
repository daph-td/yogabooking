import schedule
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime
import sys
from selenium.webdriver.common.action_chains import ActionChains
sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')
print('Finish importing standard packages ...')

# Initialize driver
def initDriver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome('chromedriver',options=chrome_options)
    print('Finish initializing a browser ...')
    return driver

# Page source
def loadPageSource(driver):
    driver.get("https://pure360.pure-yoga.com/en/SG?location_id=80")
    sleep(10)
    content = driver.page_source.encode('utf-8').strip()
    soup = BeautifulSoup(content, "html.parser")
    schedule_table = soup.find('table', {'class':'table table-bordered table-striped'})
    print('Finish loading page source ...')
    return schedule_table

# Login
def Login(driver):
    login_but = driver.find_element_by_id('sign-in-btn')
    login_but.click()
    sleep(5)
    username = driver.find_element_by_id('username')
    username.send_keys('zzz7hrs@gmail.com')
    password = driver.find_element_by_id('password')
    password.send_keys('Kaikai12@pr')
    submit = driver.find_element_by_xpath('//*[@id="sign-in-form"]/input[3]')
    submit.click()
    print('Finish logging in ...')

def getTimePosition(schedule_table, chosen_time):
    # Locate the chosen time slot
    all_time_slots = []
    all_time_slots_tag = schedule_table.find('tbody', {'id':'schedule-list'})
    all_time_slots = all_time_slots_tag.find_all('tr')
    all_desire_time_slots = ['']
    for time_slot_tag in all_time_slots:
        time_slot = time_slot_tag.get_text().strip()[:5]
        all_desire_time_slots.append(time_slot)
    try:
        index_time = all_desire_time_slots.index(chosen_time)
        return index_time
    except:
        print(f'- {chosen_time} is an invalid time slot')

def getDatePosition(chosen_date):
    all_desire_dates = ['', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    # Locate the chosen date
    index_date = all_desire_dates.index(chosen_date)
    return index_date

# Check successful booking
def confirmBooking(driver):
    my_booking = driver.find_element_by_xpath('//*[@id="tab-2"]')
    sleep(5)
    ActionChains(driver).move_to_element(my_booking).click(my_booking).perform()
    # my_booking.click()
    sleep(5)
    soup_bookings = BeautifulSoup(driver.page_source.encode('utf-8').strip(), "html.parser")
    schedule_booked = soup_bookings.find('tbody', {'id':'upcoming-classes-list'})
    sessions = schedule_booked.find_all('tr')
    for session in sessions:
        detail = session.get_text().strip()
        end = detail.index('Booked')
        print('** Successfully booked session:')
        print(f'{detail[:end]}')

advanced_schedules = []
desire_no_slot = int(input('How many slots do you want to book this week? (eg. 4) '))
# for turn in list(range(desire_no_slot)):
for turn in list(range(1, desire_no_slot+1)):
    desire_date = input(f'Slot-{turn} | Please select the date: ')
    desire_time = input(f'Slot-{turn} | Please select the time: ')
    advanced_schedules.append([desire_time, desire_date])

def job():
    print(f'Start booking schedule at: {datetime.now()}')
    driver = initDriver()
    schedule_table = loadPageSource(driver)
    try:
        Login(driver)
    except:
        print('- Already login') 
    for schedule in advanced_schedules:
        time_picked = schedule[0]
        date_picked = schedule[1]
        index_time = getTimePosition(schedule_table, time_picked)
        index_date = getDatePosition(date_picked)
        if index_time == None:
            pass
        try:
            book_but = driver.find_element_by_xpath(f'//*[@id="schedule-list"]/tr[{index_time}]/td[{index_date+1}]/div/div[4]/button')
            sleep(3)
            ActionChains(driver).move_to_element(book_but).click(book_but).perform()
            print(f'- Selected: {time_picked} on {date_picked}')
        except:
            print(f'- Cannot select {time_picked} on {date_picked}')
        sleep(5)

    print('\nBooking confirmation ...')
    confirmBooking(driver)

job()
print(f'Successfully selected the schedule. We will book the session on your behalf ...')
schedule.every(5).minutes.do(job)
# schedule.every().day.at("09:00").do(job)
print('Finish scheduling')

while True:
    schedule.run_pending()
    print('Waiting for the next attempt to book ...')
    sleep(60)