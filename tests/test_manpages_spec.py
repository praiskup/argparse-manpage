"""Tests for parsing build_manpages spec strings."""

import os.path
import sys

import pytest

sys.path = [
    os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
] + sys.path

from build_manpages.build_manpages import parse_manpages_spec


def test_parse_manpages_spec_accepts_quoted_url():
    """Quoted URL values may contain colons."""
    data = parse_manpages_spec(
        'some-file.1:module=somefile:function=get_parser:'
        'url="https://example.com/docs"'
    )

    assert data["some-file.1"]["url"] == "https://example.com/docs"


def test_parse_manpages_spec_keeps_equals_in_value():
    """Quoted values preserve equals signs."""
    data = parse_manpages_spec(
        'some-file.1:module=somefile:function=get_parser:'
        'url="https://example.com/docs?x=1&y=2"'
    )

    assert data["some-file.1"]["url"] == "https://example.com/docs?x=1&y=2"


def test_parse_manpages_spec_rejects_unterminated_quote():
    """An unterminated quoted value is rejected."""
    with pytest.raises(ValueError, match="Invalid manpage configuration option"):
        parse_manpages_spec(
            'some-file.1:module=somefile:function=get_parser:'
            'url="https://example.com/docs'
        )
