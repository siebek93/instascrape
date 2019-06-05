from random import choice
import json
import requests
from bs4 import BeautifulSoup
from PIL import Image
import io
from io import BytesIO
import requests
from pprint import pprint

_user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
]

class InstaGramScraper:

    def __init__(self, user_agents=None, proxy=None):
        self.user_agents = user_agents
        self.proxy = proxy
 
    def __random_agent(self):
        if self.user_agents and isinstance(self.user_agents, list):
            return choice(self.user_agents)
        return choice(_user_agents)
    def __request_url(self, url):
        try:
            response = requests.get(url, headers={'User-Agent': self.__random_agent()}, proxies={'http': self.proxy,
                                                                                                 'https': self.proxy})
            response.raise_for_status()
        except requests.HTTPError:
            raise requests.HTTPError('Geeft een http error!!')
        except requests.RequestException:
            raise requests.RequestException
        else:
            return response.text

    @staticmethod
    def extract_json_data(html):
        soup = BeautifulSoup(html, 'html.parser')
        body = soup.find('body')
        script_tag = body.findAll('script')
        for i in script_tag:
            raw_string = i.text.strip().replace('window._sharedData =', '').replace(';', '')
            return json.loads(raw_string)

    def profile_page_metrics(self, profile_url):
        results = {}
        try:
            response = self.__request_url(profile_url)
            json_data = self.extract_json_data(response)
            metrics = json_data['entry_data']['ProfilePage'][0]['graphql']['user']
        except Exception as e:
            raise e
        else:
            for key, value in metrics.items():
                if key != 'edge_owner_to_timeline_media':
                    if value and isinstance(value, dict):
                        value = value['count']
                        results[key] = value
                    elif value and isinstance(value, dict):
                        value = value
                        results[key] = value
        return results  

    def comments_on_picture(self, profile_url):
        results = []
        try:
            response = self.__request_url(profile_url)
            json_data = self.extract_json_data(response)
            metrics = json_data['entry_data']['PostPage'][0]['graphql']['shortcode_media']['edge_media_to_parent_comment']['edges']
        except Exception as e:
            raise e
        else:
            for node in metrics:
                try:
                    node = node.get('node')
                except AttributeError:
                    pass
                if node and isinstance(node, dict or str):
                    results.append(node)
                    print(node["text"])
                    print(node["owner"]["username"])
                    print('\n')
        return results


    def profile_page_recent_posts(self, profile_url):
        results = []
        try:
            response = self.__request_url(profile_url)
            json_data = self.extract_json_data(response)
            metrics = json_data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']["edges"]
        except Exception as e:
            raise e
        else:
            for node in metrics:
                node = node.get('node')
                if node and isinstance(node, dict):
                    results.append(node)
                    node['edge_media_to_comment']['Aantal comments: '] = node['edge_media_to_comment'].pop('count')
                    node['edge_liked_by']["Aantal likes: "] = node['edge_liked_by'].pop('count')
                    print('\n')
                    print(node['thumbnail_src'])
                    print(node['edge_media_to_comment'], node['edge_liked_by'])
        return results



    def links_to_pictures(self, profile_url):
        results = []
        try:
            response = self.__request_url(profile_url)
            json_data = self.extract_json_data(response)
            metrics = json_data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']["edges"]
        except Exception as e:
            raise e
        else:
            for node in metrics:
                node = node.get('node')
                if node and isinstance(node, dict):
                    results.append(node)
                    plaatjes = node['thumbnail_src']
                    r = plaatjes.split()
                    for plaat in r:
                        q = []
                        q.append(plaat)
                        for s in q:
                            response = requests.get(s)
                            img = Image.open(BytesIO(response.content))
                            img.show()
        return results



k = InstaGramScraper()
url = input('Give an url: ')
choices = input('Kies het profiel of de posts? (PR/po/plaatjes/comments/none)?')
if choices == 'PR':
   resultsprofiel = k.profile_page_metrics(url)
   pprint(resultsprofiel)
elif choices == 'po':
  k.profile_page_recent_posts(url)
elif choices == 'none':
    pprint('niets gekozen')
    exit(0)
elif choices == 'plaatjes':
    k.links_to_pictures(url)
elif choices == 'comments':
    if "https://www.instagram.com/p/" in url:
        k.comments_on_picture(url)
    else:
        print("geef een url van een plaatje!")
