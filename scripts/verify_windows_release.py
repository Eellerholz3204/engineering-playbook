"""Exercise a ZIP after relocation, with Python and Git removed from PATH."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
import zipfile


def verify(archive: Path, graphical: bool):
    with tempfile.TemporaryDirectory(prefix="Repository Builder relocated ") as temporary:
        folder = Path(temporary)
        with zipfile.ZipFile(archive) as zip_file:
            for entry in zip_file.infolist():
                if not (folder / entry.filename).resolve().is_relative_to(folder.resolve()):
                    raise ValueError("Unsafe archive entry.")
            zip_file.extractall(folder)
        bundle = next(p for p in folder.iterdir() if p.is_dir())
        runtime = bundle / "_runtime/RepositoryBuilder.Runtime.exe"
        environment = {**os.environ, "PATH": os.pathsep.join([
            str(Path(os.environ["WINDIR"]) / "System32"),
            str(Path(os.environ["WINDIR"]) / "System32/WindowsPowerShell/v1.0")])}
        report = folder / "self-test.json"
        subprocess.run([str(runtime), "--self-test", str(report)], env=environment, cwd=folder, check=True, timeout=120)
        result = json.loads(report.read_text())
        if not result["success"] or not Path(result["resource_root"]).is_relative_to(bundle):
            raise RuntimeError("Relocated package did not use its bundled playbook.")
        if graphical:
            screenshots = folder / "screenshots"
            subprocess.run([str(runtime), "--smoke-test", str(screenshots)], env=environment, cwd=folder, check=True, timeout=120)
            if not json.loads((screenshots / "result.json").read_text())["success"]:
                raise RuntimeError("Packaged desktop creation failed.")
            # Retain screenshots as review evidence outside the disposable package.
            import shutil
            evidence = Path(__file__).resolve().parents[1] / ".builder-qa/release"
            evidence.mkdir(parents=True, exist_ok=True)
            for path in screenshots.iterdir():
                shutil.copy2(path, evidence / path.name)
        print("PASS: relocated package creates repositories without Python or Git on PATH.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--graphical", action="store_true")
    args = parser.parse_args()
    verify(args.archive.resolve(), args.graphical)
