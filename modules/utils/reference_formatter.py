"""
Reference and citation formatting utilities for academic papers.

This module provides functions to format references and citations in APA7 style
for academic papers and articles.
"""

import re
from typing import Dict, List, Optional, Union


def create_apa7_citation(metadata: Dict) -> str:
    """
    Create an APA7 in-text citation from metadata.
    
    Args:
        metadata (Dict): Metadata dictionary containing author and year information
        
    Returns:
        str: APA7 formatted citation (e.g., "(Smith, 2020)")
    """
    # Handle missing or invalid metadata
    if not metadata or not isinstance(metadata, dict):
        return "(Unknown, n.d.)"
    
    # Get author information
    authors = metadata.get("authors", [])
    if not authors or not isinstance(authors, list) or authors[0] == "Unknown Author":
        author_text = "Unknown"
    else:
        # Use the first author's last name
        author_text = extract_last_name(authors[0])
    
    # Get year information
    year = metadata.get("year", "")
    if not year or year == "0000":
        year = "n.d."  # n.d. = no date
    
    # Create citation in APA7 format
    citation = f"({author_text}, {year})"
    return citation


def create_apa7_reference(metadata: Dict) -> str:
    """
    Create a complete APA7 reference from metadata.
    
    Args:
        metadata (Dict): Metadata dictionary containing author, year, title, etc.
        
    Returns:
        str: APA7 formatted reference
    """
    # Handle missing or invalid metadata
    if not metadata or not isinstance(metadata, dict):
        return "Unknown. (n.d.). Unknown title."
    
    # Get author information
    authors = metadata.get("authors", [])
    author_text = format_authors_for_reference(authors)
    
    # Get year information
    year = metadata.get("year", "")
    if not year or year == "0000":
        year = "n.d."  # n.d. = no date
    
    # Get title
    title = metadata.get("title", "Unknown title")
    
    # Get journal/publication
    journal = metadata.get("journal", "")
    volume = metadata.get("volume", "")
    issue = metadata.get("issue", "")
    pages = metadata.get("pages", "")
    doi = metadata.get("doi", "")
    
    # Create reference in APA7 format
    reference = f"{author_text} ({year}). {title}."
    
    # Add journal information if available
    if journal:
        reference += f" {journal}"
        if volume:
            reference += f", {volume}"
            if issue:
                reference += f"({issue})"
        if pages:
            reference += f", {pages}"
    
    # Add DOI if available
    if doi:
        reference += f". https://doi.org/{doi}"
    
    return reference


def format_authors_for_reference(authors: List[Union[Dict, str]]) -> str:
    """
    Format a list of authors for an APA7 reference.
    Handles lists containing strings or dictionaries.
    
    Args:
        authors (List[Union[Dict, str]]): List of author data (strings or dicts)
        
    Returns:
        str: Formatted author string for APA7 reference
    """
    if not authors or not isinstance(authors, list):
        return "Unknown"
    
    # Filter out invalid entries
    valid_authors = [author for author in authors if author and author != "Unknown Author"]
    
    if not valid_authors:
        return "Unknown"
    
    if len(valid_authors) == 1:
        # Format: Last, F. I.
        return format_author_name(valid_authors[0])
    
    if len(valid_authors) < 8:
        # For 2-7 authors, list all, separated by commas with ampersand before last
        formatted_authors = [format_author_name(author) for author in valid_authors]
        # Ensure no empty strings before joining
        formatted_authors = [fa for fa in formatted_authors if fa]
        if not formatted_authors: return "Unknown"
        if len(formatted_authors) == 1: return formatted_authors[0]
        return ", ".join(formatted_authors[:-1]) + ", & " + formatted_authors[-1]
    else:
        # For 8+ authors, list first 6, then ellipsis, then last author
        formatted_authors = [format_author_name(author) for author in valid_authors[:6]]
        last_author_formatted = format_author_name(valid_authors[-1])
        # Ensure no empty strings before joining
        formatted_authors = [fa for fa in formatted_authors if fa]
        if not formatted_authors: return "Unknown"
        
        formatted_authors.append("...")
        if last_author_formatted:
             formatted_authors.append(last_author_formatted)
        else: # Handle case where last author formatting failed
             formatted_authors.append("Unknown")
             
        return ", ".join(formatted_authors)


def format_author_name(author_data: Union[Dict, str]) -> str:
    """
    Format a single author name (from dict or string) for APA7 reference.
    
    Args:
        author_data (Union[Dict, str]): Author data (dict with 'family', 'given' or string)
        
    Returns:
        str: Formatted author name (e.g., Smith, J. D.)
    """
    if isinstance(author_data, dict):
        last_name = author_data.get('family', '').strip()
        given_name = author_data.get('given', '').strip()
        
        if not last_name:
            # If family name is missing, use the full name if available, or fallback
            full_name = author_data.get('name', '').strip()
            if full_name: return full_name # Return full name if family name missing
            return "Unknown"
            
        initials = ""
        if given_name:
            # Create initials from given names
            for name_part in given_name.split():
                if name_part:
                    initials += name_part[0].upper() + ". " # Add space after dot
            initials = initials.strip()
        
        return f"{last_name}, {initials}" if initials else last_name
        
    elif isinstance(author_data, str):
        # Handle simple string input (legacy or fallback)
        author_str = author_data.strip()
        if not author_str or author_str == "Unknown Author":
            return "Unknown"
            
        # Check if the name already contains a comma (Last, First format)
        if "," in author_str:
            parts = author_str.split(",", 1)
            last_name = parts[0].strip()
            first_names = parts[1].strip()
            
            # Format initials
            initials = ""
            for name in first_names.split():
                if name:
                    initials += name[0].upper() + ". " # Add space after dot
            initials = initials.strip()
            
            return f"{last_name}, {initials}" if initials else last_name
        
        # If no comma, assume First Last format
        parts = author_str.split()
        if len(parts) == 1:
            return parts[0]  # Only one name
        
        # Last name is the last part
        last_name = parts[-1]
        
        # Initials from other parts
        initials = ""
        for name in parts[:-1]:
            if name:
                initials += name[0].upper() + ". " # Add space after dot
        initials = initials.strip()
        
        return f"{last_name}, {initials}" if initials else last_name
    else:
        return "Unknown"


def extract_last_name(author_data: Union[Dict, str]) -> str:
    """
    Extract the last name from an author dictionary or string.
    Handles both dictionary format {'family': '...'} and simple string format.
    
    Args:
        author_data (Union[Dict, str]): Author information (dictionary or string)
        
    Returns:
        str: Last name
    """
    if isinstance(author_data, dict):
        # If it's a dictionary, get the 'family' name, fallback to 'name' if family missing
        family_name = author_data.get('family', '').strip()
        if family_name:
            return family_name
        # Fallback: try to get last word from 'name' field if 'family' is empty
        full_name = author_data.get('name', '').strip()
        if full_name:
            parts = full_name.split()
            if parts: return parts[-1]
        return "Unknown"
    elif isinstance(author_data, str):
        # If it's a string, process as before
        author_str = author_data.strip()
        if not author_str or author_str == "Unknown Author":
            return "Unknown"
            
        # If there's a comma, the last name is likely before it
        if "," in author_str:
            return author_str.split(",")[0].strip()
        
        # Otherwise take the last word as the last name
        parts = author_str.split()
        if parts:
            return parts[-1].strip()
        
        return "Unknown"
    else:
        # Handle unexpected types
        return "Unknown" 