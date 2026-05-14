from pathlib import Path
from zipfile import ZipFile

from examples.bspm.bspm_harness.data.bspm_superfile import (
    NODE_COUNT,
    audit_superfile_source,
    build_sparse_reconstruction_batch,
    derive_12_lead,
    node_indices,
    parse_node_label_xlsx,
    parse_superfile_text,
)


def _sample_text() -> str:
    rows = []
    for sample_number in (1, 2):
        flags = [0, 0, 1, 1, 0]
        limb = [10 + sample_number, 20 + sample_number, 30 + sample_number]
        nodes = list(range(sample_number, sample_number + NODE_COUNT))
        values = [1, sample_number, *flags, *limb, *nodes]
        rows.append(" ".join(str(value) for value in values))
    return "\n".join(
        [
            "1 record001 2.0 100.0 210.0 268.0 372.0 693.0",
            *rows,
        ]
    )


def test_parse_superfile_text_splits_header_limb_and_nodes():
    record = parse_superfile_text(_sample_text(), "node0001.txt")

    assert record.header.sampling_interval_ms == 2.0
    assert record.sample_numbers == [1, 2]
    assert record.flags[0] == [0, 0, 1, 1, 0]
    assert record.limb_potentials[0] == [11.0, 21.0, 31.0]
    assert len(record.node_potentials[0]) == NODE_COUNT


def test_derive_12_lead_uses_limb_and_one_based_node_definitions():
    record = parse_superfile_text(_sample_text(), "node0001.txt")
    leads = derive_12_lead(record)

    assert leads["I"] == [10.0, 10.0]
    assert leads["II"] == [20.0, 20.0]
    assert leads["III"] == [10.0, 10.0]
    assert leads["V1"][0] == 169.0
    assert leads["V2"][0] == 171.0
    assert leads["V3"][0] == 192.5
    assert leads["V4"][0] == 216.0
    assert leads["V5"][0] == (217.0 + 2 * 218.0) / 3
    assert leads["V6"][0] == 219.0


def test_audit_superfile_source_reads_zip_archive(tmp_path: Path):
    archive_path = tmp_path / "bspm.zip"
    with ZipFile(archive_path, "w") as archive:
        archive.writestr("Dal_BSPM/892_BSPM/superfile/node0001.txt", _sample_text())

    summary = audit_superfile_source(archive_path)

    assert summary["record_count"] == 1
    assert summary["sample_count_min"] == 2
    assert summary["sampling_intervals_ms"] == [2.0]
    assert summary["node_potential_min"] == 1.0
    assert summary["node_9999_count"] == 0


def test_audit_superfile_source_reads_direct_superfile_directory(tmp_path: Path):
    superfile_dir = tmp_path / "superfile"
    superfile_dir.mkdir()
    (superfile_dir / "node0001.txt").write_text(_sample_text(), encoding="utf-8")

    summary = audit_superfile_source(superfile_dir)

    assert summary["record_count"] == 1
    assert summary["first_record"].endswith("node0001.txt")


def test_parse_node_label_xlsx_and_build_sparse_batch(tmp_path: Path):
    label_path = tmp_path / "node_label.xlsx"
    _write_node_label_xlsx(label_path)

    labels = parse_node_label_xlsx(label_path)
    input_universe = node_indices(labels, "node_120")
    target_352 = node_indices(labels, "node_352")
    record = parse_superfile_text(_sample_text(), "node0001.txt")

    batch_120 = build_sparse_reconstruction_batch(record, input_universe[:3], input_universe)
    batch_352 = build_sparse_reconstruction_batch(record, input_universe[:3], target_352)

    assert len(labels) == NODE_COUNT
    assert len(input_universe) == 120
    assert len(target_352) == NODE_COUNT
    assert batch_120["input_shape"] == (2, 3)
    assert batch_120["target_shape"] == (2, 120)
    assert batch_352["target_shape"] == (2, NODE_COUNT)


def _write_node_label_xlsx(path: Path) -> None:
    shared_strings = [
        "node_number",
        "node_120",
        "node_352",
        "mason_likar",
        "precordial_leads",
        "easi_leads",
    ]
    rows = [
        '<row r="1">'
        '<c r="A1" t="s"><v>0</v></c>'
        '<c r="B1" t="s"><v>1</v></c>'
        '<c r="C1" t="s"><v>2</v></c>'
        '<c r="D1" t="s"><v>3</v></c>'
        '<c r="E1" t="s"><v>4</v></c>'
        '<c r="F1" t="s"><v>5</v></c>'
        "</row>"
    ]
    for node_number in range(NODE_COUNT):
        row_number = node_number + 2
        cells = [f'<c r="A{row_number}"><v>{node_number}</v></c>']
        if node_number < 120:
            cells.append(f'<c r="B{row_number}"><v>1</v></c>')
        cells.append(f'<c r="C{row_number}"><v>1</v></c>')
        rows.append(f'<row r="{row_number}">{"".join(cells)}</row>')

    with ZipFile(path, "w") as archive:
        archive.writestr(
            "[Content_Types].xml",
            """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>
</Types>""",
        )
        archive.writestr(
            "_rels/.rels",
            """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>""",
        )
        archive.writestr(
            "xl/workbook.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets><sheet name="Sheet1" sheetId="1" r:id="rId1"/></sheets>
</workbook>""",
        )
        archive.writestr(
            "xl/_rels/workbook.xml.rels",
            """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>""",
        )
        archive.writestr(
            "xl/sharedStrings.xml",
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
            '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="6" uniqueCount="6">'
            + "".join(f"<si><t>{value}</t></si>" for value in shared_strings)
            + "</sst>",
        )
        archive.writestr(
            "xl/worksheets/sheet1.xml",
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            f"<sheetData>{''.join(rows)}</sheetData>"
            "</worksheet>",
        )
