#!/usr/bin/env python3
"""
populate_html.py
Populates Helio QGIS layout HTML cards from a plain-text data file.

Usage:
    python populate_html.py data.txt [--templates-dir DIR] [--output-dir DIR]

The data file format is one `key: value` pair per line.
Lines starting with # are comments. Keys are case-insensitive.

KNOWN KEYS inject into pre-existing elements (matched by label or CSS class).

EXTRA KEYS (section.label_name: value) append new rows dynamically to any section.
Supported prefixes:
    geology.   → Geology & Surface Form
    env.       → Environmental Constraints
    drainage.  → Drainage & Hydrology
    property.  → Property Details
    water.     → Water & Sewer

Example extra key:
    geology.rare_mineral: Quartz deposits present
    → Adds a new "Rare Mineral" row to the Geology & Surface Form section
"""

import sys
import os
import argparse
from bs4 import BeautifulSoup, NavigableString, Tag


# ---------------------------------------------------------------------------
# Field configuration — maps known data-file keys to injection strategy
# ---------------------------------------------------------------------------

FIELD_CONFIG = {
    # --- Common header fields ---
    'pid':              ('class',   'pid',              'PID: {value}'),
    'address':          ('address',),
    'area_m2':          ('class',   'area-badge',       '{value}'),
    'area_ft2':         ('class',   'area-badge-sub',   '{value}'),

    # --- Zone block ---
    'zone':             ('class',   'zone-value',       '{value}'),
    'zone_desc':        ('zone_full_desc',),

    # --- Footer ---
    'municipality':     ('footer_text',),

    # --- Property Details (all files) ---
    'plan_area':        ('label',   'Plan Area'),

    # --- parcelinfo / Environmental: Geology & Surface Form ---
    'groundwater':      ('label',   'Groundwater Region'),
    'surficial_geology':('label',   'Surficial Geology'),

    # --- parcelinfo / Environmental: Environmental Constraints (env-item-row) ---
    'vs30':             ('env_label', 'VS30 Velocity'),
    'surface_form':     ('env_label', 'Surface Form'),
    'karst_risk':       ('env_label', 'Karst Risk'),
    'flood_risk':       ('env_label', 'Flood Risk'),

    # --- parcelinfo / Environmental: Drainage & Hydrology ---
    'soil_drainage':    ('label',   'Soil Drainage'),
    'dtw':              ('label',   'Depth-to-Water (DTW)'),
    'saltwater':        ('label',   'Saltwater Intrusion'),
    'site_condition':   ('label',   'Site Condition'),

    # --- parcelinfo / Environmental: Topography description block ---
    'topography':       ('description_block',),

    # --- Utilities: Property Details extras ---
    'min_setback':      ('label',   'Min Bldg Setback'),
    'service_req':      ('label',   'Service Requirement'),

    # --- Utilities: Water & Sewer ---
    'stormwater':       ('label',   'Stormwater Area'),
    'sewershed':        ('label',   'Sewershed'),
    'distribution':     ('label',   'Distribution Area'),
}


# ---------------------------------------------------------------------------
# Section prefix → HTML section title mapping (for dynamic extra rows)
# ---------------------------------------------------------------------------

SECTION_PREFIX_MAP = {
    'geology':   'Geology & Surface Form',
    'env':       'Environmental Constraints',
    'drainage':  'Drainage & Hydrology',
    'property':  'Property Details',
    'water':     'Water & Sewer',
}

# Sections that use .env-item-row / .env-label / .env-value (blue accent text)
ENV_STYLE_SECTIONS = {'Environmental Constraints'}


# ---------------------------------------------------------------------------
# Injection helpers
# ---------------------------------------------------------------------------

def extract_city(address):
    """
    Extract the city name from an address string.
    Handles both literal \\n and real newlines.
    Expects a format like '257 Main St\\nYarmouth, NS' or '1538 Larch St, Halifax, NS'.
    Returns the city string, or None if it can't be determined.
    """
    # Normalise line breaks
    normalised = address.replace('\\n', '\n')
    lines = [l.strip() for l in normalised.splitlines() if l.strip()]

    if len(lines) >= 2:
        # Second line is typically "City, Province" — strip the province
        city_line = lines[-1]
        city = city_line.rsplit(',', 1)[0].strip()
    else:
        # Single line like "100 King St, Truro, NS" — city is second-to-last segment
        city_line = lines[0] if lines else ''
        parts = [p.strip() for p in city_line.split(',')]
        if len(parts) >= 3:
            city = parts[-2]          # e.g. "Truro" from "100 King St, Truro, NS"
        elif len(parts) == 2:
            city = parts[0].strip()   # e.g. "Halifax" from "Halifax, NS"
        else:
            city = city_line

    return city if city else None


