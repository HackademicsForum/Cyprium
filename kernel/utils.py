########################################################################
#                                                                      #
#   Cyprium is a multifunction cryptographic, steganographic and       #
#   cryptanalysis tool developped by members of The Hackademy.         #
#   French White Hat Hackers Community!                                #
#   cyprium.hackademics.fr                                             #                                                  #
#   Authors: SAKAROV, mont29, afranck64                                #
#   Contact: admin@hackademics.fr                                      #
#   Forum: hackademics.fr                                              #
#   Twitter: @hackademics_                                             #
#                                                                      #
#   Cyprium is free software: you can redistribute it and/or modify    #
#   it under the terms of the GNU General Public License as published  #
#   by the Free Software Foundation, either version 3 of the License,  #
#   or any later version.                                              #
#                                                                      #
#   This program is distributed in the hope that it will be useful,    #
#   but without any warranty; without even the implied warranty of     #
#   merchantability or fitness for a particular purpose. See the       #
#   GNU General Public License for more details.                       #
#                                                                      #
#   The terms of the GNU General Public License is detailed in the     #
#   COPYING attached file. If not, see : http://www.gnu.org/licenses   #
#                                                                      #
########################################################################


import sys
import itertools
import time
import string


###############################################################################
# Flags.
###############################################################################
DEBUG = True


###############################################################################
# Misc platform abstraction code.
###############################################################################
__pf__ = sys.platform
if __pf__ == "win32":
    if sys.getwindowsversion().platform == 2:
        winpf = " (NT/2000/XP/Vista/7)"
    else:
        winpf = ""
    __pf__ = "Windows" + winpf
elif __pf__ == "cygwin":
    __pf__ = "Windows/Cygwin"
elif __pf__ == "linux2":
    __pf__ = "Linux"
elif __pf__ == "os2":
    __pf__ = "OS/2"
elif __pf__ == "os2emx":
    __pf__ = "OS/2 EMX"
elif __pf__ == "darwin":
    __pf__ = "Mac OS X"
else:
    __pf__ = "?"

major, minor, micro, _, _ = sys.version_info
__pytver__ = "{}.{}.{}".format(major, minor, micro)


###############################################################################
# Misc utils.
###############################################################################
def revert_dict(d, exceptions={}):
    """
    Revert a mapping (dict).
    If several keys have the same values, use the optional exceptions dict
    to give the result you want for those values-as-key.
    """
    return {v: exceptions.get(v, k) for k, v in d.items()}


# XXX this does not work nice!
def msgerr():
    """Returns a clear error message: error name + error message."""
    return " ".join((sys.exc_info()[0].__name__, str(sys.exc_info()[1])))


def int8_to_bytes(int8):
    """
    Return a bytes string made from the given sequence of [0..255] integers.
    """
    # XXX Why in hell python does not feature such conversion???
    # XXX Just ignores ints out of bounds.
    hex_s = "".join(("{:0>2x}".format(i) for i in int8 if 0 <= i <= 255))
    return bytes.fromhex(hex_s)


def printf(*args, **kwargs):
    """
    A print() that always flushes!
    """
    print(*args, **kwargs)
    if "file" in kwargs:
        kwargs["file"].flush()
    else:
        sys.stdout.flush()


###############################################################################
# Bases ops.
###############################################################################
def num_to_base(num, base, min_digits=1):
    """
    Returns a string with the integer num encoded in base.
    base is a list or tuple containing all "digits" (the first being '0' one).
    If the encoded number is shorter than min_digits, base[0] is used as left
    fill value.
    """
    b = len(base)
    out = []
    # Standard "decimal to base n" algo...
    # Note that that algo generates digits in "reversed" order...
    while num != 0:
        r = num % b
        num //= b
        out.append(str(base[r]))
    if len(out) < min_digits:
        out += [str(base[0])] * (min_digits - len(out))
    return "".join(reversed(out))


BASE_DIGITS_ALLOWED = tuple((string.digits + string.ascii_lowercase))


