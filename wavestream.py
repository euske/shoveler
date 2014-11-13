#!/usr/bin/env python
import sys
import wave
import struct
import array
import subprocess


##  WaveReader
##
class WaveReader(object):

    def __init__(self, path):
        self._fp = wave.open(path)
        self.nchannels = self._fp.getnchannels()
        self.sampwidth = self._fp.getsampwidth()
        self.framerate = self._fp.getframerate()
        self.nframes = self._fp.getnframes()
        self._nframesleft = self.nframes
        if self.sampwidth == 1:
            self.ratio = 1.0/256.0
            self.arraytype = 'b'
        else:
            self.ratio = 1.0/32768.0
            self.arraytype = 'h'
        return

    def __len__(self):
        return self.nframes

    def close(self):
        self._fp.close()
        return

    def eof(self):
        return (self._nframesleft == 0)
    
    def tell(self):
        return self._fp.tell()

    def seek(self, i):
        self._fp.setpos(i)
        self._nframesleft = self.nframes-i
        return

    def readraw(self, nframes=0):
        if nframes == 0 or self._nframesleft < nframes:
            nframes = self._nframesleft
        self._nframesleft -= nframes
        return (nframes, self._fp.readframes(nframes))
    
    def read(self, nframes=0):
        assert self.nchannels == 1
        (_,data) = self.readraw(nframes)
        a = array.array(self.arraytype)
        a.fromstring(data)
        return [ x*self.ratio for x in a ]


##  WaveWriter
##
class WaveWriter(object):

    def __init__(self, fp, 
                 nchannels=1, sampwidth=2,
                 framerate=44100, nframes=None):
        self.fp = fp
        self.nchannels = nchannels
        self.sampwidth = sampwidth
        self.framerate = framerate
        self.nframes = nframes
        self._nframeswritten = 0
        if self.sampwidth == 1:
            self.ratio = 255.0
            self.arraytype = 'b'
        else:
            self.ratio = 32767.0
            self.arraytype = 'h'
        if nframes is None:
            self._write_header(0, 0, 0, 0)
        else:
            self._write_header(nchannels, sampwidth, framerate, nframes)
        return

    def __len__(self):
        return self.nframes

    def _write_header(self, nchannels, sampwidth, framerate, nframes):
        datalen = nchannels * sampwidth * nframes
        self.fp.write('RIFF')
        self.fp.write(struct.pack('<l4s4slhhllhh4sl',
                                  36+datalen, 'WAVE', 'fmt ', 16,
                                  0x0001, nchannels, framerate,
                                  nchannels*sampwidth*framerate,
                                  nchannels*sampwidth,
                                  sampwidth*8, 'data', datalen))
        return

    def close(self):
        if self.nframes is None:
            self.fp.seek(0)
            self._write_header(self.nchannels, self.sampwidth,
                               self.framerate, self._nframeswritten)
        return

    def eof(self):
        return (self.nframes is not None and self.nframes <= self._nframeswritten)
    
    def tell(self):
        return self._nframeswritten

    def writeraw(self, bytes):
        self.fp.write(bytes)
        nframes = len(bytes) / (self.sampwidth*self.nchannels)
        self._nframeswritten += nframes
        return
    
    def write(self, frames):
        assert self.nchannels == 1
        a = [ int(x*self.ratio) for x in frames ]
        a = array.array(self.arraytype, a)
        self.writeraw(a.tostring())
        return


##  CommandWavePlayer
##
class CommandWavePlayer(object):

    PLAYER = ('aplay','-t','raw')

    def __init__(self, nchannels=1, sampwidth=2, framerate=44100,
                 player=PLAYER):
        if sampwidth == 1:
            fmt = 'U8'
            self.ratio = 255.0
            self.arraytype = 'b'
        else:
            fmt = 'S16_LE'
            self.ratio = 32767.0
            self.arraytype = 'h'
        cmdline = player+('-c',str(nchannels),'-r',str(framerate),'-f',fmt)
        self._process = subprocess.Popen(cmdline, stdin=subprocess.PIPE)
        self._nframeswritten = 0
        return

    def wait(self):
        self._process.wait()
        return

    def close(self):
        self._process.stdin.close()
        self._process = None
        return
    
    def tell(self):
        return self._nframeswritten

    def write(self, frames):
        data = [ int(x*self.ratio) for x in frames ]
        data = array.array(self.arraytype, data)
        self._process.stdin.write(data.tostring())
        self._nframeswritten += len(frames)
        return


##  PygameWavePlayer
##
class PygameWavePlayer(WaveWriter):

    def __init__(self, nchannels=1, sampwidth=2,
                 framerate=44100, nframes=None):
        import pygame
        from cStringIO import StringIO
        fp = StringIO()
        pygame.mixer.init()
        self.sound = None
        WaveWriter.__init__(self, fp, nchannels, sampwidth, framerate, nframes)
        return

    def close(self):
        import pygame
        from cStringIO import StringIO
        WaveWriter.close(self)
        fp = StringIO(self.fp.getvalue())
        self.sound = pygame.mixer.Sound(fp)
        self.play()
        return

    def play(self):
        if self.sound is not None:
            self.sound.play()
        return
