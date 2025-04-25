'''PubMed data fetching utilities.'''

import pandas as pd
import asyncio
import aiohttp
import nest_asyncio
from urllib.parse import quote
from aiohttp import ClientSession, TCPConnector
from bs4 import BeautifulSoup
import re
import unicodedata 
import os
import logging

nest_asyncio.apply()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    medical_db = pd.read_csv(os.path.join('data', 'pubmed_medical_info.csv'))
    logger.info("Loaded pubmed_medical_info.csv")
except Exception as e:
    logger.error(f"Error loading pubmed_medical_info.csv: {e}")
    
def fetch_medical_info(disease, symptoms):
    '''Fetch medical info from preloaded PubMed data (pubmed_medical_info.csv).

    Args:
        disease (str): Disease name.
        symptoms (str): User symptoms.

    Returns:
        str: Medical description.

    Raises:
        ValueError: If inputs are invalid.
    '''
    if not disease or not symptoms or not isinstance(disease, str) or not isinstance(symptoms, str):
        raise ValueError('Disease symptom must be non-empty and string formatted')
    try:
        result = medical_db[medical_db['disease'].str.lower() == disease.lower()]
        if not result.empty:
            desc = result['description'].iloc[0]
            # Validate description
            if not desc or len(desc.strip()) < 10 or any(x in desc for x in ['title:', 'abstract:']):
                return f"A condition that may cause {symptoms}."
            
            desc = unicodedata.normalize('NFKD', desc).replace('\xa0', ' ').replace('\u2009', ' ')
            desc = desc.split('...')[0]
            sentences = re.split(r'(?<=[.!?])\s+', desc.strip())
            valid_sentences = []
            for s in sentences:
                s = s.strip()
                if s and s.endswith(('.', '!', '?')):
                    valid_sentences.append(s.rstrip('.!?'))
            if not valid_sentences:
                return f'A condition that may cause {symptoms}.'
            cleaned_desc = '. '.join(valid_sentences)
            return f"A condition {cleaned_desc}. "
        return f"No info available for {disease} yet."
    except Exception as e:
        raise RuntimeError(f'Fetch medical info failed: {e}')
     

async def fetch_pubmed_info(session, disease, semaphore, api_key=None):
    '''Fetch PubMed info for a disease (only for reference).

    Args:
        session (ClientSession): aiohttp session.
        disease (str): Disease name.
        semaphore (asyncio.Semaphore): Concurrency limiter.
        api_key (str, optional): PubMed API key.

    Returns:
        dict: Disease info dictionary (disease: description).
    '''
    if not api_key:
        return {'disease': disease, 'description': "API key required for live PubMed fetch."}
    
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    disease_clean = disease.split(" (")[0]
    search_url = f"{base_url}esearch.fcgi?db=pubmed&term={quote(disease_clean)}[MeSH Terms]+OR+{quote(disease_clean)}[Title/Abstract]+OR+{quote(disease_clean)}&retmode=json&retmax=1&sort=relevance&api_key={api_key}"
    async with semaphore:
        for attempt in range(5):
            try:
                async with session.get(search_url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status == 200:
                        data = await response.json()
                        pmids = data.get("esearchresult", {}).get("idlist", [])
                        if pmids:
                            summary_url = f"{base_url}efetch.fcgi?db=pubmed&id={pmids[0]}&retmode=xml&api_key={api_key}"
                            async with session.get(summary_url, timeout=aiohttp.ClientTimeout(total=15)) as summary_resp:
                                if summary_resp.status == 200:
                                    xml = await summary_resp.text()
                                    soup = BeautifulSoup(xml, 'xml')
                                    abstract = soup.find("AbstractText")
                                    if abstract:
                                        return {'disease': disease, 'description': abstract.text[:500] + "..."}
                                    title = soup.find("ArticleTitle")
                                    return {'disease': disease, 'description': f"Title: {title.text[:500]}..." if title else "No abstract or title found."}
                        return {'disease': disease, 'description': "Consult a healthcare provider for more information."}
                    elif response.status == 429:
                        await asyncio.sleep(5 * (2 ** attempt))
                        continue
                    return {'disease': disease, 'description': f"Search HTTP error: {response.status}"}
            except (asyncio.TimeoutError, aiohttp.ClientConnectionError, aiohttp.ClientOSError) as e:
                if attempt < 4:
                    await asyncio.sleep(2 ** attempt + 1)
                    continue
                return {'disease': disease, 'description': "Connection issue; info unavailable."}
            except Exception as e:
                return {'disease': disease, 'description': "Error retrieving info."}
        return {'disease': disease, 'description': "Failed after retries."}

async def scrape_pubmed_diseases(diseases, api_key=None):
    '''Scrape PubMed for diseases (reference only).

    Args:
        diseases (list): List of disease names.
        api_key (str, optional): PubMed API key.

    Returns:
        list: List of disease info dictionaries.
    '''
    semaphore = asyncio.Semaphore(10)
    async with ClientSession(connector=TCPConnector(limit=10, force_close=True)) as session:
        tasks = {disease: fetch_pubmed_info(session, disease, semaphore, api_key) for disease in diseases}
        results = await asyncio.gather(*tasks.values(), return_exceptions=False)
        for disease, result in zip(tasks.keys(), results):
            return [{"disease": disease, "description": result["description"]}]


def run_pubmed_scrape():
    '''Run PubMed scraping and save results (reference only).'''
    try:
        aug_df = pd.read_csv('data/aug_df.csv')
        diseases = aug_df['Prognosis'].unique()
        medical_info = asyncio.run(scrape_pubmed_diseases(diseases))
        df = pd.DataFrame(medical_info)
        df.to_csv('data/pubmed_medical_info.csv', index=False)
    except Exception as e:
        raise RuntimeError(f'PubMed scraping failed: {e}')
    

if __name__ == '__main__':
    pass