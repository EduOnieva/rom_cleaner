import re
from functools import reduce
from dateutil.parser import parse
from datetime import datetime
from colorama import Fore, Style, Back
from constants import COUNTRY_CODES, RELEASE_CODES, SKIP_CODES


class Rom():
    def __init__(self, table_element: 'TableElement'): # type: ignore
        self.url = table_element.url
        self.base_filename, self.stripped_filename, self.tokens = self.describe_rom(table_element)

    # Helper function:
    def find(self, s, ch):
        return [i for i, ltr in enumerate(s) if ltr == ch]

    @staticmethod
    def valid_brackets(filename):
        """ Validate that the filename has matching parentheses or brackets. """
        stack = []
        matching_bracket = {')': '(', ']': '['}
        
        for char in filename:
            if char in '([':
                stack.append(char)
            elif char in ')]':
                if not stack or stack.pop() != matching_bracket[char]:
                    return False
        return not stack
    
    @staticmethod
    def extract_brackets_content(filename):
        """ Extract content within parentheses and square brackets using regular expressions. """
        # Patterns to match content within parentheses and square brackets
        pattern_parentheses = re.compile(r'\(([^()]+)\)')
        pattern_brackets = re.compile(r'\[([^\[\]]+)\]')

        # Find all matches
        matches_parentheses = pattern_parentheses.findall(filename)
        matches_brackets = pattern_brackets.findall(filename)
        
        return matches_parentheses + matches_brackets
            
    def extract_tags(self, filename):
        if not self.valid_brackets(filename):
            print("Invalid format: Unmatched parentheses or square brackets for file:\n"+filename)
            raise ValueError
        else:
            rom_tags = []
            brackets_contents = self.extract_brackets_content(filename)
            if brackets_contents:
                per_bracket_tags = map(lambda s: set([tag.strip() for tag in s.split(',')]),brackets_contents)
                rom_tags = list(sorted(reduce(set.union, per_bracket_tags)))
            
            return rom_tags
    
    # Extraction tags:
    def describe_rom(self, table_element):
        base_filename = table_element.name
        # Strip filename of brackets and contents
        stripped_filename = re.sub(r'[\[\(].*?[\]\)]', '', base_filename).strip()
        # Also remove any leftover spaces before file extension
        stripped_filename = re.sub(r'\s+\.', '.', stripped_filename)
        tags = self.extract_tags(base_filename)
        return base_filename, stripped_filename, tags
   
    # Deduce rom region or regions based on filename tags
    def get_romregions(self):
        countries = []
        for tag in self.tokens:
            for k, v in COUNTRY_CODES.items():
                if tag in (k,v) : countries.append(k)
        
        if len(countries):
            return countries
        else: return 'Unk'
        
    def tag_isvolume(self, tag):
        valid_parts = ['disk', 'disc', 'side', 'volume']
        pattern = r'^({})\s+(\w+)'.format('|'.join(valid_parts))
        regex = re.compile(pattern)
        match = regex.search(tag.lower())
        if match:
            part_type = match.group(1) 
            part_val = match.group(2)
            # Check if numeric or not, some tags use letters for sequence
            if part_val.isnumeric(): part_num= int(part_val)
            else: part_num = ord(part_val[0])
            
            return (part_type, int(part_num))
        return None

    def get_disc_number(self):
        for tag in self.tokens:
            v_info = self.tag_isvolume(tag)
            if v_info: return v_info[1]
        return 0
                
    def has_multiple_disc(self):
        return self.get_disc_number()
    
    # Returns true if roms differ from each other only by volume information
    def is_part_of_main_of(self, rom):
        if not rom.has_multiple_disc() or not self.has_multiple_disc(): return False
        if rom.get_disc_number() == self.get_disc_number(): return False        
        else:
            # Calculate tag diffbuild_rankerences between roms 
            differences = set(rom.tokens) ^ set(self.tokens)
            return all([self.tag_isvolume(tag) for tag in differences])        

    # If build information is included in filename, use build type and
    # version (if provided) to score roms according to 'RELEASE_CODES' order.
    def build_rank(self):
        # '!' , rev and v should have higher priority than no build information whatsoever
        build = len(RELEASE_CODES) - 4
        version = float('inf')
        
        escaped_RELEASE_CODES = [re.escape(code) for code in RELEASE_CODES]
        
        # Create a regex pattern dynamically
        # Adding word boundaries for most release codes
        # Special handling for release codes that are just special characters (!)
        escaped_RELEASE_CODES_with_boundaries = [r'\b' + code for code in escaped_RELEASE_CODES if code.isalnum()]
        escaped_special_codes = [code for code in escaped_RELEASE_CODES if not code.isalnum()]        
        
        pattern = r'^((?:{}))\s*(\d*\.?\d*)'.format('|'.join(escaped_RELEASE_CODES_with_boundaries + escaped_special_codes))        
        regex = re.compile(pattern)
        
        for tag in self.tokens:
            match = regex.search(tag.lower())
            if match:
                build = match.group(1)
                if len(match.groups()) == 2 and match.group(2):
                    version = float(match.group(2).lstrip('0'))
                break
                
        # Build ranking table according to RELEASE_CODES order
        ranks = [(i,item) for i, item in enumerate(reversed(RELEASE_CODES))]
        for score, rank in ranks:
            if rank == build:
                return (score, version)
        return (build, version)

    # Rank rom according to tagged region(s) and user preferences
    def region_rank(self, rank_table):
        def score_rom(rom_ccs):
            result = []
            for item in rank_table:
                if item[1] in rom_ccs:
                    result.append(item[0])
            return result
    
        rom_ccs = self.get_romregions()       
        return max(score_rom(rom_ccs))
    
    # If a timestamp is included capture it to resolve ties, if no timestamp
    # was supplied assume it is the most recent build
    def timestamp_rank(self):
        for tag in self.tokens:
            try:
                return parse(tag)
            except (ValueError, OverflowError):
                continue
        return datetime.max

    def force_skip(self):
        for sc in SKIP_CODES:
            if f"({sc})" in self.base_filename:
                return True
        return False


