import imp
import logging
from numpy import source
sweetness_logger = logging.getLogger(__name__)

from spacy.matcher import PhraseMatcher
from load_models import nlp
from load_models import MATCHER

def extract_sweetness(text: str, source: str) -> dict:
    if isinstance(text, str):
        doc = nlp(text)
        sweetness_descriptors = []
        for match_id, start, end in MATCHER(doc):
            rule_id = nlp.vocab.strings[match_id]
            if rule_id == 'Sweetness':
                sweetness_descriptors.append(doc[start:end].text)
        
        if len(sweetness_descriptors) > 0:
            sweetness_descriptors_cleaned = []

            for i in sweetness_descriptors:
                sweetness_descriptors_cleaned.append(i.strip().lower())

            result = {
                'data': sweetness_descriptors_cleaned,
                'source': source
            }
            return result
        else:
            return None
    else:
        return None


if __name__ == "__main__":
    pass