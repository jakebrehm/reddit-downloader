# -*- coding: utf-8 -*-

'''
Uses PRAW to download all media that was submitted by a specified
Reddit user.
'''

import argparse
import concurrent.futures
import configparser
import os
import re

import praw
import requests


def print_progress_bar(current, total, decimals=1, length=100, fill='█'):
    """Can be called in a loop in order to print a progress bar to the
    console.

    Args:
        current (int):
            Current iteration count.
        total (int):
            Total number of iterations.
    
    Kwargs:
        decimals (int):
            A positive number denoting how much decimals to show in the
            percentage complete.
        length (int):
            Number of characters in the progress bar.
        fill (str, █):
            Fill character of the progress bar.
    """

    # Calculate percentage and format according to arguments
    percent = f'{(current / total * 100):0.{decimals}f}'
    # Calculate how much of the bar to fill and make the graphics
    filled_length = int(length * current // total)
    bar = (fill * filled_length) + ('-' * (length - filled_length))
    # Print the progress bar
    print(f'\r|{bar}| {percent}% ({current}/{total})', end='\r')
    # Print New Line on Complete
    if current == total: 
        print()


class RedditDownloader(praw.Reddit):
    """Downloads all detectable media that was submitted by a Reddit
    user.
    
    Parses arguments to gather relevant information, including the
    username of the Reddit profile to download posts from, and
    optionally, the location to save the media to.
    
    Args:
        client_id (str):
            Client ID provided directly by Reddit.
        client_secret (str):
            Client Secret provided directly by Reddit.
        user_agent (str):
            User agent of the Reddit client. Is not provided by Reddit,
            so it can be anything you want it to be.
    
    Kwargs:
        create_directory (bool, True):
            Creates the specified output directory if necessary.
            True by default.
    """


    def __init__(self, client_id, client_secret, user_agent,
                 create_directory=True):

        # Initialize the Reddit client
        praw.Reddit.__init__(
            self,
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )

        # Set up the argument parser
        parser = argparse.ArgumentParser()
        # Allow the user to specify whether to show the progress bar or not
        parser.add_argument(
            '-q',
            '--quick',
            action='store_true',
            help='Whether or not to show a progress bar (impedes speed).',
        )
        # Allow the user to specify whether to make a folder for each user
        parser.add_argument(
            '-s',
            '--separate',
            action='store_true',
            help='Whether or not to make a separate folder for each user.',
        )
        # Allow the user to specify the output location
        current_directory = os.path.dirname(os.path.realpath(__file__))
        default_directory = os.path.join(current_directory, 'media')
        parser.add_argument(
            '-o',
            '--output',
            type=str,
            default=default_directory,
            help='Location of the folder that will hold the downloaded media.',
        )
        # Allow for specification of the reddit user
        parser.add_argument(
            'user',
            type=str,
            nargs='+',
            help='Name of the user(s) you want to download all media from',
        )
        # Parse the arguments for the specified user
        args = parser.parse_args()
        self.QUICK = args.quick
        self.SEPARATE = args.separate
        self.DESTINATION = args.output
        self.USERS = args.user

        # Create a media folder to store the downloads
        if create_directory:
            self._make_output_directory()
        # Create a folder for each user if necessary
        if self.SEPARATE:
            for user in self.USERS:
                self._make_user_folder(user)

        # # Get the specified user's posts
        self.profiles = [self.redditor(user) for user in self.USERS]
        if self.QUICK:
            self.posts = [p.submissions.new(limit=None) for p in self.profiles]
        else:
            posts = [p.submissions.new(limit=None) for p in self.profiles]
            # Convert to lists in order to get the total length
            self.posts = [list(post) for post in posts]
            # Calculate the total length
            self._total = 0
            for post in self.posts:
                self._total += len(post)
            # Initialize the progress bar
            self._completed = 0
            self.print_progress_bar()


    def print_progress_bar(self):
        """Prints a progress bar to the console."""

        print_progress_bar(self._completed, self._total, length=50)


    def _make_output_directory(self):
        """Checks if the specified directory exists, and creates it if
        not."""

        if not os.path.exists(self.DESTINATION):
            os.makedirs(self.DESTINATION)
        print(f'Files will be downloaded to: {self.DESTINATION}')


    def _make_user_folder(self, user):
        """Makes a folder for a specific user inside the output
        directory."""

        location = os.path.join(self.DESTINATION, user)
        os.makedirs(location)


    def _verify_response(self, url):
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
            # print(f'Could not verify response from {url}.')
            return False
        # If no exception occured...
        else:
            # Return the response if it is valid with a status code of 200
            if response.status_code == 200:
                return response
            # Otherwise, return False
            else:
                # print(f'Invalid response from {url}.')
                return False


    def _download_file(self, response, filename):
    # def _download_file(self, response, filename, user):
        """Downloads the media file in chunks to an images folder, which
        will be placed in the same directory as this script.
        
        Args:
            response (obj):
                The object that was return by the requests.get() method.
            filename (str):
                The filename to give the downloaded file.
        """

        # Download the file in chunks
        destination = os.path.join(self.DESTINATION, filename)
        # if self.SEPARATE:
        #     destination = os.path.join(destination, user)
        with open(destination, 'wb') as output:
            for chunk in response:
                output.write(chunk)
        # Print a confirmation message
        if self.QUICK:
            print(f'Successfully downloaded {filename}.')


    def _download_post(self, submission):
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
            response = self._verify_response(link)
            # Parse the filename from the link itself, then download
            if response:
                filename = link.split('/')[-1]
                self._download_file(response, filename)
        # Otherwise, if the submission is a link to an Imgur album...
        elif 'imgur.com/a/' in link:
            # Get a link to the zip file and verify the response
            response = self._verify_response(f'{link}/zip')
            if response:
                # Parse the filename from the repsonse header, then download
                disposition = response.headers['Content-Disposition']
                matches = re.search(r'filename="(.*)"', disposition)
                filename = matches.group(1)
                self._download_file(response, filename)

        # Update the progress bar if necessary
        if not self.QUICK:
            self._completed += 1
            self.print_progress_bar()


    def start_download(self):
        """Execute a thread pool to download the files as quickly as
        possible."""

        # Flatten the posts list and start downloading the media
        posts = [item for sublist in self.posts for item in sublist]
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self._download_post, posts)


if __name__ == '__main__':

    # Read the configuration file
    config = configparser.ConfigParser()
    config.read(r'config.ini')

    # Initialize the Reddit downloader
    downloader = RedditDownloader(
        client_id=config['credentials']['client id'],
        client_secret=config['credentials']['client secret'],
        user_agent=config['credentials']['user agent'],
        create_directory=True,
    )
    # Download all of the posts
    downloader.start_download()
