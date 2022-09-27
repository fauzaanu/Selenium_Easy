import os
import time
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, InvalidArgumentException
from selenium.webdriver import Proxy, ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import ProxyType
import pyderman as driver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
import psutil
from bs4 import BeautifulSoup
import re


class Session:
    def __del__(self):
        try:
            self.driver.quit()

            # try statement used because why is an error happening here??????

        except ImportError:
            pass

        except:
            self.driver.quit()
            pass

    def __init__(self, browser_path, browser_profile_path="", use_proxy=False, ignored_exceptions=TimeoutException,
                 delay=10, headless=False, incognito=False, forceshutdown=False, proxy=""):
        self.wait = None
        self.driver = None
        self.ignored_x = ignored_exceptions
        self.driver_path = self.drivers_check()
        self.delay = delay
        self.last_status = 1
        self.cookies = None

        # self.brave_path = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
        # self.brave_profile = 'C:/Users/Fauzaanu/AppData/Local/BraveSoftware/Brave-Browser/User Data/'
        self.brave_path = browser_path
        self.brave_profile = browser_profile_path
        self.capabilities = webdriver.DesiredCapabilities.CHROME
        self.options = webdriver.ChromeOptions()

        if use_proxy:
            if len(proxy) > 5:
                prox = Proxy()
                prox.proxy_type = ProxyType.MANUAL
                prox.http_proxy = proxy
                prox.socks_proxy = ""
                prox.ssl_proxy = proxy

                # adding the proxy as a capabilty of chrome
                prox.add_to_capabilities(self.capabilities)
            else:
                print(
                    "Proxy was set to true however a proxy was not provided. Proxy not added(eg: pass proxy=45.66.238.4:8800")

        if browser_profile_path != "":
            self.options.add_argument(f"user-data-dir={self.brave_profile}")

        if headless:
            self.options.add_argument(f"--headless")
            self.options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36")

        if incognito:
            self.options.add_argument(f"--incognito")

        self.options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.options.binary_location = self.brave_path

        # not recommended to turn on unless necessary
        if forceshutdown:
            PROCNAME = Path(browser_path).stem

            for proc in psutil.process_iter():

                # check whether the process name matches
                if proc.name() == PROCNAME:
                    print("Killing", proc.name())
                    proc.kill()
            time.sleep(1)

        # start the driver
        # if proxy doesn't work, the main code should be able to call close_driver() and then call start driver after
        # setting up a new proxy. Not necessary for class to handle multiple proxy at once
        self.start_driver()

    def close_driver(self):
        """
        Closes the Selenium Driver
        :return:
        """
        self.driver.quit()

    def start_driver(self):
        """
        Starts a selenium Driver
        :return:
        """
        self.driver = webdriver.Chrome(executable_path=self.driver_path, desired_capabilities=self.capabilities,
                                       options=self.options, )
        self.wait = WebDriverWait(self.driver, 20, ignored_exceptions=self.ignored_x)
        self.driver.set_window_size(width=1920, height=1080)  # todo: start maximized

    def browse(self, url):
        """
        Browses to a URL
        :param url:
        :return:
        """
        self.driver.get(url)

    def save_cookies(self, ):
        """
        Saves all the current cookies to self.cookies
        :return:
        """
        self.cookies = self.driver.get_cookies()

    def load_cookies(self, cookies):
        """
        loads the passed cookies to current driver session
        :param cookies:
        :return:
        """
        self.driver.add_cookie(cookies)

    def go_forward(self):
        """
        Go Forward button browser
        :return:
        """
        self.driver.forward()

    def screenshot(self, name):
        """
        Takes a  screenshot of the screen
        :param name:
        :return:
        """
        self.driver.save_screenshot("image.png")

    def screenrec(self, frames=30):
        """
        Records the screen via frames. No sound obv.
        :param frames:
        :return:
        """
        for i in range(0, frames):
            self.driver.save_screenshot(f"frame{i}.png")

    def SwitchToTab(self, title_contains):
        """
        :param title_contains: A piece of text that the title contains that other tabs will not contains. (All handles are looped. First to be found will be returned"
        :return: 1 on success, 0 on fail
        """
        window_handles = self.driver.window_handles
        current_handle = self.driver.current_window_handle
        for window in window_handles:
            handle = self.driver.switch_to.window(window)
            handle_title = self.driver.title
            if title_contains in handle_title:
                return 1

        # switch to the original handle before ending
        self.driver.switch_to.window(current_handle)
        return 0

    def print_all_tabs_with_handles(self, ):
        """
        prints all tabs and handles
        :return:
        """
        window_handles = self.driver.window_handles
        current_handle = self.driver.current_window_handle

        for window in window_handles:
            handle = self.driver.switch_to.window(window)
            print(window, self.driver.title)

        self.driver.switch_to.window(current_handle)

    def go_back(self):
        """
        Back button browser
        :return:
        """
        self.driver.back()

    def drivers_check(self):
        """
        Using pyderman to return the path as a function..
        :return:
        """
        path = driver.install(browser=driver.chrome)
        return path

        # #moving the chromedriver file to the base location
        # dir = os.listdir(f"lib{os.sep}")
        # if len(dir) == 1:
        #     os.remove()
        #     os.rename(f"lib{os.sep}{dir[0]}", "chromedriver.exe")

    def wait_for_selject(self, xpath, multiple=False, verbose=False):
        """
        waits for an xpath to be found. if not found returns 0
        :param xpath: The xpath to be searched for
        :return: returns 0 on not found, the selenium object on true
        """
        try:
            element = 0
            if verbose:
                print("looking for", xpath)
            if not multiple:
                element = self.wait.until(expected_conditions.visibility_of_element_located((By.XPATH, xpath)))
            elif multiple:
                element = self.wait.until(expected_conditions.presence_of_all_elements_located((By.XPATH, xpath)))

            if element == 0:
                print("Element not found:", xpath)
                self.driver.quit()
            else:
                # print(element)
                return element

        except:
            self.last_status = 0
            return 0

    def xpath_by_attribute_adder_text(self, xpath, text_value):
        """
        adds a text (innerhtml) to an existing xpath
        :param xpath:
        :param text_value:
        :return:
        """
        # remove the closing brance
        xpath = xpath.replace("]", " and ")
        repeating_portion = f"contains(text(),'{text_value}')"

        # add the
        xpath = xpath + repeating_portion + "]"

        return xpath

    def xpath_by_attribute_adder(self, xpath, attribbute, attribute_value):
        """
        adds any attribute to an xpath
        :param xpath:
        :param attribbute:
        :param attribute_value:
        :return:
        """
        # remove the closing brance
        xpath = xpath.replace("]", " and ")
        repeating_portion = f"contains(@{attribbute} ,'{attribute_value}')"

        # add the
        xpath = xpath + repeating_portion + "]"

        return xpath

    def xpath_by_attribute(self, element, attribbute, attribute_value):
        """
        A function to automatically generate xpath for a specefic element by 1 class
        :param attribbute: eg: class for <div class="class1">
        :param element: eg: div for <div class="class1">
        :param attribute_value: eg: 'class1' for <div class="class1">
        :return: returns an xpath for finding the element (0 on error)
        """

        xpath = f"//{element}["

        xpath = xpath + f"contains(@{attribbute} ,'{attribute_value}')]"

        return xpath

    def xpath_by_text(self, element, text_value):
        """
        A function to automatically generate xpath for a specefic element by 1 class
        :param attribbute: eg: class for <div class="class1">
        :param element: eg: div for <div class="class1">
        :param attribute_value: eg: 'class1' for <div class="class1">
        :return: returns an xpath for finding the element (0 on error)
        """

        xpath = f"//{element}["

        xpath = xpath + f"contains(text(),'{text_value}')]"

        return xpath

    def click_element(self, selenium_object, sleep=10):
        """
        actions chain click element
        :param selenium_object:
        :param sleep:
        :return:
        """
        try:
            ac = ActionChains(self.driver)
            ac.move_to_element(selenium_object)
            ac.click()
            ac.perform()
            time.sleep(self.delay)

            return 1
        except:
            self.last_status = 0
            return 0

    def input_to_element(self, selenium_object, keys, ):
        """
        sends an input to an element via ac
        :param selenium_object:
        :param keys:
        :return:
        """
        try:
            ac = ActionChains(self.driver)
            ac.move_to_element(selenium_object).click()
            ac.send_keys(keys)
            ac.perform()
            time.sleep(self.delay)

            return 1

        except:
            self.last_status = 0
            return 0

    def scrape_content(self, selject):
        """
        gets the inner html contents: Will get to the final content even if multiple layers of html tags are present.
        but try to keep it more precise
        :param selject:
        :return:
        """
        html_string = selject.get_attribute('innerHTML')
        soup = BeautifulSoup(html_string, "html.parser").prettify()

        html_string = html_string.replace("&amp;", "")
        html_string = html_string.replace("  ", "")
        html_string = html_string.replace('\n', '')

        while html_string.find("<") != -1:
            pos_open = html_string.find("<")
            pos_end = html_string.find(">")

            content_to_remove = html_string[pos_open:pos_end + 1]
            html_string = html_string.replace(content_to_remove, "")
        html_string = html_string.strip()
        html_string = html_string.strip(";")
        return html_string

    def scrape_attribute(self, selject, tag, attribute):
        """
        scrape an attributes value: useful for img tags src and a tags href
        :param selject:
        :param tag:
        :param attribute:
        :return:
        """
        initial = selject.get_attribute('outerHTML')

        # using Bs4
        soup = BeautifulSoup(initial, 'html.parser')
        # print(soup.prettify())
        html_string = soup.find(tag)

        try:
            html_string = html_string[attribute]
        except KeyError:
            return None

        return html_string

    def regex_search(self, pattern, extract_from_string):
        """
        using regex extract anything from the given string
        :param pattern:
        :param extract_from_string:
        :return:
        """
        dm = re.search(fr"{pattern}", extract_from_string)
        if dm is not None:
            dm = dm.group()
            return dm

    def scroll_down(self, amount):
        bunch_of_downs = ActionChains(self.driver)
        for i in range(0, amount):
            bunch_of_downs.send_keys(Keys.PAGE_DOWN)
        bunch_of_downs.pause(1).perform()
