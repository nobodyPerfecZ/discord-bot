from enum import IntEnum


class MusicState(IntEnum):
    """
    This class represents different states of an audio player.

    Attributes:
        DISCONNECT (int):
            The audio player is disconnected from the voice channel
        
        CONNECT (int):
            The audio player is connected to the voice channel (and does not play/pause any audio stream)
        
        PLAY (int):
            The audioplayer is playing an audio stream
        
        PAUSE (int):
            The audio player is pausing an audio stream
    """
    DISCONNECT = 1
    CONNECT = 2
    PLAY = 3
    PAUSE = 4
