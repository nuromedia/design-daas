import os
import subprocess

# Import necessary modules
from libqtile import layout
from libqtile.config import Key, Screen, Click, Drag
from libqtile.lazy import lazy

from libqtile import hook


@hook.subscribe.startup_once
def autostart():
    """Default autostart programs"""
    home = os.path.expanduser("~/.config/qtile/autostart.sh")
    subprocess.Popen([home])


mod = ["mod1", "control"]
ROFI_THEME = "-theme solarized -font 'hack 10'"
ROFI_COMBI = "-modi combi -show combi -combi-modi window,drun"
RESIZE_AMOUNT = 100
keys: list[Key] = [
    # Close focused window
    Key(mod, "q", lazy.window.kill()),
    Key(mod, "s", lazy.spawn("kitty")),
    Key(mod, "g", lazy.spawn("galculator")),
    Key(mod, "e", lazy.spawn("gedit")),
    Key(mod, "b", lazy.spawn("firefox-esr")),
    Key(mod, "r", lazy.spawn(f"rofi -show drun {ROFI_THEME}")),
    Key(mod, "w", lazy.spawn(f"rofi -show window {ROFI_THEME}")),
    Key(mod, "c", lazy.spawn(f"rofi {ROFI_COMBI} {ROFI_THEME}")),
    Key(mod, "n", lazy.next_layout()),
    Key(mod, "p", lazy.prev_layout()),
    Key(mod, "f", lazy.window.toggle_floating()),
]


mouse = [
    Drag(
        mod,
        "Button1",
        lazy.window.set_position_floating(),
        start=lazy.window.get_position(),
    ),
    Drag(
        mod,
        "Button2",
        lazy.window.set_size_floating(),
        start=lazy.window.get_position(),
    ),
    Click(
        mod,
        "Button4",
        lazy.window.resize_floating(RESIZE_AMOUNT, RESIZE_AMOUNT),
    ),
    Click(
        mod,
        "Button5",
        lazy.window.resize_floating(-RESIZE_AMOUNT, -RESIZE_AMOUNT),
    ),
    Click(mod, "Button3", lazy.window.bring_to_front()),
]

# Define layouts (fullscreen layout)
layouts = [
    layout.Max(),
    layout.Floating(),
    layout.Matrix(),
]

# Define a screen with no bar
screens = [Screen(wallpaper="/root/daas/env/daas.jpg", wallpaper_mode="stretch")]

# Define the Qtile configuration
widget_defaults = {"font": "Arial", "fontsize": 12, "padding": 3}
extension_defaults = widget_defaults.copy()

# Configure Qtile
# Auto start applications can be added here

# Start Qtile
# startup applications can be added here
