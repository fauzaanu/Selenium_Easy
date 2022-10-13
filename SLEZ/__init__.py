import json
import os
import pathlib
import pprint
import re
import shutil
import time
import uuid
import webbrowser
import xml.etree.ElementTree as ET
from subprocess import Popen, STDOUT

import pyderman as driver
from PIL import ImageDraw, Image
from bs4 import BeautifulSoup
from pyscreeze import locate
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException, \
    InvalidSelectorException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_actions import PointerActions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


class Session:
    def __del__(self):
        if self.driver is not None:
            self.driver.quit()
        return -1

    def __init__(self, browser_path, browser_profile_path="", ignored_exceptions=TimeoutException,
                 delay=10, headless=False, incognito=False, debug=False):
        self.wait = None
        self.driver = None
        self.ignored_x = [ignored_exceptions]
        self.driver_path = self.drivers_check()
        self.delay = delay
        self.last_status = 1
        self.cookies = None
        self.debug = debug

        self.brave_path = browser_path

        get_profile_name = browser_profile_path.find(r"User Data")

        self.profile_name = browser_profile_path[get_profile_name + 10:]
        self.profiles_dir = browser_profile_path[:get_profile_name + 10]

        # print("self.profiles_dir", self.profiles_dir)
        # print("self.profile_name", self.profile_name)

        self.capabilities = webdriver.DesiredCapabilities.CHROME
        self.capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
        self.options = webdriver.ChromeOptions()
        self.rundir = os.getcwd()
        print(self.rundir)

        if browser_profile_path != "":
            self.options.add_argument(f"user-data-dir={self.profiles_dir}")
            self.options.add_argument(f'--profile-directory={self.profile_name}')
            self.options.add_argument(f'--log-net-log={self.rundir}{os.sep}network.json')

        if headless:
            self.options.add_argument(f"--headless")
            self.options.add_argument(
                f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36")

        if incognito:
            self.options.add_argument(f"--incognito")

        self.options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.options.binary_location = self.brave_path

        # start the driver
        # if proxy doesn't work, the main code should be able to call close_driver() and then call start driver after
        # setting up a new proxy. Not necessary for class to handle multiple proxy at once
        # self.start_driver()

    # # Functions for closing and opening the driver # #
    def cf_detect(self):
        print("Checking if cloudflare is happening!")
        source = self.driver.page_source

    def log_network(self):
        """
        generates a network_log.txt file to observe what has happened
        HUGE THANKS TO https://www.rkengler.com/how-to-capture-network-traffic-when-scraping-with-selenium-and-python/
        """

        def process_browser_logs_for_network_events(logs):
            for entry in logs:
                log = json.loads(entry["message"])["message"]
                if (
                        "Network.response" in log["method"]
                        or "Network.request" in log["method"]
                        or "Network.webSocket" in log["method"]
                ):
                    yield log

        logs = self.driver.get_log("performance")
        # events = process_browser_logs_for_network_events(logs)
        with open("get_requests.txt", "wt") as out:
            for log in logs:
                if '"method":"GET"' in log["message"]:
                    if 'cloudflare' in log["message"]:
                        continue
                    else:
                        pprint.pprint(log["message"], stream=out)
                        pprint.pprint("-------------", stream=out)

        with open("post_requests.txt", "wt") as out:
            for log in logs:
                if '"method":"POST"' in log["message"]:
                    if 'cloudflare' in log["message"]:
                        continue
                    else:
                        pprint.pprint(log["message"], stream=out)
                        pprint.pprint("-------------", stream=out)

        with open("json_networks.txt", "wt") as out:
            for log in logs:
                if 'application/json' in log["message"]:
                    if 'cloudflare' in log["message"]:
                        continue
                    else:
                        pprint.pprint(log["message"], stream=out)
                        pprint.pprint("-------------", stream=out)

        with open("xhr_network.txt", "wt") as out:
            for log in logs:
                if '"type":"XHR"' in log["message"]:
                    if 'cloudflare' in log["message"]:
                        continue
                    else:
                        pprint.pprint(log["message"], stream=out)
                        pprint.pprint("-------------", stream=out)

        with open("tokens.txt", "wt") as out:
            for log in logs:
                if 'TOKEN' in log["message"]:
                    if 'cloudflare' in log["message"]:
                        continue
                    else:
                        pprint.pprint(log["message"], stream=out)
                        pprint.pprint("-------------", stream=out)

        with open("get_requests.txt", "wt") as out:
            for log in logs:
                pprint.pprint(log["message"], stream=out)
                pprint.pprint("-------------", stream=out)

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

    def close_driver(self):
        """
        Closes the Selenium Driver
        :return:
        """

        x = self.driver.quit()

        if self.debug:
            print(x)

    def start_driver(self):
        """
        Starts a selenium Driver
        :return:
        """
        try:
            AServiceOBJ = Service(executable_path=self.driver_path, port=20)
            self.driver = webdriver.Chrome(service=AServiceOBJ, desired_capabilities=self.capabilities,
                                           options=self.options)

            self.wait = WebDriverWait(self.driver, 20, ignored_exceptions=self.ignored_x)
            self.driver.maximize_window()
            self.driver.set_window_position(0, 0)

            # print(self.driver)
        except WebDriverException:
            raise
            # return -1
        if self.driver is None:
            print("Error: Driver Initialization Failed! Make sure to Close any already running instances!")

    # # Browse, Back, Forward # #
    def browse(self, url):
        """
        Browses to a URL
        :param url:
        :return:
        """
        # sleep for the delay secs
        time.sleep(self.delay)
        if self.driver is not None:
            x = self.driver.get(url)
        else:
            print("Error: Driver Not Running!")

    def browser_resolution(self, width, height):
        self.driver.set_window_size(width, height)

    def go_forward(self):
        """
        Go Forward button browser
        :return:
        """
        self.driver.forward()

    def go_back(self):
        """
        Back button browser
        :return:
        """
        self.driver.back()

    # # Cookies # #
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

    # # Screen Shots # #
    def screenshot(self, name):
        """
        Takes a  screenshot of the screen
        :param name:
        :return:
        """
        self.driver.save_screenshot(f"{name}.png")

    def screenrec(self, frames=30):
        """
        Records the screen via frames. No sound obv.
        :param frames:
        :return:
        """
        for i in range(0, frames):
            self.driver.save_screenshot(f"frame{i}.png")

    def set_location(self, lat: float, long: float, acc: int):
        map_coordinates = dict({
            "latitude": lat,
            "longitude": long,
            "accuracy": acc
        })
        self.driver.execute_cdp_cmd("Emulation.setGeolocationOverride", map_coordinates)

    # # Switching Tabs # #
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

    # # UX INTERACTIONS # #

    def hidden_selject(self, xpath):
        """
        waits for an xpath to be found. if not found returns 0
        :param xpath: The xpath to be searched for
        :return: returns 0 on not found, the selenium object on true
        """

        element = "NOTFOUND"
        try:
            element = self.wait.until(expected_conditions.presence_of_element_located((By.XPATH, xpath)))

        except InvalidSelectorException:
            raise

        except TimeoutException:
            raise

        if element == "NOTFOUND":
            print("Unable to locate element - trying to understand why!")
            ## call cloudflare checker from here

        # print(element)
        return element

    def wait_for_selject(self, xpath, multiple=False, verbose=False):
        """
        waits for an xpath to be found. if not found returns 0
        :param xpath: The xpath to be searched for
        :return: returns 0 on not found, the selenium object on true
        """

        element = "NOTFOUND"
        try:
            if verbose:
                print("looking for", xpath)
            if not multiple:
                element = self.wait.until(expected_conditions.visibility_of_element_located((By.XPATH, xpath)))
                if verbose:
                    print(element)
            elif multiple:
                element = self.wait.until(expected_conditions.presence_of_all_elements_located((By.XPATH, xpath)))
                if verbose:
                    print(element)

        except InvalidSelectorException:
            raise

        except TimeoutException:
            raise

        if element == "NOTFOUND":
            print("Unable to locate element - trying to understand why!")
            ## call cloudflare checker from here

        # print(element)
        return element

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


class ProxSession(Session):
    def __init__(self, proxy_address: str, browser_path, browser_profile_path="", ignored_exceptions=TimeoutException,
                 delay=10, headless=False, incognito=False, debug=False):
        super(ProxSession, self).__init__(browser_path, browser_profile_path=browser_profile_path,
                                          ignored_exceptions=ignored_exceptions,
                                          delay=delay, headless=headless, incognito=incognito, debug=debug)

        self.options.add_argument(f'--proxy-server={proxy_address}')
        self.start_driver()


class SLEZSession(Session):
    def __init__(self, browser_path, browser_profile_path="", ignored_exceptions=TimeoutException,
                 delay=10, headless=False, incognito=False, debug=False):
        super(SLEZSession, self).__init__(browser_path, browser_profile_path=browser_profile_path,
                                          ignored_exceptions=ignored_exceptions,
                                          delay=delay, headless=headless, incognito=incognito, debug=debug)
        # print(browser_profile_path)
        self.start_driver()
        # print(self.driver)
        # print(self.wait)


class HumanBrowser:
    def __init__(self, browser_path, browser_profile_path):
        self.brave_path = str(browser_path).replace(os.sep, "/")

        get_profile_name = browser_profile_path.find(r"User Data")

        self.profile_name = browser_profile_path[get_profile_name + 10:]
        self.profiles_dir = browser_profile_path[:get_profile_name + 10]
        self.profiles_dir = str(self.profiles_dir).replace(r"\\", r"\\\\")

        self.rundir = os.getcwd()

    def browse(self, url):
        x = [rf"""{self.brave_path}""", rf"""{url}""", rf"""--profile-directory={self.profile_name}""",
             rf"""--log-net-log={self.rundir}/human.json"""]
        Popen(x, stdout=os.open(os.devnull, os.O_RDWR), stderr=STDOUT)


class XpathHelpers:
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


class Actionable:
    def __init__(self, xpath: str, instance: Session, invisible=False, single=True):
        self.xpath = xpath
        self.invisible = invisible
        self.single = single
        self.instance = instance
        self.record_num = uuid.uuid4()
        self.find_selenium_object()
        self.h = 1080
        self.w = 1920

    def find_selenium_object(self, xpath=None):
        if xpath is None:
            xpath = self.xpath

        try:
            if self.invisible:
                if self.single:
                    element = self.instance.wait.until(
                        expected_conditions.presence_of_element_located((By.XPATH, xpath)))
                    self.generate_image_reference(element)

                elif not self.single:
                    element = self.instance.wait.until(
                        expected_conditions.presence_of_all_elements_located((By.XPATH, xpath)))
                    self.generate_image_reference(element)

            elif not self.invisible:
                if self.single:
                    element = self.instance.wait.until(
                        expected_conditions.visibility_of_element_located((By.XPATH, xpath)))
                    self.generate_image_reference(element)

                elif not self.single:
                    element = self.instance.wait.until(
                        expected_conditions.visibility_of_all_elements_located((By.XPATH, xpath)))
                    self.generate_image_reference(element)

        except InvalidSelectorException:
            raise

        except TimeoutException:
            raise

        if element == "NOTFOUND":
            print("Unable to locate element - trying to understand why!")

        return element

    def generate_image_reference(self, selject, rec=False):
        if rec is False:
            selject.screenshot(f"refs/{self.record_num}.png")
        else:
            selject_r = selject[0]
            id = selject[1]
            selject_r.screenshot(f"refs/elements/{id}_.png")

    def image_xpath(self, nexpath="//body/child::*[not(self::script)]", aggressive=False):
        # //body/child::*
        # //body//following::*
        # //body/child::*[not(self::script)]
        # todo: Reminder close eyes or turn off monitor ; needs a better way to handle this
        source = self.instance.driver.page_source
        if not aggressive:
            nexpath = nexpath
        else:
            # //body//following::*[not(self::script)]
            nexpath = "//body//following::*[not(self::script)]"

        elements = self.instance.wait.until(expected_conditions.presence_of_all_elements_located((By.XPATH, nexpath)))
        print(len(elements))

        elem_id = int()

        self.instance.driver.maximize_window()
        for elem in elements:
            # while taking the screenshot there is a lot of flickering - this will damage my eyes. So we are moving the screen out of bounds
            self.instance.driver.set_window_position(self.h - (self.h + self.h), self.w - (self.w + self.w))
            self.instance.browser_resolution(width=self.w, height=self.h)

            elem_id += 1
            print(elem)
            elem = [elem, elem_id]
            # print(elem)
            try:
                self.generate_image_reference(elem, rec=True)
            except WebDriverException:
                continue
        # bring back to the right positions
        self.instance.driver.set_window_position(0, 0)
        self.instance.browser_resolution(width=self.w, height=self.h)
        self.instance.driver.maximize_window()

    def find_image_cordinates(self, ref_img):
        # os.rename(ref_img,str(ref_img).replace("_","-"))
        current = self.instance.driver.save_screenshot("current_screen.png")
        cord = locate(ref_img, "current_screen.png")
        print(cord)
        cordinates = (cord.left, cord.top, cord.left + cord.width, cord.top + cord.height)
        shutil.copyfile("current_screen.png", "for_marking.png")
        source_img = Image.open("for_marking.png").convert("RGBA")
        draw = ImageDraw.Draw(source_img)
        draw.rectangle(cordinates, outline="red")
        source_img.save("for_marking.png")

        return cordinates

    def click_cordinates(self, cordinate):

        ## what i want is to move it visually, both aproaches below has failed to do it.

        action = ActionBuilder(self.instance.driver)
        action.pointer_action.move_to_location(cordinate[0], cordinate[1]).pause(2).click()
        action.perform()

        # a valid and working aproach
        # ac = ActionChains(self.instance.driver)
        # ac.move_by_offset(cordinate[0], cordinate[1]).pause(2)
        # ac.click()
        # ac.perform()
