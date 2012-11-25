#!/usr/bin/env python
# -*- coding: euc-jp -*-
import sys
import array
import struct
from yomi import Wakacher
from yomi import Yomer
from mora import MoraTable
from math import cos, pi

def mix(x, y):
    assert len(x) == len(y)
    C = pi/len(x)
    r = []
    for (i,(a,b)) in enumerate(zip(x,y)):
        p = (1.0-cos(C*i))*0.5
        r.append(p*a + (1.0-p)*b)
    return r


##  Synthesizer
##
class Synthesizer(object):

    def __init__(self, langdb, phonedb,
                 dictcodec='euc-jp', framerate=44100, ratio=1.0/32768.0):
        self.yomer = Yomer(langdb, dictcodec)
        self.wakacher = Wakacher(langdb, dictcodec)
        self.phonedb = phonedb
        self.framerate = framerate
        self.ratio = ratio
        return

    def synth(self, writer, text):
        self._genwave(writer, self._genphones(text))
        return

    def _genphones(self, text):
        k0 = '_'
        for s in self.wakacher.get_chunks(text):
            for y in self.yomer.get_yomi(s):
                for (k,v) in y:
                    for m in MoraTable.parse(v or k):
                        if m.name == '-':
                            k = k0
                        elif m.name == 'q':
                            k = k0+m.name
                            k0 = '_'
                        else:
                            k = k0+m.name
                            k0 = m.name[-1:]
                        yield k
                    yield k0+'_'
        return

    def _genwave(self, writer, keys):
        (f0, w0, k0) = (None, 0, None)
        for k1 in keys:
            try:
                data = self.phonedb[k1]
            except KeyError:
                continue
            a = array.array('h')
            a.fromstring(data)
            f1 = [ x*self.ratio for x in a ]
            w1 = 0
            if k0 is not None:
                k = k0+'+'+k1
                if k in self.phonedb:
                    (w1,) = struct.unpack('<i', self.phonedb[k])
                if w1:
                    writer.write(f0[w0:-w1])
                    writer.write(mix(f0[-w1:], f1[:w1]))
                else:
                    writer.write(f0[w0:])                    
            (f0,w0,k0) = (f1,w1,k1)
        if f0 is not None:
            writer.write(f0[w0:])
        return

# main
def main(argv):
    import getopt, fileinput, os.path
    from pycdb import TCDBReader, CDBReader
    from wavestream import WaveWriter
    def usage():
        print 'usage: %s [-d] [-c codec] [-D dictpath] [file ...]' % argv[0]
        return 100
    try:
        (opts, args) = getopt.getopt(argv[1:], 'dc:C:D:')
    except getopt.GetoptError:
        return usage()
    debug = 0
    codec = 'utf-8'
    dictcodec = 'euc-jp'
    dictpath = os.path.join(os.path.dirname(__file__), 'yomi.tcdb')
    phonepath = os.path.join(os.path.dirname(__file__), 'diphone.cdb')
    for (k, v) in opts:
        if k == '-d': debug += 1
        elif k == '-c': codec = v
        elif k == '-C': dictcodec = v
        elif k == '-D': dictpath = v
    langdb = TCDBReader(dictpath)
    phonedb = CDBReader(phonepath)
    synth = Synthesizer(langdb, phonedb, dictcodec=dictcodec)
    for line in fileinput.input(args):
        line = line.decode(codec, 'ignore')
        fp = open('out.wav', 'wb')
        writer = WaveWriter(fp)
        synth.synth(writer, line)
        writer.close()
        fp.close()
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
