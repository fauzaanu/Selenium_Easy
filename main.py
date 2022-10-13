import os
import time

from SLEZ import Session, ProxSession, SLEZSession, HumanBrowser, Actionable

username = 'fauzaanu'

browser = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
profile = rf'C:\Users\{username}\AppData\Local\BraveSoftware\Brave-Browser\SLEZPROFILE\User Data\Profile 1'

BASE = os.getcwd()
# profile = rf'{BASE}\Custom\User Data\Profile 1'
# browser = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


proxyBasedSession = SLEZSession(browser, browser_profile_path=profile, headless=False, delay=0)
proxyBasedSession.browse(f"https://example.com")
time.sleep(3)
link_xp = "/html"
link = Actionable(link_xp, proxyBasedSession)
link.image_xpath(aggressive=True)
time.sleep(3)
c = link.find_image_cordinates(ref_img="refs/elements/5_.png")
link.click_cordinates(c)
time.sleep(3)
proxyBasedSession.screenshot("final.png")

# fmovies = HumanBrowser(browser, browser_profile_path=profile)
# fmovies.browse("https://fmovies.wtf/movie/amsterdam-roq3o/1-full")
# class ACTIONABLE (xpath) -- done
# the class will store, the xpath, and an image of the actionable -- done
# if xpath detection fails the image detection will be the faill back
# wait for selject goes down and actionable class begins -- done
# multiple elements returning function -- done
# invisisble element returning function -- done
# one invisible element returning function -- done
# one visible element returning fucntion -- done
# what if we could generate xpath recursively linking all of them into images. would be pretty nuts
# but how do we even differentiate the elements.
