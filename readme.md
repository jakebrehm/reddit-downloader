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

Open command prompt in the directory that you cloned this repository to, and use the command:
```
python reddit_download.py <username>
```
where *<username>* is the name of the Reddit profile that you wish to download all media from.

For now, the images will be placed into a folder named *img* in the same directory as the script. This folder will be created automatically if necessary.

# Ideas for future changes
- Give the user the ability to specify a custom output path instead of having the files downloaded to a static folder

---

# Authors
- **Jake Brehm** - *Initial Work* - [Email](mailto:jbrehm@tactair.com) | [Github](http://github.com/jakebrehm) | [LinkedIn](http://linkedin.com/in/jacobbrehm)