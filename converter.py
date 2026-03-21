#!/usr/bin/env python3
"""
PDF to ePub Converter Engine
Handles the actual conversion while preserving hyperlinks and formatting
"""

import fitz  # PyMuPDF
from ebooklib import epub
import os
import re
import uuid
from pathlib import Path
from urllib.parse import quote
import base64
from PIL import Image
import io


class PDFToEpubConverter:
    def __init__(self):
        self.doc = None
        self.epub_book = None
        self.toc_items = []
        self.links_map = {}  # Maps PDF page references to ePub chapter anchors
        self.images = {}     # Stores extracted images
        
    def convert(self, pdf_path, epub_path, options, progress_callback=None, log_callback=None):
        """
        Main conversion function
        
        Args:
            pdf_path: Path to input PDF file
            epub_path: Path to output ePub file
            options: Dictionary of conversion options
            progress_callback: Function to call for progress updates
            log_callback: Function to call for logging messages
            
        Returns:
            bool: True if conversion successful, False otherwise
        """
        try:
            if log_callback:
                log_callback("Opening PDF document...")
            
            # Open PDF document
            self.doc = fitz.open(pdf_path)
            
            if log_callback:
                log_callback(f"PDF loaded: {len(self.doc)} pages")
            
            # Create ePub book
            self.epub_book = epub.EpubBook()
            
            # Set basic metadata
            self._set_metadata(pdf_path)
            
            if progress_callback:
                progress_callback("Extracting table of contents...")
            
            # Extract table of contents if preserve_hyperlinks is enabled
            if options.get('preserve_hyperlinks', True):
                self._extract_toc()
                if log_callback:
                    log_callback(f"Extracted {len(self.toc_items)} TOC items")
            
            if progress_callback:
                progress_callback("Processing pages...")
            
            # Process each page
            chapters = []
            for page_num in range(len(self.doc)):
                if progress_callback:
                    progress_callback(f"Processing page {page_num + 1} of {len(self.doc)}")
                    
                chapter = self._process_page(page_num, options, log_callback)
                if chapter:
                    chapters.append(chapter)
                    self.epub_book.add_item(chapter)
                    
            if progress_callback:
                progress_callback("Creating navigation...")
                
            # Create table of contents and navigation
            self._create_navigation(chapters)
            
            if progress_callback:
                progress_callback("Adding stylesheets...")
                
            # Add default CSS
            self._add_stylesheet()
            
            if progress_callback:
                progress_callback("Saving ePub file...")
                
            # Write ePub file
            epub.write_epub(epub_path, self.epub_book)
            
            if log_callback:
                log_callback(f"ePub file saved successfully: {epub_path}")
                
            return True
            
        except Exception as e:
            if log_callback:
                log_callback(f"Error during conversion: {str(e)}")
            return False
            
        finally:
            if self.doc:
                self.doc.close()
                
    def _set_metadata(self, pdf_path):
        """Set ePub metadata from PDF"""
        # Get PDF metadata
        metadata = self.doc.metadata
        
        # Set basic metadata
        filename = Path(pdf_path).stem
        self.epub_book.set_identifier(str(uuid.uuid4()))
        self.epub_book.set_title(metadata.get('title', filename))
        self.epub_book.set_language('en')
        
        if metadata.get('author'):
            self.epub_book.add_author(metadata['author'])
        else:
            self.epub_book.add_author('Unknown')
            
        if metadata.get('subject'):
            self.epub_book.add_metadata('DC', 'description', metadata['subject'])
            
    def _extract_toc(self):
        """Extract table of contents from PDF"""
        try:
            toc = self.doc.get_toc()
            self.toc_items = []
            
            for item in toc:
                level, title, page_num = item
                # Convert 1-based page number to 0-based
                page_index = max(0, page_num - 1)
                
                self.toc_items.append({
                    'level': level,
                    'title': title.strip(),
                    'page': page_index,
                    'anchor': f"page_{page_index}"
                })
                
            # Sort by page number to ensure proper order
            self.toc_items.sort(key=lambda x: x['page'])
            
        except Exception as e:
            # If TOC extraction fails, continue without it
            self.toc_items = []
            
    def _process_page(self, page_num, options, log_callback):
        """Process a single PDF page"""
        try:
            page = self.doc[page_num]
            
            # Get text with formatting
            text_dict = page.get_text("dict")
            
            # Extract images if enabled
            images_html = ""
            if options.get('include_images', True):
                images_html = self._extract_page_images(page, page_num)
                
            # Convert text to HTML with formatting
            html_content = self._convert_text_to_html(text_dict, options.get('preserve_formatting', True))
            
            # Combine images and text
            full_content = images_html + html_content
            
            if not full_content.strip():
                return None  # Skip empty pages
                
            # Create chapter
            chapter_id = f"chapter_{page_num:03d}"
            chapter_filename = f"{chapter_id}.xhtml"
            
            # Add page anchor for TOC linking
            page_anchor = f'<div id="page_{page_num}"></div>'
            
            chapter_html = f"""<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Page {page_num + 1}</title>
    <link rel="stylesheet" type="text/css" href="stylesheet.css"/>
</head>
<body>
    {page_anchor}
    <div class="page-content">
        {full_content}
    </div>
</body>
</html>"""

            chapter = epub.EpubHtml(
                title=f"Page {page_num + 1}",
                file_name=chapter_filename,
                content=chapter_html
            )
            
            return chapter
            
        except Exception as e:
            if log_callback:
                log_callback(f"Error processing page {page_num + 1}: {str(e)}")
            return None
            
    def _extract_page_images(self, page, page_num):
        """Extract images from a PDF page"""
        images_html = ""
        
        try:
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                
                # Extract image data
                base_image = self.doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # Create image filename
                image_filename = f"image_page_{page_num:03d}_{img_index:03d}.{image_ext}"
                
                # Add image to ePub
                epub_image = epub.EpubImage()
                epub_image.file_name = f"images/{image_filename}"
                epub_image.media_type = f"image/{image_ext}"
                epub_image.content = image_bytes
                
                self.epub_book.add_item(epub_image)
                
                # Add image to HTML
                images_html += f'<div class="image-container"><img src="images/{image_filename}" alt="Image from page {page_num + 1}" /></div>\n'
                
        except Exception:
            # If image extraction fails, continue without images
            pass
            
        return images_html
        
    def _convert_text_to_html(self, text_dict, preserve_formatting):
        """Convert PyMuPDF text dictionary to HTML"""
        html_parts = []
        
        try:
            for block in text_dict.get("blocks", []):
                if block.get("type") == 0:  # Text block
                    block_html = self._process_text_block(block, preserve_formatting)
                    if block_html:
                        html_parts.append(block_html)
                        
        except Exception:
            # Fallback to simple text extraction
            page = self.doc[0]  # This should be the current page
            simple_text = page.get_text()
            html_parts.append(f'<p>{self._escape_html(simple_text)}</p>')
            
        return "\n".join(html_parts)
        
    def _process_text_block(self, block, preserve_formatting):
        """Process a text block and convert to HTML"""
        html_lines = []
        
        for line in block.get("lines", []):
            line_html = ""
            
            for span in line.get("spans", []):
                text = span.get("text", "")
                if not text.strip():
                    continue
                    
                # Escape HTML characters
                text = self._escape_html(text)
                
                if preserve_formatting:
                    # Apply formatting based on font flags
                    flags = span.get("flags", 0)
                    
                    # Check for bold
                    if flags & 2**4:  # Bold flag
                        text = f"<strong>{text}</strong>"
                        
                    # Check for italic  
                    if flags & 2**1:  # Italic flag
                        text = f"<em>{text}</em>"
                        
                    # Check font size for headings
                    font_size = span.get("size", 12)
                    if font_size > 16:
                        text = f"<h2>{text}</h2>"
                    elif font_size > 14:
                        text = f"<h3>{text}</h3>"
                        
                line_html += text
                
            if line_html.strip():
                html_lines.append(f"<p>{line_html}</p>")
                
        return "\n".join(html_lines)
        
    def _escape_html(self, text):
        """Escape HTML special characters"""
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        text = text.replace('"', "&quot;")
        text = text.replace("'", "&#x27;")
        return text
        
    def _create_navigation(self, chapters):
        """Create ePub navigation from TOC items"""
        
        # Create navigation document
        nav_content = '''<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
    <title>Navigation</title>
    <link rel="stylesheet" type="text/css" href="stylesheet.css"/>
</head>
<body>
    <nav epub:type="toc" id="toc">
        <h2>Table of Contents</h2>
        <ol>'''
        
        if self.toc_items:
            # Use extracted TOC
            for item in self.toc_items:
                title = self._escape_html(item['title'])
                page_num = item['page']
                
                # Find corresponding chapter
                if page_num < len(chapters):
                    chapter_filename = f"chapter_{page_num:03d}.xhtml"
                    anchor = f"#{item['anchor']}"
                    nav_content += f'<li><a href="{chapter_filename}{anchor}">{title}</a></li>\n'
        else:
            # Create simple navigation based on pages
            for i, chapter in enumerate(chapters):
                nav_content += f'<li><a href="{chapter.file_name}">Page {i + 1}</a></li>\n'
                
        nav_content += '''        </ol>
    </nav>
</body>
</html>'''

        # Add navigation document
        nav_doc = epub.EpubNav()
        nav_doc.content = nav_content
        self.epub_book.add_item(nav_doc)
        
        # Create spine (reading order)
        self.epub_book.spine = ['nav'] + chapters
        
        # Create NCX (for compatibility)
        self.epub_book.add_item(epub.EpubNcx())
        
    def _add_stylesheet(self):
        """Add default CSS stylesheet"""
        css_content = """
/* Default styles for PDF to ePub conversion */

body {
    font-family: "Times New Roman", serif;
    line-height: 1.6;
    margin: 1em;
    color: #000000;
}

h1, h2, h3, h4, h5, h6 {
    color: #333333;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
}

h1 { font-size: 1.8em; }
h2 { font-size: 1.5em; }
h3 { font-size: 1.2em; }

p {
    margin-bottom: 1em;
    text-align: justify;
}

.page-content {
    max-width: 100%;
    margin: 0 auto;
}

.image-container {
    text-align: center;
    margin: 1em 0;
}

.image-container img {
    max-width: 100%;
    height: auto;
}

/* Navigation styles */
nav#toc ol {
    list-style-type: none;
    padding-left: 0;
}

nav#toc li {
    margin: 0.5em 0;
}

nav#toc a {
    text-decoration: none;
    color: #0066cc;
}

nav#toc a:hover {
    text-decoration: underline;
}

/* Responsive design */
@media screen and (max-width: 600px) {
    body {
        margin: 0.5em;
        font-size: 1.1em;
    }
}
"""

        # Add CSS file
        nav_css = epub.EpubItem(
            uid="style",
            file_name="stylesheet.css",
            media_type="text/css",
            content=css_content
        )
        self.epub_book.add_item(nav_css)