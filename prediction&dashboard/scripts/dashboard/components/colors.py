"""
Central color & style constants for the PFZ Classifier System dashboard.
Import from here everywhere instead of hardcoding hex values, so the
palette only ever needs to change in one place.
"""

# --- Brand palette (echoes the INCOIS emblem: navy circle + ocean blue/teal) ---
NAVY = "#0B3D6B"          # primary brand navy - header, nav, key accents
NAVY_DARK = "#082B4D"     # darker navy for gradient ends / hover states
TEAL = "#0E7C86"          # secondary ocean-teal accent - chart lines, links
TEAL_LIGHT = "#128C99"    # lighter teal for gradient stops

HERO_GRADIENT = f"linear-gradient(135deg, {NAVY} 0%, {TEAL_LIGHT} 100%)"

BG = "#FFFFFF"
BG_SOFT = "#F8FAFB"       # subtle off-white for card/section backgrounds
BORDER = "#E3E8EC"

TEXT_PRIMARY = "#1F2937"
TEXT_SECONDARY = "#5B6472"
TEXT_MUTED = "#8A93A0"

# --- PFZ category colors (High / Medium / Low fishing suitability) ---
CATEGORY_COLORS = {
    "High": "#28a745",
    "Medium": "#ffc107",
    "Low": "#fd7e14",
}

# Slightly softened fill variants, used for map markers / chart fills
CATEGORY_COLORS_SOFT = {
    "High": "#6FCF8E",
    "Medium": "#FFDD7A",
    "Low": "#FEB27A",
}

CATEGORY_ORDER = ["High", "Medium", "Low"]

# --- Status colors ---
SUCCESS = "#28a745"
WARNING = "#ffc107"
ERROR = "#dc3545"
INFO = TEAL
