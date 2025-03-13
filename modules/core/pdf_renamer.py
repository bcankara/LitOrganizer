"""
PDF renaming and processing module.

This module handles the main PDF processing functionality, including
metadata extraction, file detection, and renaming operations based on
bibliographic information such as authors, year, and title.
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from modules.utils.file_utils import ensure_dir, sanitize_filename
from modules.utils.pdf_metadata_extractor import (
    extract_doi,
    get_metadata_from_crossref,
    get_metadata_from_multiple_sources,
    extract_metadata_from_content,
    has_sufficient_metadata,
)
from modules.utils.reference_formatter import create_apa7_citation, create_apa7_reference


class PDFProcessor:
    """
    Process PDF files to extract metadata and rename according to citation format.
    """
    
    def __init__(
        self,
        directory: Union[str, Path] = "pdf",
        use_ocr: bool = False,
        create_references: bool = False,
        create_backups: bool = True,
        move_problematic: bool = False,
        problematic_dir: Optional[Union[str, Path]] = None,
        auto_analyze: bool = False,
        categorize_options: Optional[Dict[str, bool]] = None,
        max_workers: int = 4,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize a new PDFProcessor instance.
        
        Args:
            directory (Union[str, Path]): Directory containing PDF files to process
            use_ocr (bool): Whether to use OCR for text extraction
            create_references (bool): Whether to create a references file
            create_backups (bool): Whether to create backups of original files
            move_problematic (bool): Whether to move Unnamed Article files to separate directory
            problematic_dir (Optional[Union[str, Path]]): Directory to move Unnamed Article files to
            auto_analyze (bool): Whether to automatically analyze the content of PDFs
            categorize_options (Optional[Dict[str, bool]]): Options for categorizing files by metadata
            max_workers (int): Maximum number of worker threads
            logger (Optional[logging.Logger]): Logger instance
        """
        # Convert to Path objects
        self.directory = Path(directory)
        self.use_ocr = use_ocr
        self.create_references = create_references
        self.references = []
        self.move_problematic = move_problematic
        self.problematic_dir = Path(problematic_dir) if problematic_dir else self.directory / "Unnamed Article"
        self.auto_analyze = auto_analyze
        self.created_references_file = False
        self.logger = logger or logging.getLogger('litorganizer.processor')
        
        # Fix backup directory settings - use only a single backup folder
        self.backup_dir = self.directory / "backups" if create_backups else None
        
        # Set up Categorized Article directory
        self.categorized_dir = self.directory / "Categorized Article"
        
        # Set up Named Article directory
        self.named_article_dir = self.directory / "Named Article"
        
        self.create_backups = create_backups
        self.max_workers = max_workers
        
        # Set default categorize options if none provided
        self.categorize_options = categorize_options or {}
        
        # Stats counters
        self.processed_count = 0
        self.renamed_count = 0
        self.problematic_count = 0
        
        # Make sure directories exist
        ensure_dir(self.directory)
        if self.move_problematic:
            ensure_dir(self.problematic_dir)
        if self.create_backups:
            ensure_dir(self.backup_dir)
    
    def process_files(self) -> bool:
        """
        Process all PDF files in the directory.
        
        Returns:
            bool: True if processing was successful, False otherwise
        """
        self.logger.info(f"Starting PDF processing in directory: {self.directory}")
        
        # Get all PDF files
        pdf_files = list(self.directory.glob("*.pdf"))
        
        if not pdf_files:
            self.logger.warning(f"No PDF files found in {self.directory}")
            return False
        
        self.logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        # Reset counters
        self.processed_count = 0
        self.renamed_count = 0
        self.problematic_count = 0
        self.references = []
        
        # Use thread pool to process files in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit jobs
            futures = [executor.submit(self.process_file, pdf_file) for pdf_file in pdf_files]
            
            # Process results as they complete
            for future in as_completed(futures):
                try:
                    result = future.result()
                    self.processed_count += 1
                    if result:
                        self.renamed_count += 1
                    else:
                        self.problematic_count += 1
                        self.logger.debug(f"File counted as problematic (could not be renamed)")
                except Exception as e:
                    self.logger.error(f"Error in worker thread: {str(e)}")
                    self.problematic_count += 1
                    self.processed_count += 1  # Count as processed even in case of error
        
        # Summary
        self.logger.info("-" * 40)
        self.logger.info(f"Processing complete. Files processed: {self.processed_count}")
        self.logger.info(f"Files successfully renamed: {self.renamed_count}")
        self.logger.info(f"Problematic files (not renamed): {self.problematic_count}")
        
        # Write references file if requested
        if self.create_references and self.references:
            self.write_references_file()
        
        return True
    
    def process_file(self, file_path: Path) -> bool:
        """
        Process a single PDF file.
        
        Args:
            file_path (Path): Path to the PDF file
            
        Returns:
            bool: True if processing is successful, False otherwise
        """
        logger = self.logger or logging.getLogger('litorganizer.processor')
        filename = file_path.name
        output_path = None
        metadata_source = "Unknown"
        
        try:
            logger.info(f"Processing file: {filename}")
            
            # Step 1: Extract DOI from PDF
            doi = extract_doi(file_path, self.use_ocr)
            
            if not doi:
                logger.warning(f"No DOI found in {filename}, moving to Unnamed Article directory")
                
                # Move to Unnamed Article directory if enabled
                if self.move_problematic and self.problematic_dir:
                    self.problematic_dir.mkdir(exist_ok=True)
                    target_path = self.problematic_dir / filename
                    try:
                        shutil.copy2(file_path, target_path)
                        logger.info(f"Moved file without DOI to Unnamed Article folder: {target_path}")
                        
                        # Remove original file
                        file_path.unlink()
                        logger.debug(f"Removed original file {filename}")
                    except Exception as e:
                        logger.error(f"Failed to move file to Unnamed Article folder: {e}")
                
                # Return False to indicate unsuccessful renaming
                return False
            
            # DOI found, try to fetch metadata
            logger.info(f"Found DOI: {doi}")
            
            # Step 2: Get metadata using our multiple API strategy
            metadata = get_metadata_from_multiple_sources(doi)
            
            if metadata:
                metadata_source = metadata.get('source', 'Unknown API')
                logger.info(f"Found metadata using {metadata_source} for {filename}")
            else:
                logger.warning(f"No metadata found for DOI: {doi} from any API")
                
                # If no metadata found, move to Unnamed Article
                if self.move_problematic and self.problematic_dir:
                    self.problematic_dir.mkdir(exist_ok=True)
                    target_path = self.problematic_dir / filename
                    try:
                        shutil.copy2(file_path, target_path)
                        logger.info(f"Moved file with no metadata to Unnamed Article folder: {target_path}")
                        
                        # Remove original file
                        file_path.unlink()
                        logger.debug(f"Removed original file {filename}")
                    except Exception as e:
                        logger.error(f"Failed to move file to Unnamed Article folder: {e}")
                
                # Return False to indicate unsuccessful renaming
                return False
            
            # If we have metadata, proceed with renaming and categorization
            if metadata and has_sufficient_metadata(metadata):
                # Check quality of metadata
                if metadata.get('metadata_quality', 'complete') == 'partial':
                    logger.warning(f"Retrieved partial metadata from {metadata.get('source', 'Unknown')}")
                    
                # Format citation and create new filename
                citation = self.format_citation(metadata)
                new_filename = self.format_filename(citation, metadata.get('title', ''))
                
                # Create backup if enabled
                if self.create_backups:
                    backup_dir = ensure_dir(self.backup_dir)
                    backup_path = backup_dir / filename
                    try:
                        shutil.copy2(file_path, backup_path)
                        logger.debug(f"Created backup at {backup_path}")
                    except Exception as e:
                        logger.error(f"Failed to create backup: {e}")
                
                # Store citation for references file - store with APA7 reference and add category information
                full_reference = create_apa7_reference(metadata)
                
                # Kategorileri belirle
                subject = metadata.get('category', 'uncategorized')
                journal = metadata.get('journal', 'uncategorized')
                author = metadata.get('authors', ['Unknown'])[0] if metadata.get('authors') else 'uncategorized'
                year = metadata.get('year', 'uncategorized') 
                
                self.references.append({
                    'author': author,
                    'filename': new_filename,
                    'citation': citation,
                    'reference': full_reference,
                    'subject': subject,
                    'journal': journal,
                    'year': year,
                    'doi': metadata.get('doi', '')  # DOI bilgisini de referans objesine ekle
                })
                
                # Move the file to Named Article folder (instead of copying)
                named_dir = ensure_dir(self.named_article_dir)
                named_path = named_dir / new_filename
                try:
                    # Copy the file directly to Named Article folder
                    shutil.copy2(file_path, named_path)
                    logger.info(f"Moved file to Named Article folder with new name: {named_path}")
                    
                    # Remove original file
                    try:
                        file_path.unlink()
                        logger.debug(f"Removed original file {filename}")
                    except Exception as e:
                        logger.error(f"Failed to remove original file: {e}")
                    
                except Exception as e:
                    logger.error(f"Failed to move to Named Article folder: {e}")
                    return False
                
                # Use Named Article folder path for categorization
                if any(self.categorize_options.values()):
                    self.categorize_file(named_path, metadata, new_filename)
                
                return True
            
            else:
                logger.warning(f"Insufficient metadata for {filename}, moving to Unnamed Article directory")
                
                # Move to Unnamed Article directory if enabled
                if self.move_problematic and self.problematic_dir:
                    self.problematic_dir.mkdir(exist_ok=True)
                    target_path = self.problematic_dir / filename
                    try:
                        shutil.copy2(file_path, target_path)
                        logger.info(f"Moved problematic file to {target_path}")
                        
                        # Remove original file
                        file_path.unlink()
                        logger.debug(f"Removed original file {filename}")
                    except Exception as e:
                        logger.error(f"Failed to move problematic file: {e}")
                
                return False
        
        except Exception as e:
            logger.error(f"Error processing {filename}: {e}")
            return False
    
    def format_citation(self, metadata: Dict[str, Any]) -> str:
        """
        Format citation for the filename according to APA7 style.
        
        Args:
            metadata (Dict[str, Any]): Metadata dictionary
        
        Returns:
            str: Citation string
        """
        # Extract first author surname
        author = "Unknown"
        if metadata.get('authors') and len(metadata['authors']) > 0:
            author = metadata['authors'][0]  # We already have only surnames
        
        # Get year
        year = metadata.get('year', 'n.d.')
        if not year or year == "":
            year = "n.d."
        
        # Format as Author_Year (adding underscore between author and year)
        citation = f"{author}_{year}"
        return citation
    
    def format_filename(self, citation: str, title: str) -> str:
        """
        Format filename according to APA7 style and make it valid for filesystem.
        
        Args:
            citation (str): Citation string (Author_Year)
            title (str): Title of the document
            
        Returns:
            str: Formatted filename
        """
        # Clean up title
        title = sanitize_filename(title)
        
        # Limit title length to 25 characters
        if len(title) > 25:
            title = title[:25]
        
        # Format as APA7 (AuthorYear_Title.pdf)
        filename = f"{citation}-{title}.pdf"
        
        # Make sure filename is valid
        return sanitize_filename(filename)
    
    def write_references_file(self) -> None:
        """
        Write references to file in APA7 format.
        
        Creates both an Excel file (references.xlsx) and a text file (references.txt).
        Format: Author - Filename - Bibliography(APA7)
        
        Also creates reference files sorted by categories.
        """
        if not self.references:
            self.logger.info("No references to write.")
            return
        
        try:
            # 1. Create main reference file
            self._create_reference_files(self.directory, self.references, "All References")
            
            # 2. Create reference files by categories
            
            # Prepare Categorized Article directory
            cat_dir = ensure_dir(self.categorized_dir)
            
            # For Subject category
            if any(self.categorize_options.values()) and self.categorize_options.get('by_subject', False):
                # First group references by subject
                subject_refs = {}
                for ref in self.references:
                    subject = ref['subject']
                    if subject not in subject_refs:
                        subject_refs[subject] = []
                    subject_refs[subject].append(ref)
                
                # Create reference file for each subject
                for subject, refs in subject_refs.items():
                    if subject and subject.strip() != "":
                        subject_folder = sanitize_filename(subject)
                        subject_dir = ensure_dir(cat_dir / "by_subject" / subject_folder)
                        self._create_reference_files(subject_dir, refs, f"References for {subject}")
            
            # For Journal category
            if any(self.categorize_options.values()) and self.categorize_options.get('by_journal', False):
                # First group references by journal
                journal_refs = {}
                for ref in self.references:
                    journal = ref['journal']
                    if journal not in journal_refs:
                        journal_refs[journal] = []
                    journal_refs[journal].append(ref)
                
                # Create reference file for each journal
                for journal, refs in journal_refs.items():
                    if journal and journal.strip() != "":
                        journal_folder = sanitize_filename(journal)
                        journal_dir = ensure_dir(cat_dir / "by_journal" / journal_folder)
                        self._create_reference_files(journal_dir, refs, f"References for {journal}")
            
            # For Author category
            if any(self.categorize_options.values()) and self.categorize_options.get('by_author', False):
                # First group references by author
                author_refs = {}
                for ref in self.references:
                    author = ref['author']
                    if author not in author_refs:
                        author_refs[author] = []
                    author_refs[author].append(ref)
                
                # Create reference file for each author
                for author, refs in author_refs.items():
                    if author and author.strip() != "":
                        author_folder = sanitize_filename(author)
                        author_dir = ensure_dir(cat_dir / "by_author" / author_folder)
                        self._create_reference_files(author_dir, refs, f"References for {author}")
            
            # For Year category
            if any(self.categorize_options.values()) and self.categorize_options.get('by_year', False):
                # First group references by year
                year_refs = {}
                for ref in self.references:
                    year = ref['year']
                    if year not in year_refs:
                        year_refs[year] = []
                    year_refs[year].append(ref)
                
                # Create reference file for each year
                for year, refs in year_refs.items():
                    if year and year.strip() != "":
                        year_folder = sanitize_filename(str(year))
                        year_dir = ensure_dir(cat_dir / "by_year" / year_folder)
                        self._create_reference_files(year_dir, refs, f"References for {year}")
            
        except Exception as e:
            self.logger.error(f"Error writing references file: {e}")
    
    def _create_reference_files(self, directory: Path, references: list, title: str = "References") -> None:
        """
        Creates reference files for the given references in the specified directory.
        
        Args:
            directory (Path): Directory where the files will be created
            references (list): List of references
            title (str, optional): Title for the references. Defaults to "References".
        """
        try:
            # Excel format using pandas
            try:
                import pandas as pd
                
                # Create DataFrame with required columns
                data = []
                for ref_item in references:
                    data.append({
                        'DOI': ref_item['doi'],  # DOI sütunu eklendi
                        'Author': ref_item['author'],  # "Yazar" -> "Author"
                        'Filename': ref_item['filename'],  # "Dosya Adı" -> "Filename"
                        'Bibliography (APA7)': ref_item['reference']  # "Kaynakça (APA7)" -> "Bibliography (APA7)"
                    })
                
                df = pd.DataFrame(data)
                
                # Save to Excel
                excel_path = directory / "references.xlsx"
                df.to_excel(excel_path, index=False)
                self.logger.info(f"References saved to Excel: {excel_path}")
            except ImportError:
                self.logger.warning("pandas not installed, cannot write Excel file")
            
            # Also save as text file
            text_path = directory / "references.txt"
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(f"=== {title} ===\n\n")
                for ref_item in references:
                    f.write(f"DOI: {ref_item['doi']}\n")  # DOI eklendi
                    f.write(f"Author: {ref_item['author']}\n")  # "Yazar" -> "Author"
                    f.write(f"Filename: {ref_item['filename']}\n")  # "Dosya Adı" -> "Filename"
                    f.write(f"Bibliography (APA7): {ref_item['reference']}\n")  # "Kaynakça (APA7)" -> "Bibliography (APA7)"
                    f.write("\n---\n\n")
            
            self.logger.info(f"References saved to text file: {text_path}")
        except Exception as e:
            self.logger.error(f"Error creating reference files in {directory}: {e}")
    
    def categorize_file(self, file_path: Path, metadata: Dict[str, Any], new_filename: str = None) -> None:
        """
        Categorize a file by moving it to appropriate subdirectories based on metadata.
        
        Args:
            file_path (Path): Path to the renamed file
            metadata (Dict[str, Any]): Metadata for the file
            new_filename (str, optional): New filename if renamed. Defaults to None.
        """
        try:
            # Dosya adını belirleme - eğer yeni isim verildiyse onu kullan, yoksa mevcut dosya adını kullan
            filename = new_filename if new_filename else file_path.name
            
            # Base directory for categories
            base_dir = ensure_dir(self.categorized_dir)
            
            # Kategorilendirme işleminden önce metadata alanlarını kontrol et ve logla
            self.logger.info(f"Categorizing file with metadata: journal='{metadata.get('journal')}', "
                             f"category='{metadata.get('category')}', year='{metadata.get('year')}'")
            
            # Metadata kaynaklarını detaylı logla
            self.logger.debug(f"Metadata source: {metadata.get('source', 'Unknown')}")
            self.logger.debug(f"Metadata keys: {', '.join(metadata.keys())}")
            
            # Kategori kontrolü - sadece gerçek kategori bilgisi varsa kategorileme yap
            category = metadata.get('category', '')
            
            # Kategoriye göre işleme
            if category and category.strip() != "":
                self.logger.info(f"Category information found: {category}")
            else:
                self.logger.warning(f"No category/subject information found for {filename}")
            
            # Categorize by journal
            if self.categorize_options.get('by_journal', False):
                journal = metadata.get('journal')
                
                if journal and journal.strip() != "":
                    # Sanitize the journal name for folder name
                    journal_folder = sanitize_filename(journal)
                    # Create journal folder
                    journal_dir = ensure_dir(base_dir / "by_journal" / journal_folder)
                    # Copy to journal folder
                    target_path = journal_dir / filename
                    shutil.copy2(file_path, target_path)
                    self.logger.info(f"Categorized {filename} by journal: {journal}")
                else:
                    # If journal metadata not available, put in uncategorized folder
                    uncategorized_dir = ensure_dir(base_dir / "by_journal" / "uncategorized")
                    target_path = uncategorized_dir / filename
                    shutil.copy2(file_path, target_path)
                    self.logger.info(f"Added {filename} to uncategorized journals")
            
            # Categorize by author (first author)
            if self.categorize_options.get('by_author', False):
                if metadata.get('authors') and metadata['authors']:
                    author = metadata['authors'][0]
                    if author and author.strip() != "":
                        # Use author surname for folder
                        author_folder = sanitize_filename(author)
                        # Create author folder
                        author_dir = ensure_dir(base_dir / "by_author" / author_folder)
                        # Copy to author folder
                        target_path = author_dir / filename
                        shutil.copy2(file_path, target_path)
                        self.logger.info(f"Categorized {filename} by author: {author}")
                    else:
                        # If author metadata not useful, put in uncategorized folder
                        uncategorized_dir = ensure_dir(base_dir / "by_author" / "uncategorized")
                        target_path = uncategorized_dir / filename
                        shutil.copy2(file_path, target_path)
                        self.logger.info(f"Added {filename} to uncategorized authors")
                else:
                    # If no author metadata, put in uncategorized folder
                    uncategorized_dir = ensure_dir(base_dir / "by_author" / "uncategorized")
                    target_path = uncategorized_dir / filename
                    shutil.copy2(file_path, target_path)
                    self.logger.info(f"Added {filename} to uncategorized authors")
            
            # Categorize by year
            if self.categorize_options.get('by_year', False):
                year = metadata.get('year')
                if year and year.strip() != "":
                    # Create year folder
                    year_dir = ensure_dir(base_dir / "by_year" / str(year))
                    # Copy to year folder
                    target_path = year_dir / filename
                    shutil.copy2(file_path, target_path)
                    self.logger.info(f"Categorized {filename} by year: {year}")
                else:
                    # If year metadata not available, put in uncategorized folder
                    uncategorized_dir = ensure_dir(base_dir / "by_year" / "uncategorized")
                    target_path = uncategorized_dir / filename
                    shutil.copy2(file_path, target_path)
                    self.logger.info(f"Added {filename} to uncategorized years")
            
            # Categorize by subject (using 'category' field) 
            if self.categorize_options.get('by_subject', False):
                # Doğrudan category alanını kullan
                category = metadata.get('category')
                
                if category and category.strip() != "":
                    # Sanitize subject for folder name
                    subject_folder = sanitize_filename(category)
                    # Log subject folder
                    self.logger.info(f"Creating subject folder: '{subject_folder}'")
                    # Create subject folder
                    subject_dir = ensure_dir(base_dir / "by_subject" / subject_folder)
                    # Copy to subject folder
                    target_path = subject_dir / filename
                    try:
                        shutil.copy2(file_path, target_path)
                        self.logger.info(f"Categorized {filename} by subject: {category}")
                    except Exception as e:
                        self.logger.error(f"Failed to categorize by subject: {e}")
                else:
                    # Kategori bilgisi yoksa, doğrudan "uncategorized" klasörüne gönder
                    uncategorized_dir = ensure_dir(base_dir / "by_subject" / "uncategorized")
                    target_path = uncategorized_dir / filename
                    try:
                        shutil.copy2(file_path, target_path)
                        self.logger.info(f"Added {filename} to uncategorized subjects")
                    except Exception as e:
                        self.logger.error(f"Failed to add to uncategorized subjects: {e}")
            
        except Exception as e:
            self.logger.error(f"Error categorizing {file_path.name}: {str(e)}") 