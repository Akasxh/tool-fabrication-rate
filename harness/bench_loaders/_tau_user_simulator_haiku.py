"""Override τ-bench's GPT-4o user simulator with Claude Haiku 4.5 (§8.9).
``HaikuUserSimulator`` drops in for ``BaseUserSimulationEnv``
(``reset``/``step``/``get_total_cost``) via the Anthropic SDK.
``patch_tau_bench_user_loader`` monkey-patches ``load_user`` so any
``MockRetailDomainEnv`` constructed afterwards uses Haiku regardless of args.
"""
from __future__ import annotations

import sys
from typing import Any, Optional

from harness.bench_loaders.tau_bench import USER_SIMULATOR_MODEL

# Reproduced verbatim from tau_bench/envs/user.py::LLMUserSimulationEnv.
_SYSTEM_PROMPT_TEMPLATE = """You are a user interacting with an agent.{instruction_display}
Rules:
- Just generate one line at a time to simulate the user's message.
- Do not give away all the instruction at once. Only provide the information that is necessary for the current step.
- Do not hallucinate information that is not provided in the instruction. For example, if the agent asks for the order id but it is not mentioned in the instruction, do not make up an order id, just say you do not remember or have it.
- If the instruction goal is satisified, generate '###STOP###' as a standalone message without anything else to end the conversation.
- Do not repeat the exact instruction in the conversation. Instead, use your own words to convey the same information.
- Try to make the conversation as natural as possible, and stick to the personalities in the instruction."""


class HaikuUserSimulator:
    """Anthropic-SDK replacement for τ-bench's LLM user simulator."""

    metadata: dict[str, Any] = {}

    def __init__(
        self,
        model: str = USER_SIMULATOR_MODEL,
        anthropic_client: Optional[Any] = None,
        max_tokens: int = 256,
    ) -> None:
        self.model = model
        self.max_tokens = max_tokens
        self._client = anthropic_client
        self._system: str = ""
        self._messages: list[dict[str, str]] = []
        self.total_cost: float = 0.0

    def _ensure_client(self) -> Any:
        if self._client is None:  # pragma: no cover — needs live creds
            import anthropic
            self._client = anthropic.Anthropic()
        return self._client

    def respond(self, conversation_so_far: list[dict[str, str]]) -> str:
        client = self._ensure_client()
        msgs = [m for m in conversation_so_far if m.get("role") != "system"]
        resp = client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=self._system or None,
            messages=msgs,
        )
        text_parts: list[str] = []
        for block in getattr(resp, "content", []) or []:
            txt = getattr(block, "text", None)
            if txt:
                text_parts.append(txt)
        out = "".join(text_parts).strip()
        usage = getattr(resp, "usage", None)
        if usage is not None:
            tin = getattr(usage, "input_tokens", 0) or 0
            tout = getattr(usage, "output_tokens", 0) or 0
            # Haiku 4.5 list price (HARNESS_SPEC §8.1): $1/M in, $5/M out.
            self.total_cost += tin * 1e-6 + tout * 5e-6
        self._messages.append({"role": "assistant", "content": out})
        return out

    def reset(self, instruction: Optional[str] = None) -> str:
        instruction_display = (
            ("\n\nInstruction: " + instruction + "\n") if instruction else ""
        )
        self._system = _SYSTEM_PROMPT_TEMPLATE.format(
            instruction_display=instruction_display
        )
        self._messages = [{"role": "user", "content": "Hi! How can I help you today?"}]
        return self.respond(self._messages)

    def step(self, content: str) -> str:
        self._messages.append({"role": "user", "content": content})
        return self.respond(self._messages)

    def get_total_cost(self) -> float:
        return self.total_cost


def patch_tau_bench_user_loader(anthropic_client: Optional[Any] = None) -> None:
    """Replace ``user.load_user`` and (if already bound) ``base.load_user``.
    Idempotent. ``base`` does ``from ... import load_user`` at import time, so
    rebinding only ``user.load_user`` would miss the already-bound symbol."""
    import tau_bench.envs.user as tb_user  # type: ignore[import-not-found]

    def _load_user(user_strategy, model=None, provider=None):  # type: ignore[no-untyped-def]
        return HaikuUserSimulator(
            model=USER_SIMULATOR_MODEL, anthropic_client=anthropic_client
        )

    tb_user.load_user = _load_user  # type: ignore[assignment]
    tb_base = sys.modules.get("tau_bench.envs.base")
    if tb_base is not None and hasattr(tb_base, "load_user"):
        tb_base.load_user = _load_user  # type: ignore[assignment]
