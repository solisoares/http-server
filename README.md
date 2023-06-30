# HTTP Server to serve files

Some features:
* Escape html
* Handle non ASCII in filenames for requests
* Do not allow higher directories traversal
* Buffer all received data before handling request
* Implement chunked transfer encoding

Usage:
```
python httpserver.py [-h] [--host HOST] [--port PORT] [--dir DIR]

optional arguments:
  -h, --help   show this help message and exit
  --host HOST  specify alternate host [default: localhost (127.0.0.1)]
  --port PORT  specify alternate port [default: 65432]
  --dir DIR    specify root directory [default: the directory you're at right now]

```


