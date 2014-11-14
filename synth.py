#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
        r.append((1.0-p)*a + p*b)
    return r


##  Synthesizer
##
class Synthesizer(object):

    def __init__(self, langdb, phonedb,
                 dictcodec='euc-jp', framerate=44100, ratio=1.0/32768.0, restdur=200):
        self.yomer = Yomer(langdb, dictcodec)
        self.wakacher = Wakacher(langdb, dictcodec)
        self.phonedb = phonedb
        self.framerate = framerate
        self.restframe = framerate*restdur/1000
        self.ratio = ratio
        return

    def synth(self, writer, text):
        self.genwave(writer, self._genphones(text))
        return

    VOWELS = ('aa','ii','uu','ee','oo','nn')
    def _genphones(self, text):
        for s in self.wakacher.get_chunks(text):
            for y in self.yomer.get_yomi(s):
                for (k,v) in y:
                    k0 = '_'
                    for m in MoraTable.parse(v or k):
                        if m.name in ('.', ','):
                            yield k0+'_'
                            k = m.name
                            k0 = '_'
                        elif m.name == '-':
                            k = k0
                        elif m.name == 'q':
                            k = k0+m.name
                            k0 = '_'
                        else:
                            k = k0+m.name
                            k0 = m.name[-1]
                            if k in self.VOWELS:
                                k = k[0]
                        yield k
                    yield k0+'_'
        return

    def genwave(self, writer, keys):
        (f0, w0, k0) = (None, 0, None)
        for k1 in keys:
            if k1 == '.':
                f1 = [0]*(self.restframe*2)
            elif k1 == ',':
                f1 = [0]*(self.restframe)
            else:
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
    from pytcdb import TCDBReader, CDBReader
    from wavestream import WaveWriter
    from wavestream import PygameWavePlayer as WavePlayer
    def usage():
        print 'usage: %s [-d] [-c codec] [-D dictpath] [-o output] [file ...]' % argv[0]
        return 100
    try:
        (opts, args) = getopt.getopt(argv[1:], 'do:c:C:D:')
    except getopt.GetoptError:
        return usage()
    debug = 0
    codec = 'utf-8'
    dictcodec = 'euc-jp'
    output = None
    dictpath = os.path.join(os.path.dirname(__file__), 'yomi.tcdb')
    phonepath = os.path.join(os.path.dirname(__file__), 'diphone.cdb')
    for (k, v) in opts:
        if k == '-d': debug += 1
        elif k == '-c': codec = v
        elif k == '-C': dictcodec = v
        elif k == '-D': dictpath = v
        elif k == '-o': output = v
    langdb = TCDBReader(dictpath)
    phonedb = CDBReader(phonepath)
    synth = Synthesizer(langdb, phonedb, dictcodec=dictcodec)
    if output is None:
        writer = WavePlayer()
    else:
        fp = open(output, 'wb')
        writer = WaveWriter(fp)
    for line in fileinput.input(args):
        line = line.decode(codec, 'ignore')
        synth.synth(writer, line)
    writer.close()
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
