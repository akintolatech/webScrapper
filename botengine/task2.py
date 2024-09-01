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
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

# Set Tesseract path
tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = tesseract_path


def basic_captcha_solver(img_path):
    """Solve CAPTCHA by processing the image."""
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
    white_img = cv2.merge([255 - thresh, 255 - thresh, 255 - thresh])
    cv2.imwrite('res/output_image.jpg', white_img)
    image = Image.open('res/output_image.jpg')
    captcha_text = pytesseract.image_to_string(image)
    return captcha_text.strip()


def solve_captcha(driver, captcha_image_path):
    """Retrieve and solve CAPTCHA."""
    captcha_image_element = driver.find_element(By.XPATH, "//img[@id='Imageid']")
    captcha_image_url = captcha_image_element.get_attribute("src")
    captcha_image_response = requests.get(captcha_image_url)

    # Save the CAPTCHA image
    with open(captcha_image_path, 'wb') as file:
        file.write(captcha_image_response.content)

    # Process the CAPTCHA image
    extracted_captcha_text = basic_captcha_solver(captcha_image_path)
    return extracted_captcha_text


def monitor_and_book_slot(driver):
    while True:
        try:
            # Find and click the date dropdown
            date_dropdown = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "valAppointmentDate"))
            )
            date_dropdown.click()
            # Find all the days with available slots
            available_slots = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//td[contains(@class, 'day') and contains(@class, 'label-available')]"))
            )
            if available_slots:
                # Click the first available slot
                available_slots[0].click()
                print("Available slot selected. Checking for appointment type dropdown.")

                # Wait and retry mechanism for appointment type dropdown
                appointment_type_selected = False
                retries = 3
                for _ in range(retries):
                    try:
                        # Select appointment type
                        appointment_type_dropdown = Select(WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.ID, "valApplicationType"))
                        ))
                        appointment_type_dropdown.select_by_visible_text("Tourist Visa")
                        appointment_type_selected = True
                        print("Appointment type selected.")
                        break  # Exit the retry loop
                    except TimeoutException:
                        print("Appointment type dropdown not found. Retrying...")
                        time.sleep(2)  # Wait before retrying

                if not appointment_type_selected:
                    print("Failed to select appointment type after retries. Continuing monitoring...")
                    continue  # Skip to the next monitoring iteration

                # Click the 'Book' button
                book_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "submit"))
                )
                book_button.click()

                print("Book button clicked.")

                # Wait for the page to load after clicking the 'Book' button
                time.sleep(5)  # Adjust the wait time if needed

                # Check if the booking was successful by looking for a success message or other indicators
                if "booking confirmed" in driver.page_source.lower():
                    print("Booking confirmed.")
                    break  # Exit the loop if the booking is successful

                else:
                    print("Booking attempt did not succeed. Continuing monitoring...")

        except TimeoutException:
            print("No available slots found or an error occurred. Retrying...")
            time.sleep(60)  # Wait before retrying (adjust the interval as needed)


def fill_booking_form(driver):
    captcha_dir = os.path.join(os.getcwd(), "res")
    captcha_image_path = os.path.join(captcha_dir, "captcha_image.jpg")

    try:
        # Navigate to the booking page
        driver.get("https://blsitalypakistan.com/bls_appmnt/bls-italy-appointment")

        # Wait until the booking page is loaded
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), 'APPOINTMENT SCHEDULE')]"))
        )

        # Select the application center
        center_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "valCenterLocationId"))
        )
        center_dropdown.send_keys("Islamabad (Pakistan)")

        # Select the service type
        service_type_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "valCenterLocationTypeId"))
        )
        service_type_dropdown.send_keys("National - Work")

        # Select the type of applicant
        applicant_type_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "valAppointmentForMembers"))
        )
        applicant_type_dropdown.send_keys("Individual")

        # Solve the CAPTCHA
        extracted_captcha_text = solve_captcha(driver, captcha_image_path)
        captcha_input = driver.find_element(By.NAME, "captcha_code")
        captcha_input.clear()  # Clear previous CAPTCHA input
        captcha_input.send_keys(extracted_captcha_text)

        # # Wait for the appointment date field
        # appointment_date_input = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.ID, "valAppointmentDate"))
        # )
        # appointment_date = appointment_date_input.get_attribute("value")

        # Find and click the date dropdown
        date_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "valAppointmentDate"))
        )
        date_dropdown.click()
        # Find all the days with available slots
        available_slots = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//td[contains(@class, 'day') and contains(@class, 'label-available')]"))
        )

        if available_slots:
            print(f"Appointment Date Available: {available_slots}")
            monitor_and_book_slot(driver)
        else:
            print("No Appointment Slots Available")

    except TimeoutException as e:
        print(f"Timeout Exception during form filling: {str(e)}")


def login(driver):
    captcha_dir = os.path.join(os.getcwd(), "res")
    captcha_image_path = os.path.join(captcha_dir, "captcha_image.jpg")
    while True:  # Loop to handle CAPTCHA retries
        try:
            driver.get("https://blsitalypakistan.com/account/login")
            email_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='text' and @placeholder='Enter Email']"))
            )
            email_input.send_keys("Waqasali885875867@gmail.com")
            password_input = driver.find_element(By.NAME, "login_password")
            password_input.send_keys("Azhar2233")

            extracted_captcha_text = solve_captcha(driver, captcha_image_path)
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
                continue  # Retry CAPTCHA resolution on the webpage
            except TimeoutException:
                # CAPTCHA alert not found, proceed with further checks
                pass

            # Check if login was successful by inspecting the page content
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), 'Profile View')]"))
            )
            print("Login Success")
            return True

        except TimeoutException:
            print("Timeout while trying to login")


# Initialize the WebDriver
def run_bot_automation():
    captcha_dir = os.path.join(os.getcwd(), "res")
    os.makedirs(captcha_dir, exist_ok=True)

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    max_retries = 10  # Number of retries if login fails

    for _ in range(max_retries):
        if login(driver):
            print("Operation successful")
            fill_booking_form(driver)
            break
        else:
            # Wait before retrying
            time.sleep(5)

    driver.quit()


run_bot_automation()
