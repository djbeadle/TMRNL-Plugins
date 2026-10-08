import json
import requests
import random
# from bs4 import BeautifulSoup
from html.parser import HTMLParser
import urllib.parse

class Event():
    def __init__(self, name, description, startDate, eventStatus, image, location, url):
        self.name = (name or "").encode("ascii", errors="ignore").decode()
        self.description = (description or "")[:750].encode("ascii", errors="ignore").decode()
        self.start_date = (startDate or "").encode("ascii", errors="ignore").decode()
        self.event_status = (eventStatus or "").encode("ascii", errors="ignore").decode()
        self.image_url = image
        self.location = location
        self.url = url

    def __str__(self):
        return f"{self.name} at {self.start_date}"

    def to_json(self):
        return [self.name, self.description, self.start_date, self.event_status, self.image_url, self.location, self.url]


class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self._in_script_tag = False
        self._script_tags_started = 0
        self._script_tag_contents = ""


    def handle_starttag(self, tag, attrs):
        # print(f'Considering {tag}')
        if tag == "script":
            self._in_script_tag = True
            self._script_tags_started += 1

    def handle_endtag(self, tag):
        # print(f'  ending {tag}')
        if tag == "script":
            self._in_script_tag =False

    def handle_data(self, data):
        # print(f'data of length {len(data)}')
        if self._in_script_tag and self._script_tags_started == 26:
            self._script_tag_contents += data


def run(x):
    # soup = BeautifulSoup(requests.get("https://partiful.com/explore/nyc").text).findAll('script')
    # jsonRaw = json.loads(soup[0].contents[0])
    parser = MyHTMLParser()
    # print('feeding')
    #raise Exception(json.dumps(x))
    contents = requests.get(f"https://partiful.com/explore/nyc").text
    # print(f'contents length {len(contents)}')
    parser.feed(contents)
    print(parser._script_tag_contents)
    # parser.feed(x)
    # print('done feeding')
    jsonRaw = json.loads(parser._script_tag_contents)
    
    events = []

    for itemRaw in jsonRaw['props']['pageProps']['trendingSection']['items']:
        item = itemRaw['event']
        print(item)
        events.append(Event(
            item.get('title'),
            item.get('description'),
            item.get('startDate'),
            item.get('status', ''),
            "https://partiful.imgix.net/" + urllib.parse.unquote(item.get('image', {}).get('url', '').replace("https://firebasestorage.googleapis.com/v0/b/getpartiful.appspot.com/o/", "")),
            f'{item.get("locationInfo", {}).get("mapsInfo", {}).get("name", "")}, {item.get("locationInfo", "").get("neighborhood", "")}',
            f'https://partiful.com/e/{item.get("id")}'
        )
    )

    random.shuffle(events)
    return {
      "events": [event.to_json() for event in events[0:8]]
    }

print(run(1))
# run(1)
