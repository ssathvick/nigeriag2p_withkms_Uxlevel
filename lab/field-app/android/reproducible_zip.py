"""Canonical ZIP order/timestamps; Python zlib/toolchain versions are evidence inputs."""
import sys, zipfile
from pathlib import Path
mode, source, target = sys.argv[1:]
if mode == "classes":
    entries = {str(p.relative_to(source)).replace("\\", "/"): p.read_bytes() for p in Path(source).rglob("*.class")}
    output = Path(target)
else:
    with zipfile.ZipFile(source) as z:
        entries = {n: z.read(n) for n in z.namelist() if n != "classes.dex"}
    entries["classes.dex"] = Path(target).read_bytes()
    output = Path(source)
with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for name, data in sorted(entries.items()):
        info = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.create_system = 3
        info.external_attr = 0o100644 << 16
        z.writestr(info, data)