def set_address(soup, value):
    """Set .address, converting literal \\n to <br> tags."""
    el = soup.find(class_='address')
    if not el:
        return
    el.clear()
    parts = value.split('\\n')
    for i, part in enumerate(parts):
        el.append(NavigableString(part.strip()))
        if i < len(parts) - 1:
            el.append(soup.new_tag('br'))


def set_by_class(soup, css_class, template, value):
    el = soup.find(class_=css_class)
    if el:
        el.string = template.format(value=value)


def set_by_label(soup, label_text, value):
    for row in soup.find_all(class_='row'):
        label_el = row.find(class_='row-label')
        value_el = row.find(class_='row-value')
        if label_el and value_el and label_el.get_text(strip=True) == label_text:
            value_el.string = value
            return True
    return False


def set_by_env_label(soup, label_text, value):
    for row in soup.find_all(class_='env-item-row'):
        label_el = row.find(class_='env-label')
        value_el = row.find(class_='env-value')
        if label_el and value_el and label_el.get_text(strip=True) == label_text:
            value_el.string = value
            return True
    return False


def set_zone_full_desc(soup, value):
    el = soup.find(class_='zone-full-desc')
    if el:
        el.string = value


def set_footer_text(soup, value):
    el = soup.find(class_='footer-text')
    if el:
        el.string = value


def set_description_block(soup, value):
    """Set the text of .description-block, preserving the inner title <div>."""
    db = soup.find(class_='description-block')
    if not db:
        return
    title_div = db.find('div')
    db.clear()
    if title_div:
        db.append(title_div)
    db.append(NavigableString(value))


# ---------------------------------------------------------------------------
# Dynamic extra-row insertion
# ---------------------------------------------------------------------------

def add_extra_row(soup, section_title, label, value):
    """
    Find the section whose .section-title text matches section_title,
    then append a new row with the given label and value.

    Uses .env-item-row style for ENV_STYLE_SECTIONS, .row style for all others.
    Returns True if the row was successfully inserted.
    """
    # Find the matching section-title element
    target_section_el = None
    for el in soup.find_all(class_='section-title'):
        if el.get_text(strip=True) == section_title:
            target_section_el = el
            break

    if not target_section_el:
        return False  # This template doesn't have this section — silently skip

    use_env_style = section_title in ENV_STYLE_SECTIONS

    if use_env_style:
        # Append inside the .env-list that follows this section-title
        env_list = target_section_el.find_next(class_='env-list')
        if not env_list:
            return False
        new_row = soup.new_tag('div', attrs={'class': 'env-item-row'})
        lbl = soup.new_tag('div', attrs={'class': 'env-label'})
        lbl.string = label
        val = soup.new_tag('div', attrs={'class': 'env-value'})
        val.string = value
        new_row.append(lbl)
        new_row.append(val)
        env_list.append(new_row)
        return True

    else:
        # Find the last .row sibling that belongs to this section
        # (stop at the next .section-title, .footer, or .description-block)
        STOP_CLASSES = {'section-title', 'footer', 'description-block'}
        last_row = None
        insertion_parent = None

        for sibling in target_section_el.next_siblings:
            if not isinstance(sibling, Tag):
                continue
            sibling_classes = set(sibling.get('class', []))
            if sibling_classes & STOP_CLASSES:
                break
            # Check if this element IS a row
            if 'row' in sibling_classes:
                last_row = sibling
                insertion_parent = sibling.parent
            # Or if it's a .rows container holding rows
            if 'rows' in sibling_classes:
                inner_rows = sibling.find_all(class_='row', recursive=False)
                if inner_rows:
                    last_row = inner_rows[-1]
                    insertion_parent = sibling  # insert inside the .rows div

        new_row = soup.new_tag('div', attrs={'class': 'row'})
        lbl = soup.new_tag('span', attrs={'class': 'row-label'})
        lbl.string = label
        val = soup.new_tag('span', attrs={'class': 'row-value'})
        val.string = value
        new_row.append(lbl)
        new_row.append(val)

        if last_row:
            last_row.insert_after(new_row)
        elif insertion_parent:
            insertion_parent.append(new_row)
        else:
            # Fallback: insert directly after the section-title
            target_section_el.insert_after(new_row)

        return True


