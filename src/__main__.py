import argparse


def parseArgs():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--url', help='URL to the system roms.')
    parser.add_argument('--regions', help='Preferences for sorting by the constants COUNTRY_CODES values, case sensitive.', default="Spain, Europe, English")

    args = parser.parse_args()
    return args


def run():
    from rom_cleaner import RomCleaner
    args = parseArgs()
    cleaner = RomCleaner(system_url=args.url, regions=args.regions)
    cleaner.run()


run()