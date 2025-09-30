#!/bin/bash

echo "🧪 OCR Backend Test Suite"
echo "========================="

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test function
run_test() {
    echo -n "Testing $1... "
    if eval "$2" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        return 0
    else
        echo -e "${RED}✗${NC}"
        return 1
    fi
}

# Local tests
echo -e "\n📍 Local Server Tests (port 5001):"
run_test "Health check" "curl -s http://127.0.0.1:5001/ | grep -q 'Asset Management'"
run_test "Error handling" "curl -s -X POST http://127.0.0.1:5001/api/upload-pdf | grep -q 'No file provided'"

# Docker tests
echo -e "\n🐳 Docker Tests:"
run_test "Image exists" "docker images | grep -q ocr-backend"

# Azure tests
echo -e "\n☁️ Azure Tests:"
run_test "Azure health" "curl -s https://ocr-backend-app.azurewebsites.net/ | grep -q 'Asset Management'"
run_test "Azure error handling" "curl -s -X POST https://ocr-backend-app.azurewebsites.net/api/upload-pdf | grep -q 'No file provided'"

# PDF processing test
echo -e "\n📄 PDF Processing Test:"
if [ -f "../sample-data/rental-statements/property-a/20230725.pdf" ]; then
    response=$(curl -s -X POST http://127.0.0.1:5001/api/upload-pdf \
        -F "file=@../sample-data/rental-statements/property-a/20230725.pdf")

    if echo "$response" | grep -q '"success": true'; then
        echo -e "Local PDF processing: ${GREEN}✓${NC}"
        echo "$response" | python3 -m json.tool | head -20
    else
        echo -e "Local PDF processing: ${RED}✗${NC}"
    fi
else
    echo "Sample PDF not found - skipping PDF test"
fi

echo -e "\n✅ Test suite complete!"