# ---------------------------------------------------------------------------
# Data file parser
# ---------------------------------------------------------------------------

def parse_data_file(filepath):
    """Parse key: value pairs. Returns dict of lowercase keys."""
    data = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if ':' not in line:
                print(f"  ⚠  Line {lineno} skipped (no colon): {line!r}")
                continue
            key, _, value = line.partition(':')
            key = key.strip().lower().replace(' ', '_')
            value = value.strip()
            data[key] = value
    return data


# ---------------------------------------------------------------------------
# Main populate function
# ---------------------------------------------------------------------------

def populate_html(template_path, data, output_path):
    with open(template_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    injected = 0
    skipped_keys = []

    for key, value in data.items():

        # --- Known field ---
        config = FIELD_CONFIG.get(key)
        if config is not None:
            strategy = config[0]

            if strategy == 'address':
                set_address(soup, value)
                injected += 1

            elif strategy == 'class':
                _, css_class, template = config
                set_by_class(soup, css_class, template, value)
                injected += 1

            elif strategy == 'label':
                _, label_text = config
                if set_by_label(soup, label_text, value):
                    injected += 1

            elif strategy == 'env_label':
                _, label_text = config
                if set_by_env_label(soup, label_text, value):
                    injected += 1

            elif strategy == 'zone_full_desc':
                set_zone_full_desc(soup, value)
                injected += 1

            elif strategy == 'footer_text':
                set_footer_text(soup, value)
                injected += 1

            elif strategy == 'description_block':
                set_description_block(soup, value)
                injected += 1

            continue

        # --- Extra / dynamic field (prefix.label_key: value) ---
        if '.' in key:
            prefix, _, label_key = key.partition('.')
            section_title = SECTION_PREFIX_MAP.get(prefix)
            if section_title:
                # Convert label_key to a human-readable label
                label = label_key.replace('_', ' ').title()
                if add_extra_row(soup, section_title, label, value):
                    injected += 1
                    continue
            # If prefix unknown or section not in this template, skip silently

        else:
            skipped_keys.append(key)

    # Auto-derive footer from address if municipality wasn't explicitly set
    if 'municipality' not in data and 'address' in data:
        city = extract_city(data['address'])
        if city:
            # Read whatever suffix the template already has (e.g. "· Parcel Report")
            footer_el = soup.find(class_='footer-text')
            if footer_el:
                existing = footer_el.get_text(strip=True)
                # Keep the suffix after the first '·', or fall back to '· Parcel Report'
                if '·' in existing:
                    suffix = existing.split('·', 1)[1].strip()
                else:
                    suffix = 'Parcel Report'
                set_footer_text(soup, f"{city} Municipality · {suffix}")

    os.makedirs(output_path.rsplit('/', 1)[0], exist_ok=True) if '/' in output_path else None
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))

    template_name = os.path.basename(template_path)
    print(f"  ✓  {template_name} → {output_path}  ({injected} fields injected)")
    if skipped_keys:
        print(f"     Unrecognised keys (skipped): {', '.join(skipped_keys)}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Populate Helio QGIS HTML layout cards from a data text file.'
    )
    parser.add_argument('data_file', help='Path to the .txt data file (key: value format)')
    parser.add_argument('--templates-dir', default='.', help='Directory containing the HTML template files')
    parser.add_argument('--output-dir', default='./outputs', help='Directory to write populated HTML files')
    args = parser.parse_args()

    if not os.path.exists(args.data_file):
        print(f"ERROR: Data file not found: {args.data_file}")
        sys.exit(1)

    print(f"\nReading data from: {args.data_file}")
    data = parse_data_file(args.data_file)
    print(f"  {len(data)} fields loaded.\n")

    templates = ['parcelinfo.html', 'Environmental.html', 'Utilities.html']
    found = 0
    for template_name in templates:
        template_path = os.path.join(args.templates_dir, template_name)
        if not os.path.exists(template_path):
            print(f"  ⚠  Template not found, skipping: {template_path}")
            continue
        found += 1
        output_path = os.path.join(args.output_dir, template_name)
        populate_html(template_path, data, output_path)

    print(f"\nDone. {found}/{len(templates)} templates processed.")
    print(f"Outputs saved to: {args.output_dir}\n")


if __name__ == '__main__':
    main()
