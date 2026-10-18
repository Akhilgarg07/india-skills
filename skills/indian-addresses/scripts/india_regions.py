#!/usr/bin/env python3
"""States and Union Territories of India, name normalisation, and PIN-code prefix
information (region and postal circle).

Data:
  * 28 States and 8 Union Territories (MHA). GST state codes from the GST state code list.
  * PIN structure (Department of Posts): first digit = region (9 regions; 9 = Army Postal
    Service), first two digits = postal circle / sub-region, first three = sorting district.
  * Two-digit circle ranges from an India Post circle page. That table predates Telangana,
    Jharkhand, Chhattisgarh and Uttarakhand as separate entries: a postal circle range is NOT a
    state boundary. Use the All India Pincode Directory (data.gov.in) for PIN -> state/district.

Module usage:
    >>> from india_regions import find_state, pin_info, STATES_AND_UTS
    >>> find_state("Orissa")["name"]
    'Odisha'
    >>> pin_info("560001")["circle"]
    'Karnataka'
    >>> len([s for s in STATES_AND_UTS if s["type"] == "state"])
    28

CLI usage:
    python3 india_regions.py list
    python3 india_regions.py state "pondicherry"
    python3 india_regions.py pin 110001

Standard library only.
"""

import json
import re
import sys

# name, type, GST state code, legislature (UTs only)
STATES_AND_UTS = [
    {"name": "Andhra Pradesh", "type": "state", "gst_code": "37"},
    {"name": "Arunachal Pradesh", "type": "state", "gst_code": "12"},
    {"name": "Assam", "type": "state", "gst_code": "18"},
    {"name": "Bihar", "type": "state", "gst_code": "10"},
    {"name": "Chhattisgarh", "type": "state", "gst_code": "22"},
    {"name": "Goa", "type": "state", "gst_code": "30"},
    {"name": "Gujarat", "type": "state", "gst_code": "24"},
    {"name": "Haryana", "type": "state", "gst_code": "06"},
    {"name": "Himachal Pradesh", "type": "state", "gst_code": "02"},
    {"name": "Jharkhand", "type": "state", "gst_code": "20"},
    {"name": "Karnataka", "type": "state", "gst_code": "29"},
    {"name": "Kerala", "type": "state", "gst_code": "32"},
    {"name": "Madhya Pradesh", "type": "state", "gst_code": "23"},
    {"name": "Maharashtra", "type": "state", "gst_code": "27"},
    {"name": "Manipur", "type": "state", "gst_code": "14"},
    {"name": "Meghalaya", "type": "state", "gst_code": "17"},
    {"name": "Mizoram", "type": "state", "gst_code": "15"},
    {"name": "Nagaland", "type": "state", "gst_code": "13"},
    {"name": "Odisha", "type": "state", "gst_code": "21"},
    {"name": "Punjab", "type": "state", "gst_code": "03"},
    {"name": "Rajasthan", "type": "state", "gst_code": "08"},
    {"name": "Sikkim", "type": "state", "gst_code": "11"},
    {"name": "Tamil Nadu", "type": "state", "gst_code": "33"},
    {"name": "Telangana", "type": "state", "gst_code": "36"},
    {"name": "Tripura", "type": "state", "gst_code": "16"},
    {"name": "Uttar Pradesh", "type": "state", "gst_code": "09"},
    {"name": "Uttarakhand", "type": "state", "gst_code": "05"},
    {"name": "West Bengal", "type": "state", "gst_code": "19"},
    {"name": "Andaman and Nicobar Islands", "type": "ut", "gst_code": "35", "legislature": False},
    {"name": "Chandigarh", "type": "ut", "gst_code": "04", "legislature": False},
    {"name": "Dadra and Nagar Haveli and Daman and Diu", "type": "ut", "gst_code": "26", "legislature": False},
    {"name": "Delhi", "type": "ut", "gst_code": "07", "legislature": True,
     "official_name": "National Capital Territory of Delhi"},
    {"name": "Jammu and Kashmir", "type": "ut", "gst_code": "01", "legislature": True},
    {"name": "Ladakh", "type": "ut", "gst_code": "38", "legislature": False},
    {"name": "Lakshadweep", "type": "ut", "gst_code": "31", "legislature": False},
    {"name": "Puducherry", "type": "ut", "gst_code": "34", "legislature": True},
]

