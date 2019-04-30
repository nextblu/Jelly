# Jelly
A smart auto-tuned messaging system in python.

## Getting Started
Follow these instructions to make Jelly operative

### Prerequisites
Jelly is written with Python 3.6 so make sure you have installed this version or above

### Installing
In order to install the right versions of the dependencies, there is the Pipfile you can use to setup Jelly by typing

```
$ pipenv install --three
```

### TO DO:
* Implement a complete data exchange cycle (send/recv)
* Implement headers
* Implement an ID system
* Implement a send_forever directive
* Implement an intent broker
* Implement a master-watchdogs

On the server side:
* Read intent file and define a well-structured api endpoint

### TESTS:

```
$ python -m unittest test.tests
```

### TEST CERTIFICATES:

To rebuild the demo certificates:

```
cd test/demo_ssl
openssl genrsa -des3 -passout pass:x1234 -out server.orig.key 2048
openssl rsa -passin pass:x1234 -in server.orig.key -out server.key
openssl req -new -key server.key -out server.csr
openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
```
