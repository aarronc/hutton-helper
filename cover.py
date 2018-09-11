"""
An unlikely cover story.
"""

import tkFont
import Tkinter as tk
import ttk


DONT_PANIC = "DON'T PANIC"
TK_DEFAULT_FONT = 'TkDefaultFont'


def _large_friendly_letters(font=None):
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
    "A label for the front cover."

    def __init__(self, frame):
        "Initialise the ``FrontCover``."

        ttk.Label.__init__(
            self,
            frame,
            text=DONT_PANIC,
            anchor=tk.CENTER,
            font=_large_friendly_letters()
        )

    def configure(self, **kwargs):
        "Reconfigure the ``FrontCover``. Called by EDMC when applying the theme."

        font = kwargs.get('font')
        if font is not None:
            kwargs['font'] = _large_friendly_letters(font)

        ttk.Label.configure(self, **kwargs)
