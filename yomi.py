#!/usr/bin/env python
# -*- coding: euc-jp -*-

import sys, re


##  utilities
##
HIRA2KATA = dict( (c, c+96) for c in xrange(0x3041,0x3094) )
def hira2kata(s):
    return s.translate(HIRA2KATA)

def decode_yomi(s):
    return u''.join( unichr(0x3000+ord(c)) for c in s )

POSTMAP = { u'��':u'��', u'��':u'��' }
POST = re.compile(ur'([�Ϥ�])([^��-��]*)$')
EUPH = re.compile(ur'([�����������ȥɥΥۥܥݥ���祩])��')
def reg_yomi(s):
    def f(m):
       return POSTMAP[m.group(1)]+m.group(2)
    s = POST.sub(f, s)
    s = hira2kata(s)
    s = EUPH.sub(ur'\1��', s)
    return s


##  Wakacher
##
class Wakacher(object):

    KIND = {}
    for (c,k) in (
        (u'AZ', 1), # latin
        (u'az', 1),
        (u'����', 1),
        (u'���', 1),
        (u'����', 2), # hira
        (u'����', 3), # kata
        (u'����', 3), # kata
        (u'\uff66\uff9f', 3),
        (u'\u3005\u3007', 4), # kanji
        (u'\u4e00\u9fff', 4), # kanji
        (u'09', 5), # digit
        (u'..', 5),
        (u'����', 5),
        ):
        for i in xrange(ord(c[0]),ord(c[1])+1):
            KIND[unichr(i)] = k
    for c in u'"([�ҡԡ֡ءڡ̡ȡʡ�\uff62':
        KIND[c] = 6
    #for c in u')]�ӡաס١ۡ͡�\��uff63':
    #    KIND[c] = 7

    PREFIX1 = set(
        [u'��'
         ])

    POST1 = {
        u'��': u'',
        u'��': u'�ä������',
        u'��': u'',
        u'��': u'�����������Ϥ��',
        u'��': u'�Ϥ�',
        # u'��',u'��',u'��'
        u'��': u'�򤬤ϤǤˤ���',
        }

    ADV1 = set(
        [u'�Ƴ�', u'����', u'����', u'���', u'����', u'���', u'��­', u'����',
         u'��Χ', u'�Ƽ�', u'�䡹', u'����', u'��´', u'����', u'����', u'���',
         u'����', u'�᡹', u'����', u'����', u'���', u'���', u'����', u'�缡',
         u'����', u'��ʬ', u'�޳�', u'����', u'��®', u'¿ʬ', u'����', u'����',
         u'����', u'����', u'���', u'����', u'����', u'����', u'��ǡ', u'����',
         u'����', u'����', u'̵��', u'��Ƭ', u'����', u'����', u'�ʸ�', u'����',
         u'�ʾ�', u'�ʹ�', u'����', u'��ǯ', u'����', u'��ǯ', u'����', u'���',
         u'�빽', u'����', u'����', u'����', u'����', u'����', u'����', u'����',
         u'��ǯ', u'����', u'����', u'����', u'����', u'����', u'�Ƕ�', u'�ǽ�',
         u'����', u'���', u'��ǯ', u'��', u'����', u'����', u'����', u'�躢',
         u'����', u'���', u'��ǯ', u'�轵', u'����', u'����', u'����', u'����',
         u'����', u'����', u'����', u'����', u'��ʬ', u'����', u'����', u'����',
         u'����', u'ǯ��', u'ǯ��', u'����', u'���', u'���', u'�轵', u'��ī',
         u'����', u'����', u'��ǯ', u'����', u'��ī', u'����', u'����', u'��ʬ',
         u'���', u'��ī', u'����', u'��ǯ', u'���', u'�轵', u'��ǯ', u'��ǯ',
         u'Ϣ��',
         ])

    MAXCONTKANJI = 2

    def __init__(self, tcdb, codec='euc-jp'):
        self._tcdb = tcdb
        self.codec = codec
        self.reset()
        return
    
    def reset(self):
        self._chunks = []
        self._chunk = u''
        self._parse = self._parse_main
        return

    def feed(self, chars):
        i = 0
        while 0 <= i and i < len(chars):
            c = chars[i]
            k = self.KIND.get(c, 0)
            i = self._parse(c, k, i)
        return

    def get_chunks(self, chars):
        self.reset()
        self.feed(chars)
        self._flush()
        (r, self._chunks) = (self._chunks, [])
        return r
    
    def _flush(self):
        if self._chunk:
            self._chunks.append(self._chunk)
            self._chunk = u''
        return
    
    def _parse_main(self, c, k, i):
        if k == 1:
            self._parse = self._parse_latin
        elif k == 2:
            self._parse = self._parse_tail
        elif k == 3:
            self._parse = self._parse_kata
        elif k == 4:
            self._dstate = 0
            self._parse = self._parse_kanji
        elif k == 5:
            self._parse = self._parse_digit
        elif k == 6:
            self._parse = self._parse_paren
        else:
            self._parse = self._parse_other
        return i

    def _parse_other(self, c, k, i):
        if k == 0:
            self._chunk += c
            return i+1
        self._flush()
        self._parse = self._parse_main
        return i

    def _parse_tail(self, c, k, i):
        if k == 2:
            # �֤��ꤤ�פʤɤΡ֤��פ�ľ�����ڤ롣
            if c in self.PREFIX1:
                self._prechunk = c
                self._parse = self._parse_tailpre
                return i+1
            self._chunk += c
            # ���줬�������ڤ뤫�⤷��ʤ���
            if c in self.POST1:
                self._parse = self._parse_tail2
            return i+1
        self._parse = self._parse_other
        return i

    def _parse_tail2(self, c, k, i):
        if k == 2:
            # ���줬³����硣
            c0 = self._chunk[-1]
            if (c0 in self.POST1 and c in self.POST1[c0]):
                self._parse = self._parse_tail
                return i
        # ���줬����ä��Τ��ڤ롣
        self._parse = self._parse_other
        return i

    def _parse_tailpre(self, c, k, i):
        if k == 4:
            # �֤�+�����פϡ֤��פ������ڤ롣
            self._flush()
            self._chunk += self._prechunk
            self._dstate = 0
            self._parse = self._parse_kanji
            return i
        self._chunk += self._prechunk
        self._parse = self._parse_tail
        return i

    def _parse_latin(self, c, k, i):
        if k == 1 or k == 5:
            self._chunk += c
            return i+1
        self._parse = self._parse_tail
        return i

    def _parse_kata(self, c, k, i):
        if k == 3:
            self._chunk += c
            return i+1
        self._parse = self._parse_tail
        return i
        
    def _parse_kanji(self, c, k, i):
        if k == 4:
            try:
                (_, self._dstate) = self._tcdb.lookup1(c.encode(self.codec), self._dstate)
            except KeyError:
                self._dstate = 0
                # MAXCONTKANJI ʸ���ʾ�δ���ñ��Τ��Ȥ��ڤ롣
                if self.MAXCONTKANJI <= len(self._chunk):
                    self._parse = self._parse_other
                    return i
            self._chunk += c
            return i+1
        self._parse = self._parse_tail
        return i
    
    def _parse_digit(self, c, k, i):
        if k == 5:
            self._chunk += c
            return i+1
        self._parse = self._parse_main
        return i

    def _parse_paren(self, c, k, i):
        if k == 6:
            self._chunk += c
            return i+1
        self._parse = self._parse_main
        return i


