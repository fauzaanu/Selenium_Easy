from SLEZ import Session

username = 'fauzaanu'

browser = r"C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
profile = rf'C:\Users\{username}\AppData\Local\BraveSoftware\Brave-Browser\User Data\Profile 3'

selenium_session = Session(browser, profile, headless=False, delay=0)
selenium_session.browse("https://www.tiktok.com/tag/maldives")

selenium_session.close_driver()
