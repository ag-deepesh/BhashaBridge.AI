import requests
import simplejson as json
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import certifi

os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ["OPENAI_API_KEY"] = <api_key>)
def translate_text_sarvam(text, target_language='hi-IN'):

    url = "https://api.sarvam.ai/translate"

    payload = {
        "input": text,
        "source_language_code": "en-IN",
        "target_language_code": "hi-IN",
        "speaker_gender": "Male",
        "mode": "formal",
        "model": "mayura:v1"
    }
    headers = {
        "api-subscription-key": "906580f6-a1bc-4baf-b7fa-7f29c048f468",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    if response.status_code == 200:
        response = json.loads(response.text)
        translated_text = response['translated_text']
    else:
        print("Failed with status code:", response.status_code)

    return translated_text

def translate_text(text, target_language="Hindi"):
    url = "http://100.123.252.79:5000/translate"
    #url = "http://100.123.252.79:5000/translate_batch"
    payload = {
        "text": text,
        "tgt_language": target_language
        }
    headers= {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json = payload, headers = headers)

    if response.status_code == 200:
        response = response.json()
        translated_text = response.get("translated_text", "")
    
    else:
        print("Failed with status code:", response.status_code)
    
    return translated_text

def translate_text_gpt(text, target_language='Hindi'):
    llm = ChatOpenAI(temperature=0.3, model_name="gpt-4o", max_tokens=512) # or gpt-4 if available
    prompt_template = """
    Act as a linguistic expert in translating documents and text from English to Indic languages. 
    Translate the following text from English to formal {target_language} with high accuracy, formal tone, 
    most appropriate word selection and respecting the grammer rules and order of parts of speech 
    of the target language. Use words with Sanskrit root. Provide best translation by self-evaluating 
    translation quality and also by backtranslating the translated text to the source language and 
    comparing it with the original text. 
    DO not provide any extra text, only provide the best translation. Translate "Maxim" as "नियम".
    English text: {text}
    Translated text: 
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["text", "target_language"])

    summary = llm.invoke(prompt.format(text=text, target_language=target_language))
    return summary.content


def back_translate_text(text, source_language="Hindi"):
    url = "http://100.123.252.79:5000/translate_indic"
    
    payload = {
        "text": text,
        "source_language": source_language
        }

    headers= {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json = payload, headers = headers)

    if response.status_code == 200:
        response = response.json()
        back_translated_text = response.get("translated_text", "")
    
    else:
        print("Failed with status code:", response.status_code)
    
    return back_translated_text

# if __name__ == "__main__":
#     text = """
#     Message on the occasion 
#     of the 69th birthday of Pujya Daaji
#     """
#     #target_language = "Hindi"

#     # target_language = "Telugu"
    
#     translated_text = translate_text_gpt(text)
#     print("translated text :", translated_text)
