"""
End-to-End tests for live Azure deployment.

WARNING: These tests:
- Hit LIVE Azure services (costs money via Azure Document Intelligence API)
- Write to REAL Azure SQL Database (or local SQLite in dev)
- Should run in CI/CD pipeline or manual QA only

These tests validate the complete production flow:
User → Azure App Service → Azure Document Intelligence → Database
"""
import pytest
import requests
import time
from pathlib import Path

# Live Azure endpoint
AZURE_BASE_URL = "https://ocr-backend-app.azurewebsites.net"

# Sample PDFs - path relative to this file
# test_e2e_azure.py is in: code/AssetManagementAnomalyDetection/tests/
# PDFs are in: code/sample-data/rental-statements/property-a/
SAMPLE_PDF_DIR = Path(__file__).parent.parent.parent / "sample-data/rental-statements/property-a"


class TestE2EPDFUpload:
    """E2E tests for PDF upload and OCR processing."""

    def test_e2e_single_pdf_upload(self):
        """Upload single PDF to live Azure and verify rent extraction."""
        pdf_path = SAMPLE_PDF_DIR / "20210304.pdf"

        assert pdf_path.exists(), f"Sample PDF not found: {pdf_path}"

        with open(pdf_path, 'rb') as f:
            response = requests.post(
                f"{AZURE_BASE_URL}/api/upload-pdf",
                files={'file': ('20210304.pdf', f, 'application/pdf')},
                timeout=30
            )

        # Verify response
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()

        assert data['success'] is True, f"Upload failed: {data.get('error', 'Unknown error')}"
        assert data['method'] == 'azure', "Should use Azure Document Intelligence"
        assert data['data']['rent'] == 400.0, f"Rent should be 400.0, got {data['data']['rent']}"
        assert data['data']['management_fee'] == 40.0, f"Mgmt fee should be 40.0, got {data['data']['management_fee']}"
        assert data['confidence'] > 0.7, f"Confidence too low: {data['confidence']}"

        print(f"✅ Single PDF upload successful: rent={data['data']['rent']}, confidence={data['confidence']}")

    def test_e2e_all_sample_pdfs(self):
        """Upload all 3 sample PDFs and verify rent extraction accuracy."""
        pdf_files = [
            "20210304.pdf",
            "20210402.pdf",
            "20210507.pdf"
        ]

        results = []

        for pdf_name in pdf_files:
            pdf_path = SAMPLE_PDF_DIR / pdf_name

            if not pdf_path.exists():
                pytest.skip(f"Sample PDF not found: {pdf_path}")

            with open(pdf_path, 'rb') as f:
                response = requests.post(
                    f"{AZURE_BASE_URL}/api/upload-pdf",
                    files={'file': (pdf_name, f, 'application/pdf')},
                    timeout=30
                )

            assert response.status_code == 200, f"{pdf_name} upload failed"
            data = response.json()

            # Critical regression test: ALL PDFs should extract rent as 400.0
            assert data['data']['rent'] == 400.0, \
                f"{pdf_name}: Rent should be 400.0, got {data['data']['rent']} (old bug: 40.0 or 20.0)"

            assert data['data']['management_fee'] == 40.0, \
                f"{pdf_name}: Management fee should be 40.0, got {data['data']['management_fee']}"

            results.append({
                'file': pdf_name,
                'rent': data['data']['rent'],
                'mgmt_fee': data['data']['management_fee'],
                'confidence': data['confidence']
            })

        print(f"✅ All PDFs processed correctly:")
        for r in results:
            print(f"   {r['file']}: rent={r['rent']}, mgmt_fee={r['mgmt_fee']}, conf={r['confidence']:.2f}")

    def test_e2e_batch_upload(self):
        """Upload multiple PDFs via batch endpoint."""
        pdf_files = [
            SAMPLE_PDF_DIR / "20210304.pdf",
            SAMPLE_PDF_DIR / "20210402.pdf",
            SAMPLE_PDF_DIR / "20210507.pdf"
        ]

        # Check files exist
        existing_files = [f for f in pdf_files if f.exists()]
        if len(existing_files) == 0:
            pytest.skip("No sample PDFs found")

        files = [
            ('files', (pdf.name, open(pdf, 'rb'), 'application/pdf'))
            for pdf in existing_files
        ]

        try:
            response = requests.post(
                f"{AZURE_BASE_URL}/api/upload-pdf-batch",
                files=files,
                timeout=60
            )
        finally:
            # Close files
            for _, (_, f, _) in files:
                f.close()

        assert response.status_code == 200, f"Batch upload failed: {response.text}"
        data = response.json()

        assert data['success'] is True, f"Batch upload failed: {data.get('message', 'Unknown')}"
        assert data['processed'] == len(existing_files), f"Expected {len(existing_files)} processed, got {data['processed']}"
        assert data['errors'] == 0, f"Expected no errors, got {data['errors']}"
        assert 'batch_id' in data, "Batch ID not returned"

        print(f"✅ Batch upload successful: {data['processed']} files, batch_id={data['batch_id']}")

    def test_e2e_invalid_file_upload(self):
        """Upload non-PDF file should fail gracefully."""
        response = requests.post(
            f"{AZURE_BASE_URL}/api/upload-pdf",
            files={'file': ('test.txt', b'not a pdf', 'text/plain')},
            timeout=10
        )

        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert data['success'] is False
        assert 'PDF' in data.get('message', '') or 'pdf' in data.get('error', '').lower()

        print(f"✅ Invalid file rejected correctly: {data.get('message', data.get('error'))}")

    def test_e2e_missing_file(self):
        """POST without file should fail gracefully."""
        response = requests.post(
            f"{AZURE_BASE_URL}/api/upload-pdf",
            timeout=10
        )

        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert data['success'] is False
        assert 'file' in data.get('error', '').lower() or 'file' in data.get('message', '').lower()

        print(f"✅ Missing file rejected correctly: {data.get('message', data.get('error'))}")


