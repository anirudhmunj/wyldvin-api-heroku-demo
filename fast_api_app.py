# FastApi
from fastapi import Depends, FastAPI, HTTPException, status
from typing import Optional, List
from fastapi.encoders import jsonable_encoder

# https://pydantic-docs.helpmanual.io/
from pydantic import BaseModel


# application specific
# load pipeline
import load_models as m_load_models

import pipeline as m_pipeline

import ageing_info_v2 as m_ageing_info

# data model class for request
class RequestData(BaseModel):
    source: str
    document: str

# data model class for response
#TODO
class ReturnData(BaseModel):
    source: str
    data: dict



app = FastAPI(
    title="Wyldvin Wine Infomation Extractor",
    description="API for information extraction, with auto docs.",
    version="1.0.0",
)


"""
    returns all possible data points for extraction
"""
@app.post("/extract")
def extract_all_data(item: RequestData):
    # extract data
    extracted_data = m_pipeline.main(item.document, item.source)
    return {"extracted_data": extracted_data}



@app.post('/ageing_info')
def extract_ageing_info(item: RequestData):
    # extract data
    extracted_data = m_ageing_info.main(item.document)

    return {"extracted_data": extracted_data}