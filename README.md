A semi-automatic downloading script for Google Arts and Culture images.

# Requirements

As this script uses `asyncio`, you'll need Python 3.6.

Other dependencies include:

* `requests` for downloading tiles
* `sh` for tailing the log file
* `xmltodict` (optional) for using `gui.py`

# Usage

This script is dubbed 'semi-automatic' because it does require some user input. The basic idea is to browse to an image you want to download and use a request-logging addon in your browser to save the image tile requests, which this script will parse and also download.

A suggested addon is the [Firefx http-request-logger](https://addons.mozilla.org/en-US/firefox/addon/http-request-logger), but others may also exist.

Run the script like: `python downloader.py *path-to-log-file*`

# GUI

`gui.py` allows you to see how many tiles of an image have been dowloaded in an ncurses window in your terminal. It requires `xmltodict` because it needs to be able to parse xml files on the website.