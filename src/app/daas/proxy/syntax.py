# pylint: disable=missing-function-docstring
r"""
Provide parsers and formatters for Guacamole messages.

A Guacamole message consists of one or more arguments, terminated by semicolon:

```
message = arg ("," arg)* ";"
```

Each argument consists of the length in Unicode codepoints,
followed by a period,
followed by the contents:

```
arg = LEN "." CONTENTS
```

This makes messages easy to generate,
but contrary to the Guacamole protocol documentation it is not easy to parse.
For example, we can't just split at each comma
because arguments can contain those characters:

``` pycon
>>> parse_one_message("3.foo,4.a,;b;")
('foo', 'a,;b')

```

It also means binary input (UTF-8 encoded)
first has to be decoded into Unicode characters.

E.g. consider the U+2603 SNOWNMAN Unicode character that is UTF-8 encoded
as three bytes:

``` pycon
>>> parse_one_message(b'7.snowman,1.\xE2\x98\x83;'.decode('utf-8'))
('snowman', '☃')

```

To address these problems,
this module provides an `IncrementalGuacamoleParser`
that can consume input in possibly incomplete chunks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeAlias, Optional
from collections import deque
import codecs


MAXIMUM_ARG_LEN = 8 * 1024
"""
Limit the maximum argument length to a reasonable value.

This is a security-relevant parameter,
as it can prevent denial-of-service attacks.

