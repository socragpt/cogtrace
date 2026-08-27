from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from cogtrace.backends import ChatRequest, OpenAICompatibleBackend


class _Response:
    def __init__(self, value: dict[str, object]) -> None:
        self.body = json.dumps(value).encode("utf-8")

    def __enter__(self) -> "_Response":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self.body


class OpenAICompatibleBackendTest(unittest.TestCase):
    def test_normalizes_reasoning_and_uses_current_vllm_schema_field(self) -> None:
        response = _Response(
            {
                "model": "fixture-live-model",
                "choices": [
                    {"message": {"content": '{"ok":true}', "reasoning": "brief"}}
                ],
                "usage": {"prompt_tokens": 3, "completion_tokens": 4},
            }
        )
        captured: dict[str, object] = {}

        def fake_urlopen(request: object, timeout: float) -> _Response:
            captured["body"] = json.loads(request.data.decode("utf-8"))  # type: ignore[attr-defined]
            captured["timeout"] = timeout
            return response

        backend = OpenAICompatibleBackend(
            base_url="http://127.0.0.1:8000/v1",
            model="fixture-live-model",
            supports_structured_outputs=True,
        )
        with patch("urllib.request.urlopen", fake_urlopen):
            generation = backend.generate(
                ChatRequest(
                    messages=({"role": "user", "content": "test"},),
                    seed=11,
                    json_schema={"type": "object"},
                )
            )

        self.assertEqual(generation.reasoning, "brief")
        self.assertEqual(generation.content, '{"ok":true}')
        self.assertEqual(generation.prompt_tokens, 3)
        self.assertEqual(
            captured["body"]["structured_outputs"],  # type: ignore[index]
            {"json": {"type": "object"}},
        )
        self.assertNotIn("guided_json", captured["body"])  # type: ignore[operator]


if __name__ == "__main__":
    unittest.main()
