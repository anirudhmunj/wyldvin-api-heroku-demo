import logging
flavors_logger = logging.getLogger(__name__)

# Scikit-Learn
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from joblib import load

# Pandas 
import pandas as pd

# For Phrase Matcher
from spacy.matcher import PhraseMatcher
from load_models import nlp
from load_models import MATCHER

# Load model for identifying(classifying) sentences
try:
    # vectorizer
    nb_countvect_flavors = load('models_flavors/count_vect_tm.pkl')
    # classifier
    nb_classifier_flavors = load('models_flavors/nb_clf_tm.pkl')
except Exception as e:
    flavors_logger.critical('MODEL FLAVORS: {}'.format(str(e)))
else:
    flavors_logger.info('SUCCESS - LOADED FLAVORS MODELS')


try:
    flavors_master_df = pd.read_csv('models_flavors/flavor_map_master.csv')
except Exception as e:
    flavors_logger.critical('FLAVORS PHRASE MATCHER: {}'.format(str(e)))
else:
    flavors_logger.info('SUCCESS - LOADED FLAVORS MAP')


try:
    # Create reverse mapper dict
    flavors_mapper_dict = dict(zip(flavors_master_df['level4'].tolist(), flavors_master_df['level3'].tolist()))
except Exception as e:
    flavors_logger.critical('FLAVORS MAPPER DICT: {}'.format(str(e)))
else:
    flavors_logger.info('SUCCESS - LOADED FLAVORS MAPPER DICT')


def make_prediction(text: str) -> str:
    """used to identify sentences that do not describe food pairings"""
    if isinstance(text, str):
        as_list = []
        as_list.append(text)
        # vectorize
        vectorized_text = nb_countvect_flavors.transform(as_list)
        # predict
        prediction = nb_classifier_flavors.predict(vectorized_text)
        # get prediction label
        prediction = prediction[0]
        # get confidence level
        prediction_probability = nb_classifier_flavors.predict_proba(vectorized_text)
        prediction_probability = max(prediction_probability[0])
        if prediction == 'others':
            return True
        else:
            return False


def flavors_reverse_mapper(extracted_flavors: list) -> list:
    """
        Remap level 4 flavors to level 3
        
        Do not remove duplicates as it would 
        make it impossible to get the most common
        flavors - top 3 and 5
    
    """
    remapped = list(map(flavors_mapper_dict.get, extracted_flavors))
    remapped = [el for el in remapped if el]
    return remapped


def sub_string_element_remover(string_list):
    string_list.sort(key=lambda s: len(s), reverse=True)
    out = []
    for s in string_list:
        if not any([s in o for o in out]):
            out.append(s)
    return out


def flavors_extractor(sentences: str, source: str) -> dict:
    """
        Flavors extrator using Phrase Matcher
        
        :params:
            - raw_text
                - Raw string
                
        :returns:
            - dict
                - level4 (original)
                - level3 (remapped)
    """
    
    punctuation_to_remove = '!"#$%&\'()*+-./:;<=>?@[\\]^_`{|}~'
    string_translator = str.maketrans(punctuation_to_remove, ' '*len(punctuation_to_remove))
    
    # segment sentences
    useful_segments = []
    
    for sent in sentences:
        sent_has_potential = make_prediction(sent)
        if sent_has_potential:
            useful_segments.append(sent)
        
    if len(useful_segments) == 0:
        return None

    else:
        # Extract flavors
        extracted_flavors = []
        for sent in useful_segments:

            try:
                # Clean raw text
                cleaned_text = sent.translate(string_translator)
                cleaned_text = cleaned_text.lower()

            except Exception as e:
                continue
            else:
                # Convert to spacy doc object
                doc = nlp(cleaned_text)

                for match_id, start, end in MATCHER(doc):
                    rule_id = nlp.vocab.strings[match_id]
                    if rule_id == 'Flavor':
                        extracted_flavors.append(str(doc[start:end]))

                extracted_flavors = sub_string_element_remover(extracted_flavors)

                # Remap flavors from level4 to level3
                remapped_flavors = flavors_reverse_mapper(extracted_flavors)


        if len(extracted_flavors) > 0:
            result = {
                'source': source,
                'extracted_flavors': extracted_flavors,
                'remapped_flavors': remapped_flavors
            }

            return result
        else:
            return None


if __name__ == "__main__":
    pass