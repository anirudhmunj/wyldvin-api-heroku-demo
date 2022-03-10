import logging
import sys
grape_variety_logger = logging.getLogger(__name__)

# Pandas 
import pandas as pd

# For Phrase Matcher
from spacy.matcher import PhraseMatcher
from load_models import nlp
from load_models import MATCHER

import re
import string

try:
    # create phrase matcher
    grapes_master_df = pd.read_csv('models_grapes/grape_variety_mapped.csv')
except Exception as e:
    grape_variety_logger.critical('GRAPE VARIETY PHRASE MATCHER: {}'.format(str(e)))
else:
    grape_variety_logger.info('SUCCESS - LOADED GRAPE VARIETY MAP')

try:
    # create reverse mapper dict
    grape_common_name = grapes_master_df['common_name'].tolist()
    grape_common_name = [word.strip() for word in grape_common_name]

    grape_variety_synonym = grapes_master_df['synonym'].tolist()
    grape_variety_synonym = [word.strip().lower() for word in grape_variety_synonym]

    grape_variety_mapper_dict = dict(zip(grape_variety_synonym, grape_common_name))
except Exception as e:
    grape_variety_logger.critical('GRAPE VARIETY MAPPER DICT: {}'.format(str(e)))
else:
    grape_variety_logger.info('SUCCESS - LOADED GRAPE VARIETY MAPPER DICT')



def grape_variety_reverse_remapper(grape: str) -> str:
    """
        remap grape variety to common name
    """

    grape = grape.strip().lower()
    
    for key, value in grape_variety_mapper_dict.items():
        if key == grape:
            return value
        
    return grape



def sub_string_element_remover(string_list):
    string_list.sort(key=lambda s: len(s), reverse=True)
    out = []
    for s in string_list:
        if not any([s in o for o in out]):
            out.append(s)
    return out



def grape_variety_extractor(raw_text: str, source: 'str') -> list:
    try:
        cleaned_text = raw_text.lower()
    except:
        return None
    else:
        # convert to spaCy doc
        doc = nlp(cleaned_text)

        # stores all extracted grapes data
        all_extracted_grape_varieties = []

        for match_id, start, end in MATCHER(doc):
            rule_id = nlp.vocab.strings[match_id]

            if rule_id != 'Grape_Variety':
                continue
            else:
                all_extracted_grape_varieties.append(doc[start:end].text)
        
        # remove substrings
        all_extracted_grape_varieties_deduped = sub_string_element_remover(all_extracted_grape_varieties)

        all_extracted_grape_varieties_dedped_with_percentage = []
        
        for grape in all_extracted_grape_varieties_deduped:
            regex = r'(\(?\d+(\.\d+)?\s?%\)?)?(\s)?({})(\s)?(\(?\d+(\.\d+)?\s?%\)?)?'.format(grape)
            matches = re.findall(regex, cleaned_text, re.IGNORECASE)
            if len(matches) > 0:
                matches_joined = []
                for i in matches:
                    match_raw = ' '.join([word for word in i if word]).strip()
                    matches_joined.append(match_raw)

                matches_joined_deduped = sub_string_element_remover(matches_joined)
                match = matches_joined_deduped[0]

                if match:
                    percentage_match = re.search(r'(\(?\d+(\.\d+)?\s?%\)?)', match)
                    if percentage_match:
                        grape_variety_percentage = percentage_match.group()
                        grape_extracted_data = {}
                        grape_extracted_data = {'grape': grape, 'percentage': grape_variety_percentage}
                        all_extracted_grape_varieties_dedped_with_percentage.append(grape_extracted_data)
                    else:
                        grape_extracted_data = {}
                        grape_extracted_data = {'grape': grape, 'percentage': ''}
                        all_extracted_grape_varieties_dedped_with_percentage.append(grape_extracted_data)

                
        # remap to common name
        if len(all_extracted_grape_varieties_dedped_with_percentage) > 0:
            # convert grape variety percenatege to integer
            for record in all_extracted_grape_varieties_dedped_with_percentage:
                record['grape_remapped'] = grape_variety_reverse_remapper(record['grape'])
                record['source'] = source
                try:
                    record_percentage = record['percentage']
                    record['percentage'] = record['percentage'].strip(')%(')
                    record['percentage'] = record['percentage'].strip()
                    record['percentage'] = float(record['percentage'])
                except:
                    record['percentage'] = None

            return all_extracted_grape_varieties_dedped_with_percentage
        else:
            return None


if __name__ == "__main__":
    print(grape_variety_extractor("2015 melot. This wine containes 100% merlot.", 'test'))