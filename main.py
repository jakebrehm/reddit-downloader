# -*- coding: utf-8 -*-

'''
Uses PRAWL to download all media that was submitted by a specified
Reddit user.
'''

import concurrent.futures
import configparser
import re

import praw
import requests


def verify_response(url):
    """Uses the requests module to get a response from the media url,
    then verifies if it is working or not.
    
    Args:
        url (str):
            The url that the media file can be found at.

    Returns:
        The response if the verification was successful, otherwise
        False.
    """

    # Attempt to connect to the url and capture the response
    try:
        response = requests.get(url, stream=True)
    # Print the error and return False upon exception
    except Exception as e:
        print(e)
        return False
    # If no exception occured...
    else:
        # Return the response if it is valid with a status code of 200
        if response.status_code == 200:
            return response
        # Otherwise, return False
        else:
            return False


def download_file(response, filename):
    """Downloads the media file in chunks to an images folder, which
    will be placed in the same directory as this script.
    
    Args:
        response (obj):
            The object that was return by the requests.get() method.
        filename (str):
            The filename to give the downloaded file.
    """

    # Download the file in chunks
    with open(f'img\\{filename}', 'wb') as output:
        for chunk in response:
            output.write(chunk)


def download_post(submission):
    """Takes a Reddit submission as an argument, determines if it is a
    media link, then downloads it if so.
    
    Args:
        submission (obj):
            Reddit submission object.
    """

    link = str(submission.url)
    # If submission is a direct link to a jpg or png file...
    if link.endswith('.jpg') or link.endswith('.png'):
        # Verify the response
        response = verify_response(link)
        # Parse the filename from the link itself, then download
        if response:
            filename = link.split('/')[-1]
            download_file(response, filename)
    # Otherwise, if the submission is a link to an Imgur album...
    elif 'imgur.com/a/' in link:
        # Get a link to the zip file and verify the response
        response = verify_response(f'{link}/zip')
        if response:
            # Parse the filename from the repsonse header, then download
            disposition = response.headers['Content-Disposition']
            matches = re.search(r'filename="(.*)"', disposition)
            filename = matches.group(1)
            download_file(response, filename)


if __name__ == '__main__':

    # Read the configuration file
    parser = configparser.ConfigParser()
    parser.read(r'config.ini')

    # Initialize the Reddit object
    reddit = praw.Reddit(
        client_id=parser['credentials']['client id'],
        client_secret=parser['credentials']['client secret'],
        user_agent=parser['credentials']['user agent'],
    )
    # Gather all of the posts by the specified user
    USER = parser['testing']['user']
    profile = reddit.redditor(USER)
    posts = profile.submissions.new(limit=None)

    # Execute a thread pool to download the files as quickly as possible
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(download_post, list(posts))
