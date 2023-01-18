# Supernote screencast receiver

Finally, the screencast feature is here 🎉\
(Version Chauvet 2.7.22_beta)

Despite what the URL suggests, it is not a proper mjpeg stream, but a multipart/x-mixed-replace continuously updated PNG image. Even ffmpeg can't work with this stream.

Fortunately the stream is simple enough to parse, so I created this simple proof-of-concept Python script to extract individual images from the stream.

It has a couple of basic options, just run it like:

```
./main.py http://10.0.3.157:8080 -c 0 -t -f img_%.3f.png
```
