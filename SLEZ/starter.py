from SLEZ import Session

######################
#       WINDOWS 11   #
######################
username = 'someuser'

browser = r"C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
profile = rf'C:\Users\{username}\AppData\Local\BraveSoftware\Brave-Browser\User Data\Profile 3'

selenium_session = Session(browser, profile, headless=False, delay=0)
selenium_session.browse("https://www.tiktok.com/tag/maldives")


selenium_session.close_driver()


# UBUNTU - TESTING CURRENTLY

# Download brave-browser in the suggested way: which is this:
# =========================================
# sudo apt install apt-transport-https curl
#
# sudo curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg
#
# echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg arch=amd64] https://brave-browser-apt-release.s3.brave.com/ stable main"|sudo tee /etc/apt/sources.list.d/brave-browser-release.list
#
# sudo apt update
#
# sudo apt install brave-browser
# =========================================

# running which brave-browser gave usr/bin/brave-browser
# which did not work when passed here (NOT A LINUX GUY, SO IDK WHY)
# so I opened Brave-browser and went to chrome://version which should give the executable path
# turns out it was different:
# Executable Path:
# /opt/brave.com/brave/brave
# thats the path passed into browser variable
# The profile should be copied from here as well: in my case
#  Profile Path:
#  /home/fauzaanu/.config/BraveSoftware/Brave-Browser/Default
# which i have set to profile variable
# ===================

######################
#       UBUNUTU      #
######################
username = 'Fauzaanu'

browser = rf"/opt/brave.com/brave/brave"
profile = rf'/home/fauzaanu/.config/BraveSoftware/Brave-Browser/Default'

selenium_session = Session(browser, profile, headless=False, delay=0)
selenium_session.browse("https://www.tiktok.com/tag/maldives")

selenium_session.close_driver()


