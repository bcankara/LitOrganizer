"""
Reference and citation formatting utilities for academic papers.

This module provides functions to format references and citations in APA7 style
for academic papers and articles.
"""

import re
from typing import Dict, List, Optional


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


def format_authors_for_reference(authors: List[str]) -> str:
    """
    Format a list of authors for an APA7 reference.
    
    Args:
        authors (List[str]): List of author names
        
    Returns:
        str: Formatted author string for APA7 reference
    """
    if not authors or not isinstance(authors, list):
        return "Unknown"
    
    # Clean up author list
    authors = [author for author in authors if author and author != "Unknown Author"]
    
    if not authors:
        return "Unknown"
    
    if len(authors) == 1:
        # Format: Last, F. I.
        return format_author_name(authors[0])
    
    if len(authors) < 8:
        # For 2-7 authors, list all, separated by commas with ampersand before last
        formatted_authors = [format_author_name(author) for author in authors]
        return ", ".join(formatted_authors[:-1]) + ", & " + formatted_authors[-1]
    else:
        # For 8+ authors, list first 6, then ellipsis, then last author
        formatted_authors = [format_author_name(author) for author in authors[:6]]
        formatted_authors.append("...")
        formatted_authors.append(format_author_name(authors[-1]))
        return ", ".join(formatted_authors)


def format_author_name(author: str) -> str:
    """
    Format a single author name for APA7 reference.
    
    Args:
        author (str): Author name as a string
        
    Returns:
        str: Formatted author name
    """
    # Check if the name already contains a comma (Last, First format)
    if "," in author:
        parts = author.split(",", 1)
        last_name = parts[0].strip()
        first_names = parts[1].strip()
        
        # Format initials
        initials = ""
        for name in first_names.split():
            if name:
                initials += name[0].upper() + "."
        
        return f"{last_name}, {initials}"
    
    # If no comma, assume First Last format
    parts = author.strip().split()
    if len(parts) == 1:
        return parts[0]  # Only one name
    
    # Last name is the last part
    last_name = parts[-1]
    
    # Initials from other parts
    initials = ""
    for name in parts[:-1]:
        if name:
            initials += name[0].upper() + "."
    
    return f"{last_name}, {initials}"


def extract_last_name(author: str) -> str:
    """
    Extract the last name from an author string.
    
    Args:
        author (str): Author name
        
    Returns:
        str: Last name
    """
    # Clean up the author string
    author = author.strip()
    
    # If there's a comma, the last name is likely before it
    if "," in author:
        return author.split(",")[0].strip()
    
    # Otherwise take the last word as the last name
    parts = author.split()
    if parts:
        return parts[-1].strip()
    
    return "Unknown" 