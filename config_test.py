import os

# Statement for enabling the development environment
TESTING = True
DEBUG = True
ENV = 'testing'
WTF_CSRF_ENABLED = False
SQLALCHEMY_DATABASE_URI = 'postgresql://acrespo@localhost:5432/test_calendarapp'
# Secret key for signing cookies
SECRET_KEY = os.urandom(32)

# Colors for new task buttons
BUTTON_CUSTOM_COLOR_VALUE = "#3EB34F"
BUTTONS_COLORS_LIST = (
    ("#FF4848", "Red"),
    ("#3EB34F", "Green"),
    ("#2966B8", "Blue"),
    ("#808080", "Grey"),
    ("#B05F3C", "Brown"),
    ("#9588EC", "Purple"),
    ("#F2981A", "Orange"),
    ("#3D3D3D", "Black"),
)
# Emojis for new task buttons
BUTTONS_EMOJIS_LIST = (
    "💬",
    "📞",
    "🍔",
    "🍺",
    "📽️",
    "🎂",
    "🏖️",
    "💻",
    "📔",
    "✂️",
    "🚂",
    "🏡",
    "🐶",
    "🐱",
)
