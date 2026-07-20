"""Step 15: generate a simple HTML report."""

from __future__ import annotations
import html

from .models import Context, Sample


def run(ctx: Context, sample: Sample) -> None:
    first = next(iter(ctx.samples))
    if sample.sample_id != first:
        return

    outdir = ctx.result_dir / "report"
    outdir.mkdir(parents=True, exist_ok=True)
    report = outdir / "index.html"

    rows = []
    for sample_id in ctx.samples:
        qc = ctx.result_dir / "qc" / sample_id / "seqkit_stats.tsv"
        host = ctx.result_dir / "host_removed" / f"{sample_id}.host_stats.tsv"
        assembly = ctx.result_dir / "assembly" / sample_id / "assembly.fasta"
        rows.append(
            f"<tr><td>{html.escape(sample_id)}</td>"
            f"<td>{'yes' if qc.exists() else 'no'}</td>"
            f"<td>{'yes' if host.exists() else 'no'}</td>"
            f"<td>{'yes' if assembly.exists() else 'no'}</td></tr>"
        )

    content = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Nanopore metagenome report</title>
<style>
body{{font-family:Arial,sans-serif;max-width:1100px;margin:40px auto;padding:0 20px}}
table{{border-collapse:collapse;width:100%}}
th,td{{border:1px solid #ddd;padding:8px;text-align:left}}
th{{background:#f3f3f3}}
</style>
</head>
<body>
<h1>Nanopore long-read metagenome report</h1>
<p>Samples: {len(ctx.samples)}</p>
<table>
<thead><tr><th>Sample</th><th>QC</th><th>Host removal</th><th>Assembly</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
</body>
</html>"""
    report.write_text(content, encoding="utf-8")
