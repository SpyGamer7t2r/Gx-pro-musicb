from EsproMusic.core.bot import app
from EsproMusic.core.dir import dirr
from EsproMusic.core.git import git
from EsproMusic.core.userbot import Userbot
from EsproMusic.misc import dbb, heroku

from .logging import LOGGER

# run setup
dirr()
git()
dbb()
heroku()

# userbot instance
userbot = Userbot()

from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()