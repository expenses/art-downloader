from sh import tail
import re
import concurrent.futures
import asyncio
import requests
import os

output = "images"
session = requests.session()
loop = asyncio.get_event_loop()
executor = concurrent.futures.ThreadPoolExecutor(max_workers=25)

def process(line):
    return line.split(" ")[-1].rstrip()

def insert_multiple(list, index, items):
    for item in items:
        list.insert(index, item)
        index += 1

def decrypt(data):
    data = list(data)

    # Fix huffman tables or some shit idk
    if data[185] == 32:
        del data[185]
        insert_multiple(data, 185, [0, 0, 1, 5, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0])
        del data[203:213]
        insert_multiple(data, 203, [1, 2, 3])
        del data[207:215]
        insert_multiple(data, 207, [5, 6, 7])
        del data[211:223]
        insert_multiple(data, 211, [9, 10, 11, 255, 196, 0])

    # Trim out unused bytes
    data = data[4:-4]

    return bytes(data)

def download(line):
    url = process(line)
    x, y, z = re.findall('x(\d+)-y(\d+)-z(\d+)', url)[0]

    filename = os.path.join(output, f"{z}-{x}-{y}.jpg")
    if not os.path.exists(filename):
        data = decrypt(session.get(url).content)
        print("Writing %s" % filename)
        open(filename, "wb").write(data)

if not os.path.isdir(output):
    os.makedirs(output)

for line in tail("-f", "../desktop/http-request-log.txt", _iter=True):
    if 'ggpht.com' in line:
        future = loop.run_in_executor(executor, download, line)
    
loop.close()