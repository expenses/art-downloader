from sh import tail
import re
import concurrent.futures
import asyncio
import requests
import os
import xmltodict
from gapdecoder.decryption import decrypt

images = "images"

session = requests.session()
loop = asyncio.get_event_loop()
executor = concurrent.futures.ThreadPoolExecutor(max_workers=40)

def process(line):
    return line.split(" ")[-1].rstrip()

def ensure_dir(dir):
    if not os.path.isdir(dir):
        os.makedirs(dir)
        print("Created '%s'." % dir)

def download(line):
    try:
        url = process(line)
        
        try:
            key, x, y, z = re.findall('ggpht.com/([^=]+)=x(\d+)-y(\d+)-z(\d+)', url)[0]
        except:
            return

        output_dir = os.path.join(images, key)
        filename = f"{z}-{x}-{y}.jpg"
        output = os.path.join(output_dir, filename)

        if not os.path.exists(output):
            ensure_dir(output_dir)

            print("Requesting '%s'..." % filename)
            data = decrypt(session.get(url).content)
            open(output, "wb").write(data)
    except Exception as exception:
        print(exception)

def main():
    ensure_dir(images)

    for line in tail("-f", "../desktop/http-request-log.txt", _iter=True):
        if 'ggpht.com' in line:
            loop.run_in_executor(executor, download, line)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        loop.close()