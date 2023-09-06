import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure Selenium options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# Set the path to your Chrome driver executable
chromedriver_path = r"C:\Users\Binod Kumar\Downloads\chromedriver_win32\chromedriver.exe"

# Set the desired district (input from the user)
desired_district = "Thane"

# Set the URL of the website
url = "https://ceoelection.maharashtra.gov.in/searchlist/"

# Set the directory to save the downloaded PDFs
download_dir = r"D:\sunidhi"

# Set up your 2Captcha API key
api_key = "12feee85f0db26ef6aed00110356a02f"

# Function to solve the captcha using 2Captcha
def solve_captcha_2captcha(api_key, site_key):
    # Send a request to 2Captcha API to solve the captcha
    response = requests.post(
        f"http://2captcha.com/in.php?key={api_key}&method=userrecaptcha&googlekey={site_key}&pageurl={url}"
    )
    response_data = response.text.split("|")

    if response_data[0] == "OK":
        captcha_id = response_data[1]
        # Wait for a few seconds for the captcha to be solved
        time.sleep(10)
        while True:
            response = requests.get(
                f"http://2captcha.com/res.php?key={api_key}&action=get&id={captcha_id}"
            )
            response_data = response.text.split("|")
            if response_data[0] == "OK":
                return response_data[1]
            elif response_data[0] != "CAPTCHA_NOT_READY":
                break
            time.sleep(5)
    else:
        raise Exception("Captcha could not be solved.")

# Start the browser
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get(url)

try:
    # Wait for the page to finish loading
    wait = WebDriverWait(driver, 20)  # Increased timeout to 20 seconds
    wait.until(EC.presence_of_element_located((By.ID, "ddlDistrict")))

    # Select the desired district
    district_select = driver.find_element_by_id("ddlDistrict")
    district_select.send_keys(desired_district)

    # Wait for the assembly constituency select options to load
    time.sleep(3)

    # Get all the assembly constituencies
    assembly_options = driver.find_elements_by_xpath("//select[@id='ddlAC']/option")

    for assembly_option in assembly_options:
        # Select the assembly constituency
        assembly_option.click()

        # Wait for the type of revision select options to load
        time.sleep(3)

        # Get all the type of revision options
        revision_options = driver.find_elements_by_xpath("//select[@id='ddlRev']/option")

        for revision_option in revision_options:
            # Select the type of revision
            revision_option.click()

            # Wait for the parts select options to load
            time.sleep(3)

            # Get all the parts
            part_options = driver.find_elements_by_xpath("//select[@id='ddlPart']/option")

            for part_option in part_options:
                # Select the part
                part_option.click()

                # Solve the captcha using 2Captcha
                site_key = driver.find_element_by_id("captchaImg").get_attribute("data-sitekey")
                captcha_value = solve_captcha_2captcha(api_key, site_key)

                # Fill in the captcha input field
                captcha_input = driver.find_element_by_id("txtcaptcha")
                captcha_input.send_keys(captcha_value)

                # Submit the captcha form
                submit_button = driver.find_element_by_id("Button1")
                submit_button.click()

                # Wait for the PDF to load
                time.sleep(5)

                # Get the download link for the PDF
                download_link = driver.find_element_by_id("Button2").get_attribute("href")

                # Download the PDF using requests
                response = requests.get(download_link)
                file_name = download_link.split("/")[-1]

                # Save the PDF to the download directory
                file_path = os.path.join(download_dir, file_name)
                with open(file_path, "wb") as file:
                    file.write(response.content)
                    print(f"Downloaded: {file_name}")

                # Clear the download link
                driver.execute_script("arguments[0].href='';", download_link)

finally:
    # Close the browser
    driver.quit()
