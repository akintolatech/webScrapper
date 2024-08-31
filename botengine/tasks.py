import os
import requests
from PIL import Image
import pytesseract
import numpy as np
import cv2
from background_task import background
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from .models import Log, Bot

bot = Bot.objects.get(id=1)


@background(schedule=30)  # Run every 30 seconds
def run_bot_automation():
    captcha_dir = os.path.join(os.getcwd(), "res")
    captcha_image_path = os.path.join(captcha_dir, "captcha_image.jpg")
    max_retries = 10  # Number of retries if login fails

    # Ensure the directory exists
    os.makedirs(captcha_dir, exist_ok=True)

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")

    def basic_captcha_solver(img_path):
        # Read Image from supplied path
        img = cv2.imread(img_path)
        # Covert image to grayscale for Open cv processing
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
        white_img = cv2.merge([255 - thresh, 255 - thresh, 255 - thresh])
        cv2.imwrite('res/output_image.jpg', white_img)
        image = Image.open('res/output_image.jpg')
        captcha_text = pytesseract.image_to_string(image)
        return captcha_text.strip()

    def login(driver):
        while True:  # Loop to handle CAPTCHA retries
            try:
                driver.get("https://blsitalypakistan.com/account/login")
                email_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='text' and @placeholder='Enter Email']"))
                )
                email_input.send_keys("Waqasali885875867@gmail.com")
                password_input = driver.find_element(By.NAME, "login_password")
                password_input.send_keys("Azhar2233")

                captcha_image_element = driver.find_element(By.XPATH, "//img[@id='Imageid']")
                captcha_image_url = captcha_image_element.get_attribute("src")
                captcha_image_response = requests.get(captcha_image_url)

                # Save the captcha image
                with open(captcha_image_path, 'wb') as file:
                    file.write(captcha_image_response.content)

                # Wait for the image to be saved and available
                max_attempts = 10
                attempt = 0
                while not os.path.isfile(captcha_image_path) and attempt < max_attempts:
                    time.sleep(1)  # Wait for 1 second before checking again
                    attempt += 1

                if not os.path.isfile(captcha_image_path):
                    raise FileNotFoundError(f"Captcha image not found after {max_attempts} attempts")

                # Process the captcha image
                extracted_captcha_text = basic_captcha_solver(captcha_image_path)
                captcha_input = driver.find_element(By.NAME, "captcha_code")
                captcha_input.clear()  # Clear previous CAPTCHA input
                captcha_input.send_keys(extracted_captcha_text)

                login_button = driver.find_element(By.XPATH, "//button[@name='submitLogin']")
                login_button.click()

                # Check for CAPTCHA failure alert
                try:
                    alert = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
                    )
                    print("CAPTCHA failed")
                    log_entry = Log(log_details="CAPTCHA failed")
                    log_entry.save()
                    continue  # Retry CAPTCHA resolution on the webpage
                    # return False #restart the web driver and try again
                except TimeoutException:
                    # CAPTCHA alert not found, proceed with further checks
                    pass

                # Check if login was successful by inspecting the page content
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), 'Profile View')]"))
                )

                # Check for profile-specific elements to confirm successful login
                profile_view_element = driver.find_element(By.XPATH, "//h3[contains(text(), 'Profile View')]")
                if profile_view_element:
                    bot.successful_logins += 1
                    log_entry = Log(log_details="Login Successful")
                    log_entry.save()
                    print("Login successful")
                    return True
                else:
                    raise ValueError("Login failed, profile view not found")

            except TimeoutException:
                print("Timeout while trying to login")
                log_entry = Log(log_details="Timeout while trying to login ... Retrying Log in")
                log_entry.save()

            # except (FileNotFoundError, ValueError) as e:
            #     print(e)
            #     log_entry = Log(log_details=str(e))
            #     log_entry.save()

    # Initialize the WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    for _ in range(max_retries):
        if login(driver):
            break  # Exit loop if login is successful
        else:
            # Wait before retrying
            time.sleep(5)

    driver.quit()
