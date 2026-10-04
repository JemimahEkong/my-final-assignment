"""Your capstone agent: the one your README demos and your CI grades.

It starts as the final assignment's starter, unchanged: the same `YourAgent`,
the same `answer_question` pipeline from the course package, the same budget.
Calling it returns a `bootcamp_agent.schema.ResearchAnswer`, the contract the
whole course used, so everything you built in the sessions plugs in here.
`run(question)` returns the whole `AgentResult`, trace included, which is what
`uv run bootcamp capstone trace "<question>"` prints.

As shipped it is honest and insufficient. On the offline `FakeLLM` it refuses
what it should refuse and answers nothing else, and some contract tests in
`tests/test_contract.py` are marked as expected failures on purpose. Making them
pass is the work. What to add, session by session, is in `docs/` (each file
names the session that fills it).

The provider comes from `.env` (`BOOTCAMP_PROVIDER`), and falls back to the
offline `FakeLLM`. Keys live only in `.env`, which git ignores.
"""

from __future__ import annotations

import copy
import re
from pathlib import Path
import concurrent.futures

from bootcamp_agent.agent import AgentResult, answer_question
from bootcamp_agent.config import load_settings
from bootcamp_agent.documents import Document, load_corpus
from bootcamp_agent.llm import LLMClient, get_client
from bootcamp_agent.schema import ResearchAnswer
from bootcamp_agent.tools import Tool, build_tools

#: The six course documents, copied in by `bootcamp capstone new`. Versioned
#: input: nothing you build writes to it.
CORPUS_DIR = Path(__file__).resolve().parent / "data" / "corpus"

INJECTION_SHAPES = (
    r"ignore\s+(?:\w+\s+){0,3}instructions",
    r"disregard\s+(?:the\s+)?(?:above|previous|prior|earlier)",
    r"(?im)^(?:SYSTEM|assistant|developer):",
    r"(?i)(?:send|post|email|forward|leak|reveal).{0,40}(?:api key|token|secret|password|\.env)",
    r"(?i)you must now",
)


def _contains_injection(text: str) -> bool:
    return any(re.search(pattern, text) for pattern in INJECTION_SHAPES)

class MemoryStore:
    """Small per-user memory store with isolation and defensive copying."""

    def __init__(self) -> None:
        self._values: dict[tuple[str, str], object] = {}

    @staticmethod
    def _owner(user_id: str) -> str:
        if not isinstance(user_id, str) or not user_id.strip():
            raise ValueError(
                "user_id is required; a memory with no owner is everybody's memory"
            )
        return user_id

    def remember(self, user_id: str, key: str, value: object) -> None:
        owner = self._owner(user_id)
        self._values[(owner, key)] = copy.deepcopy(value)

    def recall(self, user_id: str, key: str) -> object | None:
        owner = self._owner(user_id)
        return copy.deepcopy(self._values.get((owner, key)))

class YourAgent:
    """The agent the tests and the grader run. Make it yours."""

    #: How long one provider call may take before the agent gives up with a
    #: flagged refusal. NOT ENFORCED YET: the starter waits for ever, which is
    #: why the `timeout` contract test is marked xfail. The test sets this low
    #: and expects an answer inside a second.
    timeout_s: float = 30.0

    def __init__(self, client: LLMClient | None = None) -> None:
        self.documents: list[Document] = load_corpus(CORPUS_DIR)
        self.client: LLMClient = client if client is not None else get_client(load_settings())
        # Every tool the agent can reach. Session 4's registry, read-only by
        # construction; session 12 has you classify each one, and the `tools`
        # contract test refuses anything not classified as a reader.
        self.tools: dict[str, Tool] = build_tools(self.documents, self.client)

    def run(self, question: str) -> AgentResult:
        """One question, answered or refused, with the trace of how."""
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        future = executor.submit(
            answer_question,
            question,
            self.documents,
            self.client,
            3,
            3,
        )

        try:
            result = future.result(timeout=self.timeout_s)

            if any(_contains_injection(document.text) for document in self.documents):
                result = AgentResult(
                    answer=ResearchAnswer(
                        answer=result.answer.answer,
                        citations=result.answer.citations,
                        confidence=min(result.answer.confidence, 0.2),
                        needs_human_review=True,
                    ),
                    trace=result.trace,
                )

            return result

        except concurrent.futures.TimeoutError:
            executor.shutdown(wait=False, cancel_futures=True)
            return AgentResult(
                answer=ResearchAnswer(
                    answer="I don't know based on the provided corpus.",
                    citations=(),
                    confidence=0.0,
                    needs_human_review=True,
                ),
                trace=(),
            )

        except Exception:
            executor.shutdown(wait=False, cancel_futures=True)
            return AgentResult(
                answer=ResearchAnswer(
                    answer="I don't know based on the provided corpus.",
                    citations=(),
                    confidence=0.0,
                    needs_human_review=True,
                ),
                trace=(),
            )

        finally:
            if not future.done():
                executor.shutdown(wait=False, cancel_futures=True)
            else:
                executor.shutdown(wait=True)

    def __call__(self, question: str) -> ResearchAnswer:
        return self.run(question).answer
