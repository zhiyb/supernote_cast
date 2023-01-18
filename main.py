#!/usr/bin/env python3
import sys
import datetime
import argparse
import requests

def sn_cast(url, callback):
    "Connect to Supernote device and receive screencast images"

    url = f"{url}/screencast.mjpeg"
    buf = bytearray()
    header_mode = True
    header = {}
    line_skip = 0
    data_len = 0

    with requests.get(url, stream=True) as r:
        ctype = [s.strip() for s in r.headers['Content-Type'].split(';')]
        if ctype[0] != 'multipart/x-mixed-replace':
            raise Exception(f"Unknown Content-Type: {ctype}")
        boundary = ''
        for param in ctype[1:]:
            key, val = param.split('=')
            if key == 'boundary':
                boundary = val

        for c in r.iter_content(chunk_size=None):
            buf += c
            while header_mode:
                try:
                    line, nbuf = buf.split(b'\n', 1)
                except:
                    break
                else:
                    buf = nbuf
                    #print(line)
                    line = line.strip().decode('utf-8')
                    if line_skip:
                        if line:
                            print(f"Warning: non-empty line skipped: {line}")
                        line_skip -= 1
                        continue
                    if line == f"--{boundary}":
                        continue
                    if not line:
                        header_mode = False
                        data_len = int(header['Content-Length'])
                        #print(header)
                    else:
                        key, val = line.split(':', 1)
                        header[key] = val
            else:
                if len(buf) >= data_len:
                    data = buf[:data_len]
                    buf = buf[data_len:]
                    line_skip = 1
                    header_mode = True
                    if not callback(data):
                        break

class SaveImg:
    def __init__(self, args):
        self.file = args.file
        self.count = args.count
        self.ts = args.timestamp
        self.index = 0

    def process(self, img):
        "Process received image data, return False to stop"

        if self.file == '-':
            sys.stdout.buffer.write(img)
        else:
            val = self.index
            if self.ts:
                dt = datetime.datetime.utcnow()
                val = dt.timestamp()
                #print(dt, val)
            fname = self.file%val if '%' in self.file else self.file
            with open(fname, 'wb') as f:
                f.write(img)

        self.index += 1
        return self.index != self.count

def main():
    parser = argparse.ArgumentParser(
        prog = 'sn_cast',
        description = 'Supernote screencast receiver')
    parser.add_argument('url',
                        help='URL of Supernote device (e.g. http://192.168.0.157:8080)')
    parser.add_argument('-c', '--count', type=int,
                        help='Number of frames to capture (0 for unlimited)')
    parser.add_argument('-t', '--timestamp', action='store_true',
                        help='Use UTC timestamp in file name instead of counter')
    parser.add_argument('-f', '--file', default='img_%d.png',
                        help='Output filename')
    args = parser.parse_args()

    c = SaveImg(args)
    sn_cast(args.url, c.process)

if __name__ == "__main__":
    main()