class TestE2EDatabase:
    """E2E tests for database persistence."""

    def test_e2e_database_round_trip(self):
        """Upload PDF via batch endpoint and verify it appears in database."""
        pdf_path = SAMPLE_PDF_DIR / "20210304.pdf"

        if not pdf_path.exists():
            pytest.skip(f"Sample PDF not found: {pdf_path}")

        # Upload via batch endpoint (stores in DB)
        with open(pdf_path, 'rb') as f:
            upload_response = requests.post(
                f"{AZURE_BASE_URL}/api/upload-pdf-batch",
                files={'files': ('20210304.pdf', f, 'application/pdf')},
                timeout=30
            )

        assert upload_response.status_code == 200, f"Upload failed: {upload_response.text}"
        batch_id = upload_response.json()['batch_id']

        # Wait for processing
        time.sleep(2)

        # Query database
        query_response = requests.get(
            f"{AZURE_BASE_URL}/api/parsed-statements",
            timeout=10
        )

        assert query_response.status_code == 200, f"Query failed: {query_response.text}"
        data = query_response.json()

        assert data['success'] is True, "Query returned success=False"
        assert len(data['data']) > 0, "No data returned from database"

        # Verify uploaded data
        statement = data['data'][0]
        assert statement['filename'] == '20210304.pdf', f"Wrong filename: {statement['filename']}"
        assert statement['rent'] == 400.0, f"Rent should be 400.0, got {statement['rent']}"
        assert statement['management_fee'] == 40.0, f"Mgmt fee should be 40.0, got {statement['management_fee']}"

        print(f"✅ Database round-trip successful: batch_id={batch_id}, {len(data['data'])} records")

    def test_e2e_summary_statistics(self):
        """Upload batch and verify summary calculations."""
        pdf_files = [
            SAMPLE_PDF_DIR / "20210304.pdf",
            SAMPLE_PDF_DIR / "20210402.pdf",
            SAMPLE_PDF_DIR / "20210507.pdf"
        ]

        existing_files = [f for f in pdf_files if f.exists()]
        if len(existing_files) == 0:
            pytest.skip("No sample PDFs found")

        # Upload batch
        files = [
            ('files', (pdf.name, open(pdf, 'rb'), 'application/pdf'))
            for pdf in existing_files
        ]

        try:
            requests.post(
                f"{AZURE_BASE_URL}/api/upload-pdf-batch",
                files=files,
                timeout=60
            )
        finally:
            for _, (_, f, _) in files:
                f.close()

        time.sleep(2)

        # Get summary
        response = requests.get(
            f"{AZURE_BASE_URL}/api/parsed-statements/summary",
            timeout=10
        )

        assert response.status_code == 200, f"Summary query failed: {response.text}"
        data = response.json()

        assert data['success'] is True, "Summary returned success=False"
        summary = data['summary']

        assert summary['total_records'] == len(existing_files), \
            f"Expected {len(existing_files)} records, got {summary['total_records']}"

        expected_rent = len(existing_files) * 400.0
        assert summary['total_rent'] == expected_rent, \
            f"Expected total rent {expected_rent}, got {summary['total_rent']}"

        expected_fees = len(existing_files) * 40.0
        assert summary['total_management_fees'] == expected_fees, \
            f"Expected total fees {expected_fees}, got {summary['total_management_fees']}"

        assert summary['average_confidence'] > 0.7, \
            f"Average confidence too low: {summary['average_confidence']}"

        print(f"✅ Summary correct: {summary['total_records']} records, "
              f"rent={summary['total_rent']}, fees={summary['total_management_fees']}")

    def test_e2e_pagination(self):
        """Test pagination of parsed statements."""
        response = requests.get(
            f"{AZURE_BASE_URL}/api/parsed-statements?page=1&per_page=10",
            timeout=10
        )

        assert response.status_code == 200, f"Pagination query failed: {response.text}"
        data = response.json()

        assert data['success'] is True
        assert 'total' in data
        assert 'page' in data
        assert 'per_page' in data
        assert 'total_pages' in data

        print(f"✅ Pagination works: page {data['page']}/{data['total_pages']}, total={data['total']}")


