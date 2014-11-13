#!/usr/bin/env python
# -*- coding: euc-jp -*-
import sys

# zen2han(s): Converts every zenkaku letters to ascii ones.
FULLWIDTH = (
    u"�����ɡ������ǡʡˡ��ܡ�\uff0d\u2212�������������������������������䡩"
    u"�����£ãģţƣǣȣɣʣˣ̣ͣΣϣУѣңӣԣգ֣ףأ٣ڡΡ��ϡ���"
    u"�ƣ���������������������������������Сá�")
HALFWIDTH = (
    u" !\"#$%&'()*+,--./0123456789:;<=>?" 
    u"@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_" 
    u"`abcdefghijklmnopqrstuvwxyz{|}")
Z2HMAP = dict( (ord(zc), ord(hc)) for (zc,hc) in zip(FULLWIDTH, HALFWIDTH) )
def zen2han(s):
  return s.translate(Z2HMAP)


##  Mora
##
class Mora(object):

    def __init__(self, name):
        self.name = name
        return

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.name)


##  TransTable
##
class TransTable(object):

    def __init__(self):
        self._tree = {}
        return
    
    def add(self, k, value):
        t = self._tree
        for c in k:
            if c in t:
                t = t[c]
            else:
                t[c] = {}
                t = t[c]
        assert None not in t, (k, t)
        t[None] = value
        return

    def parse(self, s):
        t = self._tree
        r = []
        i = 0
        while i < len(s):
            c = s[i]
            if c in t:
                t = t[c]
                i += 1
            elif t is self._tree:
                i += 1
            else:
                if None in t:
                    v = t[None]
                    r.append(v)
                    if v.name == 'qq':
                        i -= 1
                t = self._tree
        if None in t:
            r.append(t[None])
        return r


##  Mora Table
##
MORA = [  
  ( '.', u'��' ),
  ( ',', u'��' ),
  ( '-', u'��' ),
  ( 'q', u'��', u'��' ),
  ( 'qq', 
    u'kk', u'ss', u'tt', u'cc',
    u'nn', u'hh', u'mm', u'yy',
    u'rr', u'ww', u'gg', u'zz',
    u'dd', u'bb', u'pp', u'jj',
    u'vv'),
  
  ( 'a', u'��',   u'��',   u'a' ),
  ( 'i', u'��',   u'��',   u'i' ),
  ( 'u', u'��',   u'��',   u'u' ),
  ( 'e', u'��',   u'��',   u'e' ),
  ( 'o', u'��',   u'��',   u'o' ),
  
  ( 'ka', u'��',   u'��',   u'ka' ),
  ( 'ki', u'��',   u'��',   u'ki' ),
  ( 'ku', u'��',   u'��',   u'ku' ),
  ( 'ke', u'��',   u'��',   u'ke' ),
  ( 'ko', u'��',   u'��',   u'ko' ),
  
  ( 'sa', u'��',   u'��',   u'sa' ),
  ( 'si', u'��',   u'��',   u'si', u'shi' ),
  ( 'su', u'��',   u'��',   u'su' ),
  ( 'se', u'��',   u'��',   u'se' ),
  ( 'so', u'��',   u'��',   u'so' ),
  
  ( 'ta', u'��',   u'��',   u'ta' ),
  ( 'ti', u'��',   u'��',   u'ti', u'chi' ),
  ( 'tu', u'��',   u'��',   u'tu', u'tsu' ),
  ( 'te', u'��',   u'��',   u'te' ),
  ( 'to', u'��',   u'��',   u'to' ),
  
  ( 'na', u'��',   u'��',   u'na' ),
  ( 'ni', u'��',   u'��',   u'ni' ),
  ( 'nu', u'��',   u'��',   u'nu' ),
  ( 'ne', u'��',   u'��',   u'ne' ),
  ( 'no', u'��',   u'��',   u'no' ),
  
  ( 'ha', u'��',   u'��',   u'ha' ),
  ( 'hi', u'��',   u'��',   u'hi' ),
  ( 'hu', u'��',   u'��',   u'hu', u'fu' ),
  ( 'he', u'��',   u'��',   u'he' ),
  ( 'ho', u'��',   u'��',   u'ho' ),
  
  ( 'ma', u'��',   u'��',   u'ma' ),
  ( 'mi', u'��',   u'��',   u'mi' ),
  ( 'mu', u'��',   u'��',   u'mu' ),
  ( 'me', u'��',   u'��',   u'me' ),
  ( 'mo', u'��',   u'��',   u'mo' ),
  
  ( 'ya', u'��',   u'��',   u'ya' ),
  ( 'yi', u'��',   u'��',   u'yi' ),
  ( 'yu', u'��',   u'��',   u'yu' ),
  ( 'ye', u'��',   u'��',   u'ye' ),
  ( 'yo', u'��',   u'��',   u'yo' ),
  
  ( 'ra', u'��',   u'��',   u'ra' ),
  ( 'ri', u'��',   u'��',   u'ri' ),
  ( 'ru', u'��',   u'��',   u'ru' ),
  ( 're', u'��',   u'��',   u're' ),
  ( 'ro', u'��',   u'��',   u'ro' ),
  
  ( 'wa', u'��',   u'��',   u'wa' ),
  ( 'wo', u'��',   u'��',   u'wo' ),
  ( 'n',  u'��',   u'��',   u'n' ),

  # voiced (Dakuon)
  ( 'ga', u'��',   u'��',   u'ga' ),
  ( 'gi', u'��',   u'��',   u'gi' ),
  ( 'gu', u'��',   u'��',   u'gu' ),
  ( 'ge', u'��',   u'��',   u'ge' ),
  ( 'go', u'��',   u'��',   u'go' ),
                  
  ( 'za', u'��',   u'��',   u'za' ),
  ( 'zi', u'��',   u'��', u'��', u'zi', u'di', u'ji' ),
  ( 'zu', u'��',   u'��', u'��', u'zu', u'du' ),
  ( 'ze', u'��',   u'��',   u'ze' ),
  ( 'zo', u'��',   u'��',   u'zo' ),
                  
  ( 'da', u'��',   u'��',   u'da' ),
  ( 'de', u'��',   u'��',   u'de' ),
  ( 'do', u'��',   u'��',   u'do' ),
  
  ( 'ba', u'��',   u'��',   u'ba' ),
  ( 'bi', u'��',   u'��',   u'bi' ),
  ( 'bu', u'��',   u'��',   u'bu' ),
  ( 'be', u'��',   u'��',   u'be' ),
  ( 'bo', u'��',   u'��',   u'bo' ),
  
  ( 'fa', u'�ե�', u'�դ�', u'fa' ),
  ( 'fi', u'�ե�', u'�դ�', u'fi' ),
  ( 'fe', u'�ե�', u'�դ�', u'fe' ),
  ( 'fo', u'�ե�', u'�դ�', u'fo' ),
  
  ( 'va', u'����', u'������', u'va' ),
  ( 'vi', u'����', u'������', u'vi' ),
  ( 'vu', u'��',   u'����',   u'vu' ),
  ( 've', u'����', u'������', u've' ),
  ( 'vo', u'����', u'������', u'vo' ),
  
  # p- sound (Handakuon)
  ( 'pa', u'��',   u'��',   u'pa' ),
  ( 'pi', u'��',   u'��',   u'pi' ),
  ( 'pu', u'��',   u'��',   u'pu' ),
  ( 'pe', u'��',   u'��',   u'pe' ),
  ( 'po', u'��',   u'��',   u'po' ),

  # double consonants (Youon)
  ( 'kya', u'����', u'����', u'kya' ),
  ( 'kyu', u'����', u'����', u'kyu' ),
  ( 'kye', u'����', u'����', u'kye' ),
  ( 'kyo', u'����', u'����', u'kyo' ),

  ( 'sya', u'����', u'����', u'sha', u'sya' ),
  ( 'syu', u'����', u'����', u'shu', u'syu' ),
  ( 'sye', u'����', u'����', u'she', u'sye' ),
  ( 'syo', u'����', u'����', u'sho', u'syo' ),
  
  ( 'cya', u'����', u'����', u'tya', u'cha' ),
  ( 'cyu', u'����', u'����', u'tyu', u'chu' ),
  ( 'cye', u'����', u'����', u'tye', u'che' ),
  ( 'cyo', u'����', u'����', u'tyo', u'cho' ),
  
  ( 'nya', u'�˥�', u'�ˤ�', u'nya' ),
  ( 'nyu', u'�˥�', u'�ˤ�', u'nyu' ),
  ( 'nye', u'�˥�', u'�ˤ�', u'nye' ),
  ( 'nyo', u'�˥�', u'�ˤ�', u'nyo' ),
  
  ( 'hya', u'�ҥ�', u'�Ҥ�', u'hya' ),
  ( 'hyu', u'�ҥ�', u'�Ҥ�', u'hyu' ),
  ( 'hye', u'�ҥ�', u'�Ҥ�', u'hye' ),
  ( 'hyo', u'�ҥ�', u'�Ҥ�', u'hyo' ),
  
  ( 'mya', u'�ߥ�', u'�ߤ�', u'mya' ),
  ( 'myu', u'�ߥ�', u'�ߤ�', u'myu' ),
  ( 'mye', u'�ߥ�', u'�ߤ�', u'mye' ),
  ( 'myo', u'�ߥ�', u'�ߤ�', u'myo' ),
  
  ( 'rya', u'���', u'���', u'rya', ),
  ( 'ryu', u'���', u'���', u'ryu', ),
  ( 'rye', u'�ꥧ', u'�ꤧ', u'rye', ),
  ( 'ryo', u'���', u'���', u'ryo', ),
  
  # double consonants + voiced
  ( 'gya', u'����', u'����', u'gya' ),
  ( 'gyu', u'����', u'����', u'gyu' ),
  ( 'gye', u'����', u'����', u'gye' ),
  ( 'gyo', u'����', u'����', u'gyo' ),
  
  ( 'jya', u'����', u'�¥�', u'����', u'�¤�', u'ja', u'zha', u'zya', u'dya' ),
  ( 'jyu', u'����', u'�¥�', u'����', u'�¤�', u'ju', u'zhu', u'zyu', u'dyu' ),
  ( 'jye', u'����', u'�¥�', u'����', u'�¤�', u'je', u'zhe', u'zye', u'dye' ),
  ( 'jyo', u'����', u'�¥�', u'����', u'�¤�', u'jo', u'zho', u'zyo', u'dyo' ),
  
  ( 'bya', u'�ӥ�', u'�Ӥ�', u'bya' ),
  ( 'byu', u'�ӥ�', u'�Ӥ�', u'byu' ),
  ( 'bye', u'�ӥ�', u'�Ӥ�', u'bye' ),
  ( 'byo', u'�ӥ�', u'�Ӥ�', u'byo' ),
  
  # double consonants + p-sound
  ( 'pya', u'�ԥ�', u'�Ԥ�', u'pya' ),
  ( 'pyu', u'�ԥ�', u'�Ԥ�', u'pyu' ),
  ( 'pye', u'�ԥ�', u'�Ԥ�', u'pye' ),
  ( 'pyo', u'�ԥ�', u'�Ԥ�', u'pyo' ),

  ]

MoraTable = TransTable()
for x in MORA:
    mora = Mora(x[0])
    for k in x[1:]:
        MoraTable.add(k, mora)

# main
def main(argv):
    import getopt, fileinput
    def usage():
        print 'usage: %s [-d] [-c codec] [file ...]' % argv[0]
        return 100
    try:
        (opts, args) = getopt.getopt(argv[1:], 'dc:D:')
    except getopt.GetoptError:
        return usage()
    debug = 0
    codec = 'utf-8'
    for (k, v) in opts:
        if k == '-d': debug += 1
        elif k == '-c': codec = v
    for line in fileinput.input(args):
        line = line.decode(codec, 'ignore')
        print MoraTable.parse(line)
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
