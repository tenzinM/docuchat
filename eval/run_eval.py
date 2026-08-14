"""
Runs the eval_dataset.json questions against a running DocuChat backend,
then scores the results with RAGAS (faithfulness, answer relevancy, context precision).

Usage:
    1. Make sure the backend + Ollama are running (docker compose up).
    2. Upload your test document via the UI or:
       curl -X POST -F "file=@yourdoc.pdf" http://localhost:8000/upload
    3. Fill in eval_dataset.json with real question/ground_truth pairs.
    4. pip install -r requirements.txt
    5. python run_eval.py

Note: RAGAS's default metrics use an LLM-as-judge. By default this script points
that judge at the SAME local Ollama instance (see judge_llm below) so the whole
pipeline stays free/local - no OpenAI key required. Judge quality with small local
models is weaker than GPT-4-class judges, which is worth calling out honestly in
your README's eval section.
"""
import json
import requests
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from ragas.llms import LangchainLLMWrapper
from langchain_community.chat_models import ChatOllama

BACKEND_URL = "http://localhost:8000"


def load_dataset():
    with open("eval_dataset.json") as f:
        data = json.load(f)
    return data["examples"]


def run_queries(examples):
    rows = []
    for ex in examples:
        resp = requests.post(f"{BACKEND_URL}/query", json={"question": ex["question"]})
        resp.raise_for_status()
        result = resp.json()
        rows.append(
            {
                "question": ex["question"],
                "answer": result["answer"],
                "contexts": [s["text"] for s in result["sources"]] or [""],
                "ground_truth": ex["ground_truth"],
            }
        )
    return rows


def main():
    examples = load_dataset()
    rows = run_queries(examples)
    dataset = Dataset.from_list(rows)

    judge_llm = LangchainLLMWrapper(ChatOllama(model="llama3.1:8b", base_url="http://localhost:11434"))

    results = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision],
        llm=judge_llm,
    )

    df = results.to_pandas()
    print("\n=== Per-question results ===")
    print(df[["question", "faithfulness", "answer_relevancy", "context_precision"]].to_string(index=False))

    print("\n=== Averages (paste these into your README) ===")
    print(df[["faithfulness", "answer_relevancy", "context_precision"]].mean().to_string())

    df.to_csv("eval_results.csv", index=False)
    print("\nFull results saved to eval_results.csv")


if __name__ == "__main__":
    main()
