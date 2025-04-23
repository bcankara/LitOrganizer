"""
PDF metadata extraction utilities.

This module provides functions to extract metadata from PDF files, including DOI,
authors, title, year, and other bibliographic information. It also includes 
functions to fetch metadata from external APIs like Crossref and Semantic Scholar.
"""

import re
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

import requests
import pdfplumber
from PIL import Image

# Setup OCR if available (optional dependency)
try:
    import pytesseract
    from pdf2image import convert_from_path
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


# Load API configuration
def load_api_config() -> Dict[str, Any]:
    """
    Load API configuration from config/api_keys.json file.
    
    Returns:
        Dict[str, Any]: Dictionary containing API configuration
    """
    logger = logging.getLogger('litorganizer.parsers')
    config_path = Path(__file__).parent.parent.parent / 'config' / 'api_keys.json'
    
    # Default configuration with all free APIs enabled
    default_config = {
        "crossref": {"enabled": True},
        "openalex": {"enabled": True},
        "datacite": {"enabled": True},
        "europepmc": {"enabled": True},
        "scopus": {"api_key": "", "enabled": False},
        "semantic_scholar": {"api_key": "", "enabled": True},
        "unpaywall": {"email": "", "enabled": False}
    }
    
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                logger.debug("Loaded API configuration from file")
                
                # Merge with default config to ensure all keys exist
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except Exception as e:
            logger.error(f"Error loading API configuration: {e}")
            return default_config
    else:
        logger.warning(f"API configuration file not found at {config_path}, using defaults")
        
        # Create directory if it doesn't exist
        os.makedirs(config_path.parent, exist_ok=True)
        
        # Write default config
        try:
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
            logger.debug("Created default API configuration file")
        except Exception as e:
            logger.error(f"Error creating default API configuration file: {e}")
        
        return default_config


def extract_doi(pdf_path: Union[str, Path], use_ocr: bool = False) -> Optional[str]:
    """
    Extract DOI from a PDF file.
    
    Args:
        pdf_path (Union[str, Path]): Path to the PDF file
        use_ocr (bool): Whether to use OCR for scanned PDFs
        
    Returns:
        Optional[str]: Extracted DOI or None if not found
    """
    logger = logging.getLogger('litorganizer.parsers')
    pdf_path = Path(pdf_path)
    
    # DOI regex patterns - Always starts with 10. prefix
    doi_patterns = [
        r'doi\.org/+(10\.[0-9]{4,}(?:\.[0-9]+)*\/[a-zA-Z0-9\._\(\)\-\+\/]+)',
        r'DOI:\s*(10\.[0-9]{4,}(?:\.[0-9]+)*\/[a-zA-Z0-9\._\(\)\-\+\/]+)',
        r'doi:\s*(10\.[0-9]{4,}(?:\.[0-9]+)*\/[a-zA-Z0-9\._\(\)\-\+\/]+)',
        r'(?:^|[^a-zA-Z0-9])(10\.[0-9]{4,}(?:\.[0-9]+)*\/[a-zA-Z0-9\._\(\)\-\+\/]+)',
        r'https?://(?:dx\.)?doi\.org/+(10\.[0-9]{4,}(?:\.[0-9]+)*\/[a-zA-Z0-9\._\(\)\-\+\/]+)'
    ]
    
    try:
        # Try to extract DOI using pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            # Check metadata first
            if pdf.metadata and 'doi' in pdf.metadata and pdf.metadata['doi']:
                logger.debug(f"DOI found in metadata: {pdf.metadata['doi']}")
                return pdf.metadata['doi']
            
            # Extract text from first few pages
            text = ""
            for i in range(min(5, len(pdf.pages))):
                page_text = pdf.pages[i].extract_text()
                if page_text:
                    text += page_text + "\n"
            
            # Search for DOI in text
            for pattern in doi_patterns:
                matches = re.search(pattern, text, re.IGNORECASE)
                if matches:
                    doi = matches.group(0).strip()
                    logger.debug(f"DOI found in text: {doi}")
                    return doi
            
            # If no DOI found and OCR is enabled, try OCR
            if not text.strip() and use_ocr and OCR_AVAILABLE:
                logger.debug("No text extracted, trying OCR...")
                return extract_doi_with_ocr(pdf_path, doi_patterns)
        
        logger.debug("No DOI found in PDF")
        return None
    
    except Exception as e:
        logger.error(f"Error extracting DOI: {e}")
        return None


def extract_doi_with_ocr(pdf_path: Union[str, Path], doi_patterns: List[str]) -> Optional[str]:
    """
    Extract DOI from a PDF file using OCR.
    
    Args:
        pdf_path (Union[str, Path]): Path to the PDF file
        doi_patterns (List[str]): List of regex patterns for DOI extraction
        
    Returns:
        Optional[str]: Extracted DOI or None if not found
    """
    logger = logging.getLogger('pdf_citation_tool.parsers')
    
    if not OCR_AVAILABLE:
        logger.warning("OCR dependencies not available. Please install pytesseract and pdf2image.")
        return None
    
    try:
        # Convert first page of PDF to image
        logger.debug("Converting PDF to image for OCR...")
        images = convert_from_path(pdf_path, first_page=1, last_page=3)
        
        # Perform OCR on each image
        text = ""
        for img in images:
            text += pytesseract.image_to_string(img) + "\n"
        
        # Search for DOI in OCR text
        for pattern in doi_patterns:
            matches = re.search(pattern, text, re.IGNORECASE)
            if matches:
                doi = matches.group(0).strip()
                logger.debug(f"DOI found with OCR: {doi}")
                return doi
        
        logger.debug("No DOI found with OCR")
        return None
    
    except Exception as e:
        logger.error(f"Error performing OCR: {e}")
        return None


