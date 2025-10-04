"""
Azure Document Intelligence processor for rental statement PDFs.
Handles multiple PDF layouts using Azure's AI-powered document extraction.
"""
import os
import io
import re
from typing import Dict, Optional, Any, Tuple
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import logging

logger = logging.getLogger(__name__)

class AzureDocumentProcessor:
    """Process rental statement PDFs using Azure Document Intelligence."""

    def __init__(self, endpoint: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize Azure Document Intelligence client.

        Args:
            endpoint: Azure endpoint URL (defaults to env var AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT)
            api_key: Azure API key (defaults to env var AZURE_DOCUMENT_INTELLIGENCE_KEY)
        """
        self.endpoint = endpoint or os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
        self.api_key = api_key or os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')

        if not self.endpoint or not self.api_key:
            raise ValueError(
                "Azure Document Intelligence credentials not provided. "
                "Set AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT and AZURE_DOCUMENT_INTELLIGENCE_KEY environment variables."
            )

        self.client = DocumentAnalysisClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.api_key)
        )

    def process_pdf_bytes(self, pdf_bytes: bytes, model_id: str = "prebuilt-document") -> Tuple[Dict[str, Any], float]:
        """
        Process PDF bytes using Azure Document Intelligence.

        Args:
            pdf_bytes: PDF file content as bytes
            model_id: Azure model to use (default: prebuilt-invoice for financial documents)

        Returns:
            Tuple of (extracted_data, confidence_score)
        """
        try:
            # Analyze document
            poller = self.client.begin_analyze_document(
                model_id=model_id,
                document=io.BytesIO(pdf_bytes)
            )
            result = poller.result()

            # Extract fields from rental statements
            extracted_data = {
                'rent': None,
                'management_fee': None,
                'repair': None,
                'deposit': None,
                'misc': None,
                'total': None,
                'date': None,
                'property_id': None
            }

            field_confidences = {}

            # For prebuilt-document, also check key-value pairs
            if result.key_value_pairs:
                print(f"[DEBUG] Found {len(result.key_value_pairs)} key-value pairs")
                for kv in result.key_value_pairs:
                    if kv.key and kv.value:
                        key_text = kv.key.content.lower()
                        value_text = kv.value.content

                        # Try to extract values based on key text
                        try:
                            if 'management fee' in key_text:
                                # Extract number from value (e.g., "40.00" from "40.00")
                                number_match = re.search(r'[\d,]+\.?\d*', value_text)
                                if number_match:
                                    extracted_data['management_fee'] = float(number_match.group().replace(',', ''))
                                    field_confidences['management_fee'] = kv.confidence or 0.8
                                    print(f"[DEBUG] Found management fee via KV pairs: {extracted_data['management_fee']}")

                            elif any(term in key_text for term in ['rent', 'income', 'rental income']):
                                number_match = re.search(r'[\d,]+\.?\d*', value_text)
                                if number_match:
                                    extracted_data['rent'] = float(number_match.group().replace(',', ''))
                                    field_confidences['rent'] = kv.confidence or 0.8
                                    print(f"[DEBUG] Found rent via KV pairs: {extracted_data['rent']}")

                            elif 'total' in key_text and 'balance' in key_text:
                                number_match = re.search(r'[\d,]+\.?\d*', value_text)
                                if number_match:
                                    extracted_data['total'] = float(number_match.group().replace(',', ''))
                                    field_confidences['total'] = kv.confidence or 0.8
                        except (ValueError, AttributeError):
                            pass

            # Process the first document (assuming single-page statements)
            if result.documents:
                doc = result.documents[0]

                # Debug logging - see what fields Azure detected
                print(f"[DEBUG] Azure detected document fields: {list(doc.fields.keys()) if doc.fields else 'None'}")

                # Map Azure fields to our schema (now using prebuilt-document model)
                # Removed CustomerName/VendorName as they map to agent/landlord, not property
                field_mappings = {
                    'InvoiceTotal': 'total',
                    'AmountDue': 'total',
                    'Total': 'total',
                    'InvoiceDate': 'date',
                    'Date': 'date',
                    # property_id will be extracted by regex fallback instead
                }

                # Known letting agents to filter out from property_id
                KNOWN_AGENTS = [
                    'TM Residential', 'Clyde Office', 'Letting', 'Property Management',
                    'Residential Services', 'Estate Agent', 'Lettings', 'Realty'
                ]

                # Extract mapped fields
                for azure_field, our_field in field_mappings.items():
                    if azure_field in doc.fields:
                        field_value = doc.fields[azure_field]
                        if field_value.value is not None:
                            # Convert CurrencyValue to float if needed
                            value = field_value.value
                            if hasattr(value, 'amount'):
                                value = float(value.amount)
                            elif isinstance(value, (int, float)):
                                value = float(value)
                            else:
                                value = str(value)

                            # Filter out known agents from property_id
                            if our_field == 'property_id' and isinstance(value, str):
                                is_agent = any(agent.lower() in value.lower() for agent in KNOWN_AGENTS)
                                if is_agent:
                                    print(f"[DEBUG] Filtered out agent name from property_id: {value}")
                                    continue  # Skip this mapping

                            extracted_data[our_field] = value
                            field_confidences[our_field] = field_value.confidence or 0.0

                # Look for line items (for detailed fee breakdown)
                if 'Items' in doc.fields and doc.fields['Items'].value:
                    print(f"[DEBUG] Found {len(doc.fields['Items'].value)} line items")
                    for idx, item in enumerate(doc.fields['Items'].value):
                        if hasattr(item, 'value') and hasattr(item.value, 'fields'):
                            item_fields = item.value.fields
                            description = item_fields.get('Description', {}).value if 'Description' in item_fields else None
                            amount = item_fields.get('Amount', {}).value if 'Amount' in item_fields else None

                            # Log what we found
                            print(f"[DEBUG] Item {idx}: Description='{description}', Amount={amount}")

                            if description and amount:
                                desc_lower = str(description).lower()
                                # Convert amount to float if it's a CurrencyValue
                                if hasattr(amount, 'amount'):
                                    amount_value = float(amount.amount)
                                else:
                                    amount_value = float(amount)

                                # More flexible matching for management fees
                                if any(term in desc_lower for term in ['management', 'admin', 'fee', 'service', 'property management']):
                                    extracted_data['management_fee'] = amount_value
                                    field_confidences['management_fee'] = item_fields.get('Amount', {}).confidence or 0.0
                                    print(f"[DEBUG] Matched management fee: {amount_value}")
                                elif any(term in desc_lower for term in ['repair', 'maintenance', 'fix']):
                                    extracted_data['repair'] = amount_value
                                    field_confidences['repair'] = item_fields.get('Amount', {}).confidence or 0.0
                                elif 'deposit' in desc_lower:
                                    extracted_data['deposit'] = amount_value
                                    field_confidences['deposit'] = item_fields.get('Amount', {}).confidence or 0.0
                                elif any(term in desc_lower for term in ['rent', 'rental', 'rent received', 'income']):
                                    # Only set if not already set by KV pairs (preserve higher confidence)
                                    if extracted_data.get('rent') is None:
                                        extracted_data['rent'] = amount_value
                                        field_confidences['rent'] = item_fields.get('Amount', {}).confidence or 0.0
                                        print(f"[DEBUG] Matched rent via line items: {amount_value}")
                else:
                    print("[DEBUG] No line items found in document")

            # Fallback: Try to extract management fee from the raw text content
            if extracted_data.get('management_fee') is None and hasattr(result, 'content'):
                print(f"[DEBUG] Trying regex fallback on document text")
                text_content = result.content

                # Look for management fee pattern
                mgmt_patterns = [
                    r'Management\s+fee\s*\([^)]+\)\s*[\d,]+\.?\d*',  # "Management fee (10%) 40.00"
                    r'Management\s+fee.*?(\d+[\d,]*\.?\d*)',  # Any management fee followed by number
                    r'Management.*?£(\d+[\d,]*\.?\d*)',  # Management with pound sign
                ]

                for pattern in mgmt_patterns:
                    match = re.search(pattern, text_content, re.IGNORECASE)
                    if match:
                        # Extract just the numeric part
                        num_match = re.search(r'(\d+[\d,]*\.?\d*)$', match.group())
                        if num_match:
                            try:
                                extracted_data['management_fee'] = float(num_match.group().replace(',', ''))
                                field_confidences['management_fee'] = 0.75  # Medium confidence for regex
                                print(f"[DEBUG] Found management fee via regex: {extracted_data['management_fee']}")
                                break
                            except ValueError:
                                pass

            # Fallback: Try to extract rent from raw text content
            if extracted_data.get('rent') is None and hasattr(result, 'content'):
                print(f"[DEBUG] Trying regex fallback for rent")
                text_content = result.content

                # Try multiple patterns for rent
                rent_patterns = [
                    r'Rent\s+received\s*\([^)]+\)\s*(\d+[\d,]*\.?\d*)',  # "Rent received (date range) 400.00"
                    r'INCOME\s*(\d+[\d,]*\.?\d*)',                        # "INCOME 400.00"
                    r'Total\s+income\s*(\d+[\d,]*\.?\d*)',                # "Total income 400.00"
                    r'Rental\s+income\s*(\d+[\d,]*\.?\d*)',               # "Rental income 400.00"
                ]

                for pattern in rent_patterns:
                    match = re.search(pattern, text_content, re.IGNORECASE)
                    if match:
                        try:
                            extracted_data['rent'] = float(match.group(1).replace(',', ''))
                            field_confidences['rent'] = 0.75  # Medium confidence for regex
                            print(f"[DEBUG] Found rent via regex: {extracted_data['rent']}")
                            break  # Stop after first match
                        except ValueError:
                            continue  # Try next pattern

            # Fallback: Try to extract property_id from raw text content
            if extracted_data.get('property_id') is None and hasattr(result, 'content'):
                print(f"[DEBUG] Trying regex fallback for property address")
                text_content = result.content

                # UK rental statement property patterns
                property_patterns = [
                    # Pattern 1: "Property: Flat 2, 1 Bedford Avenue, G81 2PL"
                    r'Property:\s*([^,\n]+(?:,\s*[^,\n]+)*,\s*[A-Z]{1,2}\d{1,2}\s?\d?[A-Z]{2})',

                    # Pattern 2: "Property Address: ..."
                    r'Property\s+[Aa]ddress:\s*([^,\n]+(?:,\s*[^,\n]+)*,\s*[A-Z]{1,2}\d{1,2}\s?\d?[A-Z]{2})',

                    # Pattern 3: Labeled line ending with UK postcode
                    r'(?:Property|Address):\s*(.+?[A-Z]{1,2}\d{1,2}\s?\d?[A-Z]{2})',
                ]

                for pattern in property_patterns:
                    match = re.search(pattern, text_content, re.IGNORECASE | re.MULTILINE)
                    if match:
                        # Clean up the extracted address
                        property_address = match.group(1).strip()
                        # Remove extra whitespace and newlines
                        property_address = ' '.join(property_address.split())

                        extracted_data['property_id'] = property_address
                        field_confidences['property_id'] = 0.75  # Medium confidence for regex
                        print(f"[DEBUG] Found property via regex: {property_address}")
                        break  # Stop after first match

            # Fallback: Try to extract date from raw text content
            if extracted_data.get('date') is None and hasattr(result, 'content'):
                print(f"[DEBUG] Trying regex fallback for statement date")
                text_content = result.content

                # UK rental statement date patterns
                date_patterns = [
                    # Pattern 1: "Statement as at 25/07/2023"
                    r'Statement\s+as\s+at\s+(\d{1,2}/\d{1,2}/\d{4})',

                    # Pattern 2: "Statement date: 25/07/2023"
                    r'Statement\s+date:\s*(\d{1,2}/\d{1,2}/\d{4})',

                    # Pattern 3: "25 July 2023" (day month year)
                    r'(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',

                    # Pattern 4: Generic DD/MM/YYYY format near top of document
                    r'^.*?(\d{1,2}/\d{1,2}/\d{4})',
                ]

                for pattern in date_patterns:
                    match = re.search(pattern, text_content, re.IGNORECASE | re.MULTILINE)
                    if match:
                        statement_date = match.group(1).strip()

                        extracted_data['date'] = statement_date
                        field_confidences['date'] = 0.75  # Medium confidence for regex
                        print(f"[DEBUG] Found statement date via regex: {statement_date}")
                        break  # Stop after first match

            # Calculate overall confidence
            if field_confidences:
                avg_confidence = sum(field_confidences.values()) / len(field_confidences)
            else:
                avg_confidence = 0.0

            # Add field confidences to response
            extracted_data['field_confidences'] = field_confidences

            return extracted_data, avg_confidence

        except Exception as e:
            logger.error(f"Azure Document Intelligence processing error: {e}")
            raise

    def process_pdf_file(self, file_path: str, model_id: str = "prebuilt-document") -> Tuple[Dict[str, Any], float]:
        """
        Process a PDF file from disk.

        Args:
            file_path: Path to PDF file
            model_id: Azure model to use

        Returns:
            Tuple of (extracted_data, confidence_score)
        """
        with open(file_path, 'rb') as f:
            pdf_bytes = f.read()
        return self.process_pdf_bytes(pdf_bytes, model_id)

    def train_custom_model(self, training_data_url: str, model_id: str) -> str:
        """
        Train a custom model for specific document layouts.

        Args:
            training_data_url: Azure Storage container URL with labeled training data
            model_id: Custom model ID to create

        Returns:
            Model ID of the trained model
        """
        try:
            poller = self.client.begin_build_document_model(
                model_id=model_id,
                build_mode="template",
                blob_container_url=training_data_url
            )
            result = poller.result()
            logger.info(f"Custom model trained successfully: {result.model_id}")
            return result.model_id
        except Exception as e:
            logger.error(f"Failed to train custom model: {e}")
            raise


# Fallback to local OCR if Azure is not configured
class LocalOCRProcessor:
    """Fallback OCR processor using local tools (pdftotext/tesseract)."""

    def process_pdf_bytes(self, pdf_bytes: bytes) -> Tuple[Dict[str, Any], float]:
        """
        Process PDF using local OCR tools as fallback.

        This is a simplified version that uses pdftotext or tesseract.
        For full implementation, integrate with existing OCR code from scripts/.
        """
        import subprocess
        import tempfile
        import re

        extracted_data = {
            'rent': None,
            'management_fee': None,
            'repair': None,
            'deposit': None,
            'misc': None,
            'total': None,
            'date': None,
            'property_id': None,
            'field_confidences': {}
        }

        try:
            # Save PDF to temp file
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_file.write(pdf_bytes)
                tmp_path = tmp_file.name

            # Try pdftotext first
            try:
                text = subprocess.check_output(['pdftotext', tmp_path, '-'],
                                             universal_newlines=True,
                                             stderr=subprocess.DEVNULL)
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to tesseract
                try:
                    # Convert PDF to images first (requires pdf2image)
                    from pdf2image import convert_from_bytes
                    import pytesseract

                    images = convert_from_bytes(pdf_bytes)
                    text = ""
                    for image in images:
                        text += pytesseract.image_to_string(image)
                except ImportError:
                    raise ValueError("Neither pdftotext nor tesseract/pdf2image available for OCR")

            # Parse text with regex patterns
            patterns = {
                'rent': r'(?:rent|rental)\s*[:=]\s*\$?([\d,]+\.?\d*)',
                'management_fee': r'(?:management|admin)\s*fee\s*[:=]\s*\$?([\d,]+\.?\d*)',
                'repair': r'(?:repair|maintenance)\s*[:=]\s*\$?([\d,]+\.?\d*)',
                'total': r'(?:total|amount\s+due)\s*[:=]\s*\$?([\d,]+\.?\d*)',
                'date': r'(?:date|invoice\s+date)\s*[:=]\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})'
            }

            for field, pattern in patterns.items():
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    value = match.group(1).replace(',', '')
                    if field == 'date':
                        extracted_data[field] = value
                    else:
                        extracted_data[field] = float(value)
                    extracted_data['field_confidences'][field] = 0.7  # Fixed confidence for regex matches

            # Cleanup temp file
            os.unlink(tmp_path)

            # Calculate confidence
            confidence = len(extracted_data['field_confidences']) * 0.7 / len(patterns)

            return extracted_data, confidence

        except Exception as e:
            logger.error(f"Local OCR processing error: {e}")
            raise


def get_ocr_processor() -> Any:
    """
    Get the appropriate OCR processor based on configuration.

    Returns Azure processor if configured, otherwise falls back to local OCR.
    """
    try:
        # Try Azure first if credentials are available
        if os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT') and os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY'):
            return AzureDocumentProcessor()
    except Exception as e:
        logger.warning(f"Failed to initialize Azure processor: {e}, falling back to local OCR")

    # Fallback to local OCR
    return LocalOCRProcessor()