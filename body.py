import re
import string
from unittest import result

from numpy import extract, source

def body_remapper(body_original: str) -> str:
    """standardize body"""
    if isinstance(body_original, str):
        
        mapper = {
            'full': 'full',
            'light': 'light',
            'medium': 'medium',
            'heavy': 'full',
        }
        
        mapper_sequence_to_num = {
            'light': 1,
            'medium': 2,
            'full': 3
        }
        
        mapper_sequence_to_text = {
            1: 'light',
            2: 'medium',
            3: 'full'
        }
        
        
        # convert to lowercase
        body_original = body_original.lower().strip()
        
        # split for remapping at whitespace
        splitted = body_original.split('to')
        # remove extra whitespace
        splitted = list(set([word.strip() for word in splitted]))
        # remap to standardize terms
        remapped = [*map(mapper.get, splitted)]
        
        # correct sequence
        if len(remapped) == 1:
            return remapped[0]
        else:
            # remap to numeric
            remapped_seq = [*map(mapper_sequence_to_num.get, remapped)]
            # sort in ascending order
            remapped_seq.sort()
            # remap back to text
            remappped = [*map(mapper_sequence_to_text.get, remapped_seq)]
            body = ' to '.join(remappped)
            return body
        
    else:
        return None
    
    
def extract_body_regex(review: str, source: str):
    """Extract body descriptors from review"""
    if isinstance(review, str):
        
        # Range match
        match = re.search(r"(((light|medium|heavy|full)\s*(to)\s*(light|medium|heavy|full))\s*(bod(y|ied)))", review, re.IGNORECASE)
        if match:
            body = match.group(2)
            body = body.strip()
            body = body.title()
            
            body_remapped = body_remapper(body)

            result = {
                'data': [body_remapped],
                'source': source
            }
            
            return result
        
        
        match = re.search(r"(light|medium|heavy|full)-?(\s*)(bod(y|ied))", review, re.IGNORECASE)
        
        if match:
            body = match.group()
            body = body.strip()
            body = body.lower()
            
            if 'light' in body:
                extracted_body =  'light'
            elif 'medium' in body:
                extracted_body =  'medium'
            elif 'heavy' in body:
                extracted_body = 'full'
            else:
                extracted_body =  'full'

            result = {
                'data': [extracted_body],
                'source': source
            }
                        
            return result
        else:
            return None
    else:
        return None


if __name__ == "__main__":
    pass