# Myrient first row string
FIRST_ROW_STR = "Parent directory/"

# Default country_codes from the original project
DEFAULT_COUNTRY_CODES = {
    'As':'Asia', 'A': 'Australia', 'B': 'Brazil', 'C': 'Canada', 'Ch':'China', 'D': 'Netherlands', 'E':'Europe', 'F':'France',
    'Fn': 'Finland', 'G': 'Germany', 'Gr': 'Greece', 'Hk': 'Hong Kong', 'I': 'Italy','J':'Japan','K':'Korea','Nl':'Netherlands',
    'No':'Norway', 'R': 'Russia', 'S': 'Spain', 'Sw': 'Sweden', 'U': 'USA', 'UK': 'United Kingdom', 'W': 'World', 
    'Unl': 'Unlicensed', 'PD': 'Public Domain', 'Unk': 'Unknown'
}

RELEASE_CODES = ['!','rev','v','alternate','alt','o','beta','proto','alpha','promo','pirate','demo','sample','bootleg','b']

# Custom codes to add
EXTRA_COUNTRY_CODES = {'Spain': 'Spain', 'Es': 'Spain', 'spain': 'Spain', 'es': 'Spain', 'Europe':'Europe', 'Eu':'Europe', 'English': 'English', 'En': 'English', 'en': 'English',}

# Custom codes to skip
SKIP_CODES = ['Beta', 'Demo',  'Japan', 'China', 'Korea', 'Italy', 'Germany', 'France', 'Netherlands', 'Asia', 'Russia', 'Japan, Asia', 'Japan, Corea', 'Norway', 'Australia']

COUNTRY_CODES = {**DEFAULT_COUNTRY_CODES, **EXTRA_COUNTRY_CODES}
