"""
Various display widgets.
"""
try:
    # for python 2
    import Tkinter as tk
    import ttk
    import tkFont
    import collections
except ImportError:
    # for python 3
    import tkinter as tk
    import tkinter.ttk as ttk
    import tkinter.font as tkFont
    try:
        # for python 3
        from collections import Iterable as DictMixin
        import collections
    except ImportError:
        # for python 3.10
        import collections.abc as collections

from ttkHyperlinkLabel import HyperlinkLabel

DONT_PANIC = "DON'T PANIC!" # Original DON'T PANIC
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

    def __init__(self, frame, text=DONT_PANIC, popup_enabled=None):
        "Initialise the ``FrontCover``."

        ttk.Label.__init__(self, frame, text=text, anchor=tk.CENTER, font=large_friendly_letters())
        self.popup_enabled = popup_enabled or (lambda: False)
        self.popup = None
        self.bind('<Button-1>', self.__show_popup)
        self.bind('<Enter>', self.__update_cursor)
        self.bind('<Leave>', lambda _event: self.configure(cursor=''))

    def __update_cursor(self, _event=None):
        "Show that the front cover is clickable when its popup is enabled."

        self.configure(cursor='hand2' if self.popup_enabled() else '')

    def __show_popup(self, _event=None):
        "Show a little reassurance when the front cover is clicked."

        if not self.popup_enabled():
            return

        popup = tk.Toplevel(self)
        self.popup = popup
        popup.title(DONT_PANIC)
        popup.resizable(False, False)

        frame = ttk.Frame(popup, padding=20)
        frame.grid(sticky=tk.NSEW)

        ttk.Label(
            frame,
            text="DON'T PANIC!\n\nThe Hutton Helper is standing by.",
            justify=tk.CENTER,
            anchor=tk.CENTER,
        ).grid(row=0, column=0, padx=10, pady=(0, 15))
        ttk.Button(frame, text='Close', command=self.close_popup).grid(row=1, column=0)

        popup.protocol('WM_DELETE_WINDOW', self.close_popup)
        popup.update_idletasks()

        # Tk geometry strings interpret negative coordinates as offsets from
        # the right/bottom edge, not as positions on monitors left/above the
        # primary display. Map first, then use Win32's virtual-screen coords.
        x = self.winfo_rootx() + self.winfo_width() + 10
        y = self.winfo_rooty()
        width = popup.winfo_width()
        height = popup.winfo_height()
        popup.geometry('{}x{}+0+0'.format(width, height))
        popup.update()

        try:
            import ctypes
            from ctypes import wintypes

            hwnd = int(popup.wm_frame(), 0)
            set_window_pos = ctypes.windll.user32.SetWindowPos
            set_window_pos.argtypes = (
                wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int,
                ctypes.c_int, ctypes.c_int, wintypes.UINT,
            )
            set_window_pos.restype = wintypes.BOOL
            positioned = set_window_pos(
                wintypes.HWND(hwnd), None, x, y, width, height,
                0x0010 | 0x0004,
            )  # SWP_NOACTIVATE | SWP_NOZORDER
            if not positioned:
                raise ctypes.WinError()
        except (AttributeError, OSError, ValueError):
            # On non-Windows systems, Tk can still place the popup when the
            # target coordinates are non-negative.
            popup.geometry('{}x{}+{}+{}'.format(
                width, height, max(0, x), max(0, y)
            ))
        popup.focus_set()

    def close_popup(self):
        "Close the popup if it is open."
        popup = self.popup
        self.popup = None
        if popup is not None:
            try:
                popup.destroy()
            except tk.TclError:
                pass

    def configure(self, *args, **kwargs):
        "Reconfigure the ``FrontCover``. Called by EDMC when applying the theme."

        font = kwargs.get('font')
        if font is not None:
            kwargs['font'] = large_friendly_letters(font)

        ttk.Label.configure(self,  *args, **kwargs)


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
