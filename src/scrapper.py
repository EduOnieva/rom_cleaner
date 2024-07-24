import requests
from typing import List
from urllib.parse import urljoin
from pydantic import BaseModel
from bs4 import BeautifulSoup, Tag
from constants import FIRST_ROW_STR 


class TableElement(BaseModel):
    name: str
    url: str

    def __init__(self, row: Tag, base_url: str):
        anchor_element = row.next_element.next_element # From tr element to td and then to a element
        file_name = anchor_element.attrs.get('title')
        full_url = urljoin(base_url, anchor_element.attrs.get('href'))
        super().__init__(name=file_name, url=full_url)
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return f"{self.name} at {self.url}"
    

class ScraperMyrientTable:

    def __init__(self, url: str):
        self._url = url

    @property
    def table_elements(self) -> List[TableElement]:
        try:
            return self._table_elements
        except AttributeError as ex:
            raise AttributeError('Table elements not found. Run the scraper first with the `run()` method.')

    def get_soup(self) -> BeautifulSoup:
        response = requests.get(self._url)
        return BeautifulSoup(response.text, features="html.parser")
    
    def _is_game_row(self, row: object) -> bool:
        if isinstance(row, Tag):
            if not row.get_text().startswith(FIRST_ROW_STR):  # Ignore the first row "Parent directory/"
                return True
        return False

    def get_table(self, soup: BeautifulSoup) -> List[TableElement]:
        table_elements = []
        table = soup.find("table", {"id": "list"})
        for children in table.tbody.children:
            if children is not None and self._is_game_row(children):
                table_elements.append(TableElement(row=children, base_url=self._url))
        return table_elements
    
    def run(self):
        print(f"Getting info from {self._url}...")
        soup = self.get_soup()
        print(f"Scraped self._url...")

        print("Parsing table...")
        self._table_elements = self.get_table(soup)
        print(f"Finished parsing the table with {len(self.table_elements)} elements.")
