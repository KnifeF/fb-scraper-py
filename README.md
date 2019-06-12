# Scrape some FB data with Python
1) Using Python and various tools to scrape/parse/store/plot facebook data.
The program gets facebook profiles (User IDs) as an input (through Tkinter GUI),
navigates to related facebook web pages and data for scraping, and then - 
generates reports as an output, or even finds some basic insights within the data. 
2) The process is based on tools like Selenium WebDriver, PyAutoGui, BeautifulSoup, 
and re - to automate the scraping process, trying to simulate a human behaviour, 
and parse some HTML. 
3) The output data is stored in various ways (csv, docx, txt).
4) This might be a useful way to organize an unstructured social web data, including: 
profiles' posts, pages, groups, friends, photos&occurences on the web, 
or other data within local files, for various purposes (including OSINT/DeepWeb/WEBINT).

## Some notes:
1) This is an old, basic and messy code (or version) that I have written for 
educational purposes. It requires a registered profile (logged-in to FB before 
the program starts) in order to view the required content for the scraping process.
2) The program is not using an official API (the data is parsed from HTML tags, 
regular expression operations, etc.). According to frequent changes in these websites 
on their client-side development, the data might not be extracted/parsed as expected 
(the structure of the html is changed often, and a long time passed since I have 
actually written the code), so when I find time for it, I will possibly update the 
code and write a "cleaner" one with more features.
3) You are also welcome to offer updates to the code and other ideas (if you understand 
something through all this mess).

## Disclaimer:
The scripts / tools are for educational purposes only, 
and they might violate some websites (including social media/search engines) TOS. 
Use at your own risk.
