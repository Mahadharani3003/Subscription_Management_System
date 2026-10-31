# -*- coding: utf-8 -*-
"""
Verification Script for Brightloop Subscription Backend Foundation.
Tests syntax, AST parsing, XML validity, and Security CSV formatting.
"""

import os
import sys
import ast
import csv
import xml.etree.ElementTree as ET

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
ADDON_DIR = os.path.join(MODULE_DIR, 'brightloop_subscription')

def test_python_syntax():
    print("=== Testing Python Syntax & AST Structure ===")
    py_files = []
    for root, _, files in os.walk(ADDON_DIR):
        for f in files:
            if f.endswith('.py'):
                py_files.append(os.path.join(root, f))
    
    assert py_files, "No Python files found!"
    for py_file in py_files:
        rel_path = os.path.relpath(py_file, MODULE_DIR)
        with open(py_file, 'r', encoding='utf-8') as src:
            code = src.read()
        try:
            tree = ast.parse(code, filename=py_file)
            print(f" [PASS] AST valid: {rel_path}")
        except SyntaxError as e:
            print(f" [FAIL] Syntax error in {rel_path}: {e}")
            return False
    return True

def test_xml_validity():
    print("\n=== Testing XML Well-Formedness & Odoo Structure ===")
    xml_files = []
    for root, _, files in os.walk(ADDON_DIR):
        for f in files:
            if f.endswith('.xml'):
                xml_files.append(os.path.join(root, f))

    assert xml_files, "No XML files found!"
    for xml_file in xml_files:
        rel_path = os.path.relpath(xml_file, MODULE_DIR)
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            assert root.tag == 'odoo', f"Root tag must be <odoo>, got <{root.tag}>"
            records = root.findall('.//record')
            print(f" [PASS] XML valid: {rel_path} ({len(records)} records)")
        except Exception as e:
            print(f" [FAIL] XML error in {rel_path}: {e}")
            return False
    return True

def test_security_csv():
    print("\n=== Testing Security ir.model.access.csv ===")
    csv_file = os.path.join(ADDON_DIR, 'security', 'ir.model.access.csv')
    assert os.path.exists(csv_file), f"Missing {csv_file}"

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        expected_cols = {'id', 'name', 'model_id:id', 'group_id:id', 'perm_read', 'perm_write', 'perm_create', 'perm_unlink'}
        actual_cols = set(reader.fieldnames)
        assert expected_cols.issubset(actual_cols), f"Missing columns in CSV: {expected_cols - actual_cols}"
        
        row_count = 0
        for row in reader:
            row_count += 1
            for perm in ('perm_read', 'perm_write', 'perm_create', 'perm_unlink'):
                assert row[perm] in ('0', '1'), f"Invalid permission value {row[perm]} for row {row['id']}"
        print(f" [PASS] Security CSV valid: {row_count} access rules configured properly.")
    return True

def main():
    py_ok = test_python_syntax()
    xml_ok = test_xml_validity()
    csv_ok = test_security_csv()

    if py_ok and xml_ok and csv_ok:
        print("\n [SUCCESS] All backend foundation tests PASSED seamlessly!")
        sys.exit(0)
    else:
        print("\n [FAILURE] Verification failed.")
        sys.exit(1)

if __name__ == '__main__':
    main()