def get_metadata_from_crossref(doi: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve metadata from Crossref API using DOI.
    
    Args:
        doi (str): Digital Object Identifier
        
    Returns:
        Optional[Dict[str, Any]]: Metadata dictionary or None if retrieval fails
    """
    logger = logging.getLogger('litorganizer.parsers')
    logger.debug(f"Querying Crossref API for DOI: {doi}")
    
    try:
        url = f"https://api.crossref.org/works/{doi}"
        headers = {
            "User-Agent": "LitOrganizer/1.0 (mailto:user@example.com)",
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            message = data.get("message", {})
            
            # Extract metadata - only necessary fields
            metadata = {
                "doi": doi,
                "title": "",
                "authors": [],
                "year": "",
                "journal": "",
                "category": "",
                "source": "crossref"
            }
            
            # Title
            if "title" in message and message["title"]:
                metadata["title"] = message["title"][0]
            
            # Authors - we only take surnames
            if "author" in message:
                authors = []
                for author in message["author"]:
                    if "family" in author:
                        authors.append(author["family"])
                metadata["authors"] = authors
            
            # Year
            date_fields = ["published-print", "published-online", "created"]
            for field in date_fields:
                if field in message and "date-parts" in message[field]:
                    date_parts = message[field]["date-parts"]
                    if date_parts and date_parts[0] and date_parts[0][0]:
                        metadata["year"] = str(date_parts[0][0])
                        break
            
            # Journal
            if "container-title" in message and message["container-title"]:
                metadata["journal"] = message["container-title"][0]
            
            # Category/Subject
            if "subject" in message and message["subject"]:
                metadata["category"] = message["subject"][0]
            
            logger.debug(f"Successfully retrieved metadata from Crossref: {metadata}")
            return metadata
        else:
            logger.warning(f"Failed to retrieve data from Crossref. Status code: {response.status_code}")
            return None
    
    except Exception as e:
        logger.error(f"Error querying Crossref API: {e}")
        return None


def get_metadata_from_openalex(doi: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve metadata from OpenAlex API using DOI.
    
    Args:
        doi (str): Digital Object Identifier
        
    Returns:
        Optional[Dict[str, Any]]: Metadata dictionary or None if retrieval fails
    """
    logger = logging.getLogger('litorganizer.parsers')
    logger.debug(f"Querying OpenAlex API for DOI: {doi}")
    
    # Read API configurations
    config = load_api_config()
    
    # Get email information
    email = config.get("openalex", {}).get("email", "user@example.com")
    
    try:
        # OpenAlex API URL
        url = f"https://api.openalex.org/works/https://doi.org/{doi}"
        headers = {
            "User-Agent": f"LitOrganizer/1.0 (mailto:{email})",
            "Accept": "application/json"
        }
        
        logger.debug(f"OpenAlex request with email: {email}")
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # Log raw data
            logger.debug(f"Raw OpenAlex data received with keys: {list(data.keys())}")
            
            # Extract metadata
            metadata = {
                "doi": doi,
                "title": "",
                "authors": [],
                "year": "",
                "journal": "",
                "volume": "",
                "issue": "",
                "pages": "",
                "category": "",
                "source": "openalex"
            }
            
            # Title
            if "title" in data:
                metadata["title"] = data["title"]
            
            # Authors - We need family and given names if possible
            if "authorships" in data:
                authors_list = []
                for authorship in data["authorships"]:
                    if "author" in authorship and "display_name" in authorship["author"]:
                        author_name = authorship["author"]["display_name"]
                        # Simple split, assuming last word is family name
                        name_parts = author_name.split()
                        family_name = name_parts[-1] if len(name_parts) > 0 else author_name
                        given_name = " ".join(name_parts[:-1]) if len(name_parts) > 1 else ""
                        authors_list.append({"family": family_name, "given": given_name, "name": author_name}) # Store full name too
                metadata["authors"] = authors_list # Store list of dicts
            
            # Year
            if "publication_date" in data and data["publication_date"]:
                # Ensure publication_date is not None before splitting
                year = str(data["publication_date"]).split("-")[0]
                metadata["year"] = year
            elif "publication_year" in data: # Fallback to publication_year
                 metadata["year"] = str(data["publication_year"])
            
            # Journal
            # Check multiple possible locations for journal/source info
            journal_name = None
            if data.get("primary_location") and data["primary_location"].get("source") and data["primary_location"]["source"].get("display_name"):
                journal_name = data["primary_location"]["source"]["display_name"]
            elif data.get("host_venue") and data["host_venue"].get("display_name"):
                 journal_name = data["host_venue"].get("display_name")
            
            if journal_name:
                metadata["journal"] = journal_name

            # Volume, issue, pages
            if "biblio" in data:
                biblio = data["biblio"]
                if "volume" in biblio:
                    metadata["volume"] = biblio["volume"]
                if "issue" in biblio:
                    metadata["issue"] = biblio["issue"]
                if "first_page" in biblio and "last_page" in biblio:
                    metadata["pages"] = f"{biblio['first_page']}-{biblio['last_page']}"
            
            # CATEGORY/SUBJECT EXTRACTION STRATEGY (BY PRIORITY)
            # Store results in 'subjects' as a list for consistency
            subjects_list = []
            category_source = "None"
            
            # 1. Use concepts field
            if data.get("concepts"):
                sorted_concepts = sorted(data["concepts"], key=lambda x: x.get("score", 0), reverse=True)
                # Take top concepts above a threshold
                for concept in sorted_concepts:
                     if concept.get("score", 0) > 0.4 and concept.get("display_name"):
                         subjects_list.append(concept["display_name"])
                         # Limit the number of subjects if desired, e.g., top 3
                         # if len(subjects_list) >= 3: break 
                if subjects_list:
                    category_source = "Concepts"
                    logger.info(f"Subjects from OpenAlex Concepts: {subjects_list}")

            # 2. Use primary_topic if no concepts found
            if not subjects_list and data.get("primary_topic") and data["primary_topic"].get("display_name"):
                topic_name = data["primary_topic"]["display_name"]
                if topic_name:
                    subjects_list.append(topic_name)
                    category_source = "Primary Topic"
                    logger.info(f"Subject from OpenAlex Primary Topic: {topic_name}")
            
            # 3. Use domain if still no subject found
            # (Consider if domain is too broad - maybe skip?)
            # if not subjects_list and data.get(...domain...):
            #     domain_name = ...
            #     subjects_list.append(domain_name)
            #     category_source = "Domain"
            #     logger.info(f"Subject from OpenAlex Domain: {domain_name}")

            # Assign the list to the 'subjects' key
            metadata["subjects"] = subjects_list
            
            if not subjects_list:
                logger.warning("No category/subject could be determined from OpenAlex data")
            
            # Clean up the old 'category' key if it exists from initialization
            if "category" in metadata:
                 del metadata["category"]
                 
            # Log the final constructed metadata for debugging
            logger.debug(f"Parsed OpenAlex metadata: {metadata}")
            return metadata
        elif response.status_code == 404:
             logger.warning(f"DOI {doi} not found in OpenAlex (404).")
             return None
    
    except Exception as e:
        logger.error(f"Error querying OpenAlex API: {e}")
        return None


def get_metadata_from_datacite(doi: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve metadata from DataCite API using DOI.
    
    Args:
        doi (str): Digital Object Identifier
        
    Returns:
        Optional[Dict[str, Any]]: Metadata dictionary or None if retrieval fails
    """
    logger = logging.getLogger('litorganizer.parsers')
    logger.debug(f"Querying DataCite API for DOI: {doi}")
    
    try:
        # DataCite API URL
        url = f"https://api.datacite.org/dois/{doi}"
        headers = {
            "User-Agent": "LitOrganizer/1.0 (mailto:user@example.com)",
            "Accept": "application/vnd.api+json"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            if "data" not in data or "attributes" not in data["data"]:
                logger.warning("Invalid response format from DataCite API")
                return None
                
            attributes = data["data"]["attributes"]
            
            # Extract metadata
            metadata = {
                "doi": doi,
                "title": "",
                "authors": [],
                "year": "",
                "journal": "",
                "volume": "",
                "issue": "",
                "pages": "",
                "category": "",
                "source": "datacite"
            }
            
            # Title
            if "titles" in attributes and attributes["titles"] and "title" in attributes["titles"][0]:
                metadata["title"] = attributes["titles"][0]["title"]
            
            # Authors - sadece soyadları alıyoruz
            if "creators" in attributes:
                authors = []
                for creator in attributes["creators"]:
                    if "name" in creator:
                        name_parts = creator["name"].split(",")
                        if len(name_parts) > 0:
                            authors.append(name_parts[0].strip())
                    elif "familyName" in creator:
                        authors.append(creator["familyName"])
                metadata["authors"] = authors
            
            # Year
            if "publicationYear" in attributes:
                metadata["year"] = str(attributes["publicationYear"])
            
            # Journal & Publisher
            if "container" in attributes:
                metadata["journal"] = attributes["container"].get("title", "")
                
                if "volume" in attributes["container"]:
                    metadata["volume"] = attributes["container"]["volume"]
                if "issue" in attributes["container"]:
                    metadata["issue"] = attributes["container"]["issue"]
                if "firstPage" in attributes["container"] and "lastPage" in attributes["container"]:
                    metadata["pages"] = f"{attributes['container']['firstPage']}-{attributes['container']['lastPage']}"
            
            # Category
            if "subjects" in attributes and attributes["subjects"] and "subject" in attributes["subjects"][0]:
                metadata["category"] = attributes["subjects"][0]["subject"]
            
            logger.debug(f"Successfully retrieved metadata from DataCite")
            return metadata
        else:
            logger.warning(f"Failed to retrieve data from DataCite. Status code: {response.status_code}")
            return None
    
    except Exception as e:
        logger.error(f"Error querying DataCite API: {e}")
        return None


def get_metadata_from_europepmc(doi: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve metadata from Europe PMC API using DOI.
    
    Args:
        doi (str): Digital Object Identifier
        
    Returns:
        Optional[Dict[str, Any]]: Metadata dictionary or None if retrieval fails
    """
    logger = logging.getLogger('litorganizer.parsers')
    logger.debug(f"Querying Europe PMC API for DOI: {doi}")
    
    try:
        # Europe PMC API URL
        url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:{doi}&format=json"
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            if "resultList" not in data or "result" not in data["resultList"] or not data["resultList"]["result"]:
                logger.warning("No results found in Europe PMC API")
                return None
                
            result = data["resultList"]["result"][0]
            
            # Extract metadata
            metadata = {
                "doi": doi,
                "title": "",
                "authors": [],
                "year": "",
                "journal": "",
                "volume": "",
                "issue": "",
                "pages": "",
                "category": "",
                "source": "europepmc"
            }
            
            # Title
            if "title" in result:
                metadata["title"] = result["title"]
            
            # Authors - sadece soyadları alıyoruz
            if "authorList" in result and "author" in result["authorList"]:
                authors = []
                for author in result["authorList"]["author"]:
                    if "lastName" in author:
                        authors.append(author["lastName"])
                metadata["authors"] = authors
            
            # Year
            if "pubYear" in result:
                metadata["year"] = result["pubYear"]
            
            # Journal
            if "journalTitle" in result:
                metadata["journal"] = result["journalTitle"]
            
            # Volume, issue, pages
            if "journalVolume" in result:
                metadata["volume"] = result["journalVolume"]
            if "journalIssue" in result:
                metadata["issue"] = result["journalIssue"]
            if "pageInfo" in result:
                metadata["pages"] = result["pageInfo"]
            
            # Category/Keywords
            if "keywordList" in result and "keyword" in result["keywordList"]:
                metadata["category"] = result["keywordList"]["keyword"][0]
            
            logger.debug(f"Successfully retrieved metadata from Europe PMC")
            return metadata
        else:
            logger.warning(f"Failed to retrieve data from Europe PMC. Status code: {response.status_code}")
            return None
    
    except Exception as e:
        logger.error(f"Error querying Europe PMC API: {e}")
        return None


def get_metadata_from_scopus(doi: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve metadata from Scopus API using DOI. Requires API key.
    
    Args:
        doi (str): Digital Object Identifier
        
    Returns:
        Optional[Dict[str, Any]]: Metadata dictionary or None if retrieval fails
    """
    logger = logging.getLogger('litorganizer.parsers')
    
    # Check if API key is configured and enabled
    config = load_api_config()
    if not config.get("scopus", {}).get("enabled", False):
        logger.debug("Scopus API is disabled in configuration")
        return None
        
    api_key = config.get("scopus", {}).get("api_key", "")
    if not api_key:
        logger.warning("Scopus API key is not configured")
        return None
    
    logger.debug(f"Querying Scopus API for DOI: {doi}")
    
    try:
        # Scopus API URL
        url = f"https://api.elsevier.com/content/abstract/doi/{doi}"
        headers = {
            "X-ELS-APIKey": api_key,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # Navigate through the Scopus API response structure
            if "abstracts-retrieval-response" not in data:
                logger.warning("Invalid response format from Scopus API")
                return None
                
            abstract_data = data["abstracts-retrieval-response"]
            
            # Extract metadata
            metadata = {
                "doi": doi,
                "title": "",
                "authors": [],
                "year": "",
                "journal": "",
                "volume": "",
                "issue": "",
                "pages": "",
                "category": "",
                "source": "scopus"
            }
            
            # Title
            if "coredata" in abstract_data and "dc:title" in abstract_data["coredata"]:
                metadata["title"] = abstract_data["coredata"]["dc:title"]
            
            # Authors - sadece soyadları alıyoruz
            if "authors" in abstract_data and "author" in abstract_data["authors"]:
                authors = []
                for author in abstract_data["authors"]["author"]:
                    if "ce:surname" in author:
                        authors.append(author["ce:surname"])
                metadata["authors"] = authors
            
            # Year
            if "coredata" in abstract_data and "prism:coverDate" in abstract_data["coredata"]:
                year = abstract_data["coredata"]["prism:coverDate"].split("-")[0]
                metadata["year"] = year
            
            # Journal
            if "coredata" in abstract_data and "prism:publicationName" in abstract_data["coredata"]:
                metadata["journal"] = abstract_data["coredata"]["prism:publicationName"]
            
            # Volume, issue, pages
            if "coredata" in abstract_data:
                coredata = abstract_data["coredata"]
                if "prism:volume" in coredata:
                    metadata["volume"] = coredata["prism:volume"]
                if "prism:issueIdentifier" in coredata:
                    metadata["issue"] = coredata["prism:issueIdentifier"]
                if "prism:pageRange" in coredata:
                    metadata["pages"] = coredata["prism:pageRange"]
            
            # Category
            if "subject-areas" in abstract_data and "subject-area" in abstract_data["subject-areas"]:
                if len(abstract_data["subject-areas"]["subject-area"]) > 0:
                    metadata["category"] = abstract_data["subject-areas"]["subject-area"][0]["$"]
            
            logger.debug(f"Successfully retrieved metadata from Scopus")
            return metadata
        elif response.status_code == 401 or response.status_code == 403:
            logger.warning(f"Authentication failed for Scopus API (invalid API key)")
            return None
        else:
            logger.warning(f"Failed to retrieve data from Scopus. Status code: {response.status_code}")
            return None
    
    except Exception as e:
        logger.error(f"Error querying Scopus API: {e}")
        return None


def get_metadata_from_semantic_scholar(doi: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve metadata from Semantic Scholar API using DOI.
    Optional API key for higher rate limits.
    
    Args:
        doi (str): Digital Object Identifier
        
    Returns:
        Optional[Dict[str, Any]]: Metadata dictionary or None if retrieval fails
    """
    logger = logging.getLogger('litorganizer.parsers')
    
    # Check if API is enabled
    config = load_api_config()
    if not config.get("semantic_scholar", {}).get("enabled", True):
        logger.debug("Semantic Scholar API is disabled in configuration")
        return None
    
    # Get API key if available (optional)
    api_key = config.get("semantic_scholar", {}).get("api_key", "")
    
    logger.debug(f"Querying Semantic Scholar API for DOI: {doi}")
    
    try:
        # Semantic Scholar API URL
        url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=title,authors,year,journal,volume,venue,publicationTypes,topics,fieldsOfStudy"
        
        headers = {
            "Accept": "application/json"
        }
        
        # Add API key if available
        if api_key:
            headers["x-api-key"] = api_key
            
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # Extract metadata
            metadata = {
                "doi": doi,
                "title": "",
                "authors": [],
                "year": "",
                "journal": "",
                "volume": "",
                "issue": "",
                "pages": "",
                "category": "",
                "source": "semantic_scholar"
            }
            
            # Title
            if "title" in data:
                metadata["title"] = data["title"]
            
            # Authors - sadece soyadları alıyoruz
            if "authors" in data:
                authors = []
                for author in data["authors"]:
                    if "name" in author:
                        # Soyadını çıkarmak için son kelimeyi al
                        author_name = author["name"]
                        last_name = author_name.split()[-1]
                        authors.append(last_name)
                metadata["authors"] = authors
            
            # Year
            if "year" in data:
                metadata["year"] = str(data["year"])
            
            # Journal & Publication Info
            if "journal" in data:
                metadata["journal"] = data["journal"].get("name", "")
                metadata["volume"] = data["journal"].get("volume", "")
                metadata["issue"] = data["journal"].get("issue", "")
                
            elif "venue" in data:
                metadata["journal"] = data["venue"]
            
            # Category
            if "fieldsOfStudy" in data and data["fieldsOfStudy"] and len(data["fieldsOfStudy"]) > 0:
                metadata["category"] = data["fieldsOfStudy"][0]
            elif "topics" in data and data["topics"] and len(data["topics"]) > 0:
                metadata["category"] = data["topics"][0]["name"]
            
            logger.debug(f"Successfully retrieved metadata from Semantic Scholar")
            return metadata
        else:
            logger.warning(f"Failed to retrieve data from Semantic Scholar. Status code: {response.status_code}")
            return None
    
    except Exception as e:
        logger.error(f"Error querying Semantic Scholar API: {e}")
        return None


def get_metadata_from_unpaywall(doi: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve metadata from Unpaywall API using DOI. Requires email.
    
    Args:
        doi (str): Digital Object Identifier
        
    Returns:
        Optional[Dict[str, Any]]: Metadata dictionary or None if retrieval fails
    """
    logger = logging.getLogger('litorganizer.parsers')
    
    # Check if API is enabled and email is configured
    config = load_api_config()
    if not config.get("unpaywall", {}).get("enabled", False):
        logger.debug("Unpaywall API is disabled in configuration")
        return None
        
    email = config.get("unpaywall", {}).get("email", "")
    if not email:
        logger.warning("Unpaywall email is not configured")
        return None
    
    logger.debug(f"Querying Unpaywall API for DOI: {doi}")
    
    try:
        # Unpaywall API URL
        url = f"https://api.unpaywall.org/v2/{doi}?email={email}"
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # Extract metadata
            metadata = {
                "doi": doi,
                "title": "",
                "authors": [],
                "year": "",
                "journal": "",
                "volume": "",
                "issue": "",
                "pages": "",
                "category": "",
                "source": "unpaywall"
            }
            
            # Title
            if "title" in data:
                metadata["title"] = data["title"]
            
            # Year
            if "year" in data:
                metadata["year"] = str(data["year"])
            
            # Journal
            if "journal_name" in data:
                metadata["journal"] = data["journal_name"]
            
            # Volume, issue
            if "journal_volume" in data:
                metadata["volume"] = data["journal_volume"]
            if "journal_issue" in data:
                metadata["issue"] = data["journal_issue"]
            
            # No direct author information in Unpaywall
            # No direct category information in Unpaywall
            
            logger.debug(f"Successfully retrieved partial metadata from Unpaywall")
            return metadata
        else:
            logger.warning(f"Failed to retrieve data from Unpaywall. Status code: {response.status_code}")
            return None
    
    except Exception as e:
        logger.error(f"Error querying Unpaywall API: {e}")
        return None


def get_metadata_from_multiple_sources(doi: str) -> Optional[Dict[str, Any]]:
    """
    Try to retrieve metadata from multiple sources in sequence.
    
    Args:
        doi (str): Digital Object Identifier
        
    Returns:
        Optional[Dict[str, Any]]: Metadata dictionary from the first successful source or None if all fail
    """
    logger = logging.getLogger('litorganizer.parsers')
    logger.info(f"Attempting to retrieve metadata for DOI: {doi} from multiple sources")
    
    # Try each API in sequence based on configuration
    config = load_api_config()
    
    # ÖNCELİK: OpenAlex (en zengin kategori bilgisi için)
    if config.get("openalex", {}).get("enabled", True):
        metadata = get_metadata_from_openalex(doi)
        if metadata and metadata.get("title"):
            logger.info(f"Retrieved metadata from OpenAlex for DOI: {doi}")
            
            # Verileri detaylı logla
            logger.debug(f"OpenAlex metadata: journal='{metadata.get('journal')}', "
                         f"category='{metadata.get('category')}', year='{metadata.get('year')}'")
            
            # Kategori bilgisini kontrol et
            if metadata.get('category'):
                logger.info(f"Category from OpenAlex: {metadata.get('category')}")
                return metadata
            else:
                logger.warning("No category information found in OpenAlex metadata")
                return metadata
    
    # Diğer API'ler
    if config.get("crossref", {}).get("enabled", True):
        metadata = get_metadata_from_crossref(doi)
        if metadata and metadata.get("title"):
            logger.info(f"Retrieved metadata from Crossref for DOI: {doi}")
            
            # Verileri detaylı logla
            logger.debug(f"Crossref metadata: journal='{metadata.get('journal')}', "
                         f"category='{metadata.get('category')}', year='{metadata.get('year')}'")
            return metadata
    
    if config.get("datacite", {}).get("enabled", True):
        metadata = get_metadata_from_datacite(doi)
        if metadata and metadata.get("title"):
            logger.info(f"Retrieved metadata from DataCite for DOI: {doi}")
            
            # Verileri detaylı logla
            logger.debug(f"DataCite metadata: journal='{metadata.get('journal')}', "
                          f"category='{metadata.get('category')}', year='{metadata.get('year')}'")
            
            return metadata
    
    if config.get("europepmc", {}).get("enabled", True):
        metadata = get_metadata_from_europepmc(doi)
        if metadata and metadata.get("title"):
            logger.info(f"Retrieved metadata from Europe PMC for DOI: {doi}")
            
            # Verileri detaylı logla
            logger.debug(f"Europe PMC metadata: journal='{metadata.get('journal')}', "
                          f"category='{metadata.get('category')}', year='{metadata.get('year')}'")
            
            return metadata
    
    # APIs requiring keys
    if config.get("semantic_scholar", {}).get("enabled", True):
        metadata = get_metadata_from_semantic_scholar(doi)
        if metadata and metadata.get("title"):
            logger.info(f"Retrieved metadata from Semantic Scholar for DOI: {doi}")
            
            # Verileri detaylı logla
            logger.debug(f"Semantic Scholar metadata: journal='{metadata.get('journal')}', "
                          f"category='{metadata.get('category')}', year='{metadata.get('year')}'")
            
            return metadata
    
    if config.get("scopus", {}).get("enabled", False) and config.get("scopus", {}).get("api_key", ""):
        metadata = get_metadata_from_scopus(doi)
        if metadata and metadata.get("title"):
            logger.info(f"Retrieved metadata from Scopus for DOI: {doi}")
            
            # Verileri detaylı logla
            logger.debug(f"Scopus metadata: journal='{metadata.get('journal')}', "
                          f"category='{metadata.get('category')}', year='{metadata.get('year')}'")
            
            return metadata
    
    if config.get("unpaywall", {}).get("enabled", False) and config.get("unpaywall", {}).get("email", ""):
        metadata = get_metadata_from_unpaywall(doi)
        if metadata and metadata.get("title"):
            logger.info(f"Retrieved metadata from Unpaywall for DOI: {doi}")
            
            # Verileri detaylı logla
            logger.debug(f"Unpaywall metadata: journal='{metadata.get('journal')}', "
                          f"category='{metadata.get('category')}', year='{metadata.get('year')}'")
            
            return metadata
    
    logger.warning(f"Failed to retrieve metadata from any source for DOI: {doi}")
    return None


def extract_metadata_from_content(pdf_path: Union[str, Path], use_ocr: bool = False) -> Dict[str, Any]:
    """
    Extract metadata from PDF content using text mining.
    
    Args:
        pdf_path (Union[str, Path]): Path to the PDF file
        use_ocr (bool): Whether to use OCR for scanned PDFs
        
    Returns:
        Dict[str, Any]: Extracted metadata
    """
    logger = logging.getLogger('pdf_citation_tool.parsers')
    pdf_path = Path(pdf_path)
    
    # Initialize metadata
    metadata = {
        "title": "",
        "authors": [],
        "year": "",
        "journal": "",
        "volume": "",
        "issue": "",
        "pages": ""
    }
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Check for metadata in PDF
            if pdf.metadata:
                if 'Title' in pdf.metadata and pdf.metadata['Title']:
                    metadata["title"] = pdf.metadata['Title']
                if 'Author' in pdf.metadata and pdf.metadata['Author']:
                    metadata["authors"] = [pdf.metadata['Author']]
                if 'CreationDate' in pdf.metadata and pdf.metadata['CreationDate']:
                    year_match = re.search(r'(19|20)\d{2}', pdf.metadata['CreationDate'])
                    if year_match:
                        metadata["year"] = year_match.group(0)
            
            # Extract text from first few pages
            text = ""
            for i in range(min(5, len(pdf.pages))):
                page_text = pdf.pages[i].extract_text()
                if page_text:
                    text += page_text + "\n"
            
            # If no text extracted and OCR is enabled, try OCR
            if not text.strip() and use_ocr and OCR_AVAILABLE:
                logger.debug("No text extracted, trying OCR...")
                text = extract_text_with_ocr(pdf_path)
            
            # If still no text, use filename as title
            if not text.strip():
                logger.warning(f"No text could be extracted from {pdf_path.name}")
                if not metadata["title"]:
                    metadata["title"] = pdf_path.stem.replace("_", " ").replace("-", " ")
                return metadata
            
            # Extract title if not already found
            if not metadata["title"]:
                metadata["title"] = extract_title_from_text(text)
            
            # Extract authors if not already found
            if not metadata["authors"]:
                metadata["authors"] = extract_authors_from_text(text)
            
            # Extract year if not already found
            if not metadata["year"]:
                metadata["year"] = extract_year_from_text(text)
            
            # Extract journal information
            if not metadata["journal"]:
                journal_info = extract_journal_info_from_text(text)
                metadata.update(journal_info)
            
            return metadata
    
    except Exception as e:
        logger.error(f"Error extracting metadata from content: {e}")
        # Fallback to filename
        metadata["title"] = pdf_path.stem.replace("_", " ").replace("-", " ")
        metadata["authors"] = ["Unknown Author"]
        metadata["year"] = ""
        return metadata


def extract_text_with_ocr(pdf_path: Union[str, Path]) -> str:
    """
    Extract text from a PDF file using OCR.
    
    Args:
        pdf_path (Union[str, Path]): Path to the PDF file
        
    Returns:
        str: Extracted text
    """
    logger = logging.getLogger('pdf_citation_tool.parsers')
    
    if not OCR_AVAILABLE:
        logger.warning("OCR dependencies not available. Please install pytesseract and pdf2image.")
        return ""
    
    try:
        # Convert first few pages of PDF to images
        logger.debug("Converting PDF to images for OCR...")
        images = convert_from_path(pdf_path, first_page=1, last_page=5)
        
        # Perform OCR on each image
        text = ""
        for img in images:
            text += pytesseract.image_to_string(img) + "\n"
        
        return text
    
    except Exception as e:
        logger.error(f"Error performing OCR: {e}")
        return ""


def extract_title_from_text(text: str) -> str:
    """
    Extract title from text content.
    
    Args:
        text (str): Text content from PDF
        
    Returns:
        str: Extracted title
    """
    # Common patterns for academic paper titles
    title_patterns = [
        # Title usually appears at the beginning of the paper
        r'^([^\n]+)\n',
        # Title sometimes appears after pattern like "Title:" or "TITLE:"
        r'(?i)title[:\s]+([^\n]+)',
        # Title might be in larger font or bold (hard to detect in plain text)
        r'^[\s\n]*([A-Z][^.!?\n]{10,150})[.!?]?[\s\n]'
    ]
    
    for pattern in title_patterns:
        match = re.search(pattern, text.strip())
        if match:
            title = match.group(1).strip()
            # Exclude likely non-titles (very short or containing specific keywords)
            if (len(title) > 10 and 
                not re.search(r'\b(abstract|introduction|keywords|references)\b', title.lower()) and
                not re.search(r'\b(doi|journal|volume|issue|vol|no)\b', title.lower())):
                return title
    
    # If no good match, try first non-empty line
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if lines:
        return lines[0]
    
    return "Unknown Title"


def extract_authors_from_text(text: str) -> List[str]:
    """
    Extract author names from text content.
    
    Args:
        text (str): Text content from PDF
        
    Returns:
        List[str]: List of author names
    """
    lines = text.split('\n')
    potential_author_lines = []
    
    # Look for potential author lines (often appears after title)
    for i, line in enumerate(lines[:20]):  # Check first 20 lines
        line = line.strip()
        # Author lists often contain commas, "and", or affiliations with superscripts
        if (',' in line or ' and ' in line.lower() or 
            re.search(r'[A-Z][a-z]+ [A-Z][a-z]+', line)):
            # Skip lines that are likely not author lists
            if not re.search(r'\b(abstract|keywords|introduction|doi)\b', line.lower()):
                potential_author_lines.append(line)
    
    authors = []
    if potential_author_lines:
        # Take the most likely author line (usually the first one found)
        author_line = potential_author_lines[0]
        
        # Split by common author separators
        author_parts = re.split(r',\s*|\s+and\s+|\s*&\s*', author_line)
        
        # Clean up author names
        for part in author_parts:
            # Remove affiliations marked with superscripts/numbers
            author = re.sub(r'\s*[¹²³⁴⁵⁶⁷⁸⁹\d,*†‡#]+\s*$', '', part.strip())
            author = re.sub(r'^\s*[¹²³⁴⁵⁶⁷⁸⁹\d,*†‡#]+\s*', '', author)
            
            if author and len(author) > 2:  # Ensure name is not just a single character
                authors.append(author)
    
    if not authors:
        authors = ["Unknown Author"]
    
    return authors


def extract_year_from_text(text: str) -> str:
    """
    Extract publication year from text content.
    
    Args:
        text (str): Text content from PDF
        
    Returns:
        str: Publication year
    """
    # Look for year patterns (4-digit numbers that could be years)
    year_pattern = r'\b(19|20)\d{2}\b'
    
    # First, try specific patterns that often indicate publication year
    specific_patterns = [
        r'©\s*(20\d{2})',  # Copyright year
        r'published[\s:]+.*?(20\d{2})',  # Published in...
        r'received[\s:]+.*?(20\d{2})',  # Received in...
        r'accepted[\s:]+.*?(20\d{2})',  # Accepted in...
        r'\(([12]\d{3})\)',  # Year in parentheses, often in citations
    ]
    
    for pattern in specific_patterns:
        match = re.search(pattern, text.lower())
        if match:
            return match.group(1)
    
    # If no specific patterns matched, find all years and take the most recent one
    # that appears in the first 20% of the document (likely publication date, not references)
    years = re.findall(year_pattern, text[:int(len(text) * 0.2)])
    if years:
        return max(years)  # Return the most recent year found
    
    # If still not found, look in the whole document
    years = re.findall(year_pattern, text)
    if years:
        return max(years)
    
    return ""


def extract_journal_info_from_text(text: str) -> Dict[str, str]:
    """
    Extract journal information from text content.
    
    Args:
        text (str): Text content from PDF
        
    Returns:
        Dict[str, str]: Dictionary with journal, volume, issue, and pages
    """
    journal_info = {
        "journal": "",
        "volume": "",
        "issue": "",
        "pages": ""
    }
    
    # Common patterns for journal information
    journal_pattern = r'([A-Z][A-Za-z\s&]+)\s+(\d+)[,:]?\s*(\(\d+\))?,?\s*(\d+[-–]\d+)?'
    
    match = re.search(journal_pattern, text[:int(len(text) * 0.3)])
    if match:
        groups = match.groups()
        if groups[0]:
            journal_info["journal"] = groups[0].strip()
        if groups[1]:
            journal_info["volume"] = groups[1].strip()
        if groups[2]:
            # Remove parentheses from issue
            journal_info["issue"] = groups[2].strip().strip('()')
        if groups[3]:
            journal_info["pages"] = groups[3].strip()
    
    return journal_info


def extract_alternative_identifiers(pdf_path: Union[str, Path], use_ocr: bool = False) -> Dict[str, str]:
    """
    Extract alternative identifiers from a PDF file.
    
    Args:
        pdf_path (Union[str, Path]): Path to the PDF file
        use_ocr (bool): Whether to use OCR for scanned PDFs
        
    Returns:
        Dict[str, str]: Dictionary of identifier types and values
    """
    logger = logging.getLogger('pdf_citation_tool.parsers')
    pdf_path = Path(pdf_path)
    
    # Initialize identifiers dictionary
    identifiers = {
        "issn": None,
        "isbn": None,
        "pmid": None,
        "arxiv": None
    }
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Extract text from first few pages
            text = ""
            for i in range(min(5, len(pdf.pages))):
                page_text = pdf.pages[i].extract_text()
                if page_text:
                    text += page_text + "\n"
            
            # If no text extracted and OCR is enabled, try OCR
            if not text.strip() and use_ocr and OCR_AVAILABLE:
                logger.debug("No text extracted, trying OCR for identifiers...")
                text = extract_text_with_ocr(pdf_path)
            
            # ISSN pattern: ISSN 1234-5678 or ISSN: 1234-5678
            issn_patterns = [
                r'ISSN\s*:?\s*(\d{4}-\d{4})',
                r'ISSN\s*:?\s*(\d{4}\s+\d{4})',
                r'ISSN\s*:?\s*(\d{8})'
            ]
            
            for pattern in issn_patterns:
                matches = re.search(pattern, text, re.IGNORECASE)
                if matches:
                    issn = matches.group(1).strip().replace(' ', '')
                    if len(issn) == 8:  # Format to standard ISSN if it's just digits
                        issn = f"{issn[:4]}-{issn[4:]}"
                    identifiers["issn"] = issn
                    logger.debug(f"ISSN found: {issn}")
                    break
            
            # ISBN pattern: ISBN 978-3-16-148410-0 or ISBN-13: 978-3-16-148410-0
            isbn_patterns = [
                r'ISBN-13\s*:?\s*([\d-]+)',
                r'ISBN-10\s*:?\s*([\d-]+)',
                r'ISBN\s*:?\s*([\d-]+)'
            ]
            
            for pattern in isbn_patterns:
                matches = re.search(pattern, text, re.IGNORECASE)
                if matches:
                    isbn = matches.group(1).strip()
                    identifiers["isbn"] = isbn
                    logger.debug(f"ISBN found: {isbn}")
                    break
            
            # PMID pattern: PMID: 12345678
            pmid_patterns = [
                r'PMID\s*:?\s*(\d+)',
                r'PubMed ID\s*:?\s*(\d+)'
            ]
            
            for pattern in pmid_patterns:
                matches = re.search(pattern, text, re.IGNORECASE)
                if matches:
                    pmid = matches.group(1).strip()
                    identifiers["pmid"] = pmid
                    logger.debug(f"PMID found: {pmid}")
                    break
            
            # arXiv pattern: arXiv:1234.56789 or arXiv preprint arXiv:1234.56789
            arxiv_patterns = [
                r'arXiv\s*:?\s*(\d+\.\d+)',
                r'arXiv\s*:?\s*([\w.-]+/\d+)'
            ]
            
            for pattern in arxiv_patterns:
                matches = re.search(pattern, text, re.IGNORECASE)
                if matches:
                    arxiv_id = matches.group(1).strip()
                    identifiers["arxiv"] = arxiv_id
                    logger.debug(f"arXiv ID found: {arxiv_id}")
                    break
        
        return identifiers
    
    except Exception as e:
        logger.error(f"Error extracting alternative identifiers: {e}")
        return identifiers


def search_metadata_with_identifiers(identifiers: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """
    Search for metadata using alternative identifiers.
    
    Args:
        identifiers (Dict[str, str]): Dictionary of identifier types and values
        
    Returns:
        Optional[Dict[str, Any]]: Metadata dictionary or None if not found
    """
    logger = logging.getLogger('pdf_citation_tool.parsers')
    
    # Try ISSN
    if identifiers.get("issn"):
        logger.debug(f"Searching with ISSN: {identifiers['issn']}")
        metadata = search_by_issn(identifiers["issn"])
        if metadata:
            metadata["source"] = f"ISSN: {identifiers['issn']}"
            logger.info(f"Found metadata via ISSN: {identifiers['issn']}")
            return metadata
        else:
            logger.info(f"No metadata found for ISSN: {identifiers['issn']}")
    
    # Try ISBN
    if identifiers.get("isbn"):
        logger.debug(f"Searching with ISBN: {identifiers['isbn']}")
        metadata = search_by_isbn(identifiers["isbn"])
        if metadata:
            metadata["source"] = f"ISBN: {identifiers['isbn']}"
            logger.info(f"Found metadata via ISBN: {identifiers['isbn']}")
            return metadata
        else:
            logger.info(f"No metadata found for ISBN: {identifiers['isbn']}")
    
    # Try PMID
    if identifiers.get("pmid"):
        logger.debug(f"Searching with PMID: {identifiers['pmid']}")
        metadata = search_by_pmid(identifiers["pmid"])
        if metadata:
            metadata["source"] = f"PMID: {identifiers['pmid']}"
            logger.info(f"Found metadata via PMID: {identifiers['pmid']}")
            return metadata
        else:
            logger.info(f"No metadata found for PMID: {identifiers['pmid']}")
    
    # Try arXiv ID
    if identifiers.get("arxiv"):
        logger.debug(f"Searching with arXiv ID: {identifiers['arxiv']}")
        metadata = search_by_arxiv(identifiers["arxiv"])
        if metadata:
            metadata["source"] = f"arXiv ID: {identifiers['arxiv']}"
            logger.info(f"Found metadata via arXiv ID: {identifiers['arxiv']}")
            return metadata
        else:
            logger.info(f"No metadata found for arXiv ID: {identifiers['arxiv']}")
    
    logger.info("No metadata found using alternative identifiers")
    return None


def search_by_title(title: str) -> Optional[Dict[str, Any]]:
    """
    Search for metadata using the paper title.
    
    Args:
        title (str): Paper title
        
    Returns:
        Optional[Dict[str, Any]]: Metadata dictionary or None if not found
    """
    logger = logging.getLogger('pdf_citation_tool.parsers')
    logger.info(f"Searching by title: {title}")
    
    # Try Semantic Scholar API
    metadata = search_semantic_scholar_by_title(title)
    if metadata:
        metadata["source"] = "Semantic Scholar"
        logger.info(f"Found metadata via Semantic Scholar API")
        return metadata
    else:
        logger.info(f"No metadata found via Semantic Scholar API")
    
    # Try arXiv API
    metadata = search_arxiv_by_title(title)
    if metadata:
        metadata["source"] = "arXiv API"
        logger.info(f"Found metadata via arXiv API")
        return metadata
    else:
        logger.info(f"No metadata found via arXiv API")
    
    logger.info("No metadata found using title search")
    return None


def search_by_issn(issn: str) -> Optional[Dict[str, Any]]:
    """
    Search for metadata using ISSN.
    
    Args:
        issn (str): ISSN identifier
        
    Returns:
        Optional[Dict[str, Any]]: Metadata dictionary or None if not found
    """
    logger = logging.getLogger('pdf_citation_tool.parsers')
    
    try:
        # First, check if we can find journal info from Crossref
        url = f"https://api.crossref.org/journals/{issn}"
        headers = {
            "User-Agent": "PDFCitationTool/1.0 (mailto:user@example.com)",
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            journal_name = data.get("message", {}).get("title", "")
            logger.debug(f"Found journal: {journal_name} for ISSN: {issn}")
            
            # Journal found, but we still need article details
            # In a real implementation, we'd need to extract more data from the PDF
            # to find the specific article in this journal
            
            # For now, we'll return limited metadata
            if journal_name:
                return {
                    "title": "Unknown article in " + journal_name,
                    "authors": ["Unknown Author"],
                    "year": "",
                    "journal": journal_name,
                    "issn": issn,
                    "metadata_quality": "partial"  # Flag to indicate incomplete metadata
                }
        
        return None
        
    except Exception as e:
        logger.error(f"Error searching by ISSN: {e}")
        return None


def search_by_isbn(isbn: str) -> Optional[Dict[str, Any]]:
    """
    Search for metadata using ISBN.
    
    Args:
        isbn (str): ISBN identifier
        
    Returns:
        Optional[Dict[str, Any]]: Metadata dictionary or None if not found
    """
    logger = logging.getLogger('pdf_citation_tool.parsers')
    
    try:
        # Use Open Library API for ISBN lookup
        url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            book_data = data.get(f"ISBN:{isbn}")
            
            if book_data:
                # Extract metadata
                title = book_data.get("title", "Unknown Title")
                
                # Extract authors
                authors = []
                for author in book_data.get("authors", []):
                    if "name" in author:
                        authors.append(author["name"])
                
                if not authors:
                    authors = ["Unknown Author"]
                
                # Extract year
                publish_date = book_data.get("publish_date", "")
                year_match = re.search(r'(19|20)\d{2}', publish_date)
                year = year_match.group(0) if year_match else ""
                
                return {
                    "title": title,
                    "authors": authors,
                    "year": year,
                    "isbn": isbn,
                    "publisher": book_data.get("publishers", [{"name": ""}])[0].get("name", "")
                }
        
        return None
        
    except Exception as e:
        logger.error(f"Error searching by ISBN: {e}")
        return None


def search_by_pmid(pmid: str) -> Optional[Dict[str, Any]]:
    """
    Search for metadata using PubMed ID.
    
    Args:
        pmid (str): PubMed ID
        
    Returns:
        Optional[Dict[str, Any]]: Metadata dictionary or None if not found
    """
    logger = logging.getLogger('pdf_citation_tool.parsers')
    
    try:
        # Use NCBI E-utilities API
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "result" in data and pmid in data["result"]:
                article = data["result"][pmid]
                
                # Extract title
                title = article.get("title", "Unknown Title")
                
                # Extract authors
                authors = []
                for author in article.get("authors", []):
                    if "name" in author:
                        authors.append(author["name"])
                
                if not authors:
                    authors = ["Unknown Author"]
                
                # Extract year
                pub_date = article.get("pubdate", "")
                year_match = re.search(r'(19|20)\d{2}', pub_date)
                year = year_match.group(0) if year_match else ""
                
                # Extract journal
                journal = article.get("source", "")
                
                return {
                    "title": title,
                    "authors": authors,
                    "year": year,
                    "journal": journal,
                    "pmid": pmid
                }
        
        return None
        
    except Exception as e:
        logger.error(f"Error searching by PMID: {e}")
        return None


def search_by_arxiv(arxiv_id: str) -> Optional[Dict[str, Any]]:
    """
    Search for metadata using arXiv ID.
    
    Args:
        arxiv_id (str): arXiv identifier
        
    Returns:
        Optional[Dict[str, Any]]: Metadata dictionary or None if not found
    """
    logger = logging.getLogger('pdf_citation_tool.parsers')
    
    try:
        # Use arXiv API
        url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            # Parse XML response
            from xml.etree import ElementTree
            
            # Define namespace
            namespace = {'arxiv': 'http://arxiv.org/schemas/atom'}
            
            root = ElementTree.fromstring(response.content)
            entries = root.findall('.//arxiv:entry', namespace)
            
            if entries:
                entry = entries[0]
                
                # Extract title
                title_elem = entry.find('.//arxiv:title', namespace)
                title = title_elem.text.strip() if title_elem is not None else "Unknown Title"
                
                # Extract authors
                authors = []
                author_elems = entry.findall('.//arxiv:author/arxiv:name', namespace)
                for author_elem in author_elems:
                    authors.append(author_elem.text.strip())
                
                if not authors:
                    authors = ["Unknown Author"]
                
                # Extract date
                date_elem = entry.find('.//arxiv:published', namespace)
                date = date_elem.text if date_elem is not None else ""
                year_match = re.search(r'(19|20)\d{2}', date)
                year = year_match.group(0) if year_match else ""
                
                return {
                    "title": title,
                    "authors": authors,
                    "year": year,
                    "arxiv_id": arxiv_id
                }
        
        return None
        
    except Exception as e:
        logger.error(f"Error searching by arXiv ID: {e}")
        return None


def search_semantic_scholar_by_title(title: str) -> Optional[Dict[str, Any]]:
    """
    Search for metadata using Semantic Scholar API with a title search.
    
    Args:
        title (str): Paper title
        
    Returns:
        Optional[Dict[str, Any]]: Metadata dictionary or None if not found
    """
    logger = logging.getLogger('pdf_citation_tool.parsers')
    
    try:
        # Encode title for URL
        import urllib.parse
        encoded_title = urllib.parse.quote(title)
        
        # Use Semantic Scholar API
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={encoded_title}&limit=1&fields=title,authors,year,journal,venue"
        
        headers = {
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            papers = data.get("data", [])
            
            if papers and len(papers) > 0:
                paper = papers[0]
                
                # Extract title
                paper_title = paper.get("title", "Unknown Title")
                
                # Extract authors
                authors = []
                for author in paper.get("authors", []):
                    if "name" in author:
                        authors.append(author["name"])
                
                if not authors:
                    authors = ["Unknown Author"]
                
                # Extract year
                year = str(paper.get("year", ""))
                
                # Extract journal or venue
                journal = paper.get("journal", {}).get("name", "") or paper.get("venue", "")
                
                # Check if the title is a reasonable match
                from difflib import SequenceMatcher
                similarity = SequenceMatcher(None, title.lower(), paper_title.lower()).ratio()
                
                if similarity >= 0.6:  # Only return if there's a reasonable match
                    logger.info(f"Found paper on Semantic Scholar with similarity: {similarity:.2f}")
                    return {
                        "title": paper_title,
                        "authors": authors,
                        "year": year,
                        "journal": journal
                    }
                else:
                    logger.debug(f"Semantic Scholar match too low: {similarity:.2f}")
        
        return None
        
    except Exception as e:
        logger.error(f"Error searching Semantic Scholar: {e}")
        return None


def search_arxiv_by_title(title: str) -> Optional[Dict[str, Any]]:
    """
    Search for metadata using arXiv API with a title search.
    
    Args:
        title (str): Paper title
        
    Returns:
        Optional[Dict[str, Any]]: Metadata dictionary or None if not found
    """
    logger = logging.getLogger('pdf_citation_tool.parsers')
    
    try:
        # Encode title for URL
        import urllib.parse
        encoded_title = urllib.parse.quote(f'ti:"{title}"')
        
        # Use arXiv API
        url = f"http://export.arxiv.org/api/query?search_query={encoded_title}&max_results=1"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            # Parse XML response
            from xml.etree import ElementTree
            
            # Define namespace
            namespace = {'arxiv': 'http://arxiv.org/schemas/atom'}
            
            root = ElementTree.fromstring(response.content)
            entries = root.findall('.//arxiv:entry', namespace)
            
            if entries:
                entry = entries[0]
                
                # Extract title
                title_elem = entry.find('.//arxiv:title', namespace)
                paper_title = title_elem.text.strip() if title_elem is not None else "Unknown Title"
                
                # Extract authors
                authors = []
                author_elems = entry.findall('.//arxiv:author/arxiv:name', namespace)
                for author_elem in author_elems:
                    authors.append(author_elem.text.strip())
                
                if not authors:
                    authors = ["Unknown Author"]
                
                # Extract date
                date_elem = entry.find('.//arxiv:published', namespace)
                date = date_elem.text if date_elem is not None else ""
                year_match = re.search(r'(19|20)\d{2}', date)
                year = year_match.group(0) if year_match else ""
                
                # Check if the title is a reasonable match
                from difflib import SequenceMatcher
                similarity = SequenceMatcher(None, title.lower(), paper_title.lower()).ratio()
                
                if similarity >= 0.6:  # Only return if there's a reasonable match
                    logger.info(f"Found paper on arXiv with similarity: {similarity:.2f}")
                    return {
                        "title": paper_title,
                        "authors": authors,
                        "year": year,
                        "arxiv_id": entry.find('.//arxiv:id', namespace).text if entry.find('.//arxiv:id', namespace) is not None else ""
                    }
                else:
                    logger.debug(f"arXiv match too low: {similarity:.2f}")
        
        return None
        
    except Exception as e:
        logger.error(f"Error searching arXiv: {e}")
        return None


def search_doi_in_apis(doi: str) -> Optional[Dict[str, Any]]:
    """
    Search for metadata using a DOI across multiple APIs when Crossref fails.
    
    Args:
        doi (str): The DOI to search for
        
    Returns:
        Optional[Dict[str, Any]]: Metadata from an alternative source, or None if not found
    """
    logger = logging.getLogger('pdf_citation_tool.parsers')
    logger.info(f"Searching for DOI {doi} in alternative APIs")
    
    # Try Semantic Scholar
    try:
        logger.info(f"Trying Semantic Scholar API for DOI: {doi}")
        response = requests.get(
            f"https://api.semanticscholar.org/v1/paper/{doi}",
            headers={"Accept": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract relevant information
            if data:
                authors = []
                if "authors" in data:
                    for author in data["authors"]:
                        if "name" in author:
                            authors.append(author["name"])
                
                # Extract year
                year = ""
                if "year" in data and data["year"]:
                    year = str(data["year"])
                
                # Create metadata object
                metadata = {
                    "title": data.get("title", "Unknown Title"),
                    "authors": authors or ["Unknown Author"],
                    "year": year or "Unknown Year",
                    "container-title": data.get("venue", ""),
                    "DOI": doi,
                    "source": "Semantic Scholar",
                    "metadata_quality": "complete" if (authors and year and "title" in data) else "partial"
                }
                
                logger.info(f"Found metadata via Semantic Scholar for DOI: {doi}")
                return metadata
    except Exception as e:
        logger.warning(f"Error searching Semantic Scholar: {e}")
    
    # Try DataCite
    try:
        logger.info(f"Trying DataCite API for DOI: {doi}")
        response = requests.get(
            f"https://api.datacite.org/dois/{doi}",
            headers={"Accept": "application/vnd.api+json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data and "data" in data and "attributes" in data["data"]:
                attributes = data["data"]["attributes"]
                
                # Extract authors
                authors = []
                if "creators" in attributes:
                    for creator in attributes["creators"]:
                        if "name" in creator:
                            authors.append(creator["name"])
                
                # Extract year
                year = ""
                if "publicationYear" in attributes:
                    year = str(attributes["publicationYear"])
                
                # Create metadata object
                metadata = {
                    "title": attributes.get("title", "Unknown Title"),
                    "authors": authors or ["Unknown Author"],
                    "year": year or "Unknown Year",
                    "container-title": attributes.get("container-title", ""),
                    "DOI": doi,
                    "source": "DataCite",
                    "metadata_quality": "complete" if (authors and year and "title" in attributes) else "partial"
                }
                
                logger.info(f"Found metadata via DataCite for DOI: {doi}")
                return metadata
    except Exception as e:
        logger.warning(f"Error searching DataCite: {e}")
    
    # Try Unpaywall
    try:
        logger.info(f"Trying Unpaywall API for DOI: {doi}")
        response = requests.get(
            f"https://api.unpaywall.org/v2/{doi}?email=info@example.com",  # Replace with your email
            headers={"Accept": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract authors
            authors = []
            if "z_authors" in data:
                for author in data["z_authors"]:
                    if "given" in author and "family" in author:
                        authors.append(f"{author['given']} {author['family']}")
                    elif "family" in author:
                        authors.append(author["family"])
            
            # Extract year
            year = ""
            if "published_date" in data:
                year_match = re.search(r'(\d{4})', data["published_date"])
                if year_match:
                    year = year_match.group(1)
            
            # Create metadata object
            metadata = {
                "title": data.get("title", "Unknown Title"),
                "authors": authors or ["Unknown Author"],
                "year": year or "Unknown Year",
                "container-title": data.get("journal_name", ""),
                "DOI": doi,
                "source": "Unpaywall",
                "metadata_quality": "complete" if (authors and year and "title" in data) else "partial"
            }
            
            logger.info(f"Found metadata via Unpaywall for DOI: {doi}")
            return metadata
    except Exception as e:
        logger.warning(f"Error searching Unpaywall: {e}")
    
    logger.warning(f"No metadata found for DOI {doi} in alternative APIs")
    return None


def has_sufficient_metadata(metadata: Dict[str, Any]) -> bool:
    """
    Check if metadata has sufficient information for processing.
    
    Args:
        metadata (Dict[str, Any]): Metadata dictionary
        
    Returns:
        bool: True if metadata is sufficient, False otherwise
    """
    # Metadata yoksa, yetersiz
    if not metadata:
        return False
    
    # Gerekli alanları kontrol et
    has_title = bool(metadata.get('title'))
    has_authors = metadata.get('authors') and len(metadata['authors']) > 0
    has_year = bool(metadata.get('year'))
    
    # En azından başlık ve ya yazarlar ya da yıl olmalı
    if has_title and (has_authors or has_year):
        return True
    
    return False


def extract_issn(pdf_path: Union[str, Path], use_ocr: bool = False) -> Optional[str]:
    """
    Extract ISSN from a PDF file.
    
    Args:
        pdf_path (Union[str, Path]): Path to the PDF file
        use_ocr (bool): Whether to use OCR for scanned PDFs
        
    Returns:
        Optional[str]: Extracted ISSN or None if not found
    """
    logger = logging.getLogger('litorganizer.parsers')
    pdf_path = Path(pdf_path)
    
    # ISSN regex pattern: Two groups of 4 digits separated by a hyphen
    issn_patterns = [
        r'ISSN[:\s]+([\d]{4}-[\d]{3}[\dX])',
        r'(?<!\d)([\d]{4}-[\d]{3}[\dX])(?!\d)',
        r'eISSN[:\s]+([\d]{4}-[\d]{3}[\dX])',
        r'pISSN[:\s]+([\d]{4}-[\d]{3}[\dX])'
    ]
    
    try:
        # Try to extract ISSN using pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            # Extract text from first few pages
            text = ""
            for i in range(min(5, len(pdf.pages))):
                page_text = pdf.pages[i].extract_text()
                if page_text:
                    text += page_text + "\n"
            
            # Search for ISSN in text
            for pattern in issn_patterns:
                matches = re.search(pattern, text, re.IGNORECASE)
                if matches:
                    issn = matches.group(1).strip()
                    logger.debug(f"ISSN found in text: {issn}")
                    return issn
            
            # If no ISSN found and OCR is enabled, try OCR
            if not text.strip() and use_ocr and OCR_AVAILABLE:
                logger.debug("No text found, attempting OCR for ISSN extraction")
                ocr_text = extract_text_with_ocr(pdf_path)
                
                for pattern in issn_patterns:
                    matches = re.search(pattern, ocr_text, re.IGNORECASE)
                    if matches:
                        issn = matches.group(1).strip()
                        logger.debug(f"ISSN found via OCR: {issn}")
                        return issn
    
    except Exception as e:
        logger.error(f"Error extracting ISSN: {e}")
    
    logger.debug("No ISSN found in PDF")
    return None


def extract_isbn(pdf_path: Union[str, Path], use_ocr: bool = False) -> Optional[str]:
    """
    Extract ISBN from a PDF file.
    
    Args:
        pdf_path (Union[str, Path]): Path to the PDF file
        use_ocr (bool): Whether to use OCR for scanned PDFs
        
    Returns:
        Optional[str]: Extracted ISBN or None if not found
    """
    logger = logging.getLogger('litorganizer.parsers')
    pdf_path = Path(pdf_path)
    
    # ISBN regex patterns (ISBN-10 and ISBN-13)
    isbn_patterns = [
        r'ISBN[:\s]+([\d-]{10,17})',
        r'ISBN-10[:\s]+([\d-]{10,13})',
        r'ISBN-13[:\s]+([\d-]{13,17})',
        r'(?<!\d)(978[\d-]{10,14})(?!\d)'  # ISBN-13 often starts with 978
    ]
    
    try:
        # Try to extract ISBN using pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            # Extract text from first few pages
            text = ""
            for i in range(min(5, len(pdf.pages))):
                page_text = pdf.pages[i].extract_text()
                if page_text:
                    text += page_text + "\n"
            
            # Search for ISBN in text
            for pattern in isbn_patterns:
                matches = re.search(pattern, text, re.IGNORECASE)
                if matches:
                    isbn = matches.group(1).strip()
                    # Remove hyphens and spaces for standardization
                    isbn = re.sub(r'[-\s]', '', isbn)
                    logger.debug(f"ISBN found in text: {isbn}")
                    return isbn
            
            # If no ISBN found and OCR is enabled, try OCR
            if not text.strip() and use_ocr and OCR_AVAILABLE:
                logger.debug("No text found, attempting OCR for ISBN extraction")
                ocr_text = extract_text_with_ocr(pdf_path)
                
                for pattern in isbn_patterns:
                    matches = re.search(pattern, ocr_text, re.IGNORECASE)
                    if matches:
                        isbn = matches.group(1).strip()
                        # Remove hyphens and spaces for standardization
                        isbn = re.sub(r'[-\s]', '', isbn)
                        logger.debug(f"ISBN found via OCR: {isbn}")
                        return isbn
    
    except Exception as e:
        logger.error(f"Error extracting ISBN: {e}")
    
    logger.debug("No ISBN found in PDF")
    return None


def extract_arxiv_id(pdf_path: Union[str, Path], use_ocr: bool = False) -> Optional[str]:
    """
    Extract arXiv ID from a PDF file.
    
    Args:
        pdf_path (Union[str, Path]): Path to the PDF file
        use_ocr (bool): Whether to use OCR for scanned PDFs
        
    Returns:
        Optional[str]: Extracted arXiv ID or None if not found
    """
    logger = logging.getLogger('litorganizer.parsers')
    pdf_path = Path(pdf_path)
    
    # arXiv ID regex patterns - both new and old format
    arxiv_patterns = [
        r'arXiv:(\d{4}\.\d{4,5})',  # New format: 4 digits, dot, 4-5 digits
        r'arXiv:([a-z\-]+\.[A-Z]{2}\/\d{7})',  # Old format: category.XX/YYMMNNN
        r'https?://arxiv.org/abs/(\d{4}\.\d{4,5})',
        r'https?://arxiv.org/abs/([a-z\-]+\.[A-Z]{2}\/\d{7})'
    ]
    
    try:
        # Check if the filename itself contains arXiv ID
        filename = pdf_path.stem
        for pattern in arxiv_patterns:
            matches = re.search(pattern, filename, re.IGNORECASE)
            if matches:
                arxiv_id = matches.group(1).strip()
                logger.debug(f"arXiv ID found in filename: {arxiv_id}")
                return arxiv_id
        
        # Try to extract arXiv ID using pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            # Extract text from first few pages
            text = ""
            for i in range(min(3, len(pdf.pages))):
                page_text = pdf.pages[i].extract_text()
                if page_text:
                    text += page_text + "\n"
            
            # Search for arXiv ID in text
            for pattern in arxiv_patterns:
                matches = re.search(pattern, text, re.IGNORECASE)
                if matches:
                    arxiv_id = matches.group(1).strip()
                    logger.debug(f"arXiv ID found in text: {arxiv_id}")
                    return arxiv_id
            
            # If no arXiv ID found and OCR is enabled, try OCR
            if not text.strip() and use_ocr and OCR_AVAILABLE:
                logger.debug("No text found, attempting OCR for arXiv ID extraction")
                ocr_text = extract_text_with_ocr(pdf_path)
                
                for pattern in arxiv_patterns:
                    matches = re.search(pattern, ocr_text, re.IGNORECASE)
                    if matches:
                        arxiv_id = matches.group(1).strip()
                        logger.debug(f"arXiv ID found via OCR: {arxiv_id}")
                        return arxiv_id
    
    except Exception as e:
        logger.error(f"Error extracting arXiv ID: {e}")
    
    logger.debug("No arXiv ID found in PDF")
    return None


def extract_pmid(pdf_path: Union[str, Path], use_ocr: bool = False) -> Optional[str]:
    """
    Extract PubMed ID (PMID) from a PDF file.
    
    Args:
        pdf_path (Union[str, Path]): Path to the PDF file
        use_ocr (bool): Whether to use OCR for scanned PDFs
        
    Returns:
        Optional[str]: Extracted PMID or None if not found
    """
    logger = logging.getLogger('litorganizer.parsers')
    pdf_path = Path(pdf_path)
    
    # PMID regex patterns
    pmid_patterns = [
        r'PMID[:\s]+(\d{1,9})',
        r'PubMed\s+ID[:\s]+(\d{1,9})',
        r'PubMed\s+PMID[:\s]+(\d{1,9})'
    ]
    
    try:
        # Try to extract PMID using pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            # Extract text from first few pages
            text = ""
            for i in range(min(5, len(pdf.pages))):
                page_text = pdf.pages[i].extract_text()
                if page_text:
                    text += page_text + "\n"
            
            # Search for PMID in text
            for pattern in pmid_patterns:
                matches = re.search(pattern, text, re.IGNORECASE)
                if matches:
                    pmid = matches.group(1).strip()
                    logger.debug(f"PMID found in text: {pmid}")
                    return pmid
            
            # If no PMID found and OCR is enabled, try OCR
            if not text.strip() and use_ocr and OCR_AVAILABLE:
                logger.debug("No text found, attempting OCR for PMID extraction")
                ocr_text = extract_text_with_ocr(pdf_path)
                
                for pattern in pmid_patterns:
                    matches = re.search(pattern, ocr_text, re.IGNORECASE)
                    if matches:
                        pmid = matches.group(1).strip()
                        logger.debug(f"PMID found via OCR: {pmid}")
                        return pmid
    
    except Exception as e:
        logger.error(f"Error extracting PMID: {e}")
    
    logger.debug("No PMID found in PDF")
    return None


def extract_title(pdf_path: Union[str, Path], use_ocr: bool = False) -> Optional[str]:
    """
    Extract title from a PDF file.
    
    Args:
        pdf_path (Union[str, Path]): Path to the PDF file
        use_ocr (bool): Whether to use OCR for scanned PDFs
        
    Returns:
        Optional[str]: Extracted title or None if not found
    """
    logger = logging.getLogger('litorganizer.parsers')
    pdf_path = Path(pdf_path)
    
    try:
        # Try to extract title using pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            # First check PDF metadata
            if pdf.metadata and 'Title' in pdf.metadata and pdf.metadata['Title']:
                title = pdf.metadata['Title'].strip()
                if title:
                    logger.debug(f"Title found in metadata: {title}")
                    return title
            
            # Extract text from first page (title is usually on the first page)
            if len(pdf.pages) > 0:
                first_page_text = pdf.pages[0].extract_text()
                if first_page_text:
                    # Split by newlines and get first non-empty line
                    lines = [line.strip() for line in first_page_text.split('\n') if line.strip()]
                    if lines:
                        # Skip very short lines that are likely not titles
                        potential_titles = [line for line in lines if len(line) > 10]
                        if potential_titles:
                            # Title is typically the first substantial line on the page
                            title = potential_titles[0]
                            # Limit title length to avoid taking too much text
                            if len(title) > 150:
                                title = title[:150] + "..."
                            logger.debug(f"Title extracted from first page: {title}")
                            return title
            
            # If no title found and OCR is enabled, try OCR on first page
            if use_ocr and OCR_AVAILABLE:
                logger.debug("Attempting OCR for title extraction")
                # Convert only the first page to image
                images = convert_from_path(pdf_path, first_page=0, last_page=1)
                if images:
                    ocr_text = pytesseract.image_to_string(images[0])
                    lines = [line.strip() for line in ocr_text.split('\n') if line.strip()]
                    potential_titles = [line for line in lines if len(line) > 10]
                    if potential_titles:
                        title = potential_titles[0]
                        if len(title) > 150:
                            title = title[:150] + "..."
                        logger.debug(f"Title extracted via OCR: {title}")
                        return title
    
    except Exception as e:
        logger.error(f"Error extracting title: {e}")
    
    # If no title found, use the filename as a fallback
    filename_title = pdf_path.stem.replace("_", " ")
    logger.debug(f"No title found in PDF, using filename: {filename_title}")
    return filename_title 