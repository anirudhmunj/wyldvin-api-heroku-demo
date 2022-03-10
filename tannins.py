import spacy

import logging
tannins_logger = logging.getLogger(__name__)

try:
    # Acidity Model
    model_dir = "models_tannins/tannins_model_v1/model-best"
    nlp_tannins = spacy.load(model_dir)
except Exception as e:
    tannins_logger.critical('TANNINS MODEL: {}'.format(str(e)))
else:
    tannins_logger.info('SUCCESS - LOADED TANNINS MODEL')


def extract_tannins(review: str, source: str) -> dict:
    if isinstance(review, str):
        doc = nlp_tannins(review)
        
        all_entities = [ent.text for ent in doc.ents]
        
        if len(all_entities) > 0:
            selected_entities = []
            for i in all_entities:
                splitted = i.split()
                if 'and' in splitted:
                    selected_entities.append(splitted[-1].strip().lower())
                else:
                    if i.strip().lower() != 'the':
                        selected_entities.append(i.strip().lower())
                    else:
                        continue
            
            if len(selected_entities) > 0:
                result = {
                    'data': selected_entities,
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