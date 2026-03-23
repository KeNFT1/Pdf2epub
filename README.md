# PDF to ePub Converter

A Windows application that converts PDF files to ePub format while preserving formatting, hyperlinks, and table of contents navigation.

## Features

✅ **Hyperlink Preservation** - Maintains TOC navigation and internal document links  
✅ **Format Preservation** - Keeps text formatting (bold, italic, headings)  
✅ **Image Support** - Extracts and includes images from PDF  
✅ **Table of Contents** - Creates navigable ePub TOC from PDF bookmarks  
✅ **Windows GUI** - Easy-to-use graphical interface  
✅ **Standalone Executable** - No Python installation required  

## Download & Installation

### Option 1: Download Pre-built Executable
1. Download `PDF2ePub-Converter.exe` from the releases page
2. Run the executable directly - no installation needed
3. Windows may show a security warning (click "More info" → "Run anyway")

### Option 2: Build from Source

#### Prerequisites
- Python 3.8 or higher
- Windows 10/11

#### Build Steps
1. Clone or download this repository
2. Open Command Prompt as Administrator
3. Navigate to the project folder
4. Run the build script:
   ```cmd
   build.bat
   ```
5. Find the executable in the `dist` folder

## Usage

1. **Launch** the application (`PDF2ePub-Converter.exe`)
2. **Select PDF** - Click "Browse..." next to "PDF File" and choose your PDF
3. **Choose output** - Specify where to save the ePub file (auto-suggested)
4. **Configure options**:
   - ✅ Preserve hyperlinks and table of contents *(recommended)*
   - ✅ Preserve text formatting *(recommended)*  
   - ✅ Include images from PDF *(recommended)*
5. **Convert** - Click "Convert to ePub" and wait for completion
6. **Open result** - Optionally open the output folder when prompted

## Conversion Options

### Preserve Hyperlinks and TOC
- Extracts PDF bookmarks and creates ePub navigation
- Maintains internal document links between sections
- **Highly recommended** for documents with navigation

### Preserve Text Formatting  
- Maintains bold, italic, and heading styles
- Detects different font sizes for heading hierarchy
- **Recommended** for formatted documents

### Include Images
- Extracts all images from PDF pages
- Embeds images in the ePub file
- **Recommended** unless file size is a concern

## Technical Details

### Supported Input
- **PDF files** with text content
- **Scanned PDFs** (limited support - text must be searchable)
- **Password-protected PDFs** are not supported

### Output Format
- **ePub 3.0** compatible with most e-readers
- **Responsive design** adapts to different screen sizes
- **Standard navigation** works with all ePub readers

### Dependencies
- **PyMuPDF** - PDF processing and text extraction
- **EbookLib** - ePub creation and manipulation  
- **Pillow** - Image processing
- **tkinter** - GUI framework (built into Python)

## Troubleshooting

### "Windows protected your PC" Warning
This is normal for unsigned executables. Click "More info" → "Run anyway"

### "Failed to execute script" Error
- Ensure the PDF file is not corrupted
- Check that you have write permissions to the output folder
- Try a different output location

### Missing Text in Output
- The PDF may contain scanned images instead of text
- Try OCR software to make the PDF searchable first

### Large File Size
- Disable "Include images" option to reduce ePub size
- Use PDF compression tools before conversion

## Command Line Usage

For advanced users, the converter can be used from command line:

```cmd
python main.py
```

Or use the converter engine directly:

```python
from converter import PDFToEpubConverter

converter = PDFToEpubConverter()
options = {
    'preserve_hyperlinks': True,
    'preserve_formatting': True, 
    'include_images': True
}
converter.convert('input.pdf', 'output.epub', options)
```

## License

MIT License - Feel free to use, modify, and distribute.

## Contributing

Issues and pull requests are welcome! Please test thoroughly on different PDF types.

## Version History

- **v1.0** - Initial release with hyperlink preservation and Windows GUI
---

<div align="center">
  <img src="https://i2c.seadn.io/base/0x7e72abdf47bd21bf0ed6ea8cb8dad60579f3fb50/15a6a479d27af55a24429efacb4050/8f15a6a479d27af55a24429efacb4050.png" width="80" alt="BAYC #2253" />
  <br/>
  <sub>Built by <a href="https://github.com/KeNFT1">KeNFT1</a> 🦍 BAYC #2253</sub>
</div>

