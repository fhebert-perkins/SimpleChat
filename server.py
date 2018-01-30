#! /bin/python3

# The MIT License (MIT)
#
# Copyright (c) 2018 Finley Hebert-Perkins
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

import asyncio

class Peer:
    def __init__(self, transport):
        self.transport = transport
        self.name = "guest{}".format(len(peers))

    def set_name(self, name):
        self.name = name

peers = []

class ChatServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(self.peername))
        self.peer = Peer(transport)
        self.transport = transport
        peers.append(self.peer)
        self.broadcast("! {} has joined".format(self.peer.name))

    def echo(self, message):
        print("echo: {}".format(message))
        message = message+"\n"
        self.transport.write(message.encode("UTF-8"))

    def broadcast(self, message):
        print("broadcast: {}".format(message))
        message = message+"\n"
        for peer in peers:
            peer.transport.write(message.encode("UTF-8"))

    def handle_command(self, tokens):
        if tokens[0] == "list":
            self.echo(",".join([peer.name for peer in peers]))
        elif tokens[0] == "name":
            if len(tokens) == 3:
                for peer in peers:
                    if peer.name == tokens[1]:
                        self.echo("! unable to set name to {} because that name is already in use".format(tokens[1]))
                        return
                self.broadcast("! {} changed thier name to {}".format(self.peer.name, tokens[1]))
                self.peer.set_name(tokens[1])
                return
            else:
                self.echo("! must specifiy a name to change")
                return
        elif tokens[0] == "whoami":
            self.echo("! you are {}".format(self.peer.name))
            return
        elif tokens[0] == "me":
            self.broadcast("*{} {}".format(self.peer.name, " ".join(tokens[2:])))
            return
        elif tokens[0] == "tell":
            for peer in peers:
                if peer.name == tokens[1]:
                    peer.transport.write(" ".join(tokens[2:]))
                    return
            self.echo("! {} not found on server".join(tokens[2]))
            return
        elif tokens[0] == "exit":
            self.peer.transport.close()
            # self.connection_lost("Exited")

    def data_received(self, data):
        message = data.decode().strip()
        # command handling
        if message.startswith('/'):
            self.handle_command(message[1:].split(" "))
        else:
            self.broadcast("<{}> {}".format(self.peer.name, message))

    def connection_lost(self, exc):
        self.broadcast("! {} has left the server".format(self.peer.name))
        print("Connection from {} lost: {}".format(self.peername, exc))
        i = 0
        for peer in peers:
            if peer.name == self.peer.name:
                del peers[i]
                return
            i+=1


loop = asyncio.get_event_loop()
# Each client connection will create a new protocol instance
coro = loop.create_server(ChatServerProtocol, '127.0.0.1', 1234)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()
