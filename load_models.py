import sys

import spacy
from spacy.matcher import PhraseMatcher

import pandas as pd

import logging
load_pipelines_logger = logging.getLogger(__name__)


# nlp pipeline
try:
    nlp = spacy.load("en_core_web_sm")
    #TODO experiment with adding or not for pairings
    # nlp.add_pipe("merge_noun_chunks")
except Exception as e:
    load_pipelines_logger.critical('PIPELINE: {}'.format(str(e)))
else:
    load_pipelines_logger.info('SUCCESS - LOADED NLP MODEL')


"""

    create spaCy PhraseMatcher
    PhraseMatcher used for:
        1. Grape variety
        2. Flavors
        3. Sweetness

"""

def get_flavors_patterns(flavors_map_path: str) -> list:
    """generate flavors level 4 patterns"""
    try:
        flavors_master_df = pd.read_csv(flavors_map_path)
    except Exception as e:
        load_pipelines_logger.critical('Flavors Patterns: {}'.format(str(e)))
        return None
    else:
        try:
            flavors_level_4_patterns = [nlp.make_doc(name.strip()) for name in list(set(flavors_master_df['level4'].tolist()))]
        except Exception as e:
            load_pipelines_logger.critical('Flavors Patterns (column): {}'.format(str(e)))
            return None
        else:
            return flavors_level_4_patterns


def get_grape_variety_patterns(grape_variety_map_path: str) -> list:
    """generate grape variety synonyms patterns"""
    try:
        grapes_master_df = pd.read_csv(grape_variety_map_path)
    except Exception as e:
        load_pipelines_logger.critical('Grape Variety Patterns: {}'.format(str(e)))
        return None
    else:
        try:
            grapes_patterns_synonyms = [nlp.make_doc(name.strip()) for name in grapes_master_df['synonym'].tolist()]
        except Exception as e:
            logging.critical('Grape Variety (column): {}'.format(str(e)))
            return None
        else:
            return grapes_patterns_synonyms


def get_sweetness_patterns() -> list:
    """generates sweetness patterns"""
    sweetness_terms = ['off dry', 'off-dry', 'medium-dry', 'medium dry','semi-sweet', 'semi sweet wine', 'very sweet wine', 'sweet wine' ,'dry wine']
    sweetness_patterns = [nlp.make_doc(name.strip()) for name in sweetness_terms]
    return sweetness_patterns



def create_matcher():
    # create PhraseMatcher instance
    matcher = PhraseMatcher(nlp.vocab, attr= "LOWER")

    # get patterns
    flavors_patterns = get_flavors_patterns('models_flavors/flavor_map_master.csv')
    grape_variety_patterns = get_grape_variety_patterns('models_grapes/grape_variety_mapped.csv')
    sweetness_patterns = get_sweetness_patterns()

    if flavors_patterns and grape_variety_patterns and sweetness_patterns:
        logging.info('Adding patterns...')
        try:

            logging.info('Adding sweetness patterns...')
            matcher.add("Sweetness", sweetness_patterns)

            logging.info('Adding grape variety patterns...')
            matcher.add("Grape_Variety", grape_variety_patterns)

            logging.info('Adding flavors patterns...')
            matcher.add("Flavor", flavors_patterns)

        except Exception as e:

            logging.critical('Error in adding patterns to matcher: {}'.format(str(e)))
            return None

        else:

            logging.info('Success: Added patterns...')
            return matcher
            
    else:
        load_pipelines_logger.critical('ERROR in creating PhraseMatcher. Exiting!!!')
        return None


MATCHER = create_matcher()

if MATCHER:
    logging.info('Succeesfully created matcher...')
else:
    logging.critical('Error in creating matcher....exiting!!')
    sys.exit(1)


if __name__ == "__main__":
    pass