def base_autodetect(text, n_digits, allowed_bases=(16, 10, 8, 2)):
    """
    Try to auto-detect base of cyphered text...
    It determines the most probable base, that's all!
    n_digits is a mapping of the number of digits per number, for each base
    (e.g. typically 8, 16, 32, etc. for binary).
    Note: bases must from higher to lower!
    """
    c_data = set(text)
    ln_txt = len(text)
    allowed_bases = list(allowed_bases) + [0]
    for idx, b in enumerate(allowed_bases):
        if b > 36:
            continue  # Max base (digits + ascii letters).
        if b == 0:
            break  # End of process (last 0 base is just used for code below).
        b_spe = set(BASE_DIGITS_ALLOWED[allowed_bases[idx + 1]:b])
        if b > 10:
            # Add uppercase version of "digits".
            b_spe |= {d.upper() for d in b_spe}
        if b_spe & c_data:
            if ln_txt % n_digits[b] == 0:
                return b  # Found a valid base.
            # If length does not match, try a upper base.
            for bb in allowed_bases[:idx]:
                if ln_txt % n_digits[bb] == 0:
                    return bb  # Found a valid base.
            # Else, return None!
            return None


def get_allowed_digits(base):
    """Return a set of all allowed digits for a given base."""
    if 0 >= base > 36:
        return None  # Invalid base.
    d_allowed = set(BASE_DIGITS_ALLOWED[:base])
    if base > 10:
        d_allowed |= {d.upper() for d in d_allowed}
    return d_allowed


###############################################################################
# Iterators/sets operations.
###############################################################################
def grouper(iterable, n, fillvalue=None):
    """
    Return an iterator of n-length chunks of iterable.

    >>> grouper('ABCDEFG', 3, 'x')
    ABC DEF Gxx
    """
    args = [iter(iterable)] * n
    return itertools.zip_longest(fillvalue=fillvalue, *args)


def grouper2(lst, n, gap=0):
    """
    Return an iterator of n-length chunks of iterable.

    >>> grouper2('ABCDEFG', 3, 1)
    ABC EFG

    Compared to grouper, it has no fillvalue (thus returning a truncated
    last element), and lst must be subscriptable (i.e. not an iterator).
    But you can get groups of n elements separated (spaced) by gap elements.
    Also, it is quicker than grouper, except for small n (tipically <10).

    Note: you can use negative gap (not below -n+1, though) to get "crossing"
    groups:
    >>> grouper('ABCDEFGHI', 5, -3)
    ABCDE CDEFG EFGHI
    """
    return (lst[i:i + n] for i in range(0, len(lst), n + gap))


def nwise(iterable, n=1):
    """s, n=2 -> (s0,s1), (s1,s2), (s2, s3), ..."""
    its = itertools.tee(iterable, n)
    for i, it in enumerate(its):
        for j in range(i):
            next(it, None)
    return zip(*its)


def cut_iter(iterable, *cuts):
    """
    Returns an iterator of iterable parts of
    len1=cuts[1], len2=cuts[2], etc.
    iterable must be subscriptable.
    """
    curr = 0
    for c in cuts:
        next = curr + c
        yield iterable[curr:next]
        curr = next


def _rec_all_groups_in_order(iterable, lengths=(1, 2)):
    """lengths is assumed sorted!"""
    # This will recursively cut iterable in all possible sets of chunks which
    # lengths are in the given values.
    # Might yield nothing, when no arrangements are possible!
    ln = len(iterable)
    for l in lengths:
        if l > ln:
            return
        base = [iterable[:l]]
        if l == ln:
            yield base
            return
        for els in _rec_all_groups_in_order(iterable[l:], lengths):
            # Void els, continue.
            if not els:
                continue
            # One element, and length does not match.
            if len(els) == 1 and len(els[0]) + l != ln:
                continue
            yield base + list(els)


