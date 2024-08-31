from background_task import background
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
import requests
from PIL import Image
import pytesseract
import numpy as np
import cv2
from .models import Log


@background(schedule=5 * 60)  # Run every 5 minutes
def run_bot_automation():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    input_email = "Waqasali885875867@gmail.com"
    input_password = "Azhar2233"

    def basic_captcha_solver(img_path):
        img = cv2.imread(img_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
        white_img = cv2.merge([255 - thresh, 255 - thresh, 255 - thresh])
        cv2.imwrite('res/output_image.jpg', white_img)
        image = Image.open('res/output_image.jpg')
        captcha_text = pytesseract.image_to_string(image)
        return captcha_text.strip()

    try:
        driver.get("https://blsitalypakistan.com/account/login")
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='text' and @placeholder='Enter Email']"))
        )
        email_input.send_keys(input_email)
        password_input = driver.find_element(By.NAME, "login_password")
        password_input.send_keys(input_password)

        captcha_image_element = driver.find_element(By.XPATH, "//img[@id='Imageid']")
        captcha_image_url = captcha_image_element.get_attribute("src")
        captcha_image_response = requests.get(captcha_image_url)
        captcha_image_path = os.path.join(os.getcwd(), "res/captcha_image.jpg")
        with open(captcha_image_path, 'wb') as file:
            file.write(captcha_image_response.content)

        extracted_captcha_text = basic_captcha_solver(captcha_image_path)
        captcha_input = driver.find_element(By.NAME, "captcha_code")
        captcha_input.send_keys(extracted_captcha_text)

        login_button = driver.find_element(By.XPATH, "//button[@name='submitLogin']")
        login_button.click()

        page_text = driver.find_element(By.TAG_NAME, "body").text
        log_entry = Log(log_details=page_text)
        log_entry.save()

        print("Login successful")

    except TimeoutException:
        print("Timeout while trying to login")
        log_entry = Log(log_details="Timeout while trying to login")
        log_entry.save()
    finally:
        driver.quit()
