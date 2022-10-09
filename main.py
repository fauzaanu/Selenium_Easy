import time

from SLEZ import Session, ProxSession

username = 'fauzaanu'

browser = r"C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
profile = rf'C:\Users\{username}\AppData\Local\BraveSoftware\Brave-Browser\User Data\Profile 3'


proxyBasedSession = ProxSession("", browser, browser_profile_path=profile, headless=False, delay=0)
proxyBasedSession.browse("https://whatismyipaddress.com/")
input("pause")
proxyBasedSession.close_driver()
