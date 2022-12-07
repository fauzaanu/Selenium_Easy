# SLEZ (Selenium Easy)

[ABANDONED]

### ABOUT
This is written to make things easy. Calling selenium functions directly is still some times needed.

### Problems Simplified by SLEZ Class
* Driver Setup (Thanks to pyderman), Human Browser Control, Proxy Use is easy, Network Logs Always Visible,
* Xpath Simplification, Image Based Element Finding, Headless Browser user-agent is same as a regular browser,
* Profile and locations need to be set

### STARTER TEMPLATE
Refer to starter.py in the folder - **not updated with new changes yet!**

### A LOT HAS CHANGED!
There are several Browser types:

SLEZSession, HumanBrowser, ProxSession and the old way of Session

HumanBrowser starts a normal browser without drivers. The application use is to evade cloudflare
or any other sites that detect the chromedriver. If you get blocked even by this approach this means:
The website is even blocking the human user. Next best approach would be to use a ProxSession with some proxies.

A good and tested site for paid solution: https://instantproxies.com/

SLEZSession is a regular selenium browser.

## BASICS

```python
# the browser executable path and the profile path: Get profile path by browsing to chrome://version
browser = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
profile = rf'C:\Users\fauzaanu\AppData\Local\BraveSoftware\Brave-Browser\SLEZPROFILE\User Data\Profile 1'

#instantiating the browser
aliexpress_scraper = SLEZSession(browser, browser_profile_path=profile, headless=False, delay=0)
```

### SOME INSTRUCTIONS
- Never use sudo/root on ubuntu - it messes things up
- \User Data\ must be a present folder in the profile path even for custom locations as it is hard coded
- Dont call Session directly
- refs/elements/ - please create manually
- human.json in root dir is the network activity of human browser
  - websites like fmovies.wtf does not allow selenium driver to browse the site
  - but a human driver can easily capture the network logs enough to get the servers
- netowrk.json is the network activity for all other selenium browsers
- the network activity jsons are not appended - they are overwritten

### TODO
- [ ] handle folder creations automatically
- [ ] tests
- [ ] firefox, edge support
- [ ] edge voice reading application: can it be done?
