# Creates a logs file
import sys

from load_models import nlp
import flavors as m_flavors
import pairings as m_pairings
import grape_variety_v2 as m_grape_variety
import body as m_body
import acidity as m_acidity
import tannins as m_tannins
import sweetness as m_sweetness
import vintage as m_vintage
import ageing_info_v2 as m_ageing_info



def segment_text(text: str) -> list:
    """returns a list of segmented sentences"""
    if isinstance(text, str):

        # convert text to spacy doc object
        doc = nlp(text)

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



def main(document: str, source: str) -> dict:
    
    #TODO Add vintage
    record = {}

    # sentence segmentation
    segmented_sentence = segment_text(document)


    extracted_ageing_info = m_ageing_info.main(document)
    if extracted_ageing_info:
        record['ageing_info'] = extracted_ageing_info

    extracted_food_pairings = m_pairings.extractor(segmented_sentence, source)
    if extracted_food_pairings:
        record['food_pairings'] = extracted_food_pairings

    extraced_flavors = m_flavors.flavors_extractor(segmented_sentence, source)
    if extraced_flavors:
        record['flavors'] = extraced_flavors

    extracted_grape_varieties = m_grape_variety.grape_variety_extractor(document, source)
    if extracted_grape_varieties:
        record['grape_variety'] = extracted_grape_varieties

    extracted_body = m_body.extract_body_regex(document, source)
    if extracted_body:
        record['body'] = extracted_body

    extracted_acidity = m_acidity.extract_acidity(document, source)
    if extracted_acidity:
        record['acidity'] = extracted_acidity

    extracted_tannins = m_tannins.extract_tannins(document, source)
    if extracted_tannins:
        record['tannins'] = extracted_tannins

    extracted_sweetness = m_sweetness.extract_sweetness(document, source)
    if extracted_sweetness:
        record['sweetness'] = extracted_sweetness

    if len(record) > 0:
        return record
    else:
        return None


if __name__ == "__main__":
    pass