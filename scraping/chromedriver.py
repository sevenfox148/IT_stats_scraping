from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, SessionNotCreatedException
from webdriver_manager.chrome import ChromeDriverManager
import time
from os import environ
from logs.set_up_logger import get_logger

username = environ.get("DJINNI_USERNAME")
password = environ.get("DJINNI_PASSWORD")

scraping_logger = get_logger("scraping_logger", "scraping.log")

def get_driver():
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--headless")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        return driver

    except SessionNotCreatedException as e:
        scraping_logger.error(f"Session not created: {e}")
        raise RuntimeError(
            "Failed to create a browser session\nEnsure chromedriver matches your Chrome version\nDetails in logs/scraping.log"
        )

    except WebDriverException as e:
        scraping_logger.error(f"Failed to initialize WebDriver: {e}")
        raise RuntimeError("WebDriver initialization failed\nDetails in logs/scraping.log")

def get_cookies():
    URL = "https://djinni.co/jobs"
    driver = get_driver()
    try:
        driver.get(URL)
    except WebDriverException as e:
        scraping_logger.error(f"Webdriver error while logging into Djinni: {e}")
        raise RuntimeError("WebDriver error\nDetails in logs/scraping.log")

    try:
        login_button = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Увійти")))
        login_button.click()
        time.sleep(1)

        username_input = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, "email")))
        username_input.send_keys(username)

        password_input = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, "password")))
        password_input.send_keys(password)

        submit_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        submit_button.click()
        time.sleep(1)
        cookies = driver.get_cookies()
        driver.quit()
        scraping_logger.info(f"Successful log in into Djinni")
        return cookies

    except TimeoutException as te:
        scraping_logger.error(f"Can't log in into Djinni: {te}")
        return None

def valid_URL(URL):
    driver = get_driver()
    try:
        driver.get(URL)
        driver.quit()
        return True
    except WebDriverException:
        driver.quit()
        return False

def scroll_dou_page(driver, URL):
    while True:
        try:
            button = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Більше вакансій")))
            if "display:none;" in button.get_attribute("style"):
                break
            button.click()
            time.sleep(1)
        except TimeoutException:
            break
        except WebDriverException as e:
            scraping_logger.error(f"Webdriver error while scraping {URL}: {e}")
            raise RuntimeError("WebDriver error\nDetails in logs/scraping.log")

def next_page_djinni(driver, URL):
    try:
        button = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located(
                (By.XPATH, "//a[span[contains(@class, 'bi bi-chevron-right page-item--icon')]]")
            )
        )
        if button.get_attribute("aria-disabled") == "True":
            return False

        button.click()
        time.sleep(1)
        return True
    except TimeoutException:
        return False
    except WebDriverException as e:
        scraping_logger.error(f"Webdriver error while scraping {URL}: {e}")
        raise RuntimeError("WebDriver error\nDetails in logs/scraping.log")