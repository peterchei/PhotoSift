"""
Common UI components shared across PhotoSift applications.

This module contains reusable UI components that are used by multiple
applications within the PhotoSift suite, helping to maintain consistency
and reduce code duplication.
"""

import tkinter as tk


class ToolTip:
    """
    Create a tooltip for a given widget
    
    This class provides a reusable tooltip implementation that can be used
    across different PhotoSift applications. It shows helpful information
    when users hover over UI elements.
    
    Args:
        widget: The tkinter widget to attach the tooltip to
        text: The tooltip text to display
    """
    
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     # milliseconds
        self.wraplength = 180   # pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.widget.bind("<Motion>", self.motion)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def motion(self, event=None):
        self.unschedule()
        self.schedule()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        if self.tw:
            return
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        self.tw.configure(bg='#ffffe0', relief='solid', borderwidth=1)
        label = tk.Label(self.tw, text=self.text, justify=tk.LEFT,
                         background='#ffffe0', foreground='#000000',
                         relief='flat', borderwidth=0,
                         font=("Segoe UI", 10))
        label.pack(ipadx=8, ipady=4)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()


# Additional common UI components can be added here in the future
# Examples: ProgressWindow, ModernButton, StatusBar, etc.