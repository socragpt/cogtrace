"""Provider-neutral model backends for CogTrace pilot experiments."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol


class BackendError(RuntimeError):
    """Raised when a generation backend cannot complete a request."""


@dataclass(frozen=True)
class ChatRequest:
    """One model generation request.

    ``json_schema`` refers to the vLLM-compatible final-output constraint. It
    does not imply that the model's private or emitted reasoning was constrained.
    """

    messages: tuple[Mapping[str, str], ...]
    seed: int
    temperature: float = 0.0
    max_tokens: int = 2048
    json_schema: Mapping[str, Any] | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Generation:
    """Normalized output from a chat-completions-style backend."""

    content: str
    reasoning: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float
    model: str


class ModelBackend(Protocol):
    """Small interface shared by live and deterministic pilot backends."""

    name: str
    supports_structured_outputs: bool

    def generate(self, request: ChatRequest) -> Generation:
        ...


class OpenAICompatibleBackend:
    """Standard-library client for a local vLLM-style chat endpoint."""

    name = "openai-compatible"

    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        api_key: str = "EMPTY",
        timeout_seconds: float = 180.0,
        supports_structured_outputs: bool = False,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self.model = model
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.supports_structured_outputs = supports_structured_outputs
        normalized = base_url.rstrip("/")
        if normalized.endswith("/chat/completions"):
            self.endpoint = normalized
        elif normalized.endswith("/v1"):
            self.endpoint = normalized + "/chat/completions"
        else:
            self.endpoint = normalized + "/v1/chat/completions"

    def generate(self, request: ChatRequest) -> Generation:
        if request.json_schema is not None and not self.supports_structured_outputs:
            raise BackendError(
                "backend was not declared to support guided JSON output"
            )

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [dict(message) for message in request.messages],
            "temperature": request.temperature,
            "seed": request.seed,
            "max_tokens": request.max_tokens,
        }
        if request.json_schema is not None:
            payload["structured_outputs"] = {"json": dict(request.json_schema)}

        body = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        http_request = urllib.request.Request(
            self.endpoint,
            data=body,
            headers=headers,
            method="POST",
        )

        started = time.perf_counter()
        try:
            with urllib.request.urlopen(
                http_request, timeout=self.timeout_seconds
            ) as response:
                response_value = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise BackendError(f"backend returned HTTP {error.code}: {detail}") from error
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
            raise BackendError(f"backend request failed: {error}") from error
        latency_ms = (time.perf_counter() - started) * 1000

        try:
            message = response_value["choices"][0]["message"]
        except (KeyError, IndexError, TypeError) as error:
            raise BackendError("backend response has no chat message") from error

        content = message.get("content") or ""
        reasoning = (
            message.get("reasoning_content")
            or message.get("reasoning")
            or message.get("analysis")
            or ""
        )
        usage = response_value.get("usage") or {}
        return Generation(
            content=str(content),
            reasoning=str(reasoning),
            prompt_tokens=int(usage.get("prompt_tokens") or 0),
            completion_tokens=int(usage.get("completion_tokens") or 0),
            latency_ms=latency_ms,
            model=str(response_value.get("model") or self.model),
        )


class FixtureBackend:
    """Deterministic backend for testing the full pilot without a model."""

    name = "fixture"
    supports_structured_outputs = True

    def __init__(self, fixtures: Mapping[str, Mapping[str, Any]]) -> None:
        self.fixtures = fixtures

    def generate(self, request: ChatRequest) -> Generation:
        task_id = str(request.metadata.get("task_id") or "")
        phase = str(request.metadata.get("phase") or "")
        fixture = self.fixtures.get(task_id)
        if fixture is None:
            raise BackendError(f"fixture task {task_id!r} is not defined")

        events = fixture.get("structured_events") or []
        reasoning = ""
        content = str(fixture.get("final_output") or "")
        if phase == "unrestricted":
            reasoning = str(fixture.get("unrestricted_reasoning") or "")
        elif phase == "translate":
            content = json.dumps(events, separators=(",", ":"))
        elif phase == "prompt_structured":
            reasoning = "\n".join(
                json.dumps(event, separators=(",", ":")) for event in events
            )
        elif phase == "checkpoint":
            step = int(request.metadata.get("step") or 0)
            if step >= len(events):
                raise BackendError(f"fixture task {task_id!r} has no checkpoint {step}")
            content = json.dumps(events[step], separators=(",", ":"))
            reasoning = "Select the next typed checkpoint."
        else:
            raise BackendError(f"unknown fixture phase {phase!r}")

        prompt_chars = sum(len(message.get("content", "")) for message in request.messages)
        completion_chars = len(content) + len(reasoning)
        return Generation(
            content=content,
            reasoning=reasoning,
            prompt_tokens=max(1, prompt_chars // 4),
            completion_tokens=max(1, completion_chars // 4),
            latency_ms=1.0,
            model="fixture-model",
        )
