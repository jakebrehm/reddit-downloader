<p align="center">
  <img src="https://github.com/jakebrehm/reddit-downloader/blob/master/img/logo.png" width="624" height="100" alt="reddit downloader logo"/>
</p>

---

# Reddit Downloader

**Reddit Downloader** is a command-line script that downloads all media content posted by a specified Reddit user.

# How to get it

To get a copy of this script, use the following command:
```
git clone https://github.com/jakebrehm/reddit-downloader.git
```

## Dependencies

On top of the standard library, **Reddit Downloader** requires the [requests](https://github.com/psf/requests) package and the Python Reddit API wrapper, [PRAW](https://github.com/praw-dev/praw).

# How to use it

In order to being using **Reddit Downloader**, you must add your own Reddit credentials to the script.

If you do not already have these credentials, log in to your Reddit account and navigate to the [authorized applications page](https://www.reddit.com/prefs/apps). Once there, press the `create another app...` button at the bottom of the page. Type in a name, description, and urls for your project, select the `script` radio button, and press `create app`. If successful, you now have all of the information required to begin using **Reddit Downloader**.

Your `client ID` can be found directly under the title of your application, `client secret` is labeled `secret`, and `user agent` can be anything you want it to be.

With this information, navigate to the bottom of *reddit_download.py* and change the arguments of the RedditDownloader instantiation accordingly.

Finally, you can open a terminal/command prompt in the directory that you cloned this repository to, and use the command:
```
python reddit_download.py [-o "path\to\desired\output directory"] <username>
```
where the optional *-o* argument is the directory to save the downladed files to and *\<username>* is the name of the Reddit profile that you wish to download all media from.

By default, if you do not enter the text shown in brackets, the images will be placed into a folder named *media* in the same directory as the script. This folder will be created automatically if necessary.

# Ideas for future changes
- Fix issue where some links are not seen as media because the url does not include a file extension

---

# Authors
- **Jake Brehm** - *Initial Work* - [Email](mailto:jbrehm@tactair.com) | [Github](http://github.com/jakebrehm) | [LinkedIn](http://linkedin.com/in/jacobbrehm)