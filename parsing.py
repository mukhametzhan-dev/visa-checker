import datetime
import time
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import mysql.connector
from mysql.connector import Error

BASE_URL = 'https://ais.usvisa-info.com'
SIGN_IN_URL = BASE_URL + '/ru-kz/niv/users/sign_in'
SCHEDULE_URL = BASE_URL + '/ru-kz/niv/schedule/59060318/appointment'
APPOINTMENTS_URL = BASE_URL + '/ru-kz/niv/schedule/59056692/appointment'

def start_driver():
    options = Options()
    options.add_argument(f"user-agent=Mozilla/5.0 (Linux; U; Linux i553 ; en-US) Gecko/20130401 Firefox/72.0")
    service = Service('C:\\chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def log_in(driver):
    driver.get(SIGN_IN_URL)
    print("Waiting for the page to load.")
    time.sleep(10)
    print('Logging in.')
    try:
        ok_button = driver.find_element(By.XPATH, '/html/body/div[7]/div[3]/div/button')
        if ok_button:
            ok_button.click()
    except Exception as e:
        print(f"Error clicking OK button: {e}")
    user_box = driver.find_element(By.NAME, 'user[email]')
    user_box.send_keys(username)
    password_box = driver.find_element(By.NAME, 'user[password]')
    password_box.send_keys(password)
    driver.find_element(By.XPATH, '//*[@id="sign_in_form"]/div[3]/label/div').click()
    driver.find_element(By.XPATH, '//*[@id="sign_in_form"]/p[1]/input').click()
    WebDriverWait(driver, 20).until(EC.url_changes(SIGN_IN_URL))
    print('Logged in.')

def get_available_dates(driver):
    available_dates = []
    current_month_index = 0
    while current_month_index < 6:
        date_pickers = driver.find_elements(By.CLASS_NAME, 'ui-datepicker-group')
        if not date_pickers:
            print("Date pickers not found.")
            return []
        for date_picker in date_pickers:
            try:
                month = date_picker.find_element(By.CLASS_NAME, 'ui-datepicker-month').text
                year = date_picker.find_element(By.CLASS_NAME, 'ui-datepicker-year').text
                days = date_picker.find_elements(By.CSS_SELECTOR, 'td[data-handler="selectDay"]')
                for day in days:
                    day_text = day.find_element(By.CLASS_NAME, 'ui-state-default').text
                    available_dates.append(f"{day_text} {month} {year}")
            except Exception as e:
                print(f"Error processing month: {e}")
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'ui-datepicker-next'))
            )
            next_button.click()
            time.sleep(1)
        except Exception as e:
            print(f"Couldn't navigate to the next month: {e}")
            break
        current_month_index += 1
    return available_dates

def check_appointments(driver, logged_in):
    if not logged_in:
        try:
            print("Not logged in, logging in...")
            log_in(driver)
            logged_in = True
        except Exception as e:
            print(f"Login failed: {e}")
            return []
    print("Checking appointments")
    driver.get(APPOINTMENTS_URL)
    if driver.current_url == APPOINTMENTS_URL:
        print("Successfully navigated to appointments page.")
    else:
        print(f"Failed to navigate to {APPOINTMENTS_URL}. Current URL: {driver.current_url}")
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'ui-datepicker-group'))
        )
    except NoSuchElementException:
        print("Date picker not found on the page.")
        return []
    return get_available_dates(driver)

def update_available_dates(driver, logged_in):
    available_dates = check_appointments(driver, logged_in)
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='bot_db'
    )
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Available_dates")
    for date in available_dates:
        cursor.execute("INSERT INTO Available_dates (date) VALUES (%s)", (date,))
    connection.commit()
    cursor.close()
    connection.close()
    print("Available dates updated in the database.")