class RomSet:
    def __init__(self, regions: str):
        self.rank_table = self.build_table([p.strip() for p in regions.split(',')])
        self.titles = {}
        self.download_roms = list()

    def add_rom(self, table_obj):
        rom_obj = Rom(table_obj)
        if rom_obj.stripped_filename not in self.titles:
            self.titles[rom_obj.stripped_filename] = {}
            self.titles[rom_obj.stripped_filename]['roms'] = []
        self.titles[rom_obj.stripped_filename]['roms'].append(rom_obj)

    def clean(self):
        for stripped_filename, title in sorted(self.titles.items()):

            print(Fore.BLACK + Back.LIGHTWHITE_EX + stripped_filename + Style.RESET_ALL)

            is_main = True
            main = None
            parts_of_main = list()
            
            for rom in sorted(title['roms'], key=lambda x: (x.region_rank(self.rank_table), *x.build_rank(), \
                x.timestamp_rank(),-x.get_disc_number()), reverse=True):            

                # Check if active rom is part of main rom.
                if not is_main:
                    is_part_of_main = rom.is_part_of_main_of(main)
                
                if is_part_of_main:
                    parts_of_main.append(rom)

                # Choose action to display for active rom.
                if (is_main or is_part_of_main) and not rom.force_skip(): action = Fore.GREEN + 'OK' + Style.RESET_ALL
                else: action = Fore.RED + 'KO' + Style.RESET_ALL

                print('\t:{}:{}'.format(action, rom.base_filename))

                if is_main:
                    is_main = False
                    main = rom
            
            if main.force_skip():
                continue
            else:
                self.download_roms.append(main)
                self.download_roms.extend(parts_of_main)
            
        print('total unique files: {}'.format(len(self.titles)))
        print('total files       : {}'.format(len(self.download_roms)))        

    # Build a table to rank title region according to supplied
    # preferences, or else according to alphabetic order.
    def build_table(self, user_ccs):
        cc_keys_in_user = []
        # Check if priority country codes is valid
        for cc in user_ccs:
            found=False
            for cc_key, cc_value in COUNTRY_CODES.items():
                if cc in cc_value:  
                    found=True
                    cc_keys_in_user.append(cc_key)
            if found==False:
                raise ValueError(f"Must be a valid country code, code is case sensitive: {cc}")
        
        alpha_rank = [(i, item) for i, item in enumerate(sorted(set(COUNTRY_CODES) - set(cc_keys_in_user), reverse=True))]
        return alpha_rank + [(i,item) for i, item in enumerate(reversed(cc_keys_in_user),start=len(alpha_rank))]
