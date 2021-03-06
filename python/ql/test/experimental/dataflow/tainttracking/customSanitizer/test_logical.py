import sys; import os; sys.path.append(os.path.dirname(os.path.dirname((__file__))))
from taintlib import *

# This has no runtime impact, but allows autocomplete to work
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..taintlib import *


# Actual tests

"""Testing logical constructs not/and/or works out of the box.
"""

import random


def random_choice():
    return bool(random.randint(0, 1))


def is_safe(arg):
    return arg == "safe"


def test_basic():
    s = TAINTED_STRING

    if is_safe(s):
        ensure_not_tainted(s)
    else:
        ensure_tainted(s)

    if not is_safe(s):
        ensure_tainted(s)
    else:
        ensure_not_tainted(s)


def test_or():
    s = TAINTED_STRING

    # x or y
    if is_safe(s) or random_choice():
        ensure_tainted(s) # might be tainted
    else:
        ensure_tainted(s) # must be tainted

    # not (x or y)
    if not(is_safe(s) or random_choice()):
        ensure_tainted(s) # must be tainted
    else:
        ensure_tainted(s) # might be tainted

    # not (x or y) == not x and not y   [de Morgan's laws]
    if not is_safe(s) and not random_choice():
        ensure_tainted(s) # must be tainted
    else:
        ensure_tainted(s) # might be tainted


def test_and():
    s = TAINTED_STRING

    # x and y
    if is_safe(s) and random_choice():
        ensure_not_tainted(s) # must not be tainted
    else:
        ensure_tainted(s) # might be tainted

    # not (x and y)
    if not(is_safe(s) and random_choice()):
        ensure_tainted(s) # might be tainted
    else:
        ensure_not_tainted(s)

    # not (x and y) == not x or not y   [de Morgan's laws]
    if not is_safe(s) or not random_choice():
        ensure_tainted(s) # might be tainted
    else:
        ensure_not_tainted(s)


def test_tricky():
    s = TAINTED_STRING

    x = is_safe(s)
    if x:
        ensure_not_tainted(s) # FP

    s_ = s
    if is_safe(s):
        ensure_not_tainted(s_) # FP


def test_nesting_not():
    s = TAINTED_STRING

    if not(not(is_safe(s))):
        ensure_not_tainted(s)
    else:
        ensure_tainted(s)

    if not(not(not(is_safe(s)))):
        ensure_tainted(s)
    else:
        ensure_not_tainted(s)


# Adding `and True` makes the sanitizer trigger when it would otherwise not. See output in
# SanitizedEdges.expected and compare with `test_nesting_not` and `test_basic`
def test_nesting_not_with_and_true():
    s = TAINTED_STRING

    if not(is_safe(s) and True):
        ensure_tainted(s)
    else:
        ensure_not_tainted(s)

    if not(not(is_safe(s) and True)):
        ensure_not_tainted(s)
    else:
        ensure_tainted(s)

    if not(not(not(is_safe(s) and True))):
        ensure_tainted(s)
    else:
        ensure_not_tainted(s)


def test_with_return():
    s = TAINTED_STRING

    if not is_safe(s):
        return

    ensure_not_tainted(s)


def test_with_exception():
    s = TAINTED_STRING

    if not is_safe(s):
        raise Exception("unsafe")

    ensure_not_tainted(s)

# Make tests runable

test_basic()
test_or()
test_and()
test_tricky()
test_nesting_not()
test_nesting_not_with_and_true()
test_with_return()
try:
    test_with_exception()
except:
    pass
