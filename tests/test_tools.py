from __future__ import annotations

import base64
import subprocess
import sys
import tempfile
import unittest
import urllib.parse
import zlib
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_DIR / "scripts"


def run_script(name: str, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


class SkillToolTests(unittest.TestCase):
    def test_portability_check(self) -> None:
        result = run_script("check_portability.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_search_from_unrelated_working_directory(self) -> None:
        with tempfile.TemporaryDirectory(prefix="drawio skill test ") as directory:
            result = run_script(
                "search_shapes.py",
                "pod",
                "--library",
                "kubernetes",
                cwd=Path(directory),
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("kubernetes:pod", result.stdout)

    def test_material_icon_is_embeddable(self) -> None:
        result = run_script("material_icon.py", "analytics", "--data-uri")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        prefix, encoded = result.stdout.strip().split(",", 1)
        self.assertEqual(prefix, "data:image/svg+xml;base64")
        self.assertTrue(base64.b64decode(encoded).lstrip().startswith(b"<svg"))

    def test_uncompressed_starter_is_valid(self) -> None:
        starter = SKILL_DIR / "assets" / "templates" / "starter.drawio"
        result = run_script("validate_drawio.py", str(starter))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("VALID", result.stdout)

    def test_compressed_page_is_valid(self) -> None:
        graph = (
            '<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
            '<mxCell id="n" value="Node" vertex="1" parent="1">'
            '<mxGeometry x="0" y="0" width="100" height="40" as="geometry"/>'
            "</mxCell></root></mxGraphModel>"
        )
        encoded = urllib.parse.quote(graph, safe="~()*!.'")
        compressor = zlib.compressobj(wbits=-15)
        packed = compressor.compress(encoded.encode("utf-8")) + compressor.flush()
        payload = base64.b64encode(packed).decode("ascii")
        document = f'<mxfile><diagram name="Page-1">{payload}</diagram></mxfile>'
        with tempfile.TemporaryDirectory(prefix="drawio compressed test ") as directory:
            path = Path(directory) / "compressed.drawio"
            path.write_text(document, encoding="utf-8")
            result = run_script("validate_drawio.py", str(path))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_duplicate_id_is_rejected(self) -> None:
        document = (
            '<mxfile><diagram name="Page-1"><mxGraphModel><root>'
            '<mxCell id="0"/><mxCell id="1" parent="0"/><mxCell id="1" parent="0"/>'
            "</root></mxGraphModel></diagram></mxfile>"
        )
        with tempfile.TemporaryDirectory(prefix="drawio invalid test ") as directory:
            path = Path(directory) / "invalid.drawio"
            path.write_text(document, encoding="utf-8")
            result = run_script("validate_drawio.py", str(path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate cell id", result.stdout)


if __name__ == "__main__":
    unittest.main()
