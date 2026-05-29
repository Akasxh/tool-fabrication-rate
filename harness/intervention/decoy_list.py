"""C0.8 condition: RVR-format envelope listing a DECOY (wrong) tool set.

The format-not-content control. C0.8 reproduces the C1 (RVR) re-prompt prose
*verbatim* but substitutes a deterministically-generated list of tool names
that are guaranteed NOT to be in the registry. Holding the envelope format
identical to C1 and varying only the list *content* isolates the causal role
of the registry content:

  - If C0.8 (wrong list) recovers as well as C1 (real list) and C0.7 (no list),
    the registry content is decorative — the structured rejection envelope is
    the active ingredient ("format-not-content recovery").
  - If C0.8 fails where C1 succeeds, the model is genuinely reading and using
    the offered list — content matters.

Decoys are matched in count to the real registry (controls for list length)
and seeded by registry contents so reruns are reproducible.
"""
from __future__ import annotations

import hashlib
import random

from harness.types import Action, ActionKind, ToolCall

# Plausible-looking but generic verb_noun tool names to draw decoys from. If the
# registry is larger than this pool, we pad with deterministically generated
# names so the decoy list always matches the registry size.
_DECOY_POOL = [
    "query_database", "send_notification", "schedule_event", "fetch_record",
    "update_profile", "compute_metric", "render_report", "validate_input",
    "archive_item", "sync_state", "resolve_address", "encode_payload",
    "dispatch_job", "rotate_key", "merge_branches", "sample_dataset",
    "throttle_request", "checkpoint_model", "publish_topic", "drain_queue",
]


def _decoy_names(registry: dict[str, dict], k: int) -> list[str]:
    """Return ``k`` tool names not present in ``registry``, deterministic in
    the registry contents (so a given task always gets the same decoys)."""
    seed = int.from_bytes(
        hashlib.sha256("".join(sorted(registry)).encode()).digest()[:4], "big"
    )
    rng = random.Random(seed)
    pool = [d for d in _DECOY_POOL if d not in registry]
    rng.shuffle(pool)
    names: list[str] = []
    i = 0
    while len(names) < k:
        if pool:
            cand = pool.pop()
        else:
            cand = f"aux_op_{i}"
            i += 1
        if cand not in registry and cand not in names:
            names.append(cand)
    return sorted(names)


def decoy_list(parsed_calls: list[ToolCall], registry: dict[str, dict]) -> Action:
    """C0.8: RVR-format re-prompt whose available-tool list is DECOY (wrong)."""
    if not parsed_calls:
        return Action(kind=ActionKind.EXECUTE, tool_call=None)

    # Count-matched to the real registry so the only varied factor vs C1 is
    # whether the listed names are the true ones.
    decoys = _decoy_names(registry, max(1, len(registry)))
    for call in parsed_calls:
        if call.name not in registry:
            feedback = (
                f"Tool '{call.name}' is not in the registry.\n"
                f"Available tools: {decoys}.\n"
                f"Choose one of these or explain why none apply."
            )
            return Action(kind=ActionKind.RE_PROMPT, feedback=feedback)

    return Action(kind=ActionKind.EXECUTE, tool_call=parsed_calls[0])
