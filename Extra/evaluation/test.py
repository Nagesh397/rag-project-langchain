import json
from pathlib import Path

from pydantic import BaseModel, Field

TEST_FILE = Path(__file__).parent / "tests.json"


class TestQuestion(BaseModel):
    """A golden question used for retrieval and answer evaluation."""

    question: str = Field(description="The question to ask the RAG system")
    keywords: list[str] = Field(default_factory=list, description="Terms expected in retrieved context")
    reference_answer: str = Field(description="The reference answer for this question")
    category: str = Field(description="Question category")
    expected_sources: list[str] = Field(default_factory=list, description="Expected source filenames")


def load_tests(path: Path | None = None) -> list[TestQuestion]:
    """Load the JSON golden dataset."""
    with (path or TEST_FILE).open("r", encoding="utf-8") as test_file:
        data = json.load(test_file)
    return [TestQuestion(**item) for item in data]
