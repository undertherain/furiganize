# -*- coding: utf-8 -*-
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# Automatic reading generation with kakasi and mecab.
# Written by Aleksandr Drozd, used some code from Anki Japanese support addon

import logging
import os
import re
import subprocess
import sys

enc = "utf-8"
isWin = False
isMac = False
logger = logging.getLogger(__name__)

# Enumeration values for the adjustment of ruby text.
LEFT = 0
CENTER = 1
RIGHT = 2
BLOCK = 3
INDENT_BLOCK = 4

srcFields = ["Expression"]
dstFields = ["Reading"]

kakasiArgsMultiple = ["-isjis", "-osjis", "-u", "-JH", "-KH", "-p"]
# kakasiArgs = ["-isjis", "-osjis", "-u", "-JH", "-KH","-s","-f"]
kakasiArgs = ["-isjis", "-osjis", "-u", "-JH", "-KH"]
mecabArgs = ["--node-format=%m[%f[7]] ", "--eos-format=\n", "--unk-format=%m[] "]


class Token:

    def __init__(self, _kanji, _reading):
        self.kanji = _kanji
        self.reading = _reading


# gCursor;


def Furiganize(dummy=""):
    """
    Macro for Writer.
    Adds furigana to kanji
    """
    doc = XSCRIPTCONTEXT.getDocument()
    xController = doc.getCurrentController()

    # current selection
    xIndexAccess = xController.getSelection()
    # number of selected pieces of text
    count = xIndexAccess.getCount()
    if count == 1 and len(xIndexAccess.getByIndex(0).getString()) == 0:
        return None
        # No selection. Process the word with the caret within it.
        # xTextRange = xIndexAccess.getByIndex(0)
        # xWordCursor = xTextRange.getText().createTextCursorByRange(xTextRange)
        # if not xWordCursor.isStartOfWord(): xWordCursor.gotoStartOfWord(False)
        # xWordCursor.gotoEndOfWord(True)
        # original=xWordCursor.getString()
        # xWordCursor.setString("aaa"+original+"bbbwr")
        # for token in processSentence(original):
        #    xWordCursor.setString(token.kanji)
        #    if token.reading is not None:
        #        xWordCursor.setPropertyValue("RubyText", token.reading)
        #    xWordCursor.goRight(len(token.kanji),False)

    else:
        # Selection occurred. Now process all the selected pieces of text.
        i = 0
        #        while i < count:
        # selected piece of text
        xTextRange = xIndexAccess.getByIndex(i)
        xText = xTextRange.getText()
        xWordCursor = xText.createTextCursorByRange(xTextRange)
        original = xTextRange.getString()
        xWordCursor.setString("")
        for token in processSentence(original):
            xWordCursor.setString(token.kanji)
            if token.reading is not None:
                xWordCursor.setPropertyValue("RubyText", token.reading)
                xWordCursor.setPropertyValue("RubyAdjust", CENTER)
            xWordCursor.goRight(len(token.kanji), False)
    return None


def escapeText(text):
    # strip characters that trip up kakasi/mecab
    text = text.replace("\n", " ")
    text = text.replace("\uff5e", "~")
    text = re.sub("<br( /)?>", "---newline---", text)
    # text = stripHTML(text)
    text = text.replace("---newline---", "<br>")
    return text


if sys.platform == "win32":
    si = subprocess.STARTUPINFO()
    try:
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    except:
        si.dwFlags |= subprocess._subprocess.STARTF_USESHOWWINDOW
else:
    si = None

# Mecab
##########################################################################


def mungeForPlatform(popen):
    if isWin:
        popen = [os.path.normpath(x) for x in popen]
        popen[0] += ".exe"
    elif not isMac:
        popen[0] += ".lin"
    return popen


class MecabController(object):

    def __init__(self):
        self.mecab = None

    def setup(self):
        #        base = "./support/"
        # elf.mecabCmd = mungeForPlatform( [base + "mecab"] + mecabArgs + ['-d', base, '-r', base + "mecabrc"])
        #        print self.mecabCmd
        #        self.mecabCmd=['./support/mecab.lin', '--node-format=%m[%f[7]] ', '--eos-format=\n', '--unk-format=%m[] ', '-d', './support/', '-r', './support/mecabrc']
        #        self.mecabCmd=['mecab', '--node-format=%m[%f[7]] ', '--eos-format=\n', '--unk-format=%m[] ']
        self.mecabCmd = ["mecab"] + mecabArgs
        # os.environ['DYLD_LIBRARY_PATH'] = base
        # os.environ['LD_LIBRARY_PATH'] = base
        # if not isWin:
        # os.chmod(self.mecabCmd[0], 0755)

    def ensureOpen(self):
        if not self.mecab:
            self.setup()
            try:
                self.mecab = subprocess.Popen(
                    self.mecabCmd,
                    bufsize=-1,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    startupinfo=si,
                )
            except OSError:
                raise Exception("Please install mecab")

    def GetReadingRaw(self, expr):
        self.ensureOpen()
        expr = escapeText(expr)
        self.mecab.stdin.write(expr.encode("euc-jp", "ignore") + b"\n")
        self.mecab.stdin.flush()
        expr = str(self.mecab.stdout.readline(), "euc-jp").rstrip("\r\n")
        return expr


# Kakasi
##########################################################################


