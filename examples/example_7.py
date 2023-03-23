"""
Example 7: Scrape all the articles from glizzykingdreko's medium account

In this example, we will create a SimpleScraper class that monitors glizzykingdreko's 
Medium blog for new articles. By defining the start method with the @with_retry() 
decorator and passing delay=5 and exceptions={"all": RETRY_EVENT} when calling it, 
we ensure that the scraper handles all exceptions with a retry and adds a delay of 
5 seconds between each request.
"""
from bs4 import BeautifulSoup
from requests import Session
from typing import List
from time import sleep
from resilenter_caller import with_retry, RETRY_EVENT

class SimpleScraper:
    def __init__(self):
        self.session, self.articles = Session(), []
        # This is making the function run through a while loop with a delay of 5 seconds
        # and handling any exception with a retry event.
        self.start(delay=5, exceptions={"all": RETRY_EVENT})

    @with_retry()
    def start(self) -> None:
        data = self.load_api_data()
        self.load_response_details(data)

    def load_response_details(self, response: str) -> List[str]:
        data = BeautifulSoup(response, "html.parser")
        new_articles = [
            [d.find("h2").text, d.find("a").get("href")] 
            for d in data.find_all("article") 
            if d.find("h2").text not in self.articles
        ]
        for article in new_articles:
            name, url = article
            print(f"New glizzykingdreko's article on medium \"{name}\"! Check it out at {url}.")
            self.articles.append(name)
        return new_articles

    def load_api_data(self) -> str:
        url = "https://medium.com/@glizzykingdreko"
        return self.session.get(url).text

if __name__ == "__main__":
    SimpleScraper()
