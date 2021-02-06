import threading
import time

from djangoProject.objects.Artist import Artist
from djangoProject.objects.Profile import Profile

artists = {}


def queue_start():
    thread1 = ArtistsQueue(50, "Thread-1ArtistsManager", 2)

    # Start new Threads
    thread1.start()

class ArtistsQueue(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        while True:
            profiles = Profile.objects.filter(type="TATTOIST")

            i = 0
            for profile in profiles:

                shop_long = profile.shop_long
                shop_lat = profile.shop_lat

                if shop_long is None or shop_lat is None or shop_long == "" or shop_lat == "":
                    shop_long = 0
                    shop_lat = 0

                shop_long = float(shop_long)
                shop_lat = float(shop_lat)

                artist = Artist(profile.unique_id, profile.shop_name, profile.shop_siret, profile.shop_localization, shop_long, shop_lat,
                                profile.shop_email, profile.shop_phone, "", [], "", "", "Mode, Beauté", "Artiste depuis 200 avant J.C")

                artists[i] = artist

                i += 1

            print('Artists: {0}'.format(i))

            time.sleep(5)