#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

# zen2han(s): Converts every zenkaku letters to ascii ones.
FULLWIDTH = (
    u"　！”＃＄％＆’（）＊＋，\uff0d\u2212．／０１２３４５６７８９：；＜＝＞？"
    u"＠ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ［＼］＾＿"
    u"‘ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ｛｜｝")
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
  ( '.', u'。' ),
  ( ',', u'、' ),
  ( '-', u'ー' ),
  ( 'q', u'ッ', u'っ' ),
  ( 'qq', 
    u'kk', u'ss', u'tt', u'cc',
    u'nn', u'hh', u'mm', u'yy',
    u'rr', u'ww', u'gg', u'zz',
    u'dd', u'bb', u'pp', u'jj',
    u'vv'),
  
  ( 'a', u'ア',   u'あ',   u'a' ),
  ( 'i', u'イ',   u'い',   u'i' ),
  ( 'u', u'ウ',   u'う',   u'u' ),
  ( 'e', u'エ',   u'え',   u'e' ),
  ( 'o', u'オ',   u'お',   u'o' ),
  
  ( 'ka', u'カ',   u'か',   u'ka' ),
  ( 'ki', u'キ',   u'き',   u'ki' ),
  ( 'ku', u'ク',   u'く',   u'ku' ),
  ( 'ke', u'ケ',   u'け',   u'ke' ),
  ( 'ko', u'コ',   u'こ',   u'ko' ),
  
  ( 'sa', u'サ',   u'さ',   u'sa' ),
  ( 'si', u'シ',   u'し',   u'si', u'shi' ),
  ( 'su', u'ス',   u'す',   u'su' ),
  ( 'se', u'セ',   u'せ',   u'se' ),
  ( 'so', u'ソ',   u'そ',   u'so' ),
  
  ( 'ta', u'タ',   u'た',   u'ta' ),
  ( 'ti', u'チ',   u'ち',   u'ti', u'chi' ),
  ( 'tu', u'ツ',   u'つ',   u'tu', u'tsu' ),
  ( 'te', u'テ',   u'て',   u'te' ),
  ( 'to', u'ト',   u'と',   u'to' ),
  
  ( 'na', u'ナ',   u'な',   u'na' ),
  ( 'ni', u'ニ',   u'に',   u'ni' ),
  ( 'nu', u'ヌ',   u'ぬ',   u'nu' ),
  ( 'ne', u'ネ',   u'ね',   u'ne' ),
  ( 'no', u'ノ',   u'の',   u'no' ),
  
  ( 'ha', u'ハ',   u'は',   u'ha' ),
  ( 'hi', u'ヒ',   u'ひ',   u'hi' ),
  ( 'hu', u'フ',   u'ふ',   u'hu', u'fu' ),
  ( 'he', u'ヘ',   u'へ',   u'he' ),
  ( 'ho', u'ホ',   u'ほ',   u'ho' ),
  
  ( 'ma', u'マ',   u'ま',   u'ma' ),
  ( 'mi', u'ミ',   u'み',   u'mi' ),
  ( 'mu', u'ム',   u'む',   u'mu' ),
  ( 'me', u'メ',   u'め',   u'me' ),
  ( 'mo', u'モ',   u'も',   u'mo' ),
  
  ( 'ya', u'ヤ',   u'や',   u'ya' ),
  ( 'yi', u'ヰ',   u'ゐ',   u'yi' ),
  ( 'yu', u'ユ',   u'ゆ',   u'yu' ),
  ( 'ye', u'ヱ',   u'ゑ',   u'ye' ),
  ( 'yo', u'ヨ',   u'よ',   u'yo' ),
  
  ( 'ra', u'ラ',   u'ら',   u'ra' ),
  ( 'ri', u'リ',   u'り',   u'ri' ),
  ( 'ru', u'ル',   u'る',   u'ru' ),
  ( 're', u'レ',   u'れ',   u're' ),
  ( 'ro', u'ロ',   u'ろ',   u'ro' ),
  
  ( 'wa', u'ワ',   u'わ',   u'wa' ),
  ( 'wo', u'ヲ',   u'を',   u'wo' ),
  ( 'n',  u'ン',   u'ん',   u'n' ),

  # voiced (Dakuon)
  ( 'ga', u'ガ',   u'が',   u'ga' ),
  ( 'gi', u'ギ',   u'ぎ',   u'gi' ),
  ( 'gu', u'グ',   u'ぐ',   u'gu' ),
  ( 'ge', u'ゲ',   u'げ',   u'ge' ),
  ( 'go', u'ゴ',   u'ご',   u'go' ),
                  
  ( 'za', u'ザ',   u'ざ',   u'za' ),
  ( 'zi', u'ジ',   u'じ', u'ぢ', u'zi', u'di', u'ji' ),
  ( 'zu', u'ズ',   u'ず', u'づ', u'zu', u'du' ),
  ( 'ze', u'ゼ',   u'ぜ',   u'ze' ),
  ( 'zo', u'ゾ',   u'ぞ',   u'zo' ),
                  
  ( 'da', u'ダ',   u'だ',   u'da' ),
  ( 'de', u'デ',   u'で',   u'de' ),
  ( 'do', u'ド',   u'ど',   u'do' ),
  
  ( 'ba', u'バ',   u'ば',   u'ba' ),
  ( 'bi', u'ビ',   u'び',   u'bi' ),
  ( 'bu', u'ブ',   u'ぶ',   u'bu' ),
  ( 'be', u'ベ',   u'べ',   u'be' ),
  ( 'bo', u'ボ',   u'ぼ',   u'bo' ),
  
  ( 'fa', u'ファ', u'ふぁ', u'fa' ),
  ( 'fi', u'フィ', u'ふぃ', u'fi' ),
  ( 'fe', u'フェ', u'ふぇ', u'fe' ),
  ( 'fo', u'フォ', u'ふぉ', u'fo' ),
  
  ( 'va', u'ヴァ', u'う゛ぁ', u'va' ),
  ( 'vi', u'ヴィ', u'う゛ぃ', u'vi' ),
  ( 'vu', u'ヴ',   u'う゛',   u'vu' ),
  ( 've', u'ヴェ', u'う゛ぇ', u've' ),
  ( 'vo', u'ヴォ', u'う゛ぉ', u'vo' ),
  
  # p- sound (Handakuon)
  ( 'pa', u'パ',   u'ぱ',   u'pa' ),
  ( 'pi', u'ピ',   u'ぴ',   u'pi' ),
  ( 'pu', u'プ',   u'ぷ',   u'pu' ),
  ( 'pe', u'ペ',   u'ぺ',   u'pe' ),
  ( 'po', u'ポ',   u'ぽ',   u'po' ),

  # double consonants (Youon)
  ( 'kya', u'キャ', u'きゃ', u'kya' ),
  ( 'kyu', u'キュ', u'きゅ', u'kyu' ),
  ( 'kye', u'キェ', u'きぇ', u'kye' ),
  ( 'kyo', u'キョ', u'きょ', u'kyo' ),

  ( 'sya', u'シャ', u'しゃ', u'sha', u'sya' ),
  ( 'syu', u'シュ', u'しゅ', u'shu', u'syu' ),
  ( 'sye', u'シェ', u'しぇ', u'she', u'sye' ),
  ( 'syo', u'ショ', u'しょ', u'sho', u'syo' ),
  
  ( 'cya', u'チャ', u'ちゃ', u'tya', u'cha' ),
  ( 'cyu', u'チュ', u'ちゅ', u'tyu', u'chu' ),
  ( 'cye', u'チェ', u'ちぇ', u'tye', u'che' ),
  ( 'cyo', u'チョ', u'ちょ', u'tyo', u'cho' ),
  
  ( 'nya', u'ニャ', u'にゃ', u'nya' ),
  ( 'nyu', u'ニュ', u'にゅ', u'nyu' ),
  ( 'nye', u'ニェ', u'にぇ', u'nye' ),
  ( 'nyo', u'ニョ', u'にょ', u'nyo' ),
  
  ( 'hya', u'ヒャ', u'ひゃ', u'hya' ),
  ( 'hyu', u'ヒュ', u'ひゅ', u'hyu' ),
  ( 'hye', u'ヒェ', u'ひぇ', u'hye' ),
  ( 'hyo', u'ヒョ', u'ひょ', u'hyo' ),
  
  ( 'mya', u'ミャ', u'みゃ', u'mya' ),
  ( 'myu', u'ミュ', u'みゅ', u'myu' ),
  ( 'mye', u'ミェ', u'みぇ', u'mye' ),
  ( 'myo', u'ミョ', u'みょ', u'myo' ),
  
  ( 'rya', u'リャ', u'りゃ', u'rya', ),
  ( 'ryu', u'リュ', u'りゅ', u'ryu', ),
  ( 'rye', u'リェ', u'りぇ', u'rye', ),
  ( 'ryo', u'リョ', u'りょ', u'ryo', ),
  
  # double consonants + voiced
  ( 'gya', u'ギャ', u'ぎゃ', u'gya' ),
  ( 'gyu', u'ギュ', u'ぎゅ', u'gyu' ),
  ( 'gye', u'ギェ', u'ぎぇ', u'gye' ),
  ( 'gyo', u'ギョ', u'ぎょ', u'gyo' ),
  
  ( 'jya', u'ジャ', u'ヂャ', u'じゃ', u'ぢゃ', u'ja', u'zha', u'zya', u'dya' ),
  ( 'jyu', u'ジュ', u'ヂュ', u'じゅ', u'ぢゅ', u'ju', u'zhu', u'zyu', u'dyu' ),
  ( 'jye', u'ジェ', u'ヂェ', u'じぇ', u'ぢぇ', u'je', u'zhe', u'zye', u'dye' ),
  ( 'jyo', u'ジョ', u'ヂョ', u'じょ', u'ぢょ', u'jo', u'zho', u'zyo', u'dyo' ),
  
  ( 'bya', u'ビャ', u'びゃ', u'bya' ),
  ( 'byu', u'ビュ', u'びゅ', u'byu' ),
  ( 'bye', u'ビェ', u'びぇ', u'bye' ),
  ( 'byo', u'ビョ', u'びょ', u'byo' ),
  
  # double consonants + p-sound
  ( 'pya', u'ピャ', u'ぴゃ', u'pya' ),
  ( 'pyu', u'ピュ', u'ぴゅ', u'pyu' ),
  ( 'pye', u'ピェ', u'ぴぇ', u'pye' ),
  ( 'pyo', u'ピョ', u'ぴょ', u'pyo' ),

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