# Old or informal names users still type -> current official name.
ALIASES = {
    "orissa": "Odisha", "pondicherry": "Puducherry", "uttaranchal": "Uttarakhand",
    "nct of delhi": "Delhi", "new delhi": "Delhi", "national capital territory of delhi": "Delhi",
    "j&k": "Jammu and Kashmir", "j & k": "Jammu and Kashmir", "jk": "Jammu and Kashmir",
    "andaman": "Andaman and Nicobar Islands", "a&n islands": "Andaman and Nicobar Islands",
    "andaman & nicobar": "Andaman and Nicobar Islands", "andaman & nicobar islands": "Andaman and Nicobar Islands",
    "dadra and nagar haveli": "Dadra and Nagar Haveli and Daman and Diu",
    "daman and diu": "Dadra and Nagar Haveli and Daman and Diu",
    "dnh and dd": "Dadra and Nagar Haveli and Daman and Diu",
    "dnhdd": "Dadra and Nagar Haveli and Daman and Diu",
    "chattisgarh": "Chhattisgarh", "tamilnadu": "Tamil Nadu", "telengana": "Telangana",
    "up": "Uttar Pradesh", "mp": "Madhya Pradesh", "ap": "Andhra Pradesh", "uk": None,  # ambiguous
}

PIN_REGIONS = {
    "1": "Northern", "2": "Northern", "3": "Western", "4": "Western",
    "5": "Southern", "6": "Southern", "7": "Eastern", "8": "Eastern",
    "9": "Army Postal Service",
}

# (low, high, circle) by first two digits, per India Post's published circle table.
PIN_CIRCLES = [
    (11, 11, "Delhi"), (12, 13, "Haryana"), (14, 16, "Punjab"), (17, 17, "Himachal Pradesh"),
    (18, 19, "Jammu and Kashmir"), (20, 28, "Uttar Pradesh"), (30, 34, "Rajasthan"),
    (36, 39, "Gujarat"), (40, 44, "Maharashtra"), (45, 49, "Madhya Pradesh"),
    (50, 53, "Andhra Pradesh"), (56, 59, "Karnataka"), (60, 64, "Tamil Nadu"),
    (67, 69, "Kerala"), (70, 74, "West Bengal"), (75, 77, "Odisha"), (78, 78, "Assam"),
    (79, 79, "North Eastern"), (80, 85, "Bihar"), (90, 99, "Army Postal Service"),
]

_BY_KEY = {re.sub(r"[^a-z]", "", s["name"].lower()): s for s in STATES_AND_UTS}


def _key(text):
    return re.sub(r"[^a-z]", "", text.lower().replace("&", "and"))


def find_state(text):
    """Return the state/UT dict for a name, alias or 2-digit GST code; None if unknown/ambiguous."""
    if not isinstance(text, str) or not text.strip():
        return None
    t = text.strip()
    if t.isdigit():
        code = t.zfill(2)
        return next((s for s in STATES_AND_UTS if s["gst_code"] == code), None)
    alias = ALIASES.get(re.sub(r"\s+", " ", t.lower()))
    if alias:
        t = alias
    elif re.sub(r"\s+", " ", t.lower()) in ALIASES:
        return None  # known-ambiguous abbreviation
    return _BY_KEY.get(_key(t))


def pin_info(pin):
    """Region and postal-circle information for a 6-digit PIN code (format only)."""
    p = str(pin).strip().replace(" ", "")
    if not re.fullmatch(r"[1-9][0-9]{5}", p):
        return {"pin": p, "valid_format": False, "region": None, "circle": None}
    two = int(p[:2])
    circle = next((c for lo, hi, c in PIN_CIRCLES if lo <= two <= hi), None)
    return {
        "pin": p,
        "valid_format": True,
        "region": PIN_REGIONS[p[0]],
        "circle": circle,
        "sorting_district_prefix": p[:3],
        "note": ("circle ranges are postal, not state boundaries; look up the PIN in the "
                 "All India Pincode Directory for state/district") if circle else
                ("prefix not in the published circle table; check the PIN directory"),
    }


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["list"]:
        for s in STATES_AND_UTS:
            print(f"{s['gst_code']}  {s['type']:5}  {s['name']}")
        return 0
    if len(argv) == 2 and argv[0] == "state":
        s = find_state(argv[1])
        print(json.dumps(s, indent=2) if s else "unknown or ambiguous state/UT name")
        return 0 if s else 1
    if len(argv) == 2 and argv[0] == "pin":
        r = pin_info(argv[1])
        print(json.dumps(r, indent=2))
        return 0 if r["valid_format"] else 1
    print("usage: india_regions.py list | state NAME | pin PINCODE", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
