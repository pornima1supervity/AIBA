#!/usr/bin/env python3
"""
Utility script to convert existing BRD markdown files to PDF
Usage: python convert_md_to_pdf.py <markdown_file>
"""

import os
import sys
from datetime import datetime

try:
    import markdown
except ImportError:
    print("❌ Error: 'markdown' library not found. Install it with: pip install markdown")
    sys.exit(1)

def markdown_to_html(markdown_content):
    """Convert markdown content to HTML"""
    # Try to use extensions, but handle if they're not available
    extensions = ['extra', 'tables']
    
    # Try to add codehilite if Pygments is available
    try:
        import pygments
        extensions.append('codehilite')
    except ImportError:
        pass
    
    html_body = markdown.markdown(
        markdown_content,
        extensions=extensions
    )
    
    # Professional CSS styling for PDF
    css_style = """
    <style>
        @page {
            size: A4;
            margin: 2cm;
            @top-center {
                content: "Business Requirements Document";
                font-size: 10pt;
                color: #666;
            }
            @bottom-center {
                content: "Page " counter(page) " of " counter(pages);
                font-size: 10pt;
                color: #666;
            }
        }
        body {
            font-family: 'Helvetica', 'Arial', sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
            max-width: 100%;
        }
        h1 {
            color: #1a237e;
            font-size: 24pt;
            margin-top: 20pt;
            margin-bottom: 12pt;
            border-bottom: 3px solid #1a237e;
            padding-bottom: 8pt;
        }
        h2 {
            color: #283593;
            font-size: 18pt;
            margin-top: 16pt;
            margin-bottom: 10pt;
            border-bottom: 2px solid #283593;
            padding-bottom: 6pt;
        }
        h3 {
            color: #3949ab;
            font-size: 14pt;
            margin-top: 12pt;
            margin-bottom: 8pt;
        }
        h4 {
            color: #5c6bc0;
            font-size: 12pt;
            margin-top: 10pt;
            margin-bottom: 6pt;
        }
        p {
            margin: 8pt 0;
            text-align: justify;
        }
        ul, ol {
            margin: 8pt 0;
            padding-left: 24pt;
        }
        li {
            margin: 4pt 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 12pt 0;
            page-break-inside: avoid;
        }
        th {
            background-color: #3949ab;
            color: white;
            padding: 8pt;
            text-align: left;
            font-weight: bold;
            border: 1px solid #283593;
        }
        td {
            padding: 6pt 8pt;
            border: 1px solid #ddd;
        }
        tr:nth-child(even) {
            background-color: #f5f5f5;
        }
        code {
            background-color: #f4f4f4;
            padding: 2pt 4pt;
            border-radius: 3pt;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
        }
        pre {
            background-color: #f4f4f4;
            padding: 10pt;
            border-radius: 4pt;
            overflow-x: auto;
            page-break-inside: avoid;
        }
        blockquote {
            border-left: 4px solid #3949ab;
            padding-left: 12pt;
            margin: 8pt 0;
            color: #555;
            font-style: italic;
        }
        hr {
            border: none;
            border-top: 2px solid #ddd;
            margin: 16pt 0;
        }
        strong {
            color: #1a237e;
            font-weight: bold;
        }
        .metadata {
            background-color: #f5f5f5;
            padding: 10pt;
            border-radius: 4pt;
            margin-bottom: 16pt;
            font-size: 10pt;
        }
    </style>
    """
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Business Requirements Document</title>
        {css_style}
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """
    
    return html_content

def convert_md_to_pdf(md_file_path):
    """Convert markdown file to PDF"""
    if not os.path.exists(md_file_path):
        print(f"❌ Error: File '{md_file_path}' not found.")
        return False
    
    # Read markdown file
    try:
        with open(md_file_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    # Generate PDF filename
    base_name = os.path.splitext(md_file_path)[0]
    pdf_filename = f"{base_name}.pdf"
    
    # Try to import WeasyPrint
    try:
        # Set library path for macOS Homebrew installations
        if 'DYLD_LIBRARY_PATH' not in os.environ:
            homebrew_lib = '/opt/homebrew/lib'
            if os.path.exists(homebrew_lib):
                os.environ['DYLD_LIBRARY_PATH'] = homebrew_lib
        
        from weasyprint import HTML
    except (ImportError, OSError) as e:
        print(f"❌ Error: WeasyPrint not available: {e}")
        print("\n💡 To enable PDF generation, you need to:")
        print("   1. Install WeasyPrint: pip install weasyprint")
        print("   2. Install system dependencies:")
        print("      macOS: brew install pango gdk-pixbuf libffi")
        print("      Linux: sudo apt-get install libpango-1.0-0 libgdk-pixbuf2.0-0")
        return False
    
    try:
        print(f"🔄 Converting '{md_file_path}' to PDF...")
        html_content = markdown_to_html(markdown_content)
        HTML(string=html_content).write_pdf(pdf_filename)
        print(f"✅ PDF generated successfully!")
        print(f"📁 PDF File: {pdf_filename}")
        print(f"📄 Size: {os.path.getsize(pdf_filename)} bytes")
        return True
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_md_to_pdf.py <markdown_file>")
        print("\nExample: python convert_md_to_pdf.py BRD_sdefsfe_adfedf_20251212_145447.md")
        sys.exit(1)
    
    md_file = sys.argv[1]
    success = convert_md_to_pdf(md_file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

