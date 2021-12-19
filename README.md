Web server test suite
=====================

## Requirements ##

* Respond to `GET` with status code in `{200,404,403}`
* Respond to `HEAD` with status code in `{200,404,403}`
* Respond to all other request methods with status code `405`
* Directory index file name `index.html`
* Respond to requests for `/<file>.html` with the contents of `DOCUMENT_ROOT/<file>.html`
* Requests for `/<directory>/` should be interpreted as requests for `DOCUMENT_ROOT/<directory>/index.html`
* Respond with the following header fields for all requests:
  * `Server`
  * `Date`
  * `Connection`
* Respond with the following additional header fields for all `200` responses to `GET` and `HEAD` requests:
  * `Content-Length`
  * `Content-Type`
* Respond with correct `Content-Type` for `.html, .css, js, jpg, .jpeg, .png, .gif, .swf`
* Respond to percent-encoding URLs
* Correctly serve a 2GB+ files
* No security vulnerabilities

## Testing environment ##

* Put `Dockerfile` to web server repository root
* Prepare docker container to run tests:
  * Read config file `/etc/httpd.conf`
  * Expose port 80

Config file spec:
```
cpu_limit 4       # maximum CPU count to use (for non-blocking servers)
thread_limit 256  # maximum simultaneous connections (for blocking servers)
document_root /var/www/html
```

Run tests:
```
git clone https://github.com/Sergei39/web-server.git
cd web-server

docker build -t web-server .
docker run -p 80:80 --name web-server -t web-server

./httptest.py
```

## Testing  

### Func tests result:  

```asm
Ran 24 tests in 0.154s
OK
```
### Load test result:  

- ab -n 10000 -c 10 127.0.0.1:80/httptest/wikipedia_russia.html
```
This is ApacheBench, Version 2.3 <$Revision: 1879490 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient)
Completed 1000 requests
Completed 2000 requests
Completed 3000 requests
Completed 4000 requests
Completed 5000 requests
Completed 6000 requests
Completed 7000 requests
Completed 8000 requests
Completed 9000 requests
Completed 10000 requests
Finished 10000 requests


Server Software:        web-server
Server Hostname:        127.0.0.1
Server Port:            80

Document Path:          /httptest/wikipedia_russia.html
Document Length:        954824 bytes

Concurrency Level:      10
Time taken for tests:   2.715 seconds
Complete requests:      10000
Failed requests:        0
Total transferred:      9549680000 bytes
HTML transferred:       9548240000 bytes
Requests per second:    3683.67 [#/sec] (mean)
Time per request:       2.715 [ms] (mean)
Time per request:       0.271 [ms] (mean, across all concurrent requests)
Transfer rate:          3435335.04 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   1.1      0     106
Processing:     2    2   4.6      2     108
Waiting:        1    2   3.5      1     107
Total:          2    3   4.7      2     108

Percentage of the requests served within a certain time (ms)
  50%      2
  66%      2
  75%      2
  80%      3
  90%      3
  95%      3
  98%      4
  99%      6
 100%    108 (longest request)
```

### Nginx:  
- ab -n 10000 -c 10 127.0.0.1/httptest/wikipedia_russia.html
```asm
This is ApacheBench, Version 2.3 <$Revision: 1879490 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient)
Completed 1000 requests
Completed 2000 requests
Completed 3000 requests
Completed 4000 requests
Completed 5000 requests
Completed 6000 requests
Completed 7000 requests
Completed 8000 requests
Completed 9000 requests
Completed 10000 requests
Finished 10000 requests


Server Software:        nginx/1.21.3
Server Hostname:        127.0.0.1
Server Port:            8000

Document Path:          /httptest/wikipedia_russia.html
Document Length:        954824 bytes

Concurrency Level:      10
Time taken for tests:   2.363 seconds
Complete requests:      10000
Failed requests:        0
Total transferred:      9550620000 bytes
HTML transferred:       9548240000 bytes
Requests per second:    4232.12 [#/sec] (mean)
Time per request:       2.363 [ms] (mean)
Time per request:       0.236 [ms] (mean, across all concurrent requests)
Transfer rate:          3947205.70 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   2.6      0     129
Processing:     1    2   3.2      2     131
Waiting:        0    0   1.8      0     129
Total:          1    2   4.2      2     131

Percentage of the requests served within a certain time (ms)
  50%      2
  66%      2
  75%      2
  80%      2
  90%      2
  95%      2
  98%      3
  99%      5
 100%    131 (longest request)
```