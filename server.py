#! /bin/python2

from twisted.internet import reactor, protocol, endpoints
from twisted.protocols import basic
import random
import time

def timestamp():
    return time.strftime("%H:%M.%S")

class PubProtocol(basic.LineReceiver):
    def __init__(self, factory):
        self.factory = factory
        self.name = "Guest{}".format(random.randint(0, 100))

    def broadcast(self, message):
        for c in self.factory.clients:
            c.sendLine(message)

    def connectionMade(self): # On connection
        self.factory.clients.add(self) # add client to client set
        self.sendLine("! Use /name <name> to rename yourself") # tell user how to change name
        self.broadcast("! {} has joined".format(self.name)) # tell all those who are connected that someone has connected


    def connectionLost(self, reason):
        self.broadcast("! {} has left".format(self.name)) # tell everyone that person has left
        self.factory.clients.remove(self) # remove from set

    def lineReceived(self, line):
        line = str(line) # turn the bits sent into a string
        if line.startswith("/name"): # name command
            if len(line.split(" ")) >= 2 :
                self.broadcast("! {} is now {}".format(self.name, line.split(" ")[1]))
                self.name = line.split(" ")[1]
                self.factory.clients.remove(self)
                self.factory.clients.add(self)

        elif line.startswith("/me"): # me command
            self.broadcast(line.replace("/me", "*{}".format(self.name)))

        elif line.startswith("/list"): # list all people connected
            self.sendLine(", ".join([c.name for c in self.factory.clients]))

        elif line.startswith("/tell"): # privately say something to someone else
            for c in self.factory.clients:
                if c.name in line.split(" ")[1].split(","):
                    c.sendLine("[{}# {}".format(self.name, " ".join(line.split(" ")[2:])))
        elif line.startswith("/help"): # help command
            self.sendLine("Help text:")
            self.sendLine("/name <name>         : sets your name")
            self.sendLine("/me <action>         : says you did something")
            self.sendLine("/list                : list all users")
            self.sendLine("/tell <name> <msg>   : tell username something")
        else:
            self.broadcast("[{}] {}".format(self.name, line)) # otherwise just broadcast it

class PubFactory(protocol.Factory):
    def __init__(self):
        self.clients = set()

    def buildProtocol(self, addr):
        return PubProtocol(self)

endpoints.serverFromString(reactor, "tcp:1234").listen(PubFactory())
reactor.run()
