# Test Suite for Azure OCR Processor

This directory contains unit tests for the Azure Document Intelligence OCR processor.

## Running Tests

```bash
# From the AssetManagementAnomalyDetection directory:
source .venv/bin/activate
python -m pytest tests/test_azure_processor.py -v
```

## Test Coverage

### `test_azure_processor.py` (13 tests)

Tests for the rent extraction fixes that resolved:
- **Bug 1**: Rent extracted as 40.0 (management fee) instead of 400.0
- **Bug 2**: Rent extracted as 20.0 (from date string) instead of 400.0

#### Test Classes

**1. TestRentExtractionRegex** (6 tests)
- `test_rent_received_pattern_with_date_range`: Validates regex skips parentheses and captures amount
- `test_rent_pattern_does_not_match_date`: Ensures "20" from date string is not matched
- `test_income_pattern`: Tests "INCOME" pattern extraction
- `test_total_income_pattern`: Tests "Total income" pattern
- `test_rental_income_pattern`: Tests "Rental income" pattern
- `test_comma_separated_amounts`: Verifies comma handling (e.g., 1,400.00)

**2. TestManagementFeeExtraction** (2 tests)
- `test_management_fee_pattern`: Tests management fee regex pattern
- `test_management_fee_with_percentage_in_parentheses`: Validates percentage handling

**3. TestAzureProcessorIntegration** (3 tests)
- `test_rent_extraction_from_text_fallback`: Mocks Azure SDK, tests regex fallback
- `test_kv_pairs_extraction`: Tests extraction from Azure key-value pairs
- `test_line_items_do_not_overwrite_rent_if_already_set`: Ensures KV pairs take precedence

**4. TestRegressionTests** (2 tests)
- `test_subtotal_does_not_map_to_rent`: Ensures SubTotal mapping was removed (caused bug)
- `test_real_world_statement_extraction`: End-to-end test with realistic statement text

## Key Regex Patterns Tested

```python
# Primary rent extraction pattern (fixed in commit ec9524b70)
r'Rent\s+received\s*\([^)]+\)\s*(\d+[\d,]*\.?\d*)'

# Fallback patterns
r'INCOME\s*(\d+[\d,]*\.?\d*)'
r'Total\s+income\s*(\d+[\d,]*\.?\d*)'
r'Rental\s+income\s*(\d+[\d,]*\.?\d*)'
```

## Test Philosophy

- **Unit tests**: Test regex patterns in isolation
- **Integration tests**: Mock Azure SDK responses to test extraction logic
- **Regression tests**: Ensure previously fixed bugs don't return
- **Real-world validation**: Test with actual rental statement text patterns

## CI/CD Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest tests/ -v
```

## Adding New Tests

When adding OCR extraction logic:
1. Add unit tests for new regex patterns
2. Add integration tests with mocked Azure responses
3. Add regression tests for any bugs found
4. Update this README with test coverage details
