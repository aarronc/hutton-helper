"""
Various display widgets.
"""

import tkFont
import Tkinter as tk
import ttk


DONT_PANIC = "DON'T PANIC!"
TK_DEFAULT_FONT = 'TkDefaultFont'


def large_friendly_letters(font=None):
    "Make a ``font`` definition more friendly."

    if font is None:
        font = TK_DEFAULT_FONT

    if isinstance(font, str):
        size = tkFont.nametofont(font).cget('size')
        return (font, size * 2, tkFont.BOLD)

    elif isinstance(font, tkFont.Font):
        font = font.copy()
        font.configure(size=font.cget('size') * 2, weight=tkFont.BOLD)
        return font

    else:
        return font  # punt


class FrontCover(ttk.Label):
    """
    A big, friendly label.
    """

    def __init__(self, frame, text=DONT_PANIC):
        "Initialise the ``FrontCover``."

        ttk.Label.__init__(self, frame, text=text, anchor=tk.CENTER, font=large_friendly_letters())

    def configure(self, **kwargs):
        "Reconfigure the ``FrontCover``. Called by EDMC when applying the theme."

        font = kwargs.get('font')
        if font is not None:
            kwargs['font'] = large_friendly_letters(font)

        ttk.Label.configure(self, **kwargs)


class StyleCaptureLabel(ttk.Label):
    """
    A label that captures style information when EDMC applies its theme.

    USE ONLY ONCE.
    """

    def __init__(self, *args, **kwargs):
        "Initialise the ``StyleCaptureLabel``."

        ttk.Label.__init__(self, *args, **kwargs)
        self.__style = ttk.Style()  # acts like a singleton

    def configure(self, *args, **kwargs):
        "Reconfigure the ``StyleCaptureLabel``. Capture the details."

        ttk.Label.configure(self, *args, **kwargs)
        self.__style.configure('HH.TCheckbutton', **kwargs)
