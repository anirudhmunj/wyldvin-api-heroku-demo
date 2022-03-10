"""
    Extract vintage

    Main source:
        1. Wine Name

"""

import re

def extract_vintage(text: str, source: str) -> dict:
    """extacts and returns vintage"""
    if isinstance(text, str):
        # reverse the name
        splitted = text.split()
        # reverse the name since vitnage is always at the end of the wine name
        # Eg: 1918 WW2 Classic Malbec 2017
        reversed_name = ' '.join(splitted[::-1])
        vintage = re.search(r'\d{4}', reversed_name)
        if vintage:
            result = {
                'vintage': vintage.group().strip(),
                'source': source
            }
            return result
        else:
            return None
    else:
        return None


if __name__ == '__main__':
    pass