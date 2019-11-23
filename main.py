import configparser
import praw
import re
import requests

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
        try:
            response = requests.get(link, stream=True)
        except Exception as e:
            print(e)
            continue
        else:
            if response.status_code == 200:
                filename = link.split('/')[-1]
    elif 'imgur.com/a/' in link:
        link += '/zip'
        try:
            response = requests.get(link, stream=True)
        except Exception as e:
            print(e)
            continue
        else:
            if response.status_code == 200:
                disposition = response.headers['Content-Disposition']
                matches = re.search(r'filename="(.*)"', disposition)
                filename = matches.group(1)
    else:
        continue

    with open(f'img\\{filename}', 'wb') as output:
        for chunk in response:
            output.write(chunk)