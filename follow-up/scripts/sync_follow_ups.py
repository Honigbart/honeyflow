#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable


SECTION_ORDER = ["Open", "Started", "Done", "Superseded", "Dropped"]
ENTRY_HEADER_RE = re.compile(r"^### (FU-\d{3,}) — (.+)$")
META_RE = re.compile(r"^- ([a-z_]+): (.+)$")
PLAN_ROW_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|")


@dataclass
class Entry:
    id: str
    title: str
    source_plan: str
    source_status: str
    linked_plan: str
    notes: str
    section: str


class Registry:
    def __init__(self, last_updated: str | None = None) -> None:
        self.last_updated = last_updated or today()
        self.sections: dict[str, list[Entry]] = {name: [] for name in SECTION_ORDER}

    def all_entries(self) -> list[Entry]:
        return [entry for name in SECTION_ORDER for entry in self.sections[name]]

    def next_id(self) -> str:
        max_num = 0
        for entry in self.all_entries():
            try:
                max_num = max(max_num, int(entry.id.split("-")[1]))
            except (IndexError, ValueError):
                continue
        return f"FU-{max_num + 1:03d}"

    def find_matches(self, identifier: str, sections: Iterable[str] | None = None) -> list[Entry]:
        needle = identifier.strip()
        haystack = (
            [entry for section in sections for entry in self.sections[section]]
            if sections is not None
            else self.all_entries()
        )
        if re.fullmatch(r"FU-\d{3,}", needle):
            return [entry for entry in haystack if entry.id == needle]
        lowered = needle.lower()
        return [entry for entry in haystack if entry.title.lower() == lowered]

    def move_entry(self, entry: Entry, target_section: str) -> None:
        if target_section not in self.sections:
            raise ValueError(f"unknown section: {target_section}")
        for section in SECTION_ORDER:
            if entry in self.sections[section]:
                self.sections[section].remove(entry)
        entry.section = target_section
        self.sections[target_section].append(entry)

    def render(self) -> str:
        lines: list[str] = [
            "# Follow-Ups",
            "",
            f"> Last updated: {self.last_updated}",
            "",
        ]
        for idx, section in enumerate(SECTION_ORDER):
            lines.append(f"## {section}")
            lines.append("")
            for entry in self.sections[section]:
                lines.extend(
                    [
                        f"### {entry.id} — {entry.title}",
                        f"- source_plan: {entry.source_plan}",
                        f"- source_status: {entry.source_status}",
                        f"- linked_plan: {entry.linked_plan}",
                        f"- notes: {entry.notes}",
                        "",
                    ]
                )
            if idx != len(SECTION_ORDER) - 1 and lines[-1] != "":
                lines.append("")
        if lines[-1] != "":
            lines.append("")
        return "\n".join(lines)


def today() -> str:
    return date.today().isoformat()


def empty_registry() -> Registry:
    return Registry(today())


def load_registry(path: Path) -> Registry:
    if not path.exists():
        return empty_registry()

    registry = Registry()
    current_section: str | None = None
    current_entry: Entry | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip("\n")
        if line.startswith("> Last updated:"):
            registry.last_updated = line.split(":", 1)[1].strip()
            continue
        if line.startswith("## "):
            current_section = line[3:].strip()
            if current_section not in registry.sections:
                raise ValueError(f"unknown section in registry: {current_section}")
            current_entry = None
            continue
        header_match = ENTRY_HEADER_RE.match(line)
        if header_match:
            if current_section is None:
                raise ValueError("entry encountered before section")
            current_entry = Entry(
                id=header_match.group(1),
                title=header_match.group(2),
                source_plan="",
                source_status="",
                linked_plan="none",
                notes="none",
                section=current_section,
            )
            registry.sections[current_section].append(current_entry)
            continue
        meta_match = META_RE.match(line)
        if meta_match and current_entry is not None:
            key, value = meta_match.groups()
            if key == "source_plan":
                current_entry.source_plan = value
            elif key == "source_status":
                current_entry.source_status = value
            elif key == "linked_plan":
                current_entry.linked_plan = value
            elif key == "notes":
                current_entry.notes = value

    return registry


def write_registry(path: Path, registry: Registry) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    registry.last_updated = today()
    path.write_text(registry.render(), encoding="utf-8")


def parse_follow_ups_from_plan(plan_file: Path) -> list[tuple[str, str]]:
    text = plan_file.read_text(encoding="utf-8")
    lines = text.splitlines()
    in_section = False
    section_lines: list[str] = []
    for line in lines:
        if line.startswith("## "):
            heading = line[3:].strip()
            if heading == "14. Follow-on Artifacts":
                in_section = True
                continue
            if in_section:
                break
        if in_section:
            section_lines.append(line.rstrip())

    cleaned = [line.strip() for line in section_lines if line.strip()]
    if not cleaned:
        return []
    if len(cleaned) == 1 and cleaned[0].lower().rstrip(".") == "none needed":
        return []

    items: list[tuple[str, str]] = []
    for line in cleaned:
        if not line.startswith("- "):
            continue
        body = line[2:].strip()
        if " — " in body:
            title, notes = body.split(" — ", 1)
        else:
            title, notes = body, "none"
        items.append((title.strip(), notes.strip() or "none"))
    return items


