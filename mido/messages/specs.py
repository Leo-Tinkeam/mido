# SPDX-FileCopyrightText: 2016 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

"""Definitions and lookup tables for MIDI messages.

TODO:

    * add lookup functions for messages definitions by type and status
      byte.
"""

from typing import Dict, List, Tuple, Union

# TODO: these include undefined messages.
CHANNEL_MESSAGES = set(range(0x80, 0xf0))
COMMON_MESSAGES = set(range(0xf0, 0xf8))
REALTIME_MESSAGES = set(range(0xf8, 0x100))

SYSEX_START = 0xf0
SYSEX_END = 0xf7

# Pitchwheel is a 14 bit signed integer
MIN_PITCHWHEEL = -8192
MAX_PITCHWHEEL = 8191

# Song pos is a 14 bit unsigned integer
MIN_SONGPOS = 0
MAX_SONGPOS = 16383

class Spec:
    def __init__(
        self, status_byte: int, type_: str, value_names: Tuple[str, ...], length: int
    ):
        self.status_byte = status_byte
        self.type = type_
        self.value_names = value_names
        self.attribute_names = set(value_names) | {'type', 'time'}
        self.length = length

SPECS = [
    Spec(0x80, 'note_off', ('channel', 'note', 'velocity'), 3),
    Spec(0x90, 'note_on', ('channel', 'note', 'velocity'), 3),
    Spec(0xa0, 'polytouch', ('channel', 'note', 'value'), 3),
    Spec(0xb0, 'control_change', ('channel', 'control', 'value'), 3),
    Spec(0xc0, 'program_change', ('channel', 'program',), 2),
    Spec(0xd0, 'aftertouch', ('channel', 'value',), 2),
    Spec(0xe0, 'pitchwheel', ('channel', 'pitch',), 3),

    # System common messages.
    # 0xf4 and 0xf5 are undefined.
    Spec(0xf0, 'sysex', ('data',), float('inf')),
    Spec(0xf1, 'quarter_frame', ('frame_type', 'frame_value'), 2),
    Spec(0xf2, 'songpos', ('pos',), 3),
    Spec(0xf3, 'song_select', ('song',), 2),
    Spec(0xf6, 'tune_request', (), 1),

    # System real time messages.
    # 0xf9 and 0xfd are undefined.
    Spec(0xf8, 'clock', (), 1),
    Spec(0xfa, 'start', (), 1),
    Spec(0xfb, 'continue', (), 1),
    Spec(0xfc, 'stop', (), 1),
    Spec(0xfe, 'active_sensing', (), 1),
    Spec(0xff, 'reset', (), 1),
]


def _make_spec_lookups(
    specs: List[Spec],
) -> Tuple[Dict[Union[int, str], Spec], Dict[int, Spec], Dict[str, Spec]]:
    lookup = {}
    by_status = {}
    by_type = {}

    for spec in specs:
        type_ = spec.type
        status_byte = spec.status_byte

        by_type[type_] = spec

        if status_byte in CHANNEL_MESSAGES:
            for channel in range(16):
                by_status[status_byte | channel] = spec
        else:
            by_status[status_byte] = spec

    lookup.update(by_status)
    lookup.update(by_type)

    return lookup, by_status, by_type


SPEC_LOOKUP, SPEC_BY_STATUS, SPEC_BY_TYPE = _make_spec_lookups(SPECS)

REALTIME_TYPES = {'tune_request', 'clock', 'start', 'continue', 'stop'}

DEFAULT_VALUES = {
    'channel': 0,
    'control': 0,
    'data': (),
    'frame_type': 0,
    'frame_value': 0,
    'note': 0,
    'pitch': 0,
    'pos': 0,
    'program': 0,
    'song': 0,
    'value': 0,
    'velocity': 64,

    'time': 0,
}


# TODO: should this be in decode.py?

def make_msgdict(type_, overrides):
    """Return a new message.

    Returns a dictionary representing a message.

    Message values can be overriden.

    No type or value checking is done.  The caller is responsible for
    calling check_msgdict().
    """
    if type_ in SPEC_BY_TYPE:
        spec = SPEC_BY_TYPE[type_]
    else:
        raise LookupError(f'Unknown message type {type_!r}')

    msg = {'type': type_, 'time': DEFAULT_VALUES['time']}

    for name in spec.value_names:
        msg[name] = DEFAULT_VALUES[name]

    msg.update(overrides)

    return msg