class TestE2EPerformance:
    """E2E performance and reliability tests."""

    def test_e2e_response_time(self):
        """Verify API responds within acceptable time."""
        pdf_path = SAMPLE_PDF_DIR / "20210304.pdf"

        if not pdf_path.exists():
            pytest.skip(f"Sample PDF not found: {pdf_path}")

        start = time.time()

        with open(pdf_path, 'rb') as f:
            response = requests.post(
                f"{AZURE_BASE_URL}/api/upload-pdf",
                files={'file': ('20210304.pdf', f, 'application/pdf')},
                timeout=30
            )

        elapsed = time.time() - start

        assert response.status_code == 200, f"Request failed: {response.text}"
        assert elapsed < 20, f"Response took {elapsed:.2f}s (should be < 20s)"

        print(f"✅ Response time acceptable: {elapsed:.2f}s")

    def test_e2e_api_health_check(self):
        """Verify API is alive and responding."""
        response = requests.get(f"{AZURE_BASE_URL}/", timeout=5)

        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        data = response.json()
        assert 'message' in data or 'Message' in data

        print(f"✅ API health check passed: {data}")


# Pytest configuration
@pytest.fixture(scope="session", autouse=True)
def verify_azure_available():
    """Verify Azure endpoint is reachable before running tests."""
    print(f"\n🔍 Checking Azure endpoint availability: {AZURE_BASE_URL}")
    try:
        response = requests.get(f"{AZURE_BASE_URL}/", timeout=10)
        if response.status_code != 200:
            pytest.exit(f"❌ Azure endpoint returned {response.status_code}", returncode=1)
        print(f"✅ Azure endpoint is available")
    except requests.RequestException as e:
        pytest.exit(f"❌ Cannot reach Azure endpoint: {e}", returncode=1)


@pytest.fixture(scope="session", autouse=True)
def warn_about_costs():
    """Warn about Azure API costs."""
    print("\n" + "="*70)
    print("⚠️  WARNING: Running E2E tests against LIVE Azure deployment")
    print("="*70)
    print("These tests will:")
    print("  - Call Azure Document Intelligence API (costs ~$1-2 per 1000 pages)")
    print("  - Write to the database (batch uploads CLEAR existing data)")
    print("  - Take 1-2 minutes to complete")
    print("="*70 + "\n")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
