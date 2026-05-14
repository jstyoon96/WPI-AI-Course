"""Parsers and audit helpers for Dalhousie/Superfile BSPM records."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET
from zipfile import ZipFile


NODE_COUNT = 352
NODE_LABEL_ROW_COUNT = 352
HEADER_FIELD_COUNT = 8
SAMPLE_PREFIX_COUNT = 10
SAMPLE_FIELD_COUNT = SAMPLE_PREFIX_COUNT + NODE_COUNT
SUPERFILE_GLOB = "**/superfile/node*.txt"
DIRECT_SUPERFILE_GLOB = "node*.txt"

XLSX_MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
XLSX_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
XLSX_PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
XLSX_NS = {"main": XLSX_MAIN_NS, "rel": XLSX_REL_NS, "pkgrel": XLSX_PKG_REL_NS}


@dataclass(frozen=True)
class SuperfileHeader:
    serial: int
    record_id: str
    sampling_interval_ms: float
    p_onset_ms: float
    p_offset_ms: float
    qrs_onset_ms: float
    qrs_offset_ms: float
    t_offset_ms: float


@dataclass(frozen=True)
class SuperfileRecord:
    source_name: str
    header: SuperfileHeader
    sample_numbers: list[int]
    flags: list[list[int]]
    limb_potentials: list[list[float]]
    node_potentials: list[list[float]]

    @property
    def sample_count(self) -> int:
        return len(self.sample_numbers)


@dataclass(frozen=True)
class NodeLabel:
    node_number: int
    node_120: bool
    node_352: bool
    mason_likar: bool
    precordial_leads: bool
    easi_leads: bool


def parse_superfile_text(text: str, source_name: str = "<memory>") -> SuperfileRecord:
    """Parse one Superfile text record into header, limb, flag, and node fields."""

    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        raise ValueError(f"{source_name}: empty Superfile record")

    header = _parse_header(lines[0], source_name)
    sample_numbers: list[int] = []
    flags: list[list[int]] = []
    limb_potentials: list[list[float]] = []
    node_potentials: list[list[float]] = []

    for line_number, line in enumerate(lines[1:], start=2):
        parts = line.split()
        if len(parts) != SAMPLE_FIELD_COUNT:
            raise ValueError(
                f"{source_name}:{line_number}: expected {SAMPLE_FIELD_COUNT} sample fields, "
                f"found {len(parts)}"
            )

        sample_numbers.append(int(parts[1]))
        flags.append([int(value) for value in parts[2:7]])
        limb_potentials.append([float(value) for value in parts[7:10]])
        node_potentials.append([float(value) for value in parts[10:]])

    return SuperfileRecord(
        source_name=source_name,
        header=header,
        sample_numbers=sample_numbers,
        flags=flags,
        limb_potentials=limb_potentials,
        node_potentials=node_potentials,
    )


def iter_superfile_records(path: str | Path, max_records: int | None = None):
    """Yield parsed Superfile records from a zip archive, directory, or single file."""

    source = Path(path)
    yielded = 0

    if source.is_file() and source.suffix.lower() == ".zip":
        with ZipFile(source) as archive:
            for member in sorted(_zip_superfile_members(archive)):
                if max_records is not None and yielded >= max_records:
                    return
                with archive.open(member) as handle:
                    text = handle.read().decode("utf-8", errors="replace")
                yield parse_superfile_text(text, member)
                yielded += 1
        return

    if source.is_dir():
        for file_path in _directory_superfile_paths(source):
            if max_records is not None and yielded >= max_records:
                return
            yield parse_superfile_text(file_path.read_text(encoding="utf-8"), str(file_path))
            yielded += 1
        return

    if source.is_file():
        yield parse_superfile_text(source.read_text(encoding="utf-8"), str(source))
        return

    raise FileNotFoundError(f"Superfile source not found: {source}")


def parse_node_label_xlsx(path: str | Path) -> list[NodeLabel]:
    """Parse the project node-label workbook without external spreadsheet dependencies."""

    workbook_path = Path(path)
    with ZipFile(workbook_path) as archive:
        sheet_path = _first_sheet_path(archive)
        shared_strings = _read_shared_strings(archive)
        rows = _read_xlsx_rows(archive, sheet_path, shared_strings)

    if not rows:
        raise ValueError(f"{workbook_path}: node-label workbook is empty")

    headers = rows[0]
    required = ["node_number", "node_120", "node_352", "mason_likar", "precordial_leads", "easi_leads"]
    if headers[: len(required)] != required:
        raise ValueError(f"{workbook_path}: unexpected node-label headers: {headers}")

    labels: list[NodeLabel] = []
    for row_number, row in enumerate(rows[1:], start=2):
        if not any(row):
            continue
        padded = [*row, *([""] * (len(required) - len(row)))]
        labels.append(
            NodeLabel(
                node_number=int(padded[0]),
                node_120=_xlsx_flag(padded[1]),
                node_352=_xlsx_flag(padded[2]),
                mason_likar=_xlsx_flag(padded[3]),
                precordial_leads=_xlsx_flag(padded[4]),
                easi_leads=_xlsx_flag(padded[5]),
            )
        )

        if labels[-1].node_number != len(labels) - 1:
            raise ValueError(
                f"{workbook_path}:{row_number}: expected 0-based node_number {len(labels) - 1}, "
                f"found {labels[-1].node_number}"
            )

    validate_node_labels(labels, source_name=str(workbook_path))
    return labels


def validate_node_labels(labels: list[NodeLabel], source_name: str = "node labels") -> None:
    if len(labels) != NODE_LABEL_ROW_COUNT:
        raise ValueError(f"{source_name}: expected {NODE_LABEL_ROW_COUNT} node-label rows, found {len(labels)}")
    node_numbers = [label.node_number for label in labels]
    if node_numbers != list(range(NODE_LABEL_ROW_COUNT)):
        raise ValueError(f"{source_name}: node_number must be contiguous 0-based indices 0..351")
    node_120_count = sum(label.node_120 for label in labels)
    node_352_count = sum(label.node_352 for label in labels)
    if node_120_count != 120:
        raise ValueError(f"{source_name}: expected exactly 120 node_120 flags, found {node_120_count}")
    if node_352_count != NODE_COUNT:
        raise ValueError(f"{source_name}: expected exactly {NODE_COUNT} node_352 flags, found {node_352_count}")


def node_indices(labels: list[NodeLabel], field: str) -> list[int]:
    """Return 0-based node indices whose boolean label field is true."""

    if field not in {"node_120", "node_352", "mason_likar", "precordial_leads", "easi_leads"}:
        raise ValueError(f"unknown node-label field: {field}")
    return [label.node_number for label in labels if bool(getattr(label, field))]


def extract_node_matrix(record: SuperfileRecord, node_numbers: list[int]) -> list[list[float]]:
    """Extract a [time, nodes] matrix from 0-based Superfile node indices."""

    for node_number in node_numbers:
        if node_number < 0 or node_number >= NODE_COUNT:
            raise ValueError(f"node index out of range: {node_number}")
    return [[row[node_number] for node_number in node_numbers] for row in record.node_potentials]


def build_sparse_reconstruction_batch(
    record: SuperfileRecord, input_node_numbers: list[int], target_node_numbers: list[int]
) -> dict[str, object]:
    """Build a small list-backed batch for sparse-k reconstruction smoke checks."""

    inputs = extract_node_matrix(record, input_node_numbers)
    targets = extract_node_matrix(record, target_node_numbers)
    return {
        "source_name": record.source_name,
        "input_node_numbers": input_node_numbers,
        "target_node_numbers": target_node_numbers,
        "inputs": inputs,
        "targets": targets,
        "input_shape": (record.sample_count, len(input_node_numbers)),
        "target_shape": (record.sample_count, len(target_node_numbers)),
    }


def derive_limb_leads(limb_potentials: list[list[float]]) -> dict[str, list[float]]:
    """Derive standard limb leads from RA, LA, and LL potentials."""

    lead_i: list[float] = []
    lead_ii: list[float] = []
    lead_iii: list[float] = []
    avr: list[float] = []
    avl: list[float] = []
    avf: list[float] = []

    for ra, la, ll in limb_potentials:
        i_value = la - ra
        ii_value = ll - ra
        iii_value = ll - la
        lead_i.append(i_value)
        lead_ii.append(ii_value)
        lead_iii.append(iii_value)
        avr.append(-(i_value + ii_value) / 2)
        avl.append((i_value - iii_value) / 2)
        avf.append((ii_value + iii_value) / 2)

    return {
        "I": lead_i,
        "II": lead_ii,
        "III": lead_iii,
        "aVR": avr,
        "aVL": avl,
        "aVF": avf,
    }


def derive_precordial_leads(node_potentials: list[list[float]]) -> dict[str, list[float]]:
    """Derive V1-V6 from one-based Superfile torso-node definitions."""

    leads = {"V1": [], "V2": [], "V3": [], "V4": [], "V5": [], "V6": []}
    for row in node_potentials:
        if len(row) != NODE_COUNT:
            raise ValueError(f"expected {NODE_COUNT} node potentials, found {len(row)}")
        leads["V1"].append(row[168])
        leads["V2"].append(row[170])
        leads["V3"].append((row[191] + row[192]) / 2)
        leads["V4"].append(row[215])
        leads["V5"].append((row[216] + 2 * row[217]) / 3)
        leads["V6"].append(row[218])
    return leads


def derive_12_lead(record: SuperfileRecord) -> dict[str, list[float]]:
    """Return derived standard 12-lead ECG traces for one Superfile record."""

    return {
        **derive_limb_leads(record.limb_potentials),
        **derive_precordial_leads(record.node_potentials),
    }


def audit_superfile_source(path: str | Path, max_records: int | None = None) -> dict[str, object]:
    """Compute a small structural audit for Superfile records."""

    record_count = 0
    sample_counts: list[int] = []
    intervals: set[float] = set()
    limb_min: float | None = None
    limb_max: float | None = None
    node_min: float | None = None
    node_max: float | None = None
    node_9999_count = 0
    node_minus_9999_count = 0
    first_record: str | None = None

    for record in iter_superfile_records(path, max_records=max_records):
        record_count += 1
        if first_record is None:
            first_record = record.source_name
        sample_counts.append(record.sample_count)
        intervals.add(record.header.sampling_interval_ms)

        flat_limb = [value for row in record.limb_potentials for value in row]
        flat_nodes = [value for row in record.node_potentials for value in row]
        node_9999_count += sum(1 for value in flat_nodes if value == 9999)
        node_minus_9999_count += sum(1 for value in flat_nodes if value == -9999)
        limb_min, limb_max = _update_range(limb_min, limb_max, flat_limb)
        node_min, node_max = _update_range(node_min, node_max, flat_nodes)

    return {
        "record_count": record_count,
        "first_record": first_record,
        "sampling_intervals_ms": sorted(intervals),
        "sample_count_min": min(sample_counts) if sample_counts else None,
        "sample_count_max": max(sample_counts) if sample_counts else None,
        "sample_count_mean": sum(sample_counts) / len(sample_counts) if sample_counts else None,
        "limb_potential_min": limb_min,
        "limb_potential_max": limb_max,
        "node_potential_min": node_min,
        "node_potential_max": node_max,
        "node_9999_count": node_9999_count,
        "node_minus_9999_count": node_minus_9999_count,
    }


def audit_superfile_records(path: str | Path, max_records: int | None = None) -> list[dict[str, object]]:
    """Return one structural audit row per parsed Superfile record."""

    rows: list[dict[str, object]] = []
    for record in iter_superfile_records(path, max_records=max_records):
        flat_limb = [value for row in record.limb_potentials for value in row]
        flat_nodes = [value for row in record.node_potentials for value in row]
        source_path = Path(record.source_name)
        filename_serial = _filename_serial(source_path.name)
        rows.append(
            {
                "source_name": record.source_name,
                "filename": source_path.name,
                "filename_serial": filename_serial,
                "header_serial": record.header.serial,
                "serial_matches_filename": filename_serial == record.header.serial if filename_serial is not None else "",
                "record_id": record.header.record_id,
                "sampling_interval_ms": record.header.sampling_interval_ms,
                "p_onset_ms": record.header.p_onset_ms,
                "p_offset_ms": record.header.p_offset_ms,
                "qrs_onset_ms": record.header.qrs_onset_ms,
                "qrs_offset_ms": record.header.qrs_offset_ms,
                "t_offset_ms": record.header.t_offset_ms,
                "sample_count": record.sample_count,
                "expected_sample_fields": SAMPLE_FIELD_COUNT,
                "malformed_row_count": 0,
                "limb_potential_min": min(flat_limb) if flat_limb else "",
                "limb_potential_max": max(flat_limb) if flat_limb else "",
                "node_potential_min": min(flat_nodes) if flat_nodes else "",
                "node_potential_max": max(flat_nodes) if flat_nodes else "",
                "node_9999_count": sum(1 for value in flat_nodes if value == 9999),
                "node_minus_9999_count": sum(1 for value in flat_nodes if value == -9999),
            }
        )
    return rows


def node_label_rows(labels: list[NodeLabel]) -> list[dict[str, object]]:
    """Convert parsed node labels into CSV-friendly dictionaries."""

    return [
        {
            "node_number": label.node_number,
            "node_1based": label.node_number + 1,
            "node_120": int(label.node_120),
            "node_352": int(label.node_352),
            "mason_likar": int(label.mason_likar),
            "precordial_leads": int(label.precordial_leads),
            "easi_leads": int(label.easi_leads),
        }
        for label in labels
    ]


def write_csv(path: str | Path, rows: list[dict[str, object]]) -> None:
    """Write dictionaries to CSV using a stable header from the first row."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        output_path.write_text("", encoding="utf-8")
        return
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _parse_header(line: str, source_name: str) -> SuperfileHeader:
    parts = line.split()
    if len(parts) != HEADER_FIELD_COUNT:
        raise ValueError(f"{source_name}: expected {HEADER_FIELD_COUNT} header fields, found {len(parts)}")

    return SuperfileHeader(
        serial=int(parts[0]),
        record_id=parts[1],
        sampling_interval_ms=float(parts[2]),
        p_onset_ms=float(parts[3]),
        p_offset_ms=float(parts[4]),
        qrs_onset_ms=float(parts[5]),
        qrs_offset_ms=float(parts[6]),
        t_offset_ms=float(parts[7]),
    )


def _zip_superfile_members(archive: ZipFile) -> list[str]:
    return [
        info.filename
        for info in archive.infolist()
        if not info.is_dir() and "/superfile/node" in info.filename and info.filename.endswith(".txt")
    ]


def _directory_superfile_paths(source: Path) -> list[Path]:
    direct = sorted(source.glob(DIRECT_SUPERFILE_GLOB))
    if direct:
        return direct
    return sorted(source.glob(SUPERFILE_GLOB))


def _update_range(
    current_min: float | None, current_max: float | None, values: list[float]
) -> tuple[float | None, float | None]:
    if not values:
        return current_min, current_max
    values_min = min(values)
    values_max = max(values)
    return (
        values_min if current_min is None else min(current_min, values_min),
        values_max if current_max is None else max(current_max, values_max),
    )


def _filename_serial(filename: str) -> int | None:
    if not filename.startswith("node") or not filename.endswith(".txt"):
        return None
    value = filename[4:-4]
    return int(value) if value.isdigit() else None


def _first_sheet_path(archive: ZipFile) -> str:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    rid_to_target = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}
    sheets = workbook.find("main:sheets", XLSX_NS)
    if sheets is None or not list(sheets):
        raise ValueError("node-label workbook contains no sheets")
    first_sheet = list(sheets)[0]
    rel_id = first_sheet.attrib[f"{{{XLSX_REL_NS}}}id"]
    target = rid_to_target[rel_id]
    return f"xl/{target}" if not target.startswith("/") else target.lstrip("/")


def _read_shared_strings(archive: ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    return [
        "".join(text.text or "" for text in item.findall(".//main:t", XLSX_NS))
        for item in root.findall("main:si", XLSX_NS)
    ]


def _read_xlsx_rows(archive: ZipFile, sheet_path: str, shared_strings: list[str]) -> list[list[str]]:
    root = ET.fromstring(archive.read(sheet_path))
    rows: list[list[str]] = []
    for row in root.findall(".//main:sheetData/main:row", XLSX_NS):
        cells: dict[int, str] = {}
        for cell in row.findall("main:c", XLSX_NS):
            cells[_column_index(cell.attrib["r"])] = _xlsx_cell_value(cell, shared_strings)
        if cells:
            rows.append([cells.get(index, "") for index in range(max(cells) + 1)])
    return rows


def _column_index(cell_ref: str) -> int:
    value = 0
    for char in "".join(character for character in cell_ref if character.isalpha()):
        value = value * 26 + ord(char.upper()) - 64
    return value - 1


def _xlsx_cell_value(cell: ET.Element, shared_strings: list[str]) -> str:
    value = cell.find("main:v", XLSX_NS)
    if value is None:
        return ""
    raw = value.text or ""
    if cell.attrib.get("t") == "s":
        return shared_strings[int(raw)]
    return raw


def _xlsx_flag(value: str) -> bool:
    return value.strip() not in {"", "0", "0.0"}
