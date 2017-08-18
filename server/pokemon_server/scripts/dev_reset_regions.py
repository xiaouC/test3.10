import settings
settings.watch()

from session.regions import reset_regions


def reset_local_regions():
    reset_regions(settings.REGIONS)

if __name__ == '__main__':
    reset_local_regions()
