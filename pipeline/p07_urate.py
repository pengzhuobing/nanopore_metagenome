"""Step 07: urate-pathway protein detection."""

from .models import Context, Sample
from .utils import cfg_path, ensure_inputs, q, require_tools, run_command


def run(ctx: Context, sample: Sample) -> None:
    require_tools(["diamond"])

    proteins = ctx.result_dir / "annotation" / sample.sample_id / "bakta" / f"{sample.sample_id}.faa"
    refs = cfg_path(ctx, "references", "urate_proteins")
    ensure_inputs([proteins, refs])

    outdir = ctx.result_dir / "urate"
    db = outdir / "urate_db"
    hits = outdir / f"{sample.sample_id}.urate_hits.tsv"
    threads = int(ctx.config["threads"]["annotation"])
    params = ctx.config["urate"]

    command = f"""
set -euo pipefail
mkdir -p {q(outdir)}
if [ ! -f {q(str(db) + ".dmnd")} ]; then
  diamond makedb --in {q(refs)} --db {q(db)}
fi
diamond blastp --query {q(proteins)} --db {q(db)} --out {q(hits)} \
  --outfmt 6 qseqid sseqid pident length qlen slen evalue bitscore qcovhsp scovhsp \
  --id {params["min_identity"]} \
  --query-cover {params["min_query_coverage"]} \
  --subject-cover {params["min_subject_coverage"]} \
  --threads {threads}
"""
    run_command(ctx, command, ctx.log_dir / sample.sample_id / "p07_urate.log",
                [hits])
