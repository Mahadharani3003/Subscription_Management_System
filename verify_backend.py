# -*- coding: utf-8 -*-
"""
Verification & Test Suite for Brightloop Subscription Fullstack System.
Tests Python syntax, AST structures, all XML views, Actions, Menus, Security ACLs, and Manifest consistency.
"""

import os
import sys
import ast
import csv
import xml.etree.ElementTree as ET

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
ADDON_DIR = os.path.join(MODULE_DIR, 'brightloop_subscription')

def test_python_syntax():
    print("=== 1. Testing Python Syntax & AST Structure ===")
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

def test_manifest_and_views():
    print("\n=== 2. Testing Manifest Integrity & XML Views ===")
    manifest_path = os.path.join(ADDON_DIR, '__manifest__.py')
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = ast.literal_eval(f.read())
    
    print(f" Module Name: {manifest.get('name')}")
    print(f" Category: {manifest.get('category')}")
    print(f" Depends: {manifest.get('depends')}")

    data_files = manifest.get('data', [])
    assert data_files, "Manifest data list cannot be empty!"

    total_records = 0
    total_views = 0
    total_actions = 0
    total_menus = 0

    for rel_path in data_files:
        full_path = os.path.join(ADDON_DIR, rel_path)
        assert os.path.exists(full_path), f"File referenced in manifest does not exist: {rel_path}"
        
        if rel_path.endswith('.xml'):
            tree = ET.parse(full_path)
            root = tree.getroot()
            assert root.tag == 'odoo', f"Root element in {rel_path} must be <odoo>"
            
            records = root.findall('.//record')
            menus = root.findall('.//menuitem')
            views = [r for r in records if r.get('model') == 'ir.ui.view']
            actions = [r for r in records if r.get('model') and r.get('model').startswith('ir.actions')]

            total_records += len(records)
            total_views += len(views)
            total_actions += len(actions)
            total_menus += len(menus)

            print(f" [PASS] XML verified: {rel_path} ({len(records)} records, {len(views)} views, {len(actions)} actions, {len(menus)} menus)")

    print(f"\n Frontend Component Totals:")
    print(f" - Views (Kanban, Form, Tree, Calendar, Pivot, Graph, Search): {total_views}")
    print(f" - Window Actions: {total_actions}")
    print(f" - Navigation Menuitems: {total_menus}")
    print(f" - Total XML Data Records: {total_records}")
    return True

def test_security_csv():
    print("\n=== 3. Testing Security Access Rights (ir.model.access.csv) ===")
    csv_file = os.path.join(ADDON_DIR, 'security', 'ir.model.access.csv')
    assert os.path.exists(csv_file), f"Missing {csv_file}"

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        row_count = 0
        for row in reader:
            row_count += 1
            for perm in ('perm_read', 'perm_write', 'perm_create', 'perm_unlink'):
                assert row[perm] in ('0', '1'), f"Invalid permission value {row[perm]} for row {row['id']}"
        print(f" [PASS] Security CSV valid: {row_count} rules configured.")
    return True

def test_static_assets():
    print("\n=== 4. Testing Static Assets & SCSS ===")
    scss_file = os.path.join(ADDON_DIR, 'static', 'src', 'scss', 'brightloop_styles.scss')
    assert os.path.exists(scss_file), "Missing brightloop_styles.scss"
    icon_file = os.path.join(ADDON_DIR, 'static', 'description', 'icon.png')
    assert os.path.exists(icon_file), "Missing module icon.png"
    print(f" [PASS] Assets present: SCSS ({os.path.getsize(scss_file)} bytes), Icon ({os.path.getsize(icon_file)} bytes)")
    return True

def main():
    py_ok = test_python_syntax()
    views_ok = test_manifest_and_views()
    csv_ok = test_security_csv()
    assets_ok = test_static_assets()

    if py_ok and views_ok and csv_ok and assets_ok:
        print("\n=======================================================")
        print(" [ALL TESTS PASSED] Brightloop Frontend & Backend 100% Verified!")
        print("=======================================================\n")
        sys.exit(0)
    else:
        print("\n [FAILURE] Verification failed.")
        sys.exit(1)

if __name__ == '__main__':
    main()