def all_groups_in_order(iterable, lengths=(1, 2)):
    """
    abc, (1,2,3) -> a,b,c   ab,c   a,bc   abc
    abcd, (2, 3) -> ab,cd
    Note that, depending on the lengths given, it might yield nothing!
    """
    # Just be sure lengths are sorted and iterable is subscriptable!
    lengths = tuple(sorted(lengths))
    iterable = tuple(iterable)
    return _rec_all_groups_in_order(iterable, lengths)


def case_variants(txt):
    """
    Yield all case variants of given text.
    "all" --> all, All, aLl, alL, ALl, AlL, aLL, ALL
    """
    TXT = txt.swapcase()
    # Nice comprehension! :p
    return ("".join(v) for v in
                       itertools.product(*(tuple(set(c))
                                         for c in zip(txt, TXT))))


###############################################################################
# Formating.
###############################################################################
def format_multiwords(words, sep=' '):
    """
    Format words as multi-lines text output.
    Returns a list of lines.
    (this) (is,was,will be) (a) (test):
           is
    this   was   a test
         will be
    """
    # Check we have no void list of words...
    t_words = words
    for i, w in enumerate(t_words):
        if not w:
            if not isinstance(words, list):
                words = list(words)
            words[i] = ('-@$!$@-',)
    # Higher number of possibilities for a single word.
    if len(words) > 1:
        max_nr = len(max(*words, key=len))
    else:
        max_nr = len(max(words, key=len))
    if max_nr == 1:
        return [sep.join((w[0] for w in words))]
    # Get start/end line number for each word in words.
    els_nr = []
    for e in words:
        diff_e = max_nr - len(e)
        min_e = diff_e // 2
        max_e = max_nr - (diff_e - min_e) - 1
        els_nr.append((min_e, max_e))
    # Format line.
    fmt_line = sep.join(["{{: ^{}}}".format(len(max(els, key=len)))
                         for els in words])

    ret = []
    for i in range(max_nr):
        els = []
        for idx, e in enumerate(words):
            if els_nr[idx][0] <= i <= els_nr[idx][1]:
                els.append(e[i - els_nr[idx][0]])
            else:
                els.append('')
        ret.append(fmt_line.format(*els))
    return ret