class KakasiController(object):

    def __init__(self):
        self.kakasi = None

    def setup(self):
        base = "./support/"
        self.kakasiCmd = mungeForPlatform([base + "kakasi"] + kakasiArgs)
        self.kakasiCmd = ["kakasi"] + kakasiArgs
        # os.environ['ITAIJIDICT'] = base + "itaijidict"
        # os.environ['KANWADICT'] = base + "kanwadict"
        # if not isWin:
        #   os.chmod(self.kakasiCmd[0], 0755)

    def ensureOpen(self):
        if not self.kakasi:
            self.setup()
            try:
                self.kakasi = subprocess.Popen(
                    self.kakasiCmd,
                    bufsize=-1,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    startupinfo=si,
                )
            except OSError:
                raise Exception("Please install kakasi")

    def reading(self, expr):
        try:
            self.ensureOpen()
            expr = escapeText(expr)
            self.kakasi.stdin.write(expr.encode("sjis", "ignore") + b"\n")
            self.kakasi.stdin.flush()
            res = str(self.kakasi.stdout.readline(), "sjis").rstrip("\r\n")
            return res
        except:
            print("something went wrong:")
            print(self.kakasi.stdout.readline())


class KakasiControllerMultiple(object):

    def __init__(self):
        self.kakasi = None

    def setup(self):
        self.kakasiCmd = ["kakasi"] + kakasiArgsMultiple

    def ensureOpen(self):
        if not self.kakasi:
            self.setup()
            try:
                self.kakasi = subprocess.Popen(
                    self.kakasiCmd,
                    bufsize=-1,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    startupinfo=si,
                )
            except OSError:
                raise Exception("Please install kakasi")

    def reading(self, expr):
        self.ensureOpen()
        expr = escapeText(expr)
        self.kakasi.stdin.write(expr.encode("sjis", "ignore") + b"\n")
        self.kakasi.stdin.flush()
        res = str(self.kakasi.stdout.readline(), "sjis").rstrip("\r\n")
        return res


# Init
##########################################################################

kakasi = KakasiController()
kakasi_multiple = KakasiControllerMultiple()
mecab = MecabController()


def SplitKanji(token):
    # kanji=node[0]
    # reading=node[1]
    if len(token.kanji) == 1:
        return [token]
    result = []
    if len(token.kanji) == len(token.reading):
        for i in range(len(token.kanji)):
            result.append(Token(token.kanji[i], token.reading[i]))
        return result
    readings = kakasi_multiple.reading(token.kanji[0])
    if readings[0] == "{":
        readings = readings[1:-1]
    readings = readings.split("|")
    for reading in readings:
        if token.reading[: len(reading)] == reading:
            result.append(Token(token.kanji[0], reading))
            token.kanji = token.kanji[1:]
            token.reading = token.reading[len(reading) :]
            result = result + SplitKanji(token)
            return result
    return [token]


def processSentence(expr):
    phrases = expr.split(" ")
    result = []
    for phrase in phrases:
        result = result + ProcessPhrase(phrase)
        result.append(Token(" ", None))
    return result[:-1]


def ProcessPhrase(expr):
    original = expr
    expr = mecab.GetReadingRaw(expr)
    out = []
    print("mecab returned:", expr)
    for node in expr.split(" "):
        if not node:
            break
        logger.debug(f"parsing node: {node}")
        (kanji, reading) = re.match(r"(.+)\[(.*)\]", node).groups()
        # hiragana, punctuation, not japanese, or lacking a reading
        if kanji == reading or not reading:
            out.append(Token(kanji, None))
            continue
        reading = kakasi.reading(reading)
        # katakana
        if kanji == reading:
            out.append(Token(kanji, None))
            continue
        # convert to hiragana
        # ended up the same
        if reading == kanji:
            out.append(Token(kanji, None))
            continue
        # don't add readings of numbers
        if kanji in "一二三四五六七八九十０１２３４５６７８９":
            out.append(Token(kanji, None))
            continue
        # strip matching characters and beginning and end of reading and kanji
        # reading should always be at least as long as the kanji
        pref = ""
        post = ""
        while len(kanji) > 0 and kanji[0] == reading[0]:
            pref = pref + kanji[0]
            kanji = kanji[1:]
            reading = reading[1:]

        while len(kanji) > 0 and kanji[-1] == reading[-1]:
            post = pref + kanji[-1]
            kanji = kanji[:-1]
            reading = reading[:-1]
        out.append(Token(pref, None))
        out = out + SplitKanji(Token(kanji, reading))
        out.append(Token(post, None))
        continue
    return out


# Tests
##########################################################################

if __name__ == "__main__":
    samples = []
    samples.append("手紙")
    samples.append("手紙.")
    samples.append("手紙。")
    samples.append("カリン、 千葉 千葉 千 彼二千三百六十円も使った。回転寿司.")
    samples.append("私は学生です。")
    samples.append("水田がある.水をのむ.")
    for expr in samples:
        print("-------------------")
        print("parsing expression:", expr)
        print("kakasi returned:", kakasi.reading(expr))
        fin = ""
        tokens = processSentence(expr)
        for token in tokens:
            fin = fin + token.kanji
            if token.reading is not None:
                fin = fin + "[" + token.reading + "]"
        print(fin)

g_exportedScripts = (Furiganize,)
