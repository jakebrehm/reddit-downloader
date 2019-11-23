import configparser
import praw
import re
import requests

def verify_response(url):
    try:
        response = requests.get(url, stream=True)
    except Exception as e:
        print(e)
        return False
    else:
        if response.status_code == 200:
            return response
        else:
            return False

def download(response, filename):
    with open(f'img\\{filename}', 'wb') as output:
        for chunk in response:
            output.write(chunk)

parser = configparser.ConfigParser()
parser.read(r'config.ini')

USER = parser['testing']['user']

reddit = praw.Reddit(
    client_id=parser['credentials']['client id'],
    client_secret=parser['credentials']['client secret'],
    user_agent=parser['credentials']['user agent'],
)

profile = reddit.redditor(USER)
posts = profile.submissions.new(limit=None)

for post in posts:
    link = str(post.url)
    if link.endswith('.jpg') or link.endswith('.png'):
        response = verify_response(link)
        if response:
            filename = link.split('/')[-1]
            download(response, filename)
    elif 'imgur.com/a/' in link:
        response = verify_response(f'{link}/zip')
        if response:
            disposition = response.headers['Content-Disposition']
            matches = re.search(r'filename="(.*)"', disposition)
            filename = matches.group(1)
            download(response, filename)
