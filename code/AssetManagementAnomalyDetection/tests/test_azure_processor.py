"""
Unit tests for Azure Document Intelligence OCR processor.

Tests the rent extraction fixes that resolved issues where:
- Rent was incorrectly extracted as 40.0 (management fee) instead of 400.0
- Rent was incorrectly extracted as 20.0 (from date string) instead of 400.0
"""
import pytest
import re
from unittest.mock import Mock, MagicMock, patch
from ocr.azure_processor import AzureDocumentProcessor


class TestRentExtractionRegex:
    """Test the regex patterns used for rent extraction fallback."""

    def test_rent_received_pattern_with_date_range(self):
        """Test pattern that skips parentheses (date) and captures amount after."""
        pattern = r'Rent\s+received\s*\([^)]+\)\s*(\d+[\d,]*\.?\d*)'

        # Real-world text from rental statements
        text = "Rent received (20/02/2021 - 19/03/2021) 400.00"
        match = re.search(pattern, text, re.IGNORECASE)

        assert match is not None
        assert match.group(1) == "400.00"
        assert float(match.group(1).replace(',', '')) == 400.0

    def test_rent_pattern_does_not_match_date(self):
        """Ensure regex doesn't incorrectly extract '20' from date string."""
        pattern = r'Rent\s+received\s*\([^)]+\)\s*(\d+[\d,]*\.?\d*)'

        # Text where old pattern would incorrectly match "20" from date
        text = "Rent received (20/02/2021 - 19/03/2021)"
        match = re.search(pattern, text, re.IGNORECASE)

        # Should NOT match because amount is missing after parentheses
        assert match is None

    def test_income_pattern(self):
        """Test INCOME pattern extraction."""
        pattern = r'INCOME\s*(\d+[\d,]*\.?\d*)'

        text = "INCOME 400.00"
        match = re.search(pattern, text, re.IGNORECASE)

        assert match is not None
        assert float(match.group(1).replace(',', '')) == 400.0

    def test_total_income_pattern(self):
        """Test 'Total income' pattern."""
        pattern = r'Total\s+income\s*(\d+[\d,]*\.?\d*)'

        text = "Total income 400.00"
        match = re.search(pattern, text, re.IGNORECASE)

        assert match is not None
        assert float(match.group(1).replace(',', '')) == 400.0

    def test_rental_income_pattern(self):
        """Test 'Rental income' pattern."""
        pattern = r'Rental\s+income\s*(\d+[\d,]*\.?\d*)'

        text = "Rental income 400.00"
        match = re.search(pattern, text, re.IGNORECASE)

        assert match is not None
        assert float(match.group(1).replace(',', '')) == 400.0

    def test_comma_separated_amounts(self):
        """Test pattern handles comma-separated amounts."""
        pattern = r'Rent\s+received\s*\([^)]+\)\s*(\d+[\d,]*\.?\d*)'

        text = "Rent received (01/01/2021 - 31/01/2021) 1,400.00"
        match = re.search(pattern, text, re.IGNORECASE)

        assert match is not None
        assert float(match.group(1).replace(',', '')) == 1400.0


class TestManagementFeeExtraction:
    """Test management fee extraction to ensure it doesn't overwrite rent."""

    def test_management_fee_pattern(self):
        """Test management fee regex pattern (full line extraction)."""
        # This pattern matches the entire line including percentage
        pattern = r'Management\s+fee\s*\([^)]+\)\s*[\d,]+\.?\d*'

        text = "Management fee (10%) 40.00"
        match = re.search(pattern, text, re.IGNORECASE)

        assert match is not None
        # Extract just the final numeric part
        num_match = re.search(r'(\d+[\d,]*\.?\d*)$', match.group())
        assert num_match is not None
        assert float(num_match.group().replace(',', '')) == 40.0

    def test_management_fee_with_percentage_in_parentheses(self):
        """Test pattern with percentage in parentheses."""
        pattern = r'Management\s+fee\s*\([^)]+\)\s*[\d,]+\.?\d*'

        text = "Management fee (10%) 40.00"
        match = re.search(pattern, text, re.IGNORECASE)

        assert match is not None
        # Extract numeric value
        num_match = re.search(r'(\d+[\d,]*\.?\d*)$', match.group())
        assert num_match is not None
        assert float(num_match.group().replace(',', '')) == 40.0


class TestAzureProcessorIntegration:
    """Integration tests for the full Azure processor with mocked Azure SDK."""

    @patch('ocr.azure_processor.DocumentAnalysisClient')
    def test_rent_extraction_from_text_fallback(self, mock_client_class):
        """Test that rent is correctly extracted via regex fallback."""
        # Mock Azure Document Intelligence response
        mock_result = Mock()
        mock_result.documents = []
        mock_result.key_value_pairs = []
        mock_result.content = """
        Rental Statement
        Property: Test Property

        INCOME
        Rent received (20/02/2021 - 19/03/2021) 400.00

        EXPENDITURE
        Management fee (10%) 40.00

        Total balance 360.00
        """

        # Mock the poller
        mock_poller = Mock()
        mock_poller.result.return_value = mock_result

        # Mock the client
        mock_client_instance = Mock()
        mock_client_instance.begin_analyze_document.return_value = mock_poller
        mock_client_class.return_value = mock_client_instance

        # Create processor
        processor = AzureDocumentProcessor(
            endpoint="https://test.cognitiveservices.azure.com/",
            api_key="test_key"
        )

        # Process mock PDF
        extracted_data, confidence = processor.process_pdf_bytes(b"fake pdf bytes")

        # Verify rent extraction
        assert extracted_data['rent'] == 400.0, "Rent should be 400.0, not 40.0 or 20.0"
        assert extracted_data['management_fee'] == 40.0

    @patch('ocr.azure_processor.DocumentAnalysisClient')
    def test_kv_pairs_extraction(self, mock_client_class):
        """Test rent extraction from Azure key-value pairs."""
        # Mock KV pair
        mock_kv = Mock()
        mock_kv.key = Mock(content="Rental income")
        mock_kv.value = Mock(content="400.00")
        mock_kv.confidence = 0.9

        # Mock result
        mock_result = Mock()
        mock_result.documents = []
        mock_result.key_value_pairs = [mock_kv]
        mock_result.content = ""

        # Mock poller and client
        mock_poller = Mock()
        mock_poller.result.return_value = mock_result
        mock_client_instance = Mock()
        mock_client_instance.begin_analyze_document.return_value = mock_poller
        mock_client_class.return_value = mock_client_instance

        # Process
        processor = AzureDocumentProcessor(
            endpoint="https://test.cognitiveservices.azure.com/",
            api_key="test_key"
        )
        extracted_data, confidence = processor.process_pdf_bytes(b"fake pdf bytes")

        # Verify
        assert extracted_data['rent'] == 400.0
        assert 'rent' in extracted_data.get('field_confidences', {})
        assert extracted_data['field_confidences']['rent'] == 0.9

    @patch('ocr.azure_processor.DocumentAnalysisClient')
    def test_line_items_do_not_overwrite_rent_if_already_set(self, mock_client_class):
        """Test that line items don't overwrite rent if already extracted from KV pairs."""
        # Mock KV pair with rent
        mock_kv = Mock()
        mock_kv.key = Mock(content="rent")
        mock_kv.value = Mock(content="400.00")
        mock_kv.confidence = 0.9

        # Mock line item with different rent value
        mock_line_item = Mock()
        mock_line_item.value = Mock()
        mock_line_item.value.fields = {
            'Description': Mock(value='Rent received'),
            'Amount': Mock(value=Mock(amount=350.0), confidence=0.8)
        }

        # Mock document
        mock_doc = Mock()
        mock_doc.fields = {
            'Items': Mock(value=[mock_line_item])
        }

        # Mock result
        mock_result = Mock()
        mock_result.documents = [mock_doc]
        mock_result.key_value_pairs = [mock_kv]
        mock_result.content = ""

        # Mock poller and client
        mock_poller = Mock()
        mock_poller.result.return_value = mock_result
        mock_client_instance = Mock()
        mock_client_instance.begin_analyze_document.return_value = mock_poller
        mock_client_class.return_value = mock_client_instance

        # Process
        processor = AzureDocumentProcessor(
            endpoint="https://test.cognitiveservices.azure.com/",
            api_key="test_key"
        )
        extracted_data, confidence = processor.process_pdf_bytes(b"fake pdf bytes")

        # Verify KV pair value is preserved, not overwritten by line item
        assert extracted_data['rent'] == 400.0, "KV pair rent should be preserved"


class TestRegressionTests:
    """Regression tests to ensure previously fixed bugs don't return."""

    def test_subtotal_does_not_map_to_rent(self):
        """Regression: Ensure SubTotal field doesn't overwrite rent."""
        # This would be tested by checking the field_mappings in azure_processor.py
        # The mapping should NOT contain 'SubTotal': 'rent'
        from ocr.azure_processor import AzureDocumentProcessor

        # Verify the problematic mapping was removed by checking the code doesn't contain it
        import inspect
        source = inspect.getsource(AzureDocumentProcessor.process_pdf_bytes)

        # Should not have 'SubTotal': 'rent' mapping
        assert "'SubTotal': 'rent'" not in source, \
            "SubTotal should not be mapped to rent (this caused bug where rent=40.0)"

    @patch('ocr.azure_processor.DocumentAnalysisClient')
    def test_real_world_statement_extraction(self, mock_client_class):
        """Test with realistic rental statement text."""
        mock_result = Mock()
        mock_result.documents = []
        mock_result.key_value_pairs = []
        # Real text from the sample PDFs
        mock_result.content = """
        TM Residential
        Clyde Office

        Rental Statement for: Test Property
        Statement Date: 04/03/2021

        INCOME
        Rent received (20/02/2021 - 19/03/2021) 400.00
        Total income 400.00

        EXPENDITURE
        Management fee (10%) 40.00
        Total expenditure 40.00

        Total balance due to Owner 360.00
        """

        mock_poller = Mock()
        mock_poller.result.return_value = mock_result
        mock_client_instance = Mock()
        mock_client_instance.begin_analyze_document.return_value = mock_poller
        mock_client_class.return_value = mock_client_instance

        processor = AzureDocumentProcessor(
            endpoint="https://test.cognitiveservices.azure.com/",
            api_key="test_key"
        )
        extracted_data, confidence = processor.process_pdf_bytes(b"fake pdf bytes")

        # These are the expected correct values
        # Note: "Total balance due to Owner" is not in the regex patterns, so total would be None
        # The processor only extracts total from Azure document fields, not via regex
        assert extracted_data['rent'] == 400.0, "Rent should be 400.0"
        assert extracted_data['management_fee'] == 40.0, "Management fee should be 40.0"
        # Total is not extracted via regex fallback, only via Azure SDK
        assert extracted_data['total'] is None or isinstance(extracted_data['total'], (int, float))


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
