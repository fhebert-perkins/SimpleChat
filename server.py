#! /bin/python2

# The MIT License (MIT)
#
# Copyright (c) 2016 Finley Hebert-Perkins
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from twisted.internet   import reactor, protocol, endpoints
from twisted.protocols  import basic
import config as cfg

class ChatProtocol(basic.LineReceiver):
    def __init__(self, factory):
        self.factory = factory
        self.name = "Guest{}".format(len(self.factory.channels[cfg.defaultChannel])+1)
        self.channel = cfg.defaultChannel

    def broadcast(self, message):
        for c in self.factory.channels[self.channel]:
            c.sendLine(message)

    def connectionMade(self): # On a new connection
        self.factory.channels[cfg.defaultChannel].add(self) # add client to client set
        self.sendLine("! Use /name <name> to rename yourself") # tell user how to change name
        self.broadcast("! {} has joined".format(self.name)) # tell all those who are connected that someone has connected

    def connectionLost(self, reason):
        self.broadcast("! {} has left".format(self.name)) # tell everyone that person has left
        self.factory.channels[self.channel].remove(self) # remove from set

    def lineReceived(self, line):
        try:
            line = line.decode("utf-8") # turn the bits sent into a string
        except:
            self.sendLine("! Malformed string sent")
            return 0

        if line.startswith("/name"): # name command
            if len(line.split(" ")) >= 2 :
                self.broadcast("! {} is now {}".format(self.name, line.split(" ")[1]))
                self.name = line.split(" ")[1]
                self.factory.channels[self.channel].remove(self)
                self.factory.channels[self.channel].add(self)

        elif line.startswith("/me"): # me command
            self.broadcast(line.replace("/me", "*{}".format(self.name)))

        elif line.startswith("/list"): # list all people connected
            self.sendLine(", ".join([c.name for c in self.factory.channels[self.channel]]))

        elif line.startswith("/tell"): # privately say something to someone else
            for c in self.factory.channels[self.channel]:
                if c.name in line.split(" ")[1].split(","):
                    c.sendLine("[{} # {}".format(self.name, " ".join(line.split(" ")[2:])))

        elif line.startswith("/channel"):
            if len(line.split(" ")) == 1:
                self.sendLine("! You are currently in {}".format(self.channel))

            elif line.split(" ")[1] == "join":
                newchannel = line.split(" ")[2]
                if newchannel not in self.factory.channels.keys():
                    self.factory.channels[newchannel] = set()
                self.factory.channels[self.channel].remove(self)
                self.factory.channels[newchannel].add(self)
                self.broadcast("! {} has left the channel".format(self.name))
                self.channel = newchannel
                self.broadcast("! {} has joined the channel".format(self.name))

            elif line.split(" ")[1] == "list":
                self.sendLine(", ".join(self.factory.channels.keys()))

            else:
                self.sendLine("! Command not understood")

        elif line.startswith("/help"): # help command
            self.sendLine("Help text:")
            self.sendLine("/name <name>         : sets your name")
            self.sendLine("/me <action>         : says you did something")
            self.sendLine("/list                : list all users in channel")
            self.sendLine("/tell <name> <msg>   : tell username something")
            self.sendLine("/channel list        : list all channels")
            self.sendLine("/channel join <name> : join a channel")

        elif line.startswith("/"): # catchall for malformed or unrecoignized commands
            self.sendLine("! command not recoignized")

        else:
            self.broadcast("{0}{1}{2} {3}".format(cfg.antecedent, self.name, cfg.postscript, line)) # otherwise just broadcast it

class ServerFactory(protocol.Factory):
    def __init__(self):
        self.channels = {}
        self.channels[cfg.defaultChannel] = set()

    def buildProtocol(self, addr):
        return ChatProtocol(self)

endpoints.serverFromString(reactor, "tcp:%s" % cfg.port).listen(ServerFactory())
reactor.run()
