# pylint: disable=invalid-name
"""Test details of the Guacamole protocol parser."""

from typing import overload, Iterable

from hypothesis import given, strategies as st

from .syntax import (
    parse_one_message,
    format_message,
    IncrementalGuacamoleParser,
    IncrementalBinaryGuacamoleParser,
)


@st.composite
def messages(draw) -> tuple[str, ...]:
    """Generate random messages."""
    opcode = draw(st.text())
    args = draw(st.lists(st.text()))
    return (opcode, *args)


@overload
def _make_chunks(source: str, division_points: list[int]) -> list[str]:
    ...


@overload
def _make_chunks(source: bytes, division_points: list[int]) -> list[bytes]:
    ...


def _make_chunks(source, division_points: list[int]):
    """
    Split the input into chunks at the given division points

    >>> _make_chunks("abc", [])
    ['abc']
    >>> _make_chunks("abc", [0])
    ['', 'abc']
    >>> _make_chunks("abc", [1])
    ['a', 'bc']
    >>> _make_chunks("abc", [3])
    ['abc', '']
    >>> _make_chunks("abc", [0,1,2,3])
    ['', 'a', 'b', 'c', '']
    """
    chunks = []
    start = 0
    for p in division_points:
        chunks.append(source[start:p])
        start = p
    chunks.append(source[start : len(source)])
    return chunks


@st.composite
def string_chunks(draw, source: str) -> list[str]:
    """Divide the source string into multiple chunks."""
    division_points = draw(
        st.lists(st.integers(min_value=0, max_value=len(source)))
    )
    return _make_chunks(source, sorted(division_points))


@st.composite
def bytes_chunks(draw, source: bytes) -> list[bytes]:
    """Divide the source bytes into multiple chunks."""
    division_points = draw(
        st.lists(st.integers(min_value=0, max_value=len(source)))
    )
    return _make_chunks(source, sorted(division_points))


@given(st.data(), st.text())
def test_string_chunks_are_valid_partitions(data, source: str):
    """
    When joined, the chunks should produce the original string again.
    """
    chunks = data.draw(string_chunks(source))
    assert "".join(chunks) == source


@given(messages())
def test_can_parse_all_message(msg: tuple[str, ...]):
    """
    No matter how complex the input, the parser should be able to deal with it.
    """
    assert parse_one_message(format_message(*msg)) == msg


@overload
def _drive_incremental_parser(
    p: IncrementalGuacamoleParser, chunks: list[str]
) -> Iterable[tuple[str, ...]]:
    ...


@overload
def _drive_incremental_parser(
    p: IncrementalBinaryGuacamoleParser, chunks: list[bytes]
) -> Iterable[tuple[str, ...]]:
    ...


def _drive_incremental_parser(p, chunks: list) -> Iterable[tuple]:
    for chunk in chunks:
        p.feed(chunk)
        if (m := p.next_message()) is not None:
            yield m

    while (m := p.next_message()) is not None:
        yield m

    assert p.next_message(final=True) is None


@given(st.data(), st.lists(messages()))
def test_can_drive_incremental_parser(data, msgs: list[tuple[str, ...]]):
    """
    The incremental parser can handle chunked input.
    """
    formatted_msgs = "".join(format_message(*msg) for msg in msgs)
    chunks = data.draw(string_chunks(formatted_msgs))

    retrieved_msgs = list(
        _drive_incremental_parser(IncrementalGuacamoleParser(), chunks)
    )

    assert msgs == retrieved_msgs


@given(st.data(), st.lists(messages()))
def test_can_drive_incremental_binary_parser(data, msgs: list[tuple[str, ...]]):
    """
    The incremental parser can handle chunked input.
    """
    formatted_msgs = "".join(format_message(*msg) for msg in msgs).encode(
        "utf-8"
    )
    chunks = data.draw(bytes_chunks(formatted_msgs))

    retrieved_msgs = list(
        _drive_incremental_parser(IncrementalBinaryGuacamoleParser(), chunks)
    )

    assert msgs == retrieved_msgs
