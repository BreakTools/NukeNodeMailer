"""Audio handling code for Node Mailer. It's a really inefficient implementation because it adds
just a tiny amount of delay to everything, but that actually adds a lot of character to the plugin
so I'm not optimizing it lol.

Written by Mervin van Brakel, 2024.
"""

from pathlib import Path

from PySide2 import QtCore, QtMultimedia

from .models.constants import SettingStrings

playing_sound_effects = []


def play_click_sound() -> None:
    """Plays a click sound."""
    path_to_click_sound = Path(__file__).parent / "resources" / "click.wav"
    play_wav_file(path_to_click_sound, 0.4)


def play_error_sound() -> None:
    """Plays an error sound."""
    path_to_error_sound = Path(__file__).parent / "resources" / "error.wav"
    play_wav_file(path_to_error_sound, 1)


def play_you_got_mail() -> None:
    """Plays a 'You've got mail' sound."""
    path_to_mail_sound = Path(__file__).parent / "resources" / "you_got_mail.wav"
    play_wav_file(path_to_mail_sound, 1)


def play_wav_file(wav_file_path: Path, volume: float) -> None:
    """Plays a wav file using QSound.

    Args:
        wav_file_path: The path to the wav file.
        volume: The volume to play the sound at.
    """
    if not is_audio_enabled():
        return

    sound_effect = QtMultimedia.QSoundEffect()
    sound_effect.setSource(QtCore.QUrl.fromLocalFile(str(wav_file_path)))
    sound_effect.setVolume(volume)

    playing_sound_effects.append(sound_effect)
    sound_effect.playingChanged.connect(
        lambda: playing_sound_effects.clear() if not sound_effect.isPlaying() else None
    )

    sound_effect.play()


def is_audio_enabled() -> bool:
    """Checks the QSettings to see if Node Mailer audio is enabled.

    Returns:
        True if audio is enabled, False otherwise.
    """
    settings = QtCore.QSettings()
    return bool(int(settings.value(SettingStrings.AUDIO_ENABLED.value, 1)))
