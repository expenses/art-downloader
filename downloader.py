import os
import re
import sys
import asyncio
import concurrent.futures
from gapdecoder.decryption import decrypt

import requests
from sh import tail

OUTPUT = "images"
LOG_FILE = sys.argv[1]

session = requests.session()
loop = asyncio.get_event_loop()
executor = concurrent.futures.ThreadPoolExecutor(max_workers=40)

def process(line):
    '''Process a line of input from the log file. If you're using a different format,
    you might have to change this function.'''

    return line.split(" ")[-1].rstrip()

def ensure_dir(dir):
    '''Make a directory if it does not exist'''

    if not os.path.isdir(dir):
        os.makedirs(dir)
        print("Created '%s'." % dir)

def download(line):
    '''Attempt to parse, download and decrypt a line of input from the log file'''

    try:
        url = process(line)

        # If getting out the data from the url fails, fail silently
        try:
            key, x, y, z = re.findall('ggpht.com/([^=]+)=x(\d+)-y(\d+)-z(\d+)', url)[0]
        except:
            return

        output_dir = os.path.join(OUTPUT, key)
        filename = f"{z}-{x}-{y}.jpg"
        output = os.path.join(output_dir, filename)

        # If the output file doesn't exist, download it
        if not os.path.exists(output):
            ensure_dir(output_dir)

            print("Requesting '%s'..." % filename)
            content = session.get(url).content
            decrypted = decrypt(content)
            open(output, "wb").write(decrypted)
    except Exception as exception:
        # If something went wrong, print out an error (spawned threads normally fail silently)
        print(exception)

def main():
    '''The main function'''

    ensure_dir(OUTPUT)

    # Use the 'tail' command with the 'sh' module to create an iterator from its output
    for line in tail("-f", LOG_FILE, _iter=True):
        # Check if the line could be a tile and download it
        if 'ggpht.com' in line:
            loop.run_in_executor(executor, download, line)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        loop.close()
