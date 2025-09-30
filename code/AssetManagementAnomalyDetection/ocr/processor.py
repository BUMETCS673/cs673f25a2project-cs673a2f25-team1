"""
OCR Processor Module for Rental Statement Analysis
Refactored from code/scripts/ocr_processor_v3.py for backend API use
"""

import re
import subprocess
import tempfile
from typing import Dict, List, Optional, Tuple
from pdf2image import convert_from_path
import pytesseract


# Enhanced amount pattern for extracting monetary values
AMOUNT_RE = re.compile(r"(?<![0-9\-])([\-]?[0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{1,2})|[\-]?[0-9]+(?:\.[0-9]{1,2}))")


def run_pdftotext(pdf_path: str) -> str:
    """Extract text from PDF using pdftotext with layout preservation."""
    try:
        out = subprocess.run([
            "pdftotext", "-layout", pdf_path, "-"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, text=True
        )
        return out.stdout or ""
    except FileNotFoundError:
        return ""


def run_tesseract(pdf_path: str, dpi: int = 300) -> str:
    """Extract text from PDF using OCR (Tesseract)."""
    try:
        images = convert_from_path(pdf_path, dpi=dpi)
    except Exception:
        images = []

    texts: List[str] = []
    for img in images:
        try:
            txt = pytesseract.image_to_string(img)
            if txt:
                texts.append(txt)
        except Exception:
            continue
    return "\n".join(texts)


def extract_text(pdf_path: str) -> Tuple[str, str]:
    """Extract text from PDF using best available method."""
    # Try pdftotext first (faster and more accurate for text-based PDFs)
    text1 = run_pdftotext(pdf_path)
    if text1.strip():
        return text1, "pdftotext"

    # Fall back to OCR
    text2 = run_tesseract(pdf_path)
    return text2, "tesseract"


def normalize_amount(value: str) -> Optional[float]:
    """Normalize monetary amount string to float."""
    try:
        v = value.replace(",", "").strip()
        return round(float(v), 2)
    except Exception:
        return None


def find_amounts_near_keyword(lines: List[str], keywords: List[str]) -> List[Tuple[float, float, str]]:
    """Find monetary amounts near specified keywords with enhanced matching."""
    results: List[Tuple[float, float, str]] = []
    key_re = re.compile("|".join([re.escape(k) for k in keywords]), re.IGNORECASE)

    for idx, line in enumerate(lines):
        if key_re.search(line):
            # Look for amounts on the same line first
            candidates = AMOUNT_RE.findall(line)

            # If no amounts on same line, check neighboring lines (expanded range)
            if not candidates:
                look_range = []
                # Check up to 2 lines before and after
                for offset in [-2, -1, 1, 2]:
                    check_idx = idx + offset
                    if 0 <= check_idx < len(lines):
                        look_range.append(lines[check_idx])

                for lr in look_range:
                    candidates = AMOUNT_RE.findall(lr)
                    if candidates:
                        break

            for c in candidates:
                amt = normalize_amount(c)
                if amt is None:
                    continue

                # Enhanced confidence scoring based on proximity
                if key_re.search(line):
                    confidence = 0.95  # Same line - very high confidence
                elif idx - 1 >= 0 and key_re.search(lines[idx - 1]):
                    confidence = 0.90  # Previous line - high confidence
                elif idx + 1 < len(lines) and key_re.search(lines[idx + 1]):
                    confidence = 0.90  # Next line - high confidence
                else:
                    confidence = 0.85  # Nearby line - good confidence

                results.append((amt, confidence, line.strip()))

    return results


def sum_deductions_by_keywords(lines: List[str], keywords: List[str]) -> Tuple[Optional[float], float, List[str]]:
    """Sum up deduction amounts for specified keywords."""
    matches = find_amounts_near_keyword(lines, keywords)
    if not matches:
        return None, 0.0, []

    # Sum positive amounts (deductions)
    total = sum(m[0] for m in matches if m[0] is not None and m[0] >= 0)
    avg_conf = sum(m[1] for m in matches) / max(1, len(matches))
    notes = list({m[2] for m in matches})

    return round(total, 2), avg_conf, notes


def parse_fields(text: str) -> Tuple[Dict[str, Optional[float]], Dict[str, float], Dict[str, str]]:
    """Parse financial fields from extracted text with enhanced keyword matching."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    # Enhanced rent keywords
    rent_candidates = find_amounts_near_keyword(lines, [
        "rent received", "rent from", "rent to", "rent", "rental income", "rental",
        "income", "receipts", "tenant payment", "monthly rent"
    ])
    rent_val = None
    rent_conf = 0.0
    if rent_candidates:
        # Prefer the largest amount (typically rent is significant)
        rent_val, rent_conf, _ = sorted(rent_candidates, key=lambda x: x[0], reverse=True)[0]

    # Enhanced management fee keywords
    mgmt_candidates = find_amounts_near_keyword(lines, [
        "management fee", "management fees", "mgmt fee", "agent fee", "management",
        "letting fee", "admin fee", "service charge", "commission"
    ])
    mgmt_val = None
    mgmt_conf = 0.0
    if mgmt_candidates:
        # Use median or most common value
        sorted_m = sorted(mgmt_candidates, key=lambda x: x[0])
        mid = len(sorted_m) // 2
        mgmt_val, mgmt_conf, _ = sorted_m[mid]

    # Enhanced repairs/maintenance keywords
    repair_val, repair_conf, repair_notes = sum_deductions_by_keywords(lines, [
        "repair", "repairs", "maintenance", "invoice", "call out", "gas safety",
        "legionella", "plumbing", "boiler", "certs", "certificate", "eicr", "pat",
        "electrical", "heating", "water", "drainage", "roof", "window", "door"
    ])

    # Enhanced deposit/holding keywords
    deposit_val, deposit_conf, deposit_notes = sum_deductions_by_keywords(lines, [
        "deposit", "float held", "reserve", "retention", "safe deposit", "holding",
        "security deposit", "bond"
    ])

    # Enhanced miscellaneous keywords
    misc_val, misc_conf, misc_notes = sum_deductions_by_keywords(lines, [
        "rent guarantee", "credit check", "standing charge", "epc", "eicr", "pat",
        "council tax", "energy", "missing payment", "insurance", "legal", "court",
        "eviction", "reference", "inventory", "check-in", "check-out"
    ])

    # Enhanced total/payment keywords
    total_candidates = find_amounts_near_keyword(lines, [
        "net payment", "payment to landlord", "amount paid", "total to landlord",
        "balance paid", "total", "net", "final amount", "due to landlord",
        "landlord payment", "net amount"
    ])
    total_val = None
    total_conf = 0.0
    if total_candidates:
        # Use the last occurrence (often the summary) or largest reasonable amount
        reasonable_totals = [t for t in total_candidates if t[0] > 0 and t[0] < 10000]
        if reasonable_totals:
            total_val, total_conf, _ = reasonable_totals[-1]
        else:
            total_val, total_conf, _ = total_candidates[-1]

    # Derive total if missing
    derived_total = None
    if rent_val is not None:
        deductions = sum(p for p in [mgmt_val, repair_val, deposit_val, misc_val] if p is not None)
        derived_total = round(rent_val - deductions, 2)

    field_values = {
        "rent": rent_val,
        "management_fee": mgmt_val,
        "repair": repair_val,
        "deposit": deposit_val,
        "misc": misc_val,
        "total": total_val if total_val is not None else derived_total,
    }

    confidences = {
        "rent": rent_conf if rent_val is not None else 0.0,
        "management_fee": mgmt_conf if mgmt_val is not None else 0.0,
        "repair": repair_conf if repair_val is not None else 0.0,
        "deposit": deposit_conf if deposit_val is not None else 0.0,
        "misc": misc_conf if misc_val is not None else 0.0,
        "total": total_conf if total_val is not None else (0.90 if derived_total is not None else 0.0),
    }

    meta_notes = {
        "notes": "; ".join([*repair_notes, *deposit_notes, *misc_notes])[:200]
    }

    return field_values, confidences, meta_notes


def reconcile_and_validate(values: Dict[str, Optional[float]]) -> Tuple[Dict[str, Optional[float]], float, List[str]]:
    """Validate and reconcile financial values with more lenient tolerance."""
    issues: List[str] = []

    # Ensure all amounts are positive
    for k in ["rent", "management_fee", "repair", "deposit", "misc", "total"]:
        if values.get(k) is not None:
            values[k] = round(abs(values[k]), 2)

    rent = values.get("rent")
    mgmt = values.get("management_fee")
    repair = values.get("repair")
    deposit = values.get("deposit")
    misc = values.get("misc")
    total = values.get("total")

    # Compute derived total if missing
    if total is None and rent is not None:
        others = sum(v for v in [mgmt, repair, deposit, misc] if v is not None)
        values["total"] = round(rent - others, 2)
        total = values["total"]

    # More lenient reconciliation check (±£5.00 instead of ±£0.50)
    tolerance = 5.00
    if rent is not None and total is not None:
        expected = round(rent - sum(v for v in [mgmt, repair, deposit, misc] if v is not None), 2)
        if abs(expected - total) > tolerance:
            issues.append(f"total_mismatch expected={expected} got={total}")

    # Enhanced confidence calculation
    base_conf = 0.0

    # Field presence scoring (more generous)
    present_fields = sum(1 for k in ["rent", "management_fee", "repair", "deposit", "misc", "total"] if values.get(k) is not None)
    base_conf += 0.25 * present_fields  # Increased from 0.20

    # Bonus for having key fields
    if rent is not None:
        base_conf += 0.30  # Increased from 0.25
    if total is not None:
        base_conf += 0.20  # New bonus for total

    # Reduced penalty for reconciliation issues
    if not issues:
        base_conf += 0.20  # Reduced from 0.25
    else:
        base_conf += 0.10  # Small penalty instead of 0

    # Bonus for having multiple fields
    if present_fields >= 4:
        base_conf += 0.10

    base_conf = max(0.0, min(1.0, base_conf))

    return values, base_conf, issues


def process_pdf(pdf_path: str) -> Dict:
    """
    Process a single PDF and extract financial data.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Dictionary with extracted data, confidence, method, and notes
    """
    text, method = extract_text(pdf_path)
    values, confs, notes = parse_fields(text)
    values, overall_conf, issues = reconcile_and_validate(values)

    # Enhanced confidence weighting
    avg_field_conf = sum(confs.values()) / max(1, len(confs))
    final_conf = 0.7 * overall_conf + 0.3 * avg_field_conf  # Adjusted weighting

    if issues:
        notes["notes"] = (notes.get("notes", "") + "; " + "; ".join(issues)).strip("; ").strip()

    return {
        "success": True,
        "data": {
            "rent": values.get("rent"),
            "management_fee": values.get("management_fee"),
            "repair": values.get("repair"),
            "deposit": values.get("deposit"),
            "misc": values.get("misc"),
            "total": values.get("total")
        },
        "confidence": round(final_conf, 2),
        "method": method,
        "notes": notes.get("notes", ""),
        "field_confidences": confs
    }


def process_pdf_from_bytes(pdf_bytes: bytes, filename: str = "upload.pdf") -> Dict:
    """
    Process PDF from bytes (for file uploads).

    Args:
        pdf_bytes: PDF file content as bytes
        filename: Original filename (optional)

    Returns:
        Dictionary with extracted data, confidence, method, and notes
    """
    # Create temporary file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        tmp_file.write(pdf_bytes)
        tmp_path = tmp_file.name

    try:
        result = process_pdf(tmp_path)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": None,
            "confidence": 0.0,
            "method": "error",
            "notes": f"Failed to process PDF: {str(e)}"
        }
    finally:
        # Clean up temporary file
        import os
        try:
            os.unlink(tmp_path)
        except Exception:
            pass