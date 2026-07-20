from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Sample:
    sample_id: str
    subject_id: str
    diet: str
    age_months: str
    timepoint: str
    batch: str
    fastq: Path


@dataclass
class Context:
    root: Path
    config: dict
    samples: dict[str, Sample]
    dry_run: bool = False
    force: bool = False

    @property
    def result_dir(self) -> Path:
        return self.root / self.config.get("result_dir", "Result")

    @property
    def log_dir(self) -> Path:
        return self.root / self.config.get("log_dir", "Logs")
