"""Step 06: MAG quality assessment with CheckM2."""

from .models import Context, Sample
from .utils import cfg_path, ensure_inputs, q, require_tools, run_command


def run(ctx: Context, sample: Sample) -> None:
    """Assess SemiBin2 bins with CheckM2.

    Expected input:
        Result/binning/<sample>/semibin2/output_bins/*.fa.gz

    Outputs:
        Result/bin_quality/<sample>/checkm2/quality_report.tsv
        Result/bin_quality/<sample>/input_bins/*.fa
    """
    require_tools(["checkm2"])

    bins_dir = (
        ctx.result_dir
        / "binning"
        / sample.sample_id
        / "semibin2"
        / "output_bins"
    )
    checkm_db = cfg_path(ctx, "databases", "checkm2")

    ensure_inputs([bins_dir, checkm_db])

    outdir = ctx.result_dir / "bin_quality" / sample.sample_id
    input_bins = outdir / "input_bins"
    checkm_out = outdir / "checkm2"
    quality_report = checkm_out / "quality_report.tsv"

    threads = int(ctx.config["threads"].get("bin_quality", ctx.config["threads"]["binning"]))

    command = f"""
set -euo pipefail

mkdir -p {q(input_bins)} {q(checkm_out)}

# Remove stale decompressed bins from a previous run.
find {q(input_bins)} -maxdepth 1 -type f \
  \\( -name '*.fa' -o -name '*.fasta' -o -name '*.fna' \\) -delete

# SemiBin2 normally produces compressed FASTA files.
found=0
for src in {q(bins_dir)}/*.fa.gz {q(bins_dir)}/*.fasta.gz {q(bins_dir)}/*.fna.gz; do
    [ -e "$src" ] || continue
    found=1
    name=$(basename "$src" .gz)
    gzip -dc "$src" > {q(input_bins)}/"$name"
done

# Also accept uncompressed FASTA files.
for src in {q(bins_dir)}/*.fa {q(bins_dir)}/*.fasta {q(bins_dir)}/*.fna; do
    [ -e "$src" ] || continue
    found=1
    cp "$src" {q(input_bins)}/
done

if [ "$found" -eq 0 ]; then
    echo "No bin FASTA files found in {bins_dir}" >&2
    exit 1
fi

checkm2 predict \
  --input {q(input_bins)} \
  --output-directory {q(checkm_out)} \
  --threads {threads} \
  --database_path {q(checkm_db)} \
  --extension fa \
  --force
"""

    run_command(
        ctx,
        command,
        ctx.log_dir / sample.sample_id / "p06_bin_quality.log",
        [quality_report],
    )