##  Yomer
##
class Yomer(object):

    UNIT = {
        u'ǯ': u'�ͥ�',
        u'��': u'����',
        u'��': u'�˥�',
        u'��': u'��',
        u'��': u'�˥�',
        u'��': u'����',
        }

    KIND = {}
    for (c,k) in (
        (u'09', 5), # digit
        (u'����', 5),
        ):
        for i in xrange(ord(c[0]),ord(c[1])+1):
            KIND[unichr(i)] = k
            
    ALPH = {
        ' ': u'���ڡ���',
        '.': u'�ԥꥪ��',
        ',': u'�����',
        '!': u'�ӥå���',
        '?': u'�ϥƥ�',
        '+': u'�ץ饹',
        '-': u'�ޥ��ʥ�',
        '*': u'������',
        '/': u'���',
        '(': u'���å�',
        ')': u'���å�',
        '@': u'���åȥޡ���',
        '~': u'�����',
        '#': u'���㡼��',
        '$': u'�ɥ�',
        '%': u'�ѡ������',
        "'": u'���ݥ��ȥ�ե�',
        '&': u'�����',
        '_': u'�������������',
        '=': u'��������',
        '<': u'���硼�ʥ�',
        '>': u'�����ʥ�',
        ':': u'�����',
        ';': u'���ߥ����',
        '[': u'�ҥ饭����',
        ']': u'�ȥ�����',

        '0': u'����',
        '1': u'����',
        '2': u'��',
        '3': u'����',
        '4': u'���',
        '5': u'��',
        '6': u'��',
        '7': u'�ʥ�',
        '8': u'�ϥ�',
        '9': u'���塼',
        
        'a': u'����',
        'b': u'�ӡ�',
        'c': u'����',
        'd': u'�ǡ�',
        'e': u'����',
        'f': u'����',
        'g': u'����',
        'h': u'������',
        'i': u'����',
        'j': u'����',
        'k': u'����',
        'l': u'����',
        'm': u'����',
        'o': u'����',
        'p': u'�ԡ�',
        'q': u'���塼',
        'r': u'������',
        's': u'����',
        't': u'�ơ�',
        'u': u'�桼',
        'v': u'�֥�',
        'w': u'���֥�',
        'x': u'���å���',
        'y': u'�磻',
        'z': u'���å�',
        }
    
    def __init__(self, tcdb, codec='euc-jp'):
        self._tcdb = tcdb
        self.codec = codec
        self.reset()
        return

    def reset(self):
        self._chunks = []
        self._part = u''
        self._yomi = None
        self._dstate = 0
        self._parse = self._parse_main
        return

    def feed(self, chars):
        i = 0
        while 0 <= i and i < len(chars):
            c = chars[i]
            k = self.KIND.get(c, 0)
            i = self._parse(c, k, i)
        return

    def get_yomi(self, chars):
        self.reset()
        self.feed(chars)
        self._flush()
        x = u''
        a = []
        for (c,y) in self._chunks:
            if y is None:
                if c.lower() in self.ALPH:
                    x += self.ALPH[c.lower()]
                else:
                    x += c
            else:
                if x:
                    a.append((x, reg_yomi(x)))
                    x = u''
                a.append((y, reg_yomi(y)))
        if x:
            a.append((x, reg_yomi(x)))
        return [a]

    def _flush(self):
        if self._yomi is not None:
            (n,y) = self._yomi
            self._chunks.append((self._part[:n], decode_yomi(y)))
            self._part = self._part[n:]
        if self._part:
            self._chunks.append((self._part, None))
        self._part = u''
        self._yomi = None
        return
    
    def _parse_main(self, c, k, i):
        if k == 5:
            self._parse = self._parse_digit
        else:
            self._parse = self._parse_other
        return i

    def _parse_digit(self, c, k, i):
        if k != 5:
            self._parse = self._parse_unit
            return i
        self._chunks.append((c, None))
        return i+1
    
    def _parse_unit(self, c, k, i):
        if c in self.UNIT:
            self._chunks.append((c, self.UNIT[c]))
            self._parse = self._parse_main
            return i+1
        self._parse = self._parse_main
        return i
    
    def _parse_other(self, c, k, i):
        if k == 5:
            self._parse = self._parse_main
            return i
        self._part += c
        try:
            (v, self._dstate) = self._tcdb.lookup1(c.encode(self.codec), self._dstate)
            if v:
                self._yomi = (len(self._part), v)
        except KeyError:
            self._dstate = 0
            self._flush()
        return i+1


# main
def main(argv):
    import getopt, fileinput, os.path
    from pycdb import TCDBReader
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
    for (k, v) in opts:
        if k == '-d': debug += 1
        elif k == '-c': codec = v
        elif k == '-C': dictcodec = v
        elif k == '-D': dictpath = v
    tcdb = TCDBReader(dictpath)
    yomer = Yomer(tcdb, dictcodec)
    wakacher = Wakacher(tcdb, dictcodec)
    for line in fileinput.input(args):
        line = line.decode(codec, 'ignore')
        for s in wakacher.get_chunks(line):
            print s
            for y in yomer.get_yomi(s):
                t = u''.join( v or k for (k,v) in y)
                print t
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
