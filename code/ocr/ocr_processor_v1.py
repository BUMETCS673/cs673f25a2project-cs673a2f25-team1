#!/usr/bin/env python3
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


PROPERTY_ALIAS_BY_DIR = {
    "property-a": "Arranview",
    "property-b": "Bedford",
    "property-c": "97B Dempster",
}


DATE_FILENAME_RE = re.compile(r"(20\d{2})(\d{2})(\d{2})")


AMOUNT_RE = re.compile(r"(?<![0-9\-])([\-]?[0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{1,2})|[\-]?[0-9]+(?:\.[0-9]{1,2}))")


def parse_statement_date_from_filename(filename: str) -> Optional[str]:
    m = DATE_FILENAME_RE.search(filename)
    if not m:
        return None
    y, mo, d = m.group(1), m.group(2), m.group(3)
    try:
        dt = datetime(int(y), int(mo), int(d))
        # labels.csv uses M/D/YYYY (no leading zeros)
        return f"{dt.month}/{dt.day}/{dt.year}"
    except ValueError:
        return None


def run_pdftotext(pdf_path: str) -> str:
    try:
        # Use layout to retain columns; suppress errors
        out = subprocess.run([
            "pdftotext", "-layout", pdf_path, "-"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, text=True
        )
        return out.stdout or ""
    except FileNotFoundError:
        return ""


def run_tesseract(pdf_path: str, dpi: int = 300) -> str:
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
    text1 = run_pdftotext(pdf_path)
    if text1.strip():
        return text1, "pdftotext"
    text2 = run_tesseract(pdf_path)
    return text2, "tesseract"


def normalize_amount(value: str) -> Optional[float]:
    try:
        v = value.replace(",", "").strip()
        return round(float(v), 2)
    except Exception:
        return None


def find_amounts_near_keyword(lines: List[str], keywords: List[str]) -> List[Tuple[float, float, str]]:
    results: List[Tuple[float, float, str]] = []
    key_re = re.compile("|".join([re.escape(k) for k in keywords]), re.IGNORECASE)
    for idx, line in enumerate(lines):
        if key_re.search(line):
            # Prefer numbers on the same line; else look at neighboring lines
            candidates = AMOUNT_RE.findall(line)
            look_range = []
            if not candidates:
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
                # Heuristic confidence: keyword proximity boosts confidence
                confidence = 0.92 if key_re.search(line) else 0.85
                results.append((amt, confidence, line.strip()))
    return results


def sum_deductions_by_keywords(lines: List[str], keywords: List[str]) -> Tuple[Optional[float], float, List[str]]:
    matches = find_amounts_near_keyword(lines, keywords)
    if not matches:
        return None, 0.0, []
    total = sum(m[0] for m in matches if m[0] is not None and m[0] >= 0)
    avg_conf = sum(m[1] for m in matches) / max(1, len(matches))
    notes = list({m[2] for m in matches})
    return round(total, 2), avg_conf, notes


def parse_fields(text: str) -> Tuple[Dict[str, Optional[float]], Dict[str, float], Dict[str, str]]:
    # Returns field_values, confidences, meta_notes
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    # Rent
    rent_candidates = find_amounts_near_keyword(lines, [
        "rent received", "rent from", "rent to", "rent", "rental income"
    ])
    rent_val = None
    rent_conf = 0.0
    if rent_candidates:
        # Prefer the largest, typical rent appears significant
        rent_val, rent_conf, _ = sorted(rent_candidates, key=lambda x: x[0], reverse=True)[0]

    # Management fee
    mgmt_candidates = find_amounts_near_keyword(lines, [
        "management fee", "management fees", "mgmt fee", "agent fee"
    ])
    mgmt_val = None
    mgmt_conf = 0.0
    if mgmt_candidates:
        # Often a percentage of rent; pick median
        sorted_m = sorted(mgmt_candidates, key=lambda x: x[0])
        mid = len(sorted_m) // 2
        mgmt_val, mgmt_conf, _ = sorted_m[mid]

    # Repairs / maintenance
    repair_val, repair_conf, repair_notes = sum_deductions_by_keywords(lines, [
        "repair", "repairs", "maintenance", "invoice", "call out", "gas safety", "legionella", "plumbing", "boiler"
    ])

    # Deposit / holding / float
    deposit_val, deposit_conf, deposit_notes = sum_deductions_by_keywords(lines, [
        "deposit", "float held", "reserve", "retention"
    ])

    # Misc (anything else like credit check, rent guarantee)
    misc_val, misc_conf, misc_notes = sum_deductions_by_keywords(lines, [
        "rent guarantee", "credit check", "standing charge", "certificate", "epc", "eicr", "pat"
    ])

    # Total / payment to landlord
    total_candidates = find_amounts_near_keyword(lines, [
        "net payment", "payment to landlord", "amount paid", "total to landlord", "balance paid", "total"
    ])
    total_val = None
    total_conf = 0.0
    if total_candidates:
        # Prefer the last occurrence (often summary)
        total_val, total_conf, _ = total_candidates[-1]

    # Derive total if missing
    derived_total = None
    parts = [p for p in [rent_val, mgmt_val, repair_val, deposit_val, misc_val] if p is not None]
    if parts and rent_val is not None:
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


def load_labels(labels_path: str) -> pd.DataFrame:
    df = pd.read_csv(labels_path)
    if "needs_review" not in df.columns:
        df["needs_review"] = ""
    return df


def is_row_present(df: pd.DataFrame, property_alias: str, statement_date: str) -> bool:
    # Existing labels appear to use (property_alias, statement_date) uniqueness
    mask = (df["property_alias"].astype(str) == property_alias) & (df["statement_date"].astype(str) == statement_date)
    return bool(mask.any())


def next_statement_id(df: pd.DataFrame) -> int:
    try:
        return int(df["statement_id"].max()) + 1
    except Exception:
        return 1


def reconcile_and_validate(values: Dict[str, Optional[float]]) -> Tuple[Dict[str, Optional[float]], float, List[str]]:
    issues: List[str] = []
    rent = values.get("rent")
    mgmt = values.get("management_fee")
    repair = values.get("repair")
    deposit = values.get("deposit")
    misc = values.get("misc")
    total = values.get("total")

    # All amounts should be positive in labels; take abs just in case
    for k in ["rent", "management_fee", "repair", "deposit", "misc", "total"]:
        if values.get(k) is not None:
            values[k] = round(abs(values[k]), 2)

    # Compute derived total if missing
    if total is None and rent is not None:
        others = sum(v for v in [mgmt, repair, deposit, misc] if v is not None)
        values["total"] = round(rent - others, 2)
        total = values["total"]

    # Reconciliation check within ±0.50
    tolerance = 0.50
    recok = True
    if rent is not None and total is not None:
        expected = round(rent - sum(v for v in [mgmt, repair, deposit, misc] if v is not None), 2)
        if abs(expected - total) > tolerance:
            recok = False
            issues.append(f"total_mismatch expected={expected} got={total}")

    # Overall heuristic confidence for needs_review flag
    # Base on presence of rent and total and reconciliation success
    base_conf = 0.0
    present_fields = sum(1 for k in ["rent", "management_fee", "repair", "deposit", "misc", "total"] if values.get(k) is not None)
    base_conf += 0.15 * present_fields
    if recok:
        base_conf += 0.25
    if rent is not None and total is not None:
        base_conf += 0.25
    # Clamp
    base_conf = max(0.0, min(1.0, base_conf))

    return values, base_conf, issues


def process_pdf(pdf_path: str) -> Tuple[Dict[str, Optional[float]], float, str, Dict[str, str]]:
    text, method = extract_text(pdf_path)
    values, confs, notes = parse_fields(text)
    values, overall_conf, issues = reconcile_and_validate(values)
    # Weight in field confidences
    avg_field_conf = sum(confs.values()) / max(1, len(confs))
    final_conf = 0.6 * overall_conf + 0.4 * avg_field_conf
    if issues:
        notes["notes"] = (notes.get("notes", "") + "; " + "; ".join(issues)).strip("; ").strip()
    return values, final_conf, method, notes


def append_rows(base_dir: str, labels_path: str) -> Tuple[int, int]:
    df = load_labels(labels_path)
    start_id = next_statement_id(df)
    appended = 0
    skipped = 0

    for prop_dir, alias in PROPERTY_ALIAS_BY_DIR.items():
        folder = os.path.join(base_dir, prop_dir)
        if not os.path.isdir(folder):
            continue
        for name in sorted(os.listdir(folder)):
            if not name.lower().endswith(".pdf"):
                continue
            pdf_path = os.path.join(folder, name)
            statement_date = parse_statement_date_from_filename(name)
            if not statement_date:
                skipped += 1
                continue
            if is_row_present(df, alias, statement_date):
                continue

            values, conf, method, notes = process_pdf(pdf_path)

            needs_review = "true" if conf < 0.90 else ""

            row = {
                "statement_id": start_id,
                "property_alias": alias,
                "statement_date": statement_date,
                "period_start": "",
                "period_end": "",
                "rent": values.get("rent", ""),
                "management_fee": values.get("management_fee", ""),
                "repair": values.get("repair", ""),
                "deposit": values.get("deposit", ""),
                "misc": values.get("misc", ""),
                "note": notes.get("notes", ""),
                "total": values.get("total", ""),
                "pay_date": statement_date,
                "needs_review": needs_review,
            }

            # Ensure columns order matches existing file plus needs_review at end
            # Read header order
            columns = list(df.columns)
            if "needs_review" not in columns:
                columns.append("needs_review")
            # Append row to df in memory
            df.loc[len(df)] = [row.get(col, df[col].dtype.type() if hasattr(df[col].dtype, 'type') else "") for col in columns]

            start_id += 1
            appended += 1

    # Write back to CSV (overwrite with updated DataFrame)
    df.to_csv(labels_path, index=False, quoting=csv.QUOTE_MINIMAL)
    return appended, skipped


def main():
    parser = argparse.ArgumentParser(description="OCR unlabeled rental statements and append to labels.csv")
    parser.add_argument("--base-dir", default="sample-data/rental-statements", help="Base directory containing property folders and labels.csv")
    parser.add_argument("--labels", default="sample-data/rental-statements/labels.csv", help="Path to labels.csv")
    args = parser.parse_args()

    appended, skipped = append_rows(args.base_dir, args.labels)
    print(f"Appended {appended} rows. Skipped {skipped} files without parseable dates or already labeled.")


if __name__ == "__main__":
    main()


