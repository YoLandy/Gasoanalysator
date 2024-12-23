from enum import Enum

class GIAnswerStatus(Enum):
    """
    This enum is for gasoanalysator answer status
    """

    ok = 0x00
    hard_error = 0x01
    later_command = 0x02
    in_progress = 0x03
    unknown_command = 0x04
    invalid_format = 0x05
    invalid_chksm = 0x06
    setting_hard = 0x07
    passive_state = 0x08
    cant_done = 0x09
    unknown_error = 0x0A


class GICommands(Enum):
    """
    This enum is for gasoanalysator commands
    """

    set_zero = b"\x8A\x01\x01\x44\x85\x4b"
    set_active = b"\x8A\x01\x01\x04\x85\x0B"
    get_data = b"\x8A\x01\x01\x43\x85\x4C"
    get_status = b"\x8A\x01\x01\x01\x85\x0E"

class GIStatus(Enum):
    """
    This enum is for gasoanalysator status
    """

    ok = 0x00
    started_zero = 0x01
    in_progress = 0x02
    done_zeroing = 0x03


class GIApiStatus(Enum):
    """
    API

    {
        'code' : GIApiStatus.data
        'content': ....
    }
    """

    data = 1
    status = 2
    error = 3