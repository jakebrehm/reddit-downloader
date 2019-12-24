# -*- coding: utf-8 -*-

'''
Uses PRAWL to download all media that was submitted by a specified
Reddit user.
'''

import argparse
import concurrent.futures
import configparser
import os
import re

import praw
import requests


def make_directory(output_location):
    """Checks if the specified directory exists, and creates it if not."""

    if not os.path.exists(output_location):
        os.makedirs(output_location)
    print(f'Files will be downloaded to: {output_location}')


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
    # Let the user know there was an error and return False upon exception
    except:
        print(f'Could not verify response from {url}.')
        return False
    # If no exception occured...
    else:
        # Return the response if it is valid with a status code of 200
        if response.status_code == 200:
            return response
        # Otherwise, return False
        else:
            print(f'Invalid response from {url}.')
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
    destination = os.path.join('img', filename)
    with open(destination, 'wb') as output:
        for chunk in response:
            output.write(chunk)
    # Print a confirmation message.
    print(f'Successfully downloaded {filename}.')


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

    # Set up the argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'user',
        type=str,
        help='Name of the user you want to download all media from',
    )
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        default='img',
        help='Location of the folder that will hold the downloaded media.',
    )
    # Parse the arguments for the specified user
    args = parser.parse_args()
    USER = args.user
    DESTINATION = args.output

    # Read the configuration file
    config = configparser.ConfigParser()
    config.read(r'config.ini')

    # Initialize the Reddit object
    reddit = praw.Reddit(
        client_id=config['credentials']['client id'],
        client_secret=config['credentials']['client secret'],
        user_agent=config['credentials']['user agent'],
    )
    # Gather all of the posts by the specified user
    profile = reddit.redditor(USER)
    posts = profile.submissions.new(limit=None)

    # Make an image folder if it doesn't already exist
    make_directory(DESTINATION)

    # Execute a thread pool to download the files as quickly as possible
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(download_post, list(posts))