def parse_plans_index(path: Path) -> dict[str, str]:
    statuses: dict[str, str] = {}
    if not path.exists():
        return statuses
    for line in path.read_text(encoding="utf-8").splitlines():
        match = PLAN_ROW_RE.match(line)
        if not match:
            continue
        slug = match.group(1).strip()
        status = match.group(2).strip()
        if slug.lower() == "slug" or set(slug) == {"-"}:
            continue
        statuses[slug] = status
    return statuses


def sync_plan(registry: Registry, source_plan: str, source_status: str, items: list[tuple[str, str]]) -> tuple[int, int, int]:
    open_section = registry.sections["Open"]
    source_open_entries = [entry for entry in open_section if entry.source_plan == source_plan]
    source_open_by_title: dict[str, list[Entry]] = {}
    for entry in source_open_entries:
        source_open_by_title.setdefault(entry.title, []).append(entry)

    new_entries: list[Entry] = []
    preserved = 0
    created = 0
    matched_ids: set[str] = set()

    for title, notes in items:
        matches = source_open_by_title.get(title, [])
        if matches:
            entry = matches.pop(0)
            preserved += 1
            matched_ids.add(entry.id)
            entry.notes = notes
            entry.source_status = source_status
            entry.linked_plan = "none" if entry.linked_plan == "" else entry.linked_plan
            new_entries.append(entry)
        else:
            created += 1
            new_entries.append(
                Entry(
                    id=registry.next_id(),
                    title=title,
                    source_plan=source_plan,
                    source_status=source_status,
                    linked_plan="none",
                    notes=notes,
                    section="Open",
                )
            )

    removed = 0
    remaining_source_entries = [entry for entry in source_open_entries if entry.id not in matched_ids]
    for entry in remaining_source_entries:
        removed += 1
        registry.move_entry(entry, "Superseded")

    rebuilt_open: list[Entry] = []
    inserted = False
    for entry in open_section:
        if entry.source_plan != source_plan:
            rebuilt_open.append(entry)
            continue
        if not inserted:
            rebuilt_open.extend(new_entries)
            inserted = True
    if not inserted:
        rebuilt_open.extend(new_entries)
    registry.sections["Open"] = rebuilt_open

    return preserved, created, removed


def mark_source_status(registry: Registry, source_plan: str, source_status: str) -> int:
    count = 0
    for entry in registry.all_entries():
        if entry.source_plan == source_plan:
            entry.source_status = source_status
            count += 1
    return count


def resolve_linked_plan(registry: Registry, linked_plan: str, target_section: str) -> int:
    matches = [entry for entry in registry.all_entries() if entry.linked_plan == linked_plan]
    for entry in matches:
        registry.move_entry(entry, target_section)
    return len(matches)


def set_started(registry: Registry, identifier: str, linked_plan: str) -> Entry:
    matches = registry.find_matches(identifier, sections=["Open", "Started"])
    if not matches:
        raise ValueError(f"no follow-up matches '{identifier}'")
    if len(matches) > 1:
        raise ValueError(f"ambiguous follow-up identifier '{identifier}'")
    entry = matches[0]
    entry.linked_plan = linked_plan
    registry.move_entry(entry, "Started")
    return entry


def resolve_item(registry: Registry, identifier: str, target_section: str, notes: str | None) -> Entry:
    matches = registry.find_matches(identifier)
    if not matches:
        raise ValueError(f"no follow-up matches '{identifier}'")
    if len(matches) > 1:
        raise ValueError(f"ambiguous follow-up identifier '{identifier}'")
    entry = matches[0]
    if notes is not None:
        entry.notes = notes
    registry.move_entry(entry, target_section)
    return entry


def rebuild_registry(plans_index: Path, plans_dir: Path, archive_dir: Path) -> Registry:
    statuses = parse_plans_index(plans_index)
    registry = empty_registry()

    for plan_file in sorted(plans_dir.glob("*/final_plan.md")):
        slug = plan_file.parent.name
        for title, notes in parse_follow_ups_from_plan(plan_file):
            registry.sections["Open"].append(
                Entry(
                    id=registry.next_id(),
                    title=title,
                    source_plan=slug,
                    source_status=statuses.get(slug, "active"),
                    linked_plan="none",
                    notes=notes,
                    section="Open",
                )
            )

    for plan_file in sorted(archive_dir.glob("*/final_plan.md")):
        slug = plan_file.parent.name
        source_status = statuses.get(slug, "completed")
        for title, notes in parse_follow_ups_from_plan(plan_file):
            registry.sections["Open"].append(
                Entry(
                    id=registry.next_id(),
                    title=title,
                    source_plan=slug,
                    source_status=source_status,
                    linked_plan="none",
                    notes=notes,
                    section="Open",
                )
            )

    return registry


