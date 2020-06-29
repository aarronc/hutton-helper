"""
Various display widgets.
"""

import collections
try:
    # for python 2
    import Tkinter as tk
    import ttk
    import tkFont
except ImportError:
    # for python 3
    import tkinter as tk
    import tkinter.ttk as ttk
    import tkinter.font as tkFont

from ttkHyperlinkLabel import HyperlinkLabel

DONT_PANIC = "Psymosn Sucks" # Original DON'T PANIC
TK_DEFAULT_FONT = 'TkDefaultFont'


def large_friendly_letters(font=None):
    "Make a ``font`` definition more friendly."

    if font is None:
        font = TK_DEFAULT_FONT

    if isinstance(font, str):
        size = tkFont.nametofont(font).cget('size')
        return (font, size * 1, tkFont.BOLD)

    elif isinstance(font, tkFont.Font):
        font = font.copy()
        font.configure(size=font.cget('size') * 1, weight=tkFont.BOLD)
        return font

    else:
        return font  # punt


class FrontCover(ttk.Label):
    """
    A big, friendly label.
    """

    def __init__(self, frame, text=DONT_PANIC):
        "Initialise the ``FrontCover``."

        ttk.Label.__init__(self, frame, text="Hutton Helper Lite", anchor=tk.CENTER, font=TK_DEFAULT_FONT)

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

        if 'font' in kwargs:  # capture full font details
            font = kwargs['font']

            if isinstance(font, str):
                kwargs['font'] = tkFont.nametofont(font)

            elif isinstance(font, collections.Iterable):
                kwargs['font'] = tkFont.Font(font=font)

        ttk.Label.configure(self, *args, **kwargs)
        self.__style.configure('HH.TCheckbutton', **kwargs)
        self.__style.configure('HH.TLabel', **kwargs)


class SelfWrappingHyperlinkLabel(HyperlinkLabel):
    "Tries to adjust its width."

    def __init__(self, *a, **kw):
        "Init."

        HyperlinkLabel.__init__(self, *a, **kw)
        self.bind('<Configure>', self.__configure_event)

    def __configure_event(self, event):
        "Handle resizing."

        self.configure(wraplength=event.width - 2)


class SelfWrappingLabel(ttk.Label):
    "Tries to adjust its width."

    def __init__(self, *a, **kw):
        "Init."

        ttk.Label.__init__(self, *a, **kw)
        self.bind('<Configure>', self.__configure_event)

    def __configure_event(self, event):
        "Handle resizing."

        self.configure(wraplength=event.width - 2)
