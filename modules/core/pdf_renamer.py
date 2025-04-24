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
import requests

from modules.utils.file_utils import ensure_dir, sanitize_filename
from modules.utils import pdf_metadata_extractor as pdf_extractor
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

        # Categorization statistics dictionaries
        self.category_counts = {
            'journal': {},
            'author': {},
            'year': {},
            'subject': {}
        }
        self.categorized_file_count = {
            'journal': 0,
            'author': 0,
            'year': 0,
            'subject': 0
        }
        
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
            bool: True if processing and renaming/categorization is successful, False otherwise
        """
        logger = self.logger or logging.getLogger('litorganizer.processor')
        filename = file_path.name
        output_path = None # Stores the final path after rename/categorization
        doi = None
        metadata = None
        metadata_source = "Unknown"
        
        try:
            logger.info(f"Processing file: {filename}")
            
            # Step 1: Extract DOI from PDF
            try:
                doi = extract_doi(file_path, self.use_ocr)
            except pdf_extractor.PDFReadError as e_pdf_read:
                logger.error(f"PDF Processing Error (read): Failed to process {filename}: {e_pdf_read}")
                if self.move_problematic:
                    self._move_to_problematic(file_path, "PDF_Read_Error")
                return False
            except pdf_extractor.PDFEncryptedError as e_pdf_encrypt:
                logger.error(f"PDF Processing Error (encrypted): File {filename} is encrypted: {e_pdf_encrypt}")
                if self.move_problematic:
                    self._move_to_problematic(file_path, "PDF_Encrypted_Error")
                return False
            except Exception as e_doi_extract: # Catch other potential DOI extraction errors
                logger.error(f"Error extracting DOI from {filename}: {e_doi_extract}", exc_info=True)
                if self.move_problematic:
                    self._move_to_problematic(file_path, f"DOI_Extract_Error_{type(e_doi_extract).__name__}")
                return False
            
            if not doi:
                logger.warning(f"No DOI found in {filename}. Moving to Unnamed.")
                if self.move_problematic:
                    self._move_to_problematic(file_path, "Missing_DOI")
                return False
            
            # DOI found
            logger.info(f"Found DOI: {doi}")
            
            # Step 2: Get metadata using multiple API strategy
            try:
                metadata = get_metadata_from_multiple_sources(doi)
                if metadata:
                    metadata_source = metadata.get('source', 'Unknown API')
            except requests.exceptions.RequestException as e_api:
                logger.error(f"API Error (network/http): Failed to fetch metadata for DOI {doi}: {e_api}")
                if self.move_problematic:
                    self._move_to_problematic(file_path, "API_Error")
                return False
            except Exception as e_meta_fetch: # Catch other potential errors during metadata fetching
                logger.error(f"Error fetching metadata for DOI {doi}: {e_meta_fetch}", exc_info=True)
                if self.move_problematic:
                    self._move_to_problematic(file_path, "Metadata_Fetch_Error")
                return False
            
            # Step 3: Check if metadata is sufficient
            if not metadata or not has_sufficient_metadata(metadata):
                logger.warning(f"Insufficient or no metadata found for DOI: {doi} (Source: {metadata_source}). Moving to Unnamed.")
                if self.move_problematic:
                    self._move_to_problematic(file_path, "Insufficient_Metadata")
                return False
            
            logger.debug(f"Sufficient metadata found for {filename} via {metadata_source}")
            
            # Step 4: Format citation and filename
            citation = self.format_citation(metadata)
            title = metadata.get('title', 'Untitled')
            new_filename_base = self.format_filename(citation, title)
            new_filename = new_filename_base + file_path.suffix
                
            # Step 5: Create backup if enabled
            if self.create_backups and self.backup_dir:
                try:
                    backup_path = self.backup_dir / file_path.name
                    ensure_dir(self.backup_dir)
                    if backup_path.exists():
                        logger.warning(f"Backup file already exists, overwriting: {backup_path}")
                        shutil.copy2(file_path, backup_path)
                    logger.info(f"Created backup: {backup_path}")
                except (OSError, IOError, PermissionError) as e_backup:
                     logger.error(f"File System Error (backup): Failed to create backup for {file_path.name}: {e_backup}")
                     # Continue processing even if backup fails
                except Exception as e_backup_generic:
                     logger.error(f"Error creating backup for {file_path.name}: {e_backup_generic}")
                     # Continue processing
            
            # Step 6 & 7: Rename / Categorize / Move
            # Önce dosyayı Named Article klasörüne taşıyalım
            target_dir_named = self.named_article_dir
            output_path_named = target_dir_named / new_filename # new_filename burada tam dosya adı (uzantılı)
            final_output_path = None # Başlangıçta None

            try:
                ensure_dir(target_dir_named)
            except OSError as e_mkdir:
                logger.error(f"File System Error (mkdir Named): Failed to create target directory {target_dir_named}: {e_mkdir}")
                if self.move_problematic:
                    self._move_to_problematic(file_path, "Mkdir_Error_Named")
                return False # Ana işlem başarısız oldu

            try:
                # Dosya adı çakışmalarını kontrol et ve yönet
                counter = 1
                temp_output_path = output_path_named
                while temp_output_path.exists():
                    logger.warning(f"Target file exists in Named Article: {temp_output_path}. Appending counter.")
                    # new_filename_base: format_filename'den dönen uzantısız isim
                    temp_output_path = target_dir_named / f"{new_filename_base}_{counter}{file_path.suffix}"
                    counter += 1
                output_path_named = temp_output_path # Çakışma yoksa orijinal isim, varsa sayaçlı isim

                # Orijinal dosyayı Named Article klasörüne taşı (yeniden adlandırarak)
                shutil.move(str(file_path), str(output_path_named))
                logger.info(f"Successfully moved original file to Named Article: {output_path_named}")
                final_output_path = output_path_named # Başarılı taşıma sonrası yolu kaydet

            except (OSError, IOError, PermissionError) as e_rename:
                logger.error(f"File System Error (move to Named): Failed to move {file_path.name} to {output_path_named}: {e_rename}")
                if self.move_problematic:
                     # Orijinal dosya hala yerinde olmalı, onu problematic'e taşı
                     self._move_to_problematic(file_path, "Move_Named_Error")
                return False # Ana işlem başarısız oldu
            except Exception as e_rename_generic:
                 logger.error(f"Error moving file {file_path.name} to {output_path_named}: {e_rename_generic}", exc_info=True)
                 if self.move_problematic:
                      self._move_to_problematic(file_path, "Move_Named_Generic_Error")
                 return False # Ana işlem başarısız oldu


            # Step 7.5: Kategorizasyon (Dosya Named Article'a taşındıktan SONRA)
            if final_output_path and any(self.categorize_options.values()):
                logger.debug(f"Attempting categorization for {final_output_path.name}...")
                # categorize_file'a Named Article'daki dosyanın yolunu ve hedef dosya adını ver
                # new_filename_base: format_filename'dan dönen uzantısız isim
                # final_output_path.name: Named Article'daki tam dosya adı (uzantılı)
                categorization_successful = self.categorize_file(final_output_path, metadata, final_output_path.name)
                if categorization_successful:
                    logger.info(f"Categorization process completed for {final_output_path.name} (at least one category created).")
            else:
                    logger.warning(f"Categorization process completed for {final_output_path.name}, but no categories were successfully created (or file existed).")


            # Step 8: Add reference if needed (only if move to Named Article was successful)
            if final_output_path and self.create_references:
                # Referans ekleme kodu - Named Article'daki yolu ve ismi kullanacak şekilde güncellendi
                try:
                    reference_entry = create_apa7_reference(metadata)
                    self.references.append({
                        'reference': reference_entry,
                        'filename': final_output_path.name, # Named Article'daki ismi kullan
                        'doi': doi,
                        'author': metadata.get('authors', [{}])[0].get('family', ''),
                        'journal': metadata.get('journal', ''),
                        'year': metadata.get('year', ''),
                        'subject': metadata.get('subjects', [''])[0] if metadata.get('subjects') else ''
                    })
                except Exception as e_ref:
                     logger.error(f"Error generating reference for {final_output_path.name}: {e_ref}", exc_info=True)
                

            # Return True if move to Named Article was successful
            return final_output_path is not None
        
        except Exception as e_main: # General catch-all
            logger.error(f"Unexpected Error processing file {filename}: {e_main}", exc_info=True)
            if self.move_problematic:
                self._move_to_problematic(file_path, f"Unexpected_{type(e_main).__name__}")
            return False
    
    def format_citation(self, metadata: Dict[str, Any]) -> str:
        """
        Formats the citation string based on metadata.
        
        Args:
            metadata (Dict[str, Any]): Metadata dictionary
        
        Returns:
            str: Formatted citation string (e.g., APA7)
        """
        citation = create_apa7_citation(metadata)
        return citation
    
    def format_filename(self, citation: str, title: str) -> str:
        """
        Creates a sanitized filename from citation and title.
        
        Args:
            citation (str): Formatted citation string
            title (str): Article title
            
        Returns:
            str: Sanitized filename string (excluding extension)
        """
        # Basic format: Citation - Title
        # Ensure title is also somewhat limited in length if needed
        max_title_len = 80 
        short_title = title[:max_title_len] + '...' if len(title) > max_title_len else title
        
        base_filename = f"{citation} - {short_title}"
        
        # Sanitize the entire string
        sanitized_filename = sanitize_filename(base_filename)
        
        # Optional: Further length check on the final sanitized name
        max_total_len = 150 # Example limit
        if len(sanitized_filename) > max_total_len:
            sanitized_filename = sanitized_filename[:max_total_len]

        return sanitized_filename
    
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

    def categorize_file(self, source_file_path: Path, metadata: Dict[str, Any], target_filename: str) -> bool:
        """
        Categorize the file based on metadata if options are enabled.
        Copies the file to category subfolders.
        
        Args:
            source_file_path (Path): The path of the successfully renamed file in the 'Named Article' directory.
            metadata (Dict[str, Any]): The metadata dictionary for the file.
            target_filename (str): The final filename (e.g., '(Author, Year) - Title.pdf').
            
        Returns:
            bool: True if at least one categorization was successful, False otherwise.
        """
        if not any(self.categorize_options.values()):
            return False # No categorization requested
            
        if not self.categorized_dir:
             self.logger.error("Categorization failed: Categorized Article directory is not set.")
             return False
             
        ensure_dir(self.categorized_dir)
        
        categorized_successfully = False
        at_least_one_category_created = False
        
        # --- Category extraction logic --- 
        category_values = {}
        if self.categorize_options.get("by_journal"):
            journal = metadata.get('journal')
            if journal:
                category_values['journal'] = sanitize_filename(journal)
        if self.categorize_options.get("by_author"):
            authors = metadata.get('authors')
            if authors:
                first_author_surname = authors[0].get('family', 'UnknownAuthor')
                category_values['author'] = sanitize_filename(first_author_surname)
        if self.categorize_options.get("by_year"):
            year = metadata.get('year')
            if year:
                category_values['year'] = str(year)
        if self.categorize_options.get("by_subject"):
            # Assuming 'subjects' might be a list or a single string - take the first one if list
            subjects = metadata.get('subjects') # Updated to 'subjects'
            if subjects:
                 # Handle both list and string cases, take first subject if list
                 first_subject = subjects[0] if isinstance(subjects, list) and subjects else subjects if isinstance(subjects, str) else None
                 if first_subject:
                      category_values['subject'] = sanitize_filename(first_subject)
        
        # --- Copy file to respective category folders --- 
        for category_type, folder_name in category_values.items():
            if not folder_name: continue # Skip if folder name is empty
            
            try:
                category_base_folder = self.categorized_dir / f"by_{category_type}"
                category_target_folder = category_base_folder / folder_name
                ensure_dir(category_target_folder)
                
                # Destination path within the category folder
                destination_path = category_target_folder / target_filename
                
                # Copy the file from the 'Named Article' directory
                shutil.copy2(source_file_path, destination_path)
                self.logger.info(f"Successfully categorized (copied) to 'by_{category_type}': {destination_path}")
                
                # --- Update categorization statistics --- 
                # Increment count for the specific category value (e.g., journal name 'Nature')
                self.category_counts[category_type][folder_name] = self.category_counts[category_type].get(folder_name, 0) + 1
                # Increment the total count for this category type (e.g., total files categorized by journal)
                self.categorized_file_count[category_type] += 1
                # --- End update --- 
                
                at_least_one_category_created = True
                
                # Create reference files within the category folder
                if self.create_references:
                     # Ensure we only use the current file's metadata for category reference files
                     current_reference = self.format_citation(metadata)
                     if current_reference:
                         self._create_reference_files(category_target_folder, [current_reference], title=f"References_{folder_name}")
                         
            except (OSError, IOError, PermissionError) as e:
                self.logger.error(f"File System Error (categorize move): Failed to copy {target_filename} to {category_target_folder}: {e}")
            except Exception as e_cat:
                 self.logger.error(f"Error during categorization of {target_filename} to by_{category_type}/{folder_name}: {e_cat}", exc_info=True)
                 
        if at_least_one_category_created:
             self.logger.info(f"Categorization process completed for {target_filename} (at least one category created).")
        else:
             self.logger.warning(f"Categorization enabled but no suitable categories found or created for {target_filename}.")
             
        return at_least_one_category_created
    
    def _move_to_problematic(self, file_path: Path, reason_tag: str) -> None:
         """ Helper function to move a file to the problematic directory. """
         if not self.move_problematic or not self.problematic_dir:
             return # Moving problematic files is disabled

         try:
             ensure_dir(self.problematic_dir)
             target_path = self.problematic_dir / f"ERROR_{reason_tag}_{file_path.name}"
             
             if not target_path.exists():
                 shutil.copy2(file_path, target_path) # Copy first
                 self.logger.info(f"Moved file with {reason_tag} to Unnamed Article: {target_path}")
                 try:
                     file_path.unlink() # Then delete original
                     self.logger.debug(f"Removed original file {file_path.name} after moving due to {reason_tag}.")
                 except Exception as e_unlink:
                     self.logger.error(f"File System Error (unlink): Failed to remove original {file_path} after moving for {reason_tag}: {e_unlink}")
             else:
                 self.logger.warning(f"File {file_path.name} already exists in problematic dir as {target_path} (reason: {reason_tag}), skipping move.")
         except (OSError, IOError, PermissionError) as e_move:
             self.logger.error(f"File System Error (move): Failed to move problematic file {file_path.name} for {reason_tag}: {e_move}")
         except Exception as e_generic:
             self.logger.error(f"Error moving problematic file {file_path.name} for {reason_tag}: {e_generic}")


# Example usage (for testing or command-line interface)
# if __name__ == '__main__':
#     # Setup basic logging for testing
#     log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
#     logging.basicConfig(level=logging.DEBUG, format=log_format)
#     logger = logging.getLogger('litorganizer.test')
    
#     # Configure processor
#     processor = PDFProcessor(
#         directory='../tests/test_pdfs', 
#         use_ocr=False, 
#         create_references=True,
#         create_backups=True,
#         move_problematic=True,
#         categorize_options={"year": True, "journal": True, "author": False, "subject": False},
#         logger=logger
#     )
    
#     # Run processing
#     success = processor.process_files()
#     if success:
#         logger.info("PDF processing completed successfully.")
#     else:
#         logger.error("PDF processing failed.") 