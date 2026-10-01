#!/usr/bin/env python3
"""Export the actual run's INCAR XML; do not use subsequently edited INCAR."""
from pathlib import Path
import xml.etree.ElementTree as ET
import re

for directory in ("scf", "bands"):
    folder = Path(directory)
    tree = ET.parse(folder / "vasprun.xml")
    incar = tree.getroot().find("incar")
    ET.ElementTree(incar).write(
        folder / "incar-run.xml", encoding="utf-8", xml_declaration=True
    )
    values = {}
    for node in incar:
        key = node.attrib["name"]
        value = " ".join((node.text or "").split())
        if key == "LREAL":
            value = value.split()[0]  # XML includes an echoed trailing comment
        values[key] = value
    # VASP 5.4.4 does not echo IVDW in <incar>; record resolved tags from OUTCAR/XML.
    outcar = (folder / "OUTCAR").read_text()
    match = re.search(r"(?m)^\s*IVDW\s*=\s*(\d+)", outcar)
    assert match, "Missing runtime IVDW record."
    values["IVDW"] = match[1]
    for key in ("NSW", "ISPIN", "LSORBIT", "LNONCOLLINEAR", "NBANDS", "NELECT", "NPAR"):
        values[key] = tree.getroot().find(f".//parameters//*[@name='{key}']").text.strip()
    text = (
        "# Reconstructed from this run's vasprun.xml and resolved OUTCAR tags; not the archived INCAR.\n"
        + "\n".join(f"{key} = {value}" for key, value in values.items()) + "\n"
    )
    (folder / "parameters-from-output.txt").write_text(text)
    print(f"{directory}: ENCUT={values['ENCUT']} eV; exported parameters-from-output.txt and incar-run.xml")
