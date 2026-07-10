"""
HTML Layout Card Populator — adapted from
extracted_skills/html-populator/html-populator/scripts/populate_html.py

Populates the three QGIS-style HTML card templates (parcelinfo, Environmental,
Utilities) from a plain key:value text payload. Operates in-memory so it can be
called directly from a FastAPI request instead of via CLI.
"""
from bs4 import BeautifulSoup, NavigableString, Tag

from config import TEMPLATES_DIR

TEMPLATE_FILES = ["parcelinfo.html", "Environmental.html", "Utilities.html"]

FIELD_CONFIG = {
    "pid": ("class", "pid", "PID: {value}"),
    "address": ("address",),
    "area_m2": ("class", "area-badge", "{value}"),
    "area_ft2": ("class", "area-badge-sub", "{value}"),
    "zone": ("class", "zone-value", "{value}"),
    "zone_desc": ("zone_full_desc",),
    "municipality": ("footer_text",),
    "plan_area": ("label", "Plan Area"),
    "groundwater": ("label", "Groundwater Region"),
    "surficial_geology": ("label", "Surficial Geology"),
    "vs30": ("env_label", "VS30 Velocity"),
    "surface_form": ("env_label", "Surface Form"),
    "karst_risk": ("env_label", "Karst Risk"),
    "flood_risk": ("env_label", "Flood Risk"),
    "soil_drainage": ("label", "Soil Drainage"),
    "dtw": ("label", "Depth-to-Water (DTW)"),
    "saltwater": ("label", "Saltwater Intrusion"),
    "site_condition": ("label", "Site Condition"),
    "topography": ("description_block",),
    "min_setback": ("label", "Min Bldg Setback"),
    "service_req": ("label", "Service Requirement"),
    "stormwater": ("label", "Stormwater Area"),
    "sewershed": ("label", "Sewershed"),
    "distribution": ("label", "Distribution Area"),
}

SECTION_PREFIX_MAP = {
    "geology": "Geology & Surface Form",
    "env": "Environmental Constraints",
    "drainage": "Drainage & Hydrology",
    "property": "Property Details",
    "water": "Water & Sewer",
}

ENV_STYLE_SECTIONS = {"Environmental Constraints"}


def extract_city(address: str) -> str | None:
    normalised = address.replace("\\n", "\n")
    lines = [l.strip() for l in normalised.splitlines() if l.strip()]

    if len(lines) >= 2:
        city_line = lines[-1]
        city = city_line.rsplit(",", 1)[0].strip()
    else:
        city_line = lines[0] if lines else ""
        parts = [p.strip() for p in city_line.split(",")]
        if len(parts) >= 3:
            city = parts[-2]
        elif len(parts) == 2:
            city = parts[0].strip()
        else:
            city = city_line
    return city if city else None


def set_address(soup, value):
    el = soup.find(class_="address")
    if not el:
        return
    el.clear()
    parts = value.split("\\n")
    for i, part in enumerate(parts):
        el.append(NavigableString(part.strip()))
        if i < len(parts) - 1:
            el.append(soup.new_tag("br"))


def set_by_class(soup, css_class, template, value):
    el = soup.find(class_=css_class)
    if el:
        el.string = template.format(value=value)


def set_by_label(soup, label_text, value) -> bool:
    for row in soup.find_all(class_="row"):
        label_el = row.find(class_="row-label")
        value_el = row.find(class_="row-value")
        if label_el and value_el and label_el.get_text(strip=True) == label_text:
            value_el.string = value
            return True
    return False


def set_by_env_label(soup, label_text, value) -> bool:
    for row in soup.find_all(class_="env-item-row"):
        label_el = row.find(class_="env-label")
        value_el = row.find(class_="env-value")
        if label_el and value_el and label_el.get_text(strip=True) == label_text:
            value_el.string = value
            return True
    return False


def set_zone_full_desc(soup, value):
    el = soup.find(class_="zone-full-desc")
    if el:
        el.string = value


def set_footer_text(soup, value):
    el = soup.find(class_="footer-text")
    if el:
        el.string = value


def set_description_block(soup, value):
    db = soup.find(class_="description-block")
    if not db:
        return
    title_div = db.find("div")
    db.clear()
    if title_div:
        db.append(title_div)
    db.append(NavigableString(value))


