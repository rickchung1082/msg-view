#!/usr/bin/env python

import sys
import os
import signal
import optparse

from PySide import QtCore, QtGui

import zmq

DEVELOPMENT_ONLY = True

class ZMQSubscriber(object):
    def __init__(self, options):
        self.callbacks = []
        self.options = options
        zctx = zmq.Context()
        self.zctx = zctx
        s = zctx.socket(zmq.SUB)
        s.connect(options.publisher)
        # message filter
        s.setsockopt(zmq.SUBSCRIBE, 'random')
        self.zsocket = s
        fd = s.getsockopt(zmq.FD)
        notifier = QtCore.QSocketNotifier(fd, QtCore.QSocketNotifier.Read)
        notifier.activated.connect(self.zmq_socket_ready)
        self.notifier = notifier

    def zmq_socket_ready(self):
        s = self.zsocket
        flags = s.getsockopt(zmq.EVENTS)
        if zmq.POLLIN & flags:
            while 1:
                try:
                    msg = s.recv(zmq.NOBLOCK)
                except zmq.error.Again:
                    break
                for i in self.callbacks:
                    i(msg)

    def connect(self, func):
        # FIXME: make Qt SIGNAL
        self.callbacks.append(func)

def main(args):
    if DEVELOPMENT_ONLY:
        signal.signal(signal.SIGINT, signal.SIG_DFL)

    p = optparse.OptionParser(option_list = [
        optparse.Option('--publisher', default='tcp://192.168.1.2:8899'),
    ])
    (options, args) = p.parse_args(args)

    app = QtGui.QApplication(sys.argv[:1])
    s = ZMQSubscriber(options)
    def dump(msg):
        t = ''.join(('%02x\n' % (ord(x),)) for x in msg)
        sys.stderr.write(t)
    s.connect(dump)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main(sys.argv[1:])