###############################################################################
# Prime numbers.
###############################################################################
def all_primes(n):
    """Yield all prime numbers from 0 to n."""
    n = int(n)
    if n < 2:
        return
    # NOTE: This is Sieve of Eratosthenes, but only on odd numbers.
    #       It's a bit more complex to grasp, but takes half of memory,
    #       and tends to be somewhat quicker when reaching high numbers
    #       (1000000 and over).

    # Create a list for all odd numbers.
    # Note: theorically, 1 is not prime, but as we never test it...
    lst = [True] * ((n // 2) + [0, 1][n % 2])
    yield 2  # 2 is the first prime number, and only even one.
    # Use **0.5 instead of Math.sqrt().
    root = int(n ** 0.5) // 2
    root = root + [1, 0][root % 2]  # Get an odd root.
    for i in range(1, root + 1):
        if lst[i]:
            y = i * 2 + 1
            # Get rid of all odd multiples of i.
            lst[i::y] = [False] * (((n // y) + 1) // 2)
            yield y
    for i in range(root, n // 2):
        if lst[i]:
            yield i * 2 + 1


_primes_under_100 = {all_primes(100)}


def is_prime(n):
    """Return True if a number is prime and False otherwise."""
    if n <= 100:
        return n in _primes_under_100
    if n % 2 == 0 or n % 3 == 0:
        return False

    for f in range(5, int(n ** 0.5), 6):
        if n % f == 0 or n % (f + 2) == 0:
            return False
    return True


def prime_range(end, start=2):
    """
    Yield prime numbers from start to end.
    Note: Only better that all_primes when start is very high, and
          end - start is relatively low.
    """
    if end < 2 or end < start:
        return
    if end == 2:
        yield 2
    if start < 3:
        for p in all_primes(end):
            yield p

    start = start + [1, 0][start % 2]  # Get an odd start.
    for i in range(start, end + 1, 2):
        if is_prime(i):
            yield i


###############################################################################
# CHARS - STRINGS
###############################################################################
def char_shift(c, base, modulo, shift, reverse=False):
    """
    Shift char c.
    base, modulo and shift might be either an integer or a char.
    """
    if isinstance(base, str) and len(base) == 1:
        base = ord(base)
    if isinstance(modulo, str) and len(modulo) == 1:
        modulo = ord(modulo) - base
    if isinstance(shift, str) and len(shift) == 1:
        shift = ord(shift) - base
    if reverse:
        return chr(((ord(c) - base - shift) % modulo) + base)
    return chr(((ord(c) - base + shift) % modulo) + base)


###############################################################################
# CHARSETS - CHARMAPS
###############################################################################
# Common charsets…
UTF8 = "utf-8"
ASCII = "ascii"
ASCII7 = "ascii7"
EBCDIC = "cp500"

DEFAULT = UTF8

# All standard codecs known by python (without there aliases)...
ALL_CODECS = (
    "ascii", "big5", "big5hkscs", "cp037", "cp424", "cp437", "cp500", "cp720",
    "cp737", "cp775", "cp850", "cp852", "cp855", "cp856", "cp857", "cp858",
    "cp860", "cp861", "cp862", "cp863", "cp864", "cp865", "cp866", "cp869",
    "cp874", "cp875", "cp932", "cp949", "cp950", "cp1006", "cp1026", "cp1140",
    "cp1250", "cp1251", "cp1252", "cp1253", "cp1254", "cp1255", "cp1256",
    "cp1257", "cp1258", "euc_jp", "euc_jis_2004", "euc_jisx0213", "euc_kr",
    "gb2312", "gbk", "gb18030", "hz", "iso2022_jp", "iso2022_jp_1",
    "iso2022_jp_2", "iso2022_jp_2004", "iso2022_jp_3", "iso2022_jp_ext",
    "iso2022_kr", "latin_1", "iso8859_2", "iso8859_3", "iso8859_4",
    "iso8859_5", "iso8859_6", "iso8859_7", "iso8859_8", "iso8859_9",
    "iso8859_10", "iso8859_13", "iso8859_14", "iso8859_15", "iso8859_16",
    "johab", "koi8_r", "koi8_u", "mac_cyrillic", "mac_greek", "mac_iceland",
    "mac_latin2", "mac_roman", "mac_turkish", "ptcp154", "shift_jis",
    "shift_jis_2004", "shift_jisx0213", "utf_32", "utf_32_be", "utf_32_le",
    "utf_16", "utf_16_be", "utf_16_le", "utf_7", "utf_8", "utf_8_sig"
)


# Western European to upper ASCII.
WE2UASCII_CHARSET = set("ABCDEFGHIJKLMNOPQRSTUVWXYZÆŒÀÁÂÄÇÉÈÊËÙÎÏÑÔÛÜß")

WE2UASCII_CHARMAP = {
    "Æ": "AE", "Œ": "OE", "À": "A", "É": "E", "È": "E", "Ù": "U",
    "Ê": "E", "Â": "A", "Î": "I", "Ô": "O", "Û": "U", "Ë": "E",
    "Ï": "I", "Ü": "U", "Ç": "C", "Ñ": "N", "ß": "SS", "Ú": "U",
    "Á": "A", "Ü": "U", "Ä": "A", "Ö": "O", "Ó": "O"}

WE2UASCII_CHARMAP.update({k.lower(): v for k, v in WE2UASCII_CHARMAP.items()})

WE2UASCII_CHARMAP.update({k.lower(): k for k in WE2UASCII_CHARSET
                          if k not in WE2UASCII_CHARMAP})

WE2UASCII_CHARSET |= {c.lower() for c in WE2UASCII_CHARSET}

WE2UASCII_CHARSET.add(" ")