def add_extra_row(soup, section_title, label, value) -> bool:
    target_section_el = None
    for el in soup.find_all(class_="section-title"):
        if el.get_text(strip=True) == section_title:
            target_section_el = el
            break
    if not target_section_el:
        return False

    use_env_style = section_title in ENV_STYLE_SECTIONS

    if use_env_style:
        env_list = target_section_el.find_next(class_="env-list")
        if not env_list:
            return False
        new_row = soup.new_tag("div", attrs={"class": "env-item-row"})
        lbl = soup.new_tag("div", attrs={"class": "env-label"})
        lbl.string = label
        val = soup.new_tag("div", attrs={"class": "env-value"})
        val.string = value
        new_row.append(lbl)
        new_row.append(val)
        env_list.append(new_row)
        return True

    STOP_CLASSES = {"section-title", "footer", "description-block"}
    last_row = None
    insertion_parent = None

    for sibling in target_section_el.next_siblings:
        if not isinstance(sibling, Tag):
            continue
        sibling_classes = set(sibling.get("class", []))
        if sibling_classes & STOP_CLASSES:
            break
        if "row" in sibling_classes:
            last_row = sibling
            insertion_parent = sibling.parent
        if "rows" in sibling_classes:
            inner_rows = sibling.find_all(class_="row", recursive=False)
            if inner_rows:
                last_row = inner_rows[-1]
                insertion_parent = sibling

    new_row = soup.new_tag("div", attrs={"class": "row"})
    lbl = soup.new_tag("span", attrs={"class": "row-label"})
    lbl.string = label
    val = soup.new_tag("span", attrs={"class": "row-value"})
    val.string = value
    new_row.append(lbl)
    new_row.append(val)

    if last_row:
        last_row.insert_after(new_row)
    elif insertion_parent:
        insertion_parent.append(new_row)
    else:
        target_section_el.insert_after(new_row)
    return True


def parse_data_text(text: str) -> dict:
    data = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip().lower().replace(" ", "_")
        data[key] = value.strip()
    return data


def populate_one(template_html: str, data: dict) -> tuple[str, int, list[str]]:
    soup = BeautifulSoup(template_html, "html.parser")
    injected = 0
    skipped_keys = []

    for key, value in data.items():
        config = FIELD_CONFIG.get(key)
        if config is not None:
            strategy = config[0]
            if strategy == "address":
                set_address(soup, value)
                injected += 1
            elif strategy == "class":
                _, css_class, template = config
                set_by_class(soup, css_class, template, value)
                injected += 1
            elif strategy == "label":
                if set_by_label(soup, config[1], value):
                    injected += 1
            elif strategy == "env_label":
                if set_by_env_label(soup, config[1], value):
                    injected += 1
            elif strategy == "zone_full_desc":
                set_zone_full_desc(soup, value)
                injected += 1
            elif strategy == "footer_text":
                set_footer_text(soup, value)
                injected += 1
            elif strategy == "description_block":
                set_description_block(soup, value)
                injected += 1
            continue

        if "." in key:
            prefix, _, label_key = key.partition(".")
            section_title = SECTION_PREFIX_MAP.get(prefix)
            if section_title:
                label = label_key.replace("_", " ").title()
                if add_extra_row(soup, section_title, label, value):
                    injected += 1
                    continue
        else:
            skipped_keys.append(key)

    if "municipality" not in data and "address" in data:
        city = extract_city(data["address"])
        if city:
            footer_el = soup.find(class_="footer-text")
            if footer_el:
                existing = footer_el.get_text(strip=True)
                suffix = existing.split("·", 1)[1].strip() if "·" in existing else "Parcel Report"
                set_footer_text(soup, f"{city} Municipality · {suffix}")

    return str(soup), injected, skipped_keys


def populate_all_templates(data_text: str) -> dict:
    data = parse_data_text(data_text)
    results = {}
    for template_name in TEMPLATE_FILES:
        template_path = TEMPLATES_DIR / template_name
        if not template_path.exists():
            results[template_name] = {"found": False}
            continue
        html = template_path.read_text(encoding="utf-8")
        populated_html, injected, skipped = populate_one(html, data)
        results[template_name] = {
            "found": True,
            "html": populated_html,
            "fields_injected": injected,
            "unrecognised_keys": skipped,
        }
    return {"fields_loaded": len(data), "templates": results}
