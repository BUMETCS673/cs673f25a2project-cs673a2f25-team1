"""
OCR processing modules for rental statement PDF extraction.

This package contains:
- azure_processor.py: Azure Document Intelligence integration for PDF OCR
- ocr_processor_v1.py, v2.py, v3.py: Original OCR processing scripts using pdftotext/Tesseract
- test_pdf_upload.html: HTML test interface for PDF upload endpoint
"""

from .azure_processor import get_ocr_processor, AzureDocumentProcessor, LocalOCRProcessor

__all__ = ['get_ocr_processor', 'AzureDocumentProcessor', 'LocalOCRProcessor']