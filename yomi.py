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

POSTMAP = { u'は':u'わ', u'へ':u'え' }
POST = re.compile(ur'([はわ])([^ぁ-ん]*)$')
EUPH = re.compile(ur'([オコゴソゾトドノホボポモヨロョォ])ウ')
def reg_yomi(s):
    def f(m):
       return POSTMAP[m.group(1)]+m.group(2)
    s = POST.sub(f, s)
    s = hira2kata(s)
    s = EUPH.sub(ur'\1ー', s)
    return s


##  Wakacher
##
class Wakacher(object):

    KIND = {}
    for (c,k) in (
        (u'AZ', 1), # latin
        (u'az', 1),
        (u'ＡＺ', 1),
        (u'ａｚ', 1),
        (u'ぁん', 2), # hira
        (u'ァヴ', 3), # kata
        (u'ーー', 3), # kata
        (u'\uff66\uff9f', 3),
        (u'\u3005\u3007', 4), # kanji
        (u'\u4e00\u9fff', 4), # kanji
        (u'09', 5), # digit
        (u'..', 5),
        (u'０９', 5),
        ):
        for i in xrange(ord(c[0]),ord(c[1])+1):
            KIND[unichr(i)] = k
    for c in u'"([〈《「『【〔“（［\uff62':
        KIND[c] = 6
    #for c in u')]〉》」』】〕）\］uff63':
    #    KIND[c] = 7

    PREFIX1 = set(
        [u'お'
         ])

    POST1 = {
        u'を': u'',
        u'が': u'っんらりるれろ',
        u'は': u'',
        u'で': u'あきさしすはもの',
        u'に': u'はも',
        # u'も',u'と',u'か'
        u'の': u'をがはでにだも',
        }

    ADV1 = set(
        [u'案外', u'以来', u'依然', u'一応', u'一切', u'一瞬', u'一足', u'一晩',
         u'一律', u'各自', u'延々', u'何故', u'何卒', u'俄然', u'皆目', u'急遽',
         u'極力', u'近々', u'今更', u'最早', u'至急', u'至極', u'時々', u'順次',
         u'所詮', u'随分', u'折角', u'全然', u'早速', u'多分', u'大抵', u'大変',
         u'大方', u'沢山', u'逐一', u'丁度', u'当然', u'到底', u'突如', u'別段',
         u'本来', u'万一', u'無論', u'毛頭', u'勿論', u'以前', u'以後', u'以来',
         u'以上', u'以降', u'昨日', u'昨年', u'近日', u'近年', u'偶然', u'結局',
         u'結構', u'元来', u'後日', u'今頃', u'今後', u'今回', u'今日', u'今月',
         u'今年', u'今週', u'今度', u'今晩', u'今夜', u'再度', u'最近', u'最初',
         u'昨日', u'昨月', u'昨年', u'昨週', u'昨晩', u'昨夜', u'先程', u'先頃',
         u'先日', u'先月', u'先年', u'先週', u'先晩', u'先夜', u'前回', u'前月',
         u'全部', u'途中', u'当初', u'当日', u'当分', u'当面', u'日中', u'日頃',
         u'日夜', u'年々', u'年中', u'本日', u'毎回', u'毎月', u'毎週', u'毎朝',
         u'毎度', u'毎日', u'毎年', u'毎晩', u'明朝', u'明日', u'明晩', u'夜分',
         u'翌月', u'翌朝', u'翌日', u'翌年', u'来月', u'来週', u'来年', u'例年',
         u'連日',
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
            # 「お願い」などの「お」は直前で切る。
            if c in self.PREFIX1:
                self._prechunk = c
                self._parse = self._parse_tailpre
                return i+1
            self._chunk += c
            # 助詞がきたら切るかもしれない。
            if c in self.POST1:
                self._parse = self._parse_tail2
            return i+1
        self._parse = self._parse_other
        return i

    def _parse_tail2(self, c, k, i):
        if k == 2:
            # 助詞が続く場合。
            c0 = self._chunk[-1]
            if (c0 in self.POST1 and c in self.POST1[c0]):
                self._parse = self._parse_tail
                return i
        # 助詞が終わったので切る。
        self._parse = self._parse_other
        return i

    def _parse_tailpre(self, c, k, i):
        if k == 4:
            # 「お+漢字」は「お」の前で切る。
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
                # MAXCONTKANJI 文字以上の漢字単語のあとは切る。
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
        u'年': u'ネン',
        u'月': u'ガツ',
        u'日': u'ニチ',
        u'時': u'ジ',
        u'人': u'ニン',
        u'歳': u'サイ',
        }

    KIND = {}
    for (c,k) in (
        (u'09', 5), # digit
        (u'０９', 5),
        ):
        for i in xrange(ord(c[0]),ord(c[1])+1):
            KIND[unichr(i)] = k
            
    ALPH = {
        ' ': u'スペース',
        '.': u'ピリオド',
        ',': u'カンマ',
        '!': u'ビックリ',
        '?': u'ハテナ',
        '+': u'プラス',
        '-': u'マイナス',
        '*': u'カケル',
        '/': u'ワル',
        '(': u'カッコ',
        ')': u'コッカ',
        '@': u'アットマーク',
        '~': u'チルダ',
        '#': u'シャープ',
        '$': u'ドル',
        '%': u'パーセント',
        "'": u'アポストロフィ',
        '&': u'アンド',
        '_': u'アンダースコア',
        '=': u'イコール',
        '<': u'ショーナリ',
        '>': u'ダイナリ',
        ':': u'コロン',
        ';': u'セミコロン',
        '[': u'ヒラキカギ',
        ']': u'トジカギ',

        '0': u'ゼロ',
        '1': u'イチ',
        '2': u'ニ',
        '3': u'サン',
        '4': u'ヨン',
        '5': u'ゴ',
        '6': u'ロク',
        '7': u'ナナ',
        '8': u'ハチ',
        '9': u'キュー',
        
        'a': u'エー',
        'b': u'ビー',
        'c': u'シー',
        'd': u'デー',
        'e': u'イー',
        'f': u'エフ',
        'g': u'ジー',
        'h': u'エイチ',
        'i': u'アイ',
        'j': u'ジエ',
        'k': u'ケイ',
        'l': u'エル',
        'm': u'エム',
        'o': u'オー',
        'p': u'ピー',
        'q': u'キュー',
        'r': u'アール',
        's': u'エス',
        't': u'テー',
        'u': u'ユー',
        'v': u'ブイ',
        'w': u'ダブル',
        'x': u'エックス',
        'y': u'ワイ',
        'z': u'ゼット',
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
