"""Step 05: metagenomic binning with SemiBin2."""

from .models import Context, Sample
from .utils import ensure_inputs, q, require_tools, run_command


def run(ctx: Context, sample: Sample) -> None:
    """Run SemiBin2 long-read binning for one sample.

    CheckM2 quality assessment is intentionally excluded from this step and
    should be run as a separate downstream module after bins are generated.
    """
    require_tools(["SemiBin2"])

    assembly_dir = ctx.result_dir / "assembly" / sample.sample_id
    assembly = assembly_dir / "assembly.fasta"
    bam = assembly_dir / "reads_to_contigs.bam"
    ensure_inputs([assembly, bam])

    outdir = ctx.result_dir / "binning" / sample.sample_id
    semibin_dir = outdir / "semibin2"
    completed = semibin_dir / ".completed"
    threads = int(ctx.config["threads"]["binning"])

    command = "\n".join([
        "set -euo pipefail",
        f"mkdir -p {q(semibin_dir)}",
        (
            f"SemiBin2 single_easy_bin "
            f"-i {q(assembly)} "
            f"-b {q(bam)} "
            f"-o {q(semibin_dir)} "
            f"--sequencing-type long_read "
            f"--threads {threads}"
        ),
        f"touch {q(completed)}",
    ])

    run_command(
        ctx,
        command,
        ctx.log_dir / sample.sample_id / "p05_binning.log",
        [completed],
    )
