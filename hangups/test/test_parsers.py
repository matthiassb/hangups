"""Tests for long poll message parsing."""

import pytest

from hangups import parsers


@pytest.mark.parametrize('input_,expected', [
    # '€' is 3 bytes in UTF-8.
    ('€€'.encode()[:6], '€€'),
    ('€€'.encode()[:5], '€'),
    ('€€'.encode()[:4], '€'),
    ('€€'.encode()[:3], '€'),
    ('€€'.encode()[:2], ''),
    ('€€'.encode()[:1], ''),
    ('€€'.encode()[:0], ''),
])
def test_best_effort_decode(input_, expected):
    assert parsers._best_effort_decode(input_) == expected


def test_simple():
    p = parsers.PushDataParser()
    assert list(p.get_submissions('10\n01234567893\nabc'.encode())) == [
        '0123456789',
        'abc',
    ]


def test_truncated_message():
    p = parsers.PushDataParser()
    assert list(p.get_submissions('12\n012345678'.encode())) == []


def test_truncated_length():
    p = parsers.PushDataParser()
    assert list(p.get_submissions('13'.encode())) == []


def test_malformed_length():
    p = parsers.PushDataParser()
    # TODO: could detect errors like these with some extra work
    assert list(p.get_submissions('11\n0123456789\n5e\n"abc"'.encode())) == [
        '0123456789\n'
    ]


def test_incremental():
    p = parsers.PushDataParser()
    assert list(p.get_submissions(''.encode())) == []
    assert list(p.get_submissions('5'.encode())) == []
    assert list(p.get_submissions('\n'.encode())) == []
    assert list(p.get_submissions('abc'.encode())) == []
    assert list(p.get_submissions('de'.encode())) == ['abcde']
    assert list(p.get_submissions(''.encode())) == []


def test_unicode():
    p = parsers.PushDataParser()
    # smile is actually 2 code units
    assert list(p.get_submissions('3\na😀'.encode())) == ['a😀']


def test_split_characters():
    p = parsers.PushDataParser()
    assert list(p.get_submissions(b'1\n\xe2\x82')) == []
    assert list(p.get_submissions(b'\xac')) == ['€']
