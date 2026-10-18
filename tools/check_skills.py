#!/usr/bin/env python3
"""Lint every skill in skills/ against the Agent Skills spec and this repo's rules.

Checks per skill:
  * SKILL.md exists and starts with YAML frontmatter
  * only Agent Skills spec frontmatter fields are used
  * name: 1-64 chars, lowercase a-z 0-9 and single hyphens, equals the folder name
  * description: 1-1024 chars
  * SKILL.md body is at most MAX_LINES lines
  * references/sources.md exists and has a "Last verified:" date
  * relative Markdown links in SKILL.md and references/*.md resolve
  * tax / legal skills carry a "not tax advice" / "not legal advice" note

Usage:
    python3 tools/check_skills.py            # lint, exit 1 on any error
    python3 tools/check_skills.py --todos    # also list every TODO(verify) in the repo

Standard library only.
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
MAX_LINES = 300
SPEC_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DISCLAIMER_RE = re.compile(r"not (tax|legal)( or (tax|legal))? advice|not (tax|legal) advice", re.I)
# Skills that give tax or legal guidance and therefore need the disclaimer.
NEEDS_DISCLAIMER = {
    "gst-invoicing", "gst-tax-calculation", "tds-basics", "dpdp-privacy",
    "indian-id-validation", "indian-dates-and-fiscal-year",
}
LINK_RE = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
TODO_RE = re.compile(r"TODO\(verify\):?[^\n]*")


def parse_frontmatter(text):
    """Return (fields, body). Supports the flat 'key: value' YAML used by skills,
    plus one nested map level (for metadata)."""
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with '---' frontmatter on line 1")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("frontmatter is not closed with '---'")
    fields, current = {}, None
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")):
            if current is None or not isinstance(fields.get(current), dict):
                raise ValueError(f"unexpected indented line: {line!r}")
            k, _, v = line.strip().partition(":")
            fields[current][k.strip()] = v.strip().strip('"').strip("'")
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise ValueError(f"bad frontmatter line: {line!r}")
        key, value = key.strip(), value.strip()
        current = key
        fields[key] = {} if value == "" else value.strip('"').strip("'")
    return fields, text[end + 5:]


def check_links(md_path, errors):
    for target in LINK_RE.findall(md_path.read_text(encoding="utf-8")):
        if re.match(r"^[a-z]+:", target):
            continue
        if not (md_path.parent / target).exists():
            errors.append(f"{md_path.relative_to(ROOT)}: broken link -> {target}")


def check_skill(skill_dir):
    errors = []
    rel = skill_dir.relative_to(ROOT)
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return [f"{rel}: missing SKILL.md"]
    text = skill_md.read_text(encoding="utf-8")
    try:
        fm, _body = parse_frontmatter(text)
    except ValueError as exc:
        return [f"{rel}/SKILL.md: {exc}"]

    extra = set(fm) - SPEC_FIELDS
    if extra:
        errors.append(f"{rel}: non-spec frontmatter fields {sorted(extra)}")
    name = fm.get("name", "")
    if not (1 <= len(name) <= 64 and NAME_RE.match(name)):
        errors.append(f"{rel}: name {name!r} must be 1-64 chars of a-z, 0-9 and single hyphens")
    if name != skill_dir.name:
        errors.append(f"{rel}: name {name!r} must match folder name {skill_dir.name!r}")
    desc = fm.get("description", "")
    if not isinstance(desc, str) or not 1 <= len(desc) <= 1024:
        errors.append(f"{rel}: description must be 1-1024 characters (got {len(desc)})")
    if "metadata" in fm and not isinstance(fm["metadata"], dict):
        errors.append(f"{rel}: metadata must be a map of string keys to string values")

    n_lines = text.count("\n") + 1
    if n_lines > MAX_LINES:
        errors.append(f"{rel}/SKILL.md: {n_lines} lines (max {MAX_LINES}); move detail to references/")

    sources = skill_dir / "references" / "sources.md"
    if not sources.exists():
        errors.append(f"{rel}: missing references/sources.md")
    elif not re.search(r"Last verified:?\**\s*\d{4}-\d{2}-\d{2}", sources.read_text(encoding="utf-8")):
        errors.append(f"{rel}/references/sources.md: needs 'Last verified: YYYY-MM-DD'")

    if skill_dir.name in NEEDS_DISCLAIMER and not DISCLAIMER_RE.search(text):
        errors.append(f"{rel}/SKILL.md: tax/legal skill needs a 'not tax/legal advice' note")

    check_links(skill_md, errors)
    for ref in sorted((skill_dir / "references").glob("*.md")):
        check_links(ref, errors)
    return errors


def skill_dirs():
    return sorted(p for p in SKILLS.iterdir() if p.is_dir() and not p.name.startswith((".", "_")))


def find_todos():
    found = []
    for path in sorted(ROOT.rglob("*")):
        if path.is_dir() or ".git" in path.parts or path.suffix not in {".md", ".py", ".json"}:
            continue
        if path.resolve() == pathlib.Path(__file__).resolve():
            continue
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for m in TODO_RE.finditer(line):
                found.append(f"{path.relative_to(ROOT)}:{i}: {m.group(0).strip()}")
    return found


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    errors = []
    dirs = skill_dirs()
    for d in dirs:
        errors.extend(check_skill(d))
    for e in errors:
        print(f"ERROR {e}")
    print(f"checked {len(dirs)} skill(s): {len(errors)} error(s)")
    if "--todos" in argv:
        todos = find_todos()
        print(f"\n{len(todos)} TODO(verify) item(s):")
        for t in todos:
            print(f"  {t}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
