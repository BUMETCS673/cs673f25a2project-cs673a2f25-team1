#!/usr/bin/env python3
"""
Enhanced OCR processor for rental statements.
Processes PDFs from property-a directory and outputs structured CSV data.
"""

import argparse
import csv
import os
import re
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import pandas as pd
from pdf2image import convert_from_path
import pytesseract


# Property mapping
PROPERTY_ALIAS_BY_DIR = {
    "property-a": "Arranview",
    "property-b": "Bedford", 
    "property-c": "97B Dempster",
}

# Date pattern for filename parsing
DATE_FILENAME_RE = re.compile(r"(20\d{2})(\d{2})(\d{2})")

# Amount pattern for extracting monetary values
AMOUNT_RE = re.compile(r"(?<![0-9\-])([\-]?[0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{1,2})|[\-]?[0-9]+(?:\.[0-9]{1,2}))")


def parse_statement_date_from_filename(filename: str) -> Optional[str]:
    """Extract statement date from filename in YYYYMMDD format."""
    m = DATE_FILENAME_RE.search(filename)
    if not m:
        return None
    y, mo, d = m.group(1), m.group(2), m.group(3)
    try:
        dt = datetime(int(y), int(mo), int(d))
        # Return in M/D/YYYY format to match labels.csv
        return f"{dt.month}/{dt.day}/{dt.year}"
    except ValueError:
        return None


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
    """Find monetary amounts near specified keywords."""
    results: List[Tuple[float, float, str]] = []
    key_re = re.compile("|".join([re.escape(k) for k in keywords]), re.IGNORECASE)
    
    for idx, line in enumerate(lines):
        if key_re.search(line):
            # Look for amounts on the same line first
            candidates = AMOUNT_RE.findall(line)
            
            # If no amounts on same line, check neighboring lines
            if not candidates:
                look_range = []
                if idx + 1 < len(lines):
                    look_range.append(lines[idx + 1])
                if idx - 1 >= 0:
                    look_range.append(lines[idx - 1])
                
                for lr in look_range:
                    candidates = AMOUNT_RE.findall(lr)
                    if candidates:
                        break
            
            for c in candidates:
                amt = normalize_amount(c)
                if amt is None:
                    continue
                
                # Higher confidence for same-line matches
                confidence = 0.92 if key_re.search(line) else 0.85
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
    """Parse financial fields from extracted text."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    
    # Rent - look for largest amount (typically rent is significant)
    rent_candidates = find_amounts_near_keyword(lines, [
        "rent received", "rent from", "rent to", "rent", "rental income", "rental"
    ])
    rent_val = None
    rent_conf = 0.0
    if rent_candidates:
        rent_val, rent_conf, _ = sorted(rent_candidates, key=lambda x: x[0], reverse=True)[0]
    
    # Management fee - often a percentage of rent
    mgmt_candidates = find_amounts_near_keyword(lines, [
        "management fee", "management fees", "mgmt fee", "agent fee", "management"
    ])
    mgmt_val = None
    mgmt_conf = 0.0
    if mgmt_candidates:
        sorted_m = sorted(mgmt_candidates, key=lambda x: x[0])
        mid = len(sorted_m) // 2
        mgmt_val, mgmt_conf, _ = sorted_m[mid]
    
    # Repairs/maintenance
    repair_val, repair_conf, repair_notes = sum_deductions_by_keywords(lines, [
        "repair", "repairs", "maintenance", "invoice", "call out", "gas safety", 
        "legionella", "plumbing", "boiler", "certs", "certificate"
    ])
    
    # Deposit/holding
    deposit_val, deposit_conf, deposit_notes = sum_deductions_by_keywords(lines, [
        "deposit", "float held", "reserve", "retention", "safe deposit"
    ])
    
    # Miscellaneous
    misc_val, misc_conf, misc_notes = sum_deductions_by_keywords(lines, [
        "rent guarantee", "credit check", "standing charge", "epc", "eicr", "pat",
        "council tax", "energy", "missing payment"
    ])
    
    # Total/payment to landlord
    total_candidates = find_amounts_near_keyword(lines, [
        "net payment", "payment to landlord", "amount paid", "total to landlord", 
        "balance paid", "total", "net"
    ])
    total_val = None
    total_conf = 0.0
    if total_candidates:
        # Use the last occurrence (often the summary)
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
        "total": total_conf if total_val is not None else (0.88 if derived_total is not None else 0.0),
    }
    
    meta_notes = {
        "notes": "; ".join([*repair_notes, *deposit_notes, *misc_notes])[:200]
    }
    
    return field_values, confidences, meta_notes


def reconcile_and_validate(values: Dict[str, Optional[float]]) -> Tuple[Dict[str, Optional[float]], float, List[str]]:
    """Validate and reconcile financial values."""
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
    
    # Reconciliation check
    tolerance = 0.50
    if rent is not None and total is not None:
        expected = round(rent - sum(v for v in [mgmt, repair, deposit, misc] if v is not None), 2)
        if abs(expected - total) > tolerance:
            issues.append(f"total_mismatch expected={expected} got={total}")
    
    # Calculate overall confidence
    base_conf = 0.0
    present_fields = sum(1 for k in ["rent", "management_fee", "repair", "deposit", "misc", "total"] if values.get(k) is not None)
    base_conf += 0.15 * present_fields
    
    if rent is not None and total is not None:
        base_conf += 0.25
    if not issues:
        base_conf += 0.25
    
    base_conf = max(0.0, min(1.0, base_conf))
    
    return values, base_conf, issues


def process_pdf(pdf_path: str) -> Tuple[Dict[str, Optional[float]], float, str, Dict[str, str]]:
    """Process a single PDF and extract financial data."""
    text, method = extract_text(pdf_path)
    values, confs, notes = parse_fields(text)
    values, overall_conf, issues = reconcile_and_validate(values)
    
    # Weight field confidences
    avg_field_conf = sum(confs.values()) / max(1, len(confs))
    final_conf = 0.6 * overall_conf + 0.4 * avg_field_conf
    
    if issues:
        notes["notes"] = (notes.get("notes", "") + "; " + "; ".join(issues)).strip("; ").strip()
    
    return values, final_conf, method, notes


def process_property_directory(property_dir: str, output_csv: str) -> Tuple[int, int]:
    """Process all PDFs in a property directory and write to CSV."""
    property_name = os.path.basename(property_dir)
    alias = PROPERTY_ALIAS_BY_DIR.get(property_name, property_name)
    
    processed = 0
    skipped = 0
    
    # CSV headers matching labels.csv format
    headers = [
        "statement_id", "property_alias", "statement_date", "period_start", "period_end",
        "rent", "management_fee", "repair", "deposit", "misc", "note", "total", "pay_date"
    ]
    
    rows = []
    statement_id = 1
    
    for filename in sorted(os.listdir(property_dir)):
        if not filename.lower().endswith(".pdf"):
            continue
        
        pdf_path = os.path.join(property_dir, filename)
        statement_date = parse_statement_date_from_filename(filename)
        
        if not statement_date:
            print(f"Skipping {filename}: Could not parse date")
            skipped += 1
            continue
        
        print(f"Processing {filename}...")
        
        try:
            values, conf, method, notes = process_pdf(pdf_path)
            
            # Determine if needs review based on confidence
            needs_review = conf < 0.90
            
            row = {
                "statement_id": statement_id,
                "property_alias": alias,
                "statement_date": statement_date,
                "period_start": "",  # Not extracted from PDFs
                "period_end": "",     # Not extracted from PDFs
                "rent": values.get("rent", ""),
                "management_fee": values.get("management_fee", ""),
                "repair": values.get("repair", ""),
                "deposit": values.get("deposit", ""),
                "misc": values.get("misc", ""),
                "note": notes.get("notes", ""),
                "total": values.get("total", ""),
                "pay_date": statement_date,
            }
            
            rows.append(row)
            statement_id += 1
            processed += 1
            
            print(f"  Confidence: {conf:.2f}, Method: {method}")
            if needs_review:
                print(f"  ⚠️  Needs review (low confidence)")
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            skipped += 1
    
    # Write to CSV
    if rows:
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
        print(f"\nWritten {len(rows)} rows to {output_csv}")
    
    return processed, skipped


def main():
    """Main function to process rental statements."""
    parser = argparse.ArgumentParser(description="Process rental statement PDFs with OCR")
    parser.add_argument("--property-dir", default="sample-data/rental-statements/property-a", 
                       help="Directory containing PDF files")
    parser.add_argument("--output", default="property-a-processed.csv", 
                       help="Output CSV file")
    parser.add_argument("--test-single", help="Test with a single PDF file")
    
    args = parser.parse_args()
    
    if args.test_single:
        # Test mode with single file
        print(f"Testing OCR on: {args.test_single}")
        values, conf, method, notes = process_pdf(args.test_single)
        print(f"Confidence: {conf:.2f}")
        print(f"Method: {method}")
        print(f"Values: {values}")
        print(f"Notes: {notes}")
    else:
        # Process entire directory
        if not os.path.isdir(args.property_dir):
            print(f"Error: Directory {args.property_dir} does not exist")
            return
        
        print(f"Processing PDFs in: {args.property_dir}")
        print(f"Output file: {args.output}")
        
        processed, skipped = process_property_directory(args.property_dir, args.output)
        print(f"\nSummary:")
        print(f"  Processed: {processed}")
        print(f"  Skipped: {skipped}")


if __name__ == "__main__":
    main()
