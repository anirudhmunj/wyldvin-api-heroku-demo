"""

    Food Pairings Extactor

    Food pairings will always will only be 
    available in winemaker notes and/or critical reviews

"""

import string
from load_models import nlp
from joblib import load
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import logging
parirings_logger = logging.getLogger(__name__)


try:
    # vectorizer
    nb_countvect_food_pairing = load('models_pairings/count_vect_tm.pkl')
    # classifier
    nb_classifier_food_pairing = load('models_pairings/nb_clf_tm.pkl')
except Exception as e:
    parirings_logger.critical('MODELS PAIRINGS: {}'.format(str(e)))
else:
    parirings_logger.info('SUCCESS - LOADED PAIRINGS MODELS')


def clean_text(text: str) -> str:
	"""
		remove punctuation characters
		remove extra whitespace
		convert to lowercase
	"""
	punctuation_to_remove = '!"#$%&\'()*+-./:;<=>?@[\\]^_`{|}~'
	string_translator = str.maketrans(punctuation_to_remove, ' '*len(punctuation_to_remove))
	
	# remove punctuation
	cleaned_text = text.translate(string_translator)
	cleaned_text = ' '.join([word for word in cleaned_text.split()])
	# convert to lowercase
	cleaned_text = cleaned_text.lower()
	return cleaned_text




def make_prediction(text: str) -> bool:
    if isinstance(text, str):
        as_list = []
        as_list.append(text)
        # vectorize
        vectorized_text = nb_countvect_food_pairing.transform(as_list)
        # predict
        prediction = nb_classifier_food_pairing.predict(vectorized_text)
        # get prediction label
        prediction = prediction[0]
        # get confidence level
        prediction_probability = nb_classifier_food_pairing.predict_proba(
            vectorized_text)
        prediction_probability = max(prediction_probability[0])

        if prediction == 'x' and prediction_probability > 0.95:
            return True
        else:
            return False


def sub_string_element_remover(string_list):
    string_list.sort(key=lambda s: len(s), reverse=True)
    out = []
    for s in string_list:
        if not any([s in o for o in out]):
            out.append(s)
    return out


def extract_pairings(text: str):
    if isinstance(text, str):
        pairings = []
        doc = nlp(text)

        stopwords = ['wine', 'pair', 'the', 'variety', 'bottle', 'it',
                     'a', 'this', 'you', 'your',
                     'choice', 'time', 'that', 'pairs', 'we', 'match',
                     'some', 'flavor', 'home', 'finish', 'plenty', 'figure', 
                     'acidity', 'tannin', 'tannins', 'lively', 'its', 'oak', 
                     'berries', 'wood', 'aroma', 'aromas', 'friends', 'party']

        for token in doc.noun_chunks:
            token = token.text.strip().lower()
            tokens_splitted = token.split()
            matched_stopwords = [i for i in stopwords if i in tokens_splitted]
            if len(matched_stopwords) > 0:
                pass
            else:
                pairings.append(token)

        if len(pairings) > 0:
            # deduplicate
            pairings_deduped = sub_string_element_remover(pairings)
            pairings_cleaned = []
            for i in pairings_deduped:
                i_cleaned = clean_text(i)
                pairings_cleaned.append(i_cleaned)
            return pairings_cleaned
        else:
            return None
    else:
        return None


def extractor(sentences: list, source: str) -> dict:
    """main caller"""

    pairings = []

    for sent in sentences:
        is_sent_potential = make_prediction(sent)
        if is_sent_potential:
            sent_pairings = extract_pairings(sent)
            if sent_pairings:
                pairings.extend(sent_pairings)

    if len(pairings) > 0:
        result = {
            'source': source,
            'data': pairings,
        }

        return result
    else:
        return None


if __name__ == "__main__":
    pass
