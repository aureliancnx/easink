from math import sin, cos, sqrt, atan2, radians


def distance(lat1, lon1, lat2, lon2):
    R = 6373.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    arc = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    dips = atan2(sqrt(arc), sqrt(1 - arc))
    dips *= 2

    return dips * R

def format_dist(km):
    if km < 1:
        return '{0} m'.format(int(km * 100))

    if km < 10:
        km = "%.2f".format(km)
        return '{0} km'.format(km.replace(".", ","))

    return '{0} km'.format(int(km))