import re
import string

import pandas as pd
import numpy as np

# spacy specific
import spacy
import ast

# scikit-learn specific
from joblib import load
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB


import logging
ageing_info_logger = logging.getLogger(__name__)



try:
    # vectorizer
    nb_count_vect_ageing_info = load('models_ageing_info/count_vect_tm.pkl')
    # classifier
    nb_classifier_ageing_info = load('models_ageing_info/nb_clf_tm.pkl')
except Exception as e:
    ageing_info_logger.critical('MODELS AGEING INFO: {}'.format(str(e)))
else:
    ageing_info_logger.info('SUCCESS - LOADED AGEING INFO MODELS')



# load spaCy nlp pipeline for text processing
try:
    nlp_ageing_info = spacy.load("en_core_web_sm")
    nlp_ageing_info.add_pipe("merge_entities")
    nlp_ageing_info.add_pipe("merge_noun_chunks")
except Exception as e:
    ageing_info_logger.critical('MODELS SPACY PIPELING AGEING: {}'.format(e))
else:
    ageing_info_logger.info('SUCCESS - LOADED AGEING INFO SPACY PIPELINE')



barrel_descriptors = ['russian', 'american', 'french', 'slovenian', 'hungarian', 'casks',
                        'vats', 'barrique', 'barriques', 'steel', 'slavonian',
                        'bourbon', 'australian', 'founders', 'demi-muids', 'demi muids', 'used barrels' ,'new barrels' , 'oak barrels', 'concrete', 'demi-muid']


country_names = ['russian', 'american', 'french', 'slovenian', 'hungarian', 'slavonian', 'bourbon', 'australian']


barrel_age_anchors = ['new', 'old', 'seasoned', 'older', 'used', '%']


#TODO remove
def segment_text(text: str) -> list:
    """returns a list of segmented sentences"""
    if isinstance(text, str):

        # convert text to spacy doc object
        doc = nlp_ageing_info(text)

        # segment sentences
        sentences = []
        for sent in doc.sents:
            # Converting back to string object (do not do if more processing to be done on the doc via spacy)
            sentences.append(sent.text.strip())
        if len(sentences) > 0:
            return sentences
        else:
            return None
    else:
        return None



def make_prediction(text: str) -> bool:
    if isinstance(text, str):
        as_list = []
        as_list.append(text)
        # vectorize
        vectorized_text = nb_count_vect_ageing_info.transform(as_list)
        # predict
        prediction = nb_classifier_ageing_info.predict(vectorized_text)
        # get prediction label
        prediction = prediction[0]
        # get confidence level
        prediction_probability = nb_classifier_ageing_info.predict_proba(
            vectorized_text)
        prediction_probability = max(prediction_probability[0])
        if prediction == 'x' and prediction_probability > 0.95:
            return True
        else:
            return False



def split_segmented_setence(text: str) -> list:
    """
    
        futher splits segmented sentences
        
        this further segmentation/splitting is specific for
        ageing info
    """
    # TODO add --> , the wine is
    splitted = re.split(r'and then | followed | and ageing | and aged | while | an additional | an addition |, the | the rest|, then| after being | , and',text)
    return splitted




def extract_ageing_time(doc): 
    """returns ageing time in months"""
    doc_ageing_time = ([w.text for w in doc if w.ent_type_ == 'DATE'])
    if len(doc_ageing_time) == 0:
           return None
    elif len(doc_ageing_time) == 1:
        doc_ageing_time = ' '.join(doc_ageing_time)
    else:
        doc_ageing_time = doc_ageing_time[-1]


    # process for digit
    # for cases 20-25 months, this would only pick up 25
    # TODO dicuss logic
    duration = None
    digits_match = re.search(r"(\d+\.?\d*)\s?(month|year)", doc_ageing_time, re.IGNORECASE)
    if digits_match:
        try:
            digits_match = digits_match.group(1)
        except:
            pass
        else:
            duration = digits_match

    # process for words representation
    # TODO one year would come to 24
    if not duration:
        ones = {'zero': 0,
                'half': 0.5,
                'an year': 1,
                'a year': 1,
                'one': 1,
                'two': 2,
                'three': 3,
                'four': 4,
                'five': 5,
                'six': 6,
                'seven': 7,
                'eight': 8,
                'nine': 9,
                'ten': 10,
                'eleven': 11,
                'twelve': 12,
                'thirteen': 13,
                'fourteen': 14,
                'fifteen': 15,
                'sixteen': 16,
                'seventeen': 17,
                'eighteen': 18,
                'nineteen': 19,
                'twenty': 20,
                'thirty': 30,
                'forty': 40,
                'fifty': 50,
                'sixty': 60,
                'seventy': 70,
                'eighty': 80,
                'ninety': 90,
                }

        numbers = []
        for token in doc_ageing_time.replace('-', ' ').split(' '):
            if token in ones:
                numbers.append(ones[token])
        duration = sum(numbers)

    if not duration:
        return None
    else:
        scale = None
        # process month and year aspects
        for i in doc_ageing_time.split(' '):
            if 'year' in i or 'years' in i:
                scale = 'year'
                break
            elif 'months' in i or 'month' in i:
                scale = 'months'
                break
            else:
                continue

        if scale:
            if scale == 'year':
                duration = float(duration) * 12.0
                return int(duration)
            else:
                duration = duration
                return int(duration)
        else:
            return None



def extract_ageing_phrase(doc):
    doc_ageing_phrase = []
    
    for token in doc:
        if any(barrel_descriptor in token.text.lower() for barrel_descriptor in barrel_descriptors):
            prefix_regex = token.text + "\s+\(\d{1,3}%\)"
            try:
                percentage_prefix_match = re.search(prefix_regex, doc.text, re.IGNORECASE)
            except:
                return None
            if percentage_prefix_match:
                doc_ageing_phrase.append(percentage_prefix_match.group())
            else:
                doc_ageing_phrase.append(token.text)
    
    if len(doc_ageing_phrase) == 0:
        return None
    else:
        return doc_ageing_phrase

    
def ageing_info_extractor(document: str):
    
    try:
        # sentence segmentation
        segmented_docs = segment_text(document)
        if not segmented_docs:
            return None
    except:
        return None
    
    # classify segmented sentences to get feeder sentences
    feeder_docs = []
#     identifiers = ['aged', 'aged in', 'spent', 'aging', 'ageing', 'careful aging', 'put', 'spend', 'aging', 'aging in', 'pressed', 'blend of']
    for i in segmented_docs:
        i_is_feeder = make_prediction(i)
        if i_is_feeder:
            feeder_docs.append(i)

    if len(feeder_docs) == 0:
        return None
    
    # loop through the feeder docs
    # extact ageing time
    # extract ageing phrases
    feeder_docs_final = []
    for i in feeder_docs:
        i_splitted_sentences = split_segmented_setence(i)
        for i_doc in i_splitted_sentences:
            if 'malolactic' in i_doc.lower() or 'fermentation' in i_doc.lower() or 'maceration' in i_doc.lower() or 'fermented' in i_doc.lower() or 'malo' in i_doc.lower() or 'ferments' in i_doc.lower():
                continue
            else:
                feeder_docs_final.append(i_doc)
    
    if len(feeder_docs_final) == 0:
        return None
    
    extracted_data_first_phase = []
    
    for i in feeder_docs_final:
        # extract ageing time
        i_spacy_doc = nlp_ageing_info(i)
        i_data_extracted_ageing_time = extract_ageing_time(i_spacy_doc)
        
        i_data_ageing_phrases = extract_ageing_phrase(i_spacy_doc)
        
        if i_data_ageing_phrases:
            result =  {
                'ageing_time': i_data_extracted_ageing_time,
                'ageing_phrases': i_data_ageing_phrases
            }
            
            extracted_data_first_phase.append(result)
            
    if len(extracted_data_first_phase) == 0:
        return None
    
    else:
        return extracted_data_first_phase
        


def extract_percentage_new(document: str) -> float:
    """extract percentage new for oak barrels"""
    try:
        match = re.search(r"(\d{1,3})\s?%\s?new", document, re.IGNORECASE)
    except:
        return None
    else:
        if match:
            match = match.group(1)
            try:
                match = float(match)
            except:
                return None
            else:
                return match
        else:
            return None


def extract_percentage_old(document: str) -> float:
    """extract percentage old for oak barrels"""
    try:
        match = re.search(r"(\d{1,3})\s?%(?!\s?new)", document, re.IGNORECASE)
    except:
        return None
    else:
        if match:
            match = match.group(1)
            try:
                match = float(match)
            except:
                return None
            else:
                return match
        else:
            return None




def process_extracted_ageing_info(ageing_phrase: str):
    
    country_names = ['russian', 'american', 'french', 'slovenian', 'hungarian', 'slavonian', 'bourbon', 'australian']
        
    # get all the barrels in the ageing phrase
    ageing_phrase = ageing_phrase.replace('-', ' ')
    ageing_phrase_splitted = ageing_phrase.split()
    ageing_phrase_splitted = [word.lower().strip() for word in ageing_phrase_splitted]
    materials = list(set(country_names).intersection(set(ageing_phrase_splitted)))


    barrel_age_neutral_flag = False
    barrel_age_new_flag = False
    barrel_age_assumed = False

    if len(set(['new', 'newer']).intersection(set(ageing_phrase_splitted))) > 0:
        barrel_age_new_flag = True

    if len(set(['used', 'old', 'older', 'used', 'neutral', 'filled']).intersection(set(ageing_phrase_splitted))) > 0:
        barrel_age_neutral_flag = True


    # extract percentage new
    percentage_new = extract_percentage_new(ageing_phrase)

    # extract percentage old
    percentage_old = extract_percentage_old(ageing_phrase)


    # no mentions of the oak age (new or old) of the barrel
    if barrel_age_new_flag == False and barrel_age_neutral_flag == False and percentage_old is None:
        barrel_age_neutral_flag = True
        barrel_age_assumed = True

    elif barrel_age_new_flag == False and barrel_age_neutral_flag == False and percentage_old is not None:
        barrel_age_netural_flag = True
        barrel_age_assumed = True
    else:
        pass

    
    if len(materials) > 0:
        result = {}
        result = {
            'materials':  materials,
            'barrel_age_neutral_flag':  barrel_age_neutral_flag,
            'barrel_age_new_flag':  barrel_age_new_flag,
            'barrel_age_assumed':  barrel_age_assumed,
            'percentage_new':  percentage_new,
            'percentage_old':  percentage_old,
        }
                

        return result
    else:
        return None



def restructure_results(extracted_ageing_info : list):
    result = []

    if len(extracted_ageing_info) == 1:
        
        for i in extracted_ageing_info[0]['ageing_phrases']:
            barrel_info = process_extracted_ageing_info(i)
            if barrel_info is not None:
                barrel_info['ageing_time_months'] = extracted_ageing_info[0]['ageing_time']
                result.append(barrel_info)

    elif len(extracted_ageing_info) == 2:
        return {"process_manually": True}
        
    else:
        return {"process_manually": True}
    
    result_final = []
    
    if len(result) > 0:
        for i in result:
            for j in i['materials']:
                material_info = {}
                material_info = {
                    'barrel_age_neutral_flag': i['barrel_age_neutral_flag'],
                    'barrel_age_new_flag': i['barrel_age_new_flag'],
                    'barrel_age_assumed': i['barrel_age_assumed'],
                    'percentage_new': i['percentage_new'],
                    'percentage_old': i['percentage_old'],
                    'ageing_time_months': i['ageing_time_months'],
                    'oak': j + ' oak'}
                
                result_final.append(material_info)
        
        return result_final
                
    else:
        return None
        
    return result


def main(document: str) -> list:
    

    if isinstance(document, str):
        # extract ageing information
        extracted_ageing_info = ageing_info_extractor(document)
        if extracted_ageing_info:
            result = restructure_results(extracted_ageing_info)
            return result
        else:
            return None
    else:
        return None



if __name__ == "__main__":
    pass
