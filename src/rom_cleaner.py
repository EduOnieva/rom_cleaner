from colorama import init as colorama_init
from clean_roms import RomSet
from scrapper import ScraperMyrientTable


class RomCleaner:
    def __init__(self, system_url: str, regions: str) -> None:
        self._url = system_url
        self.regions = regions
        colorama_init()

    def run(self):
        # Run the scraper to retrieve the list of roms:
        scrapper = ScraperMyrientTable(url=self._url)
        scrapper.run()
        
        # create the ROMSET class:
        romset = RomSet(regions=self.regions)

        # create a rom object for each file:
        for table_element in scrapper.table_elements:
            romset.add_rom(table_element)

        romset.clean()

        self.print_urls_to_download(romset.download_roms)

    @staticmethod
    def print_urls_to_download(_kept_roms):
        print(f"List of {len(_kept_roms)} urls to download:")
        for rom in _kept_roms:
            print(rom.url)
