<p align="center">
  <img src="https://raw.githubusercontent.com/MattiaFailla/Jelly/master/docs/img/Jelly-icon.png" alt="Logo" width="150" height="150" />
</p>
<h1 align="center">Jelly</h1>
<p align="center">
  <b>Smart auto-tuned messaging system in Python over socket</b></br>
  <sub>Use this module to let several scripts communicate over sockets.<sub>
</p>


<p align="center">
  <img src="https://raw.githubusercontent.com/MattiaFailla/Jelly/master/docs/img/jellyserver.gif" alt="Demo-server" width="800" />
</p>

* **Simple**: Extremely simple to use - so simple that it almost feels like magic!
* **Powerful**: Let an enormous amount of clients communicate to the server
* **Awesome**: Create intent, setup clients and enjoy!

[![-----------------------------------------------------](https://raw.githubusercontent.com/MattiaFailla/Jelly/master/docs/img/colored.png)](#getting-started)

## Getting Started
Follow these instructions to make Jelly operative

### Prerequisites
Jelly is written with Python 3.6 so make sure you have installed this version or above

### Installing
In order to install the right versions of the dependencies, there is the Pipfile you can use to setup Jelly by typing

```
$ pipenv install --three
```

[![-----------------------------------------------------](https://raw.githubusercontent.com/MattiaFailla/Jelly/master/docs/img/colored.png)](#tests)

## Minimal working example:

Start Server:

```
$ python cli.py server --cafile tests/demo_ssl/server.crt --keyfile tests/demo_ssl/server.key tests.mock_commands
```

Run some client requests:

```
$ python cli.py client --cafile tests/demo_ssl/server.crt echo ciao
$ python cli.py client --cafile tests/demo_ssl/server.crt uuid
$ python cli.py client --cafile tests/demo_ssl/server.crt maximum 6 9 99 987

```


## Running the tests:
Jelly's tests are made with unittest.

```
$ python -m unittest discover tests
```

### Test certficates:

To rebuild the demo certificates for SSL/TLS encryption use:

```
$ cd test/demo_ssl
$ openssl genrsa -des3 -passout pass:x1234 -out server.orig.key 2048
$ openssl rsa -passin pass:x1234 -in server.orig.key -out server.key
$ openssl req -new -key server.key -out server.csr
$ openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
```

[![-----------------------------------------------------](https://raw.githubusercontent.com/MattiaFailla/Jelly/master/docs/img/colored.png)](#info)
### Authors:
In alphabetic order:
* [Cavuti Christian](https://github.com/Kavuti)
* [De Paoli Marco](https://github.com/depaolim)
* [Failla Mattia](https://github.com/MattiaFailla)

## What we are working on:
Client side:
* Implement headers - Done
* Implement an ID system - Done
* Implement a send_forever directive - Done
* Implement an intent broker
* Implement a master-watchdogs

Server side:
* Read intent file and define a well-structured api endpoint

[![-----------------------------------------------------](https://raw.githubusercontent.com/MattiaFailla/Jelly/master/docs/img/colored.png)](#contribute)
## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License ![alt text](https://img.shields.io/npm/l/express.svg)
[MIT](https://choosealicense.com/licenses/mit/)