8KB matches the limit used by the Guacamole proxy.
"""


def parse_one_message(raw: str) -> tuple[str, ...]:
    """Parse one Guacamole message."""
    parser = IncrementalGuacamoleParser()
    parser.feed(raw)
    msg = parser.next_message(final=True)
    assert msg is not None
    return msg


def format_message(opcode: str, *args: str) -> str:
    """
    Encode a Guacamole message into a string.

    ```pycon
    >>> format_message("foo", "42")
    '3.foo,2.42;'
    >>> format_message("", "!,")
    '0.,2.!,;'
    >>> format_message("snowman", "☃")
    '7.snowman,1.☃;'

    ```
    """
    return "".join(
        (
            f"{len(opcode)}.{opcode}",
            *(f",{len(arg)}.{arg}" for arg in args),
            ";",
        )
    )


def format_message_b(opcode: str, *args: str) -> bytes:
    """Encode a Guacamole message into bytes."""
    return format_message(opcode, *args).encode("utf-8")


class IncrementalGuacamoleParser:
    """
    An incremental parser for Guacamole instructions.

    This is useful when reading incomplete records from a TCP socket.

    ```pycon
    >>> p = IncrementalGuacamoleParser()
    >>> p.feed("2.f")
    >>> p.next_message() is None
    True
    >>> p.feed("o,3.bar")
    >>> p.next_message() is None
    True
    >>> p.feed(";1.x;2.xy,0")
    >>> p.next_message()
    ('fo', 'bar')
    >>> p.feed(".;")
    >>> p.next_message()
    ('x',)
    >>> p.next_message(final=True)
    ('xy', '')
    >>> p.next_message(final=True) is None
    True

    ```

    Internally, this class uses the State Object Pattern
    to drive the incremental parser.
    """

    def __init__(self) -> None:
        self._buf = _Buffer()
        self._state: _ParserState = _ParserStateWantLength(args=[])

    def feed(self, fragment: str) -> None:
        """Feed a fragment into the parser."""
        self._buf.push(fragment)

    def next_message(self, *, final: bool = False) -> Optional[tuple[str, ...]]:
        """
        Try to read the next message, if complete.

        In `final=True`, ensure that no unconsumed input remains.
        """
        result = self._next_message()

        if final:
            # potential problem: state not at the beginning of a new message
            match self._state:
                case _ParserStateWantLength(args=[]):
                    pass
                case _:
                    raise ValueError(
                        f"requested final message, but parser has partial progress: {self._state}"
                    )

            # potential problem: the buffer still has input
            if not self._buf.is_empty():
                raise ValueError(
                    "requested final message, but buffered input remains"
                )

        return result

    def _next_message(self) -> Optional[tuple[str, ...]]:
        # if we are already in done state, return that
        match self._state:
            case _ParserStateDone(args=args):
                self._state = _ParserStateWantLength(args=[])
                return tuple(args)

        # make as much progress as possibles
        while True:
            next_state = self._state.process(self._buf)

            if next_state is None:
                # no further progress is possible, but not done yet
                return None

            if isinstance(next_state, _ParserStateDone):
                # done
                self._state = _ParserStateWantLength(args=[])
                return tuple(next_state.args)

            # intermediate state, continue
            self._state = next_state


class IncrementalBinaryGuacamoleParser:
    r"""
    An IncrementalGuacamoleParser that handles binary fragments.

    The main difference is that this parser can handle fragments
    that consist of partial Unicode characters.

    For example with the Unicode SNOWMAN character:

    ```pycon
    >>> p = IncrementalBinaryGuacamoleParser()
    >>> p.feed(b'1.\xE2')
    >>> p.next_message() # is None
    >>> p.feed(b'\x98')
    >>> p.next_message() # is None
    >>> p.feed(b'\x83;')
    >>> p.next_message(final=True)
    ('☃',)

    ```
    """

    def __init__(self) -> None:
        self._inner = IncrementalGuacamoleParser()
        self._decoder: codecs.IncrementalDecoder = codecs.getincrementaldecoder(
            "utf-8"
        )()

    def _feed(self, fragment: bytes | bytearray, *, final: bool) -> None:
        string_fragment = self._decoder.decode(fragment, final=final)
        self._inner.feed(string_fragment)

    def feed(self, fragment: bytes | bytearray) -> None:
        """Feed a binary fragment."""
        self._feed(fragment, final=False)

    def next_message(self, *, final: bool = False) -> Optional[tuple[str, ...]]:
        """
        Obtain the next Guacamole message, if one has been completed.

        If `final=True`, this also ensures that no unconsumed input remains.
        """
        if final:
            self._feed(b"", final=True)
        return self._inner.next_message(final=final)


class _Buffer:
    """
    Buffer objects offer a roughly file-like view onto string fragments.

    ```pycon
    >>> b = _Buffer()
    >>> b.is_empty()
    True
    >>> b.push("foo")
    >>> b.push("bar")
    >>> b.is_empty()
    False
    >>> b.read(1)
    'f'
    >>> b.read(6)
    'oo'
    >>> b.read(6)
    'bar'
    >>> b.read(6)
    ''

    ```
    """

    def __init__(self, initial: str = "") -> None:
        self.__current: Optional[str] = initial if initial else None
        self.__queue: deque[str] = deque()
        self.__offset: int = 0

    def is_empty(self) -> bool:
        """Check if the buffer is empyt."""
        return self.__current is None and not self.__queue

    def push(self, fragment: str) -> None:
        """Add a fragment to the buffer to be read later."""
        if fragment:
            self.__queue.append(fragment)

    def read(self, maxlen: int) -> str:
        """Consume up to `maxlen` character from the buffer."""
        if self.__current is None:
            self.__offset = 0
            try:
                self.__current = self.__queue.popleft()
            except IndexError:
                return ""

        # for long reads, return the rest of the current string
        if self.__offset + maxlen >= len(self.__current):
            out, self.__current = self.__current, None
            return out[self.__offset :]

        # normally handle short reads that just advance the offset
        out = self.__current[self.__offset : (self.__offset + maxlen)]
        self.__offset += maxlen
        return out

    def __str__(self) -> str:
        """Concatenate all remaining contents."""
        parts = []
        if self.__current:
            parts.append(self.__current[self.__offset :])
        parts.extend(self.__queue)
        return "".join(parts)


@dataclass(kw_only=True, slots=True)
class _ParserStateWantLength:
    """
    Parser state at the beginning of an argument.

    To know how long the argument is,
    this consumes characters one at a time
    until a period `.` is encountered.

    Compare: https://github.com/apache/guacamole-client/blob/940c7ad37aefc06cb42c764a1deb6abab86f8290/guacamole-common/src/main/java/org/apache/guacamole/protocol/GuacamoleParser.java#L141-L166

    >>> _ParserStateWantLength(args=[...]).process(_Buffer("")) is None
    True
    >>> _ParserStateWantLength(args=[...]).process(_Buffer("5"))
    _ParserStateWantLength(args=[...], next_arg_len=5)
    >>> buf = _Buffer("54")
    >>> _ParserStateWantLength(args=[...]).process(buf).process(buf)
    _ParserStateWantLength(args=[...], next_arg_len=54)
    >>> _ParserStateWantLength(args=[...], next_arg_len=17).process(_Buffer(".foo"))
    _ParserStateWantValue(args=[...], expected_length=17, have_length=0, fragments=[])
    """

    args: list[str]

    next_arg_len: int = 0

    def process(self, buf: _Buffer) -> Optional[_ParserState]:
        digit = buf.read(1)

        if not digit:
            return None

        if digit == ".":
            if self.next_arg_len > MAXIMUM_ARG_LEN:
                raise ValueError(
                    f"instruction length exceeded {self.next_arg_len}/{MAXIMUM_ARG_LEN}"
                )
            return _ParserStateWantValue(
                expected_length=self.next_arg_len, args=self.args
            )

        if "0" <= digit <= "9":
            self.next_arg_len = 10 * self.next_arg_len + int(digit)
            return self

        raise ValueError(f"cannot have character {digit!r} in state WantLength")


@dataclass(kw_only=True, slots=True)
class _ParserStateWantValue:
    """
    Parse state when reading an argument value.

    The total length is already known at this point,
    but the contents might be split across multiple messages.

    >>> buf = _Buffer("a,;bcdef")
    >>> _ParserStateWantValue(args=[...], expected_length=5).process(buf), str(buf)
    (_ParserStateWantSep(args=[..., 'a,;bc']), 'def')

    >>> (_ParserStateWantValue(args=[...], expected_length=3)
    ...   .process(_Buffer("12"))
    ...   .process(_Buffer("34")))
    _ParserStateWantSep(args=[..., '123'])
    """

    args: list[str]

    expected_length: int
    have_length: int = 0
    fragments: list[str] = field(default_factory=list)

    def process(self, buf: _Buffer) -> Optional[_ParserState]:
        # check if already done
        remaining_length = self.expected_length - self.have_length
        if not remaining_length:
            self.args.append("".join(self.fragments))
            return _ParserStateWantSep(args=self.args)

        # try to make progress
        fragment = buf.read(remaining_length)
        if not fragment:
            return None

        self.have_length += len(fragment)
        self.fragments.append(fragment)

        # check again if done
        remaining_length = self.expected_length - self.have_length
        if not remaining_length:
            self.args.append("".join(self.fragments))
            return _ParserStateWantSep(args=self.args)

        # ok, made progress but stay in current state
        return self


@dataclass(kw_only=True, slots=True)
class _ParserStateWantSep:
    args: list[str]

    def process(self, buf: _Buffer) -> Optional[_ParserState]:
        match buf.read(1):
            case "":
                return None
            case ",":
                return _ParserStateWantLength(args=self.args)
            case ";":
                return _ParserStateDone(args=self.args)
            case other:
                raise ValueError(
                    f"cannot have character {other!r} in state WantSep"
                )


@dataclass(kw_only=True, slots=True)
class _ParserStateDone:
    args: list[str]


_ParserState: TypeAlias = (
    _ParserStateWantLength
    | _ParserStateWantValue
    | _ParserStateWantSep
    | _ParserStateDone
)
