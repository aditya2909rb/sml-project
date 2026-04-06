from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any


@dataclass
class GMPBatchRecord:
    """Minimal GMP-style batch release record for research manufacturing readiness."""

    batch_id: str
    sample_id: str
    created_utc: str
    gc_content: float
    gc_window_pass: bool
    mrna_length: int
    sterility_check: str
    endotoxin_check: str
    identity_check: str
    release_status: str
    qa_signoff_required: bool
    traceability_hash: str


def build_gmp_batch_record(sample_id: str, mrna_construct: dict[str, Any]) -> dict[str, Any]:
    """Create a serializable GMP record from a designed mRNA construct."""
    sequence = str(mrna_construct.get("sequence", ""))
    gc_content = float(mrna_construct.get("gc_content", 0.0))
    mrna_length = int(mrna_construct.get("length", len(sequence)))

    gc_window_pass = 0.40 <= gc_content <= 0.60
    release_status = "CONDITIONAL_RELEASE" if gc_window_pass else "HOLD"

    timestamp = datetime.now(timezone.utc)
    batch_id = f"GMP-{sample_id}-{timestamp.strftime('%Y%m%d%H%M%S')}"
    traceability_hash = sha256(sequence.encode("utf-8")).hexdigest()

    record = GMPBatchRecord(
        batch_id=batch_id,
        sample_id=sample_id,
        created_utc=timestamp.isoformat(),
        gc_content=gc_content,
        gc_window_pass=gc_window_pass,
        mrna_length=mrna_length,
        sterility_check="PENDING",
        endotoxin_check="PENDING",
        identity_check="PASS" if sequence else "FAIL",
        release_status=release_status,
        qa_signoff_required=True,
        traceability_hash=traceability_hash,
    )
    return asdict(record)