def cmd_sync_plan(args: argparse.Namespace) -> int:
    registry = load_registry(Path(args.registry))
    items = parse_follow_ups_from_plan(Path(args.plan_file))
    preserved, created, removed = sync_plan(registry, args.source_plan, args.source_status, items)
    write_registry(Path(args.registry), registry)
    print(f"sync-plan: preserved={preserved} created={created} superseded={removed}")
    return 0


def cmd_mark_source_status(args: argparse.Namespace) -> int:
    registry_path = Path(args.registry)
    registry = load_registry(registry_path)
    updated = mark_source_status(registry, args.source_plan, args.source_status)
    write_registry(registry_path, registry)
    print(f"mark-source-status: updated={updated}")
    return 0


def cmd_resolve_linked_plan(args: argparse.Namespace) -> int:
    registry_path = Path(args.registry)
    registry = load_registry(registry_path)
    updated = resolve_linked_plan(registry, args.linked_plan, args.target_section)
    write_registry(registry_path, registry)
    print(f"resolve-linked-plan: moved={updated}")
    return 0


def cmd_start_item(args: argparse.Namespace) -> int:
    registry_path = Path(args.registry)
    registry = load_registry(registry_path)
    entry = set_started(registry, args.identifier, args.linked_plan)
    write_registry(registry_path, registry)
    print(f"start-item: {entry.id} -> Started linked_plan={entry.linked_plan}")
    return 0


def cmd_resolve_item(args: argparse.Namespace) -> int:
    registry_path = Path(args.registry)
    registry = load_registry(registry_path)
    entry = resolve_item(registry, args.identifier, args.target_section, args.notes)
    write_registry(registry_path, registry)
    print(f"resolve-item: {entry.id} -> {args.target_section}")
    return 0


def cmd_rebuild(args: argparse.Namespace) -> int:
    registry = rebuild_registry(Path(args.plans_index), Path(args.plans_dir), Path(args.archive_dir))
    write_registry(Path(args.registry), registry)
    print(f"rebuild: open={len(registry.sections['Open'])}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    registry = load_registry(Path(args.registry))
    sections = SECTION_ORDER if args.all else ["Open", "Started"]
    for section in sections:
        print(f"## {section}")
        for entry in registry.sections[section]:
            print(
                f"{entry.id}\t{entry.title}\t"
                f"source={entry.source_plan}:{entry.source_status}\t"
                f"linked={entry.linked_plan}\t"
                f"notes={entry.notes}"
            )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Synchronize .ai/follow_ups.md")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sync_plan_parser = subparsers.add_parser("sync-plan")
    sync_plan_parser.add_argument("--source-plan", required=True)
    sync_plan_parser.add_argument("--source-status", required=True, choices=["active", "completed", "abandoned"])
    sync_plan_parser.add_argument("--plan-file", required=True)
    sync_plan_parser.add_argument("--registry", required=True)
    sync_plan_parser.set_defaults(func=cmd_sync_plan)

    source_status_parser = subparsers.add_parser("mark-source-status")
    source_status_parser.add_argument("--source-plan", required=True)
    source_status_parser.add_argument("--source-status", required=True, choices=["active", "completed", "abandoned"])
    source_status_parser.add_argument("--registry", required=True)
    source_status_parser.set_defaults(func=cmd_mark_source_status)

    resolve_linked_parser = subparsers.add_parser("resolve-linked-plan")
    resolve_linked_parser.add_argument("--linked-plan", required=True)
    resolve_linked_parser.add_argument(
        "--target-section",
        default="Done",
        choices=["Done", "Superseded", "Dropped"],
    )
    resolve_linked_parser.add_argument("--registry", required=True)
    resolve_linked_parser.set_defaults(func=cmd_resolve_linked_plan)

    start_item_parser = subparsers.add_parser("start-item")
    start_item_parser.add_argument("--identifier", required=True)
    start_item_parser.add_argument("--linked-plan", required=True)
    start_item_parser.add_argument("--registry", required=True)
    start_item_parser.set_defaults(func=cmd_start_item)

    resolve_item_parser = subparsers.add_parser("resolve-item")
    resolve_item_parser.add_argument("--identifier", required=True)
    resolve_item_parser.add_argument(
        "--target-section",
        required=True,
        choices=["Done", "Superseded", "Dropped"],
    )
    resolve_item_parser.add_argument("--notes")
    resolve_item_parser.add_argument("--registry", required=True)
    resolve_item_parser.set_defaults(func=cmd_resolve_item)

    rebuild_parser = subparsers.add_parser("rebuild")
    rebuild_parser.add_argument("--plans-index", required=True)
    rebuild_parser.add_argument("--plans-dir", required=True)
    rebuild_parser.add_argument("--archive-dir", required=True)
    rebuild_parser.add_argument("--registry", required=True)
    rebuild_parser.set_defaults(func=cmd_rebuild)

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--registry", required=True)
    list_parser.add_argument("--all", action="store_true")
    list_parser.set_defaults(func=cmd_list)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except Exception as exc:  # pragma: no cover - operational script
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
