from build_feed import write_feed
from config import CHANNELS


for channel in CHANNELS:
    print(write_feed(channel))

