import json


class Artist:
    def __init__(self, unique_id, shop_name, shop_siret, shop_localization, shop_long, shop_lat, shop_email, shop_phone, profile_picture, pictures, social_facebook, social_instagram, styles, bio):
        self.unique_id = unique_id
        self.shop_name = shop_name
        self.shop_siret = shop_siret
        self.shop_localization = shop_localization
        self.shop_long = shop_long
        self.shop_lat = shop_lat
        self.shop_email = shop_email
        self.shop_phone = shop_phone
        self.profile_picture = profile_picture
        self.pictures = pictures
        self.social_facebook = social_facebook
        self.social_instagram = social_instagram
        self.styles = styles
        self.bio = bio

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True, indent=4)