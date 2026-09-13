"""Convert canonical STEP through a separate FreeCAD runtime and verify reopening."""

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def freecad_command() -> list[str]:
    """Prefer a configured/native FreeCADCmd; fall back to the installed Flatpak."""
    configured = os.environ.get("FREECAD_CMD")
    if configured:
        executable = shutil.which(configured)
        if not executable:
            raise RuntimeError(f"FREECAD_CMD executable does not exist: {configured}")
        return [executable]
    for name in ("FreeCADCmd", "freecadcmd", "freecadcmd-daily"):
        executable = shutil.which(name)
        if executable:
            return [executable]
    flatpak = shutil.which("flatpak")
    if flatpak:
        check = subprocess.run([flatpak, "info", "org.freecad.FreeCAD"], capture_output=True)
        if check.returncode == 0:
            return [flatpak, "run", "--command=FreeCADCmd", "org.freecad.FreeCAD"]
    raise RuntimeError(
        "FreeCADCmd not found. Install FreeCAD or set FREECAD_CMD to its executable."
    )


def convert_step(step: Path, output: Path, *, timeout: float = 180) -> Path:
    """Import STEP, save FCStd, reopen it, and write a verified JSON report beside it."""
    step, output = step.resolve(), output.resolve()
    if not step.is_file():
        raise FileNotFoundError(step)
    command = freecad_command()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".freecad-", dir=output.parent) as temporary:
        folder = Path(temporary)
        converted = folder / output.name
        report = folder / "reopen.json"
        worker = folder / "convert.py"
        shutil.copyfile(Path(__file__).with_name("freecad_worker.py"), worker)
        job = folder / "job.json"
        job.write_text(
            json.dumps({"step": str(step), "output": str(converted), "report": str(report)}),
            encoding="utf-8",
        )
        environment = dict(os.environ, FPV_FREECAD_JOB=str(job), QT_QPA_PLATFORM="offscreen")
        if "--command=FreeCADCmd" in command:
            # Flatpak isolates /tmp and only exposes explicitly granted document paths.
            command[2:2] = [
                f"--filesystem={step.parent}",
                f"--filesystem={folder}",
                f"--env=FPV_FREECAD_JOB={job}",
                "--env=QT_QPA_PLATFORM=offscreen",
            ]
        process = subprocess.run(
            command + [str(worker)],
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        if process.returncode or not converted.is_file() or not report.is_file():
            raise RuntimeError(
                f"FreeCAD conversion/reopen failed (exit {process.returncode}): "
                f"{process.stdout[-3000:]}\n{process.stderr[-3000:]}"
            )
        evidence = json.loads(report.read_text(encoding="utf-8"))
        if evidence.get("status") != "passed" or not evidence.get("reopened"):
            raise RuntimeError("FreeCAD did not verify the saved document")
        converted.replace(output)
        report.replace(output.with_suffix(".reopen.json"))
    return output
