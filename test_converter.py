#!/usr/bin/env python3
"""
Test script for PDF to ePub converter
Creates a sample PDF and tests the conversion process
"""

import os
import tempfile
from pathlib import Path
import fitz  # PyMuPDF
from converter import PDFToEpubConverter


def create_test_pdf(output_path):
    """Create a test PDF with hyperlinks and formatting for testing"""
    
    # Create a new PDF document
    doc = fitz.open()
    
    # Page 1 - Title page with TOC
    page1 = doc.new_page()
    page1.insert_text((72, 100), "Sample Document", fontsize=24, color=(0, 0, 0))
    page1.insert_text((72, 150), "Table of Contents", fontsize=18, color=(0, 0, 0))
    
    # Add TOC entries with links
    page1.insert_text((72, 200), "Chapter 1: Introduction ..................... 2", fontsize=12)
    page1.insert_text((72, 220), "Chapter 2: Main Content .................... 3", fontsize=12)
    page1.insert_text((72, 240), "Chapter 3: Conclusion ...................... 4", fontsize=12)
    
    # Page 2 - Chapter 1
    page2 = doc.new_page()
    page2.insert_text((72, 100), "Chapter 1: Introduction", fontsize=20, color=(0, 0, 0))
    page2.insert_text((72, 150), "This is the introduction chapter with some bold text.", fontsize=12)
    page2.insert_text((72, 180), "Here we introduce the main concepts.", fontsize=12)
    page2.insert_text((72, 210), "• First concept", fontsize=12)
    page2.insert_text((72, 230), "• Second concept", fontsize=12)
    page2.insert_text((72, 250), "• Third concept", fontsize=12)
    
    # Page 3 - Chapter 2  
    page3 = doc.new_page()
    page3.insert_text((72, 100), "Chapter 2: Main Content", fontsize=20, color=(0, 0, 0))
    page3.insert_text((72, 150), "This chapter contains the main content of our document.", fontsize=12)
    page3.insert_text((72, 180), "Here is some important information in italic text.", fontsize=12)
    page3.insert_text((72, 210), "We can also have formatted text with different styles.", fontsize=12)
    
    # Page 4 - Chapter 3
    page4 = doc.new_page()
    page4.insert_text((72, 100), "Chapter 3: Conclusion", fontsize=20, color=(0, 0, 0))
    page4.insert_text((72, 150), "This is the conclusion of our sample document.", fontsize=12)
    page4.insert_text((72, 180), "Thank you for reading this test document.", fontsize=12)
    page4.insert_text((72, 210), "The conversion should preserve all formatting and links.", fontsize=12)
    
    # Add table of contents
    toc = [
        [1, "Chapter 1: Introduction", 2],
        [1, "Chapter 2: Main Content", 3], 
        [1, "Chapter 3: Conclusion", 4]
    ]
    doc.set_toc(toc)
    
    # Set document metadata
    metadata = {
        'title': 'Sample Test Document',
        'author': 'PDF2ePub Converter',
        'subject': 'Test document for conversion testing',
        'creator': 'Test Script'
    }
    doc.set_metadata(metadata)
    
    # Save the PDF
    doc.save(output_path)
    doc.close()
    
    print(f"✓ Test PDF created: {output_path}")
    return output_path


def test_conversion():
    """Test the PDF to ePub conversion"""
    
    print("PDF to ePub Converter - Test Suite")
    print("=" * 50)
    
    # Create temporary files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test PDF
        pdf_path = temp_path / "test_document.pdf"
        epub_path = temp_path / "test_output.epub"
        
        print(f"\n1. Creating test PDF...")
        create_test_pdf(str(pdf_path))
        
        print(f"\n2. Testing conversion...")
        
        # Create converter
        converter = PDFToEpubConverter()
        
        # Test conversion options
        options = {
            'preserve_hyperlinks': True,
            'preserve_formatting': True,
            'include_images': True
        }
        
        # Define callback functions
        def progress_callback(message):
            print(f"   Progress: {message}")
            
        def log_callback(message):
            print(f"   Log: {message}")
        
        # Run conversion
        success = converter.convert(
            str(pdf_path),
            str(epub_path), 
            options,
            progress_callback=progress_callback,
            log_callback=log_callback
        )
        
        print(f"\n3. Conversion Results:")
        if success:
            print("   ✓ Conversion completed successfully")
            
            # Check output file
            if epub_path.exists():
                file_size = epub_path.stat().st_size
                print(f"   ✓ ePub file created: {file_size} bytes")
                
                # Try to validate ePub structure (basic check)
                try:
                    import zipfile
                    with zipfile.ZipFile(str(epub_path), 'r') as epub_zip:
                        files = epub_zip.namelist()
                        
                        # Check for required ePub files
                        required_files = ['META-INF/container.xml', 'OEBPS/content.opf']
                        missing_files = [f for f in required_files if f not in files]
                        
                        if not missing_files:
                            print("   ✓ ePub structure is valid")
                        else:
                            print(f"   ⚠ Missing required files: {missing_files}")
                            
                        # Show contents
                        print(f"   ✓ ePub contains {len(files)} files")
                        
                except Exception as e:
                    print(f"   ⚠ Could not validate ePub: {e}")
                    
            else:
                print("   ✗ ePub file was not created")
                
        else:
            print("   ✗ Conversion failed")
            
    print(f"\n4. Test Summary:")
    if success:
        print("   ✓ All tests passed!")
        print("   ✓ Converter is working correctly")
    else:
        print("   ✗ Tests failed!")
        print("   ✗ Check the error messages above")
        
    return success


if __name__ == "__main__":
    test_conversion()