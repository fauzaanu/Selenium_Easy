# SLEZ (Selenium Easy)

### ABOUT
This is written to make things easy. Calling selenium functions directly is still some times needed.

### Simplifying the problems
* Driver Downloading+Adding to path is Built in:
  * Thanks to shadowmoose for Pyderman
* Dealing with Anti Bot Stuff
  * Delays can be set
  * Using Proxies are supported (Partially)
  * headless mode is builtin (default: not headless)
  * Skip Logins by using an already existing browser 
    * use `chrome://version` to get the data path in chromium browsers
    * _Only chromium is supported as of now_
    * User agent is modified to a normal value when headless (Cloudflare evasion)
* Xpaths
  * Functions are built in to 
    * generate xpath 
      * based on attribute
      * based on text, 
    * add to a generated xpath 
      * based on attribute
      * based on text
  * This will cover almost all xpaths in general web automation
  * Less Googling More automating

### STARTER TEMPLATE
Refer to starter.py in the folder

### XPATH GENERATION EXPLAINED

to generate the Xpath for ```<h1 class="heading-text anotherclass">heading</h1>```

```heading_text = example.xpath_by_attribute("h1","class","heading-text")```

but this is not enough as there is one more class present for the class attribute,
so we should do:
```heading_text = example.xpath_by_attribute_adder(heading_text,"class","heading-text")```

context: In any adder function we have to pass another xpath to add to. Also important that adding to your custom
xpaths may not work as intended because the adder functions will try to remove the "]" by default.

xpath generators will return xpaths, not selenium objects. so we need one more step to get that.
```heading_selject = example.wait_for_selject(heading_text)```

context: The Class has a WebdriverWait of 20 secs

### Waiting for SELJECTS (Selenium Objects)
Important to remember that if not found it will return a 0

If multiple = True it will use the xpath and get a list.

Or else by default the search will be for one object

There definitely will be cases that go out of this scope. 
Not planning to include a function for all of them as these two modes will accomodate most cases. (use selenium directly when those cases happen)


### A LOT MORE...
A lot more is inside of SLEZ, like regex, scraping, scrolling down and more... Going through the class is the best thing to do.
