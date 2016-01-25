# SimpleChat
Simple telnet chat server with twisted and python 2

## Why?

Simple chat was designed to be extremely portable and therefore requires no special client. Telnet is installed by default on OSX and most linux distros and easily installable on windows via the features system. This means that you can connect on almost any system. Netcat (`nc`) can also be used if you telnet is not available.

This means that you can easily use it on locked down computers where installing new software is not always an option.

### Features
- No need for a special client
- Extremely portable
- Server is very simple and easy to install on most server configurations

### Caveats
- Chat history is not saved on the server side
- There is no authentication to make sure that a username is the same person
- No chat notification
- Depending on your client output can be weird

## To Run

```
$ ./server.py
```

or

```
$ python2 server.py
```

## To connect

```
$ telnet <ip address> 1234
```

or

```
$ nc <ip address> 1234
```
