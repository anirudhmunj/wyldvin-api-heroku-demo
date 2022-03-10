import spacy

import logging
acidity_logger = logging.getLogger(__name__)

try:
    # Acidity Model
    model_dir = "models_acidity/wines_acidity/model-best"
    nlp_acidity = spacy.load(model_dir)
except Exception as e:
    acidity_logger.critical('ACIDTY MODEL: {}'.format(str(e)))
else:
    acidity_logger.info('SUCCESS - LOADED ACIDITY MODEL')


def extract_acidity(review: str, source: str) -> dict:
    """Extract acidity from review"""
    if isinstance(review, str):
        doc = nlp_acidity(review)
        acidity_terms = [ent.text for ent in doc.ents]
        if len(acidity_terms) > 0:
            acidity_list = [acidity.lower().strip() for acidity in acidity_terms if len(acidity.strip()) > 4]
            if len(acidity_list) > 0:
                result = {
                    'data': acidity_list,
                    'source': source
                }
                return result
            else:
                return None
        else:
            return None
    else:
        return None


if __name__ == "__main__":
    pass