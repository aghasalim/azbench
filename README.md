# azbench — the Azerbaijani LLM benchmark

Zero-shot, multiple-choice, scored by exact letter, prompts in Azerbaijani. Any OpenAI-compatible endpoint (Groq, OpenRouter, vLLM, Ollama).

| Task | Source | Items | What it measures |
|---|---|---|---|
| `belebele-az` | Meta Belebele, azj_Latn (human-translated) | 900 | reading comprehension |
| `include-az` | INCLUDE (Cohere/EPFL), real Azerbaijani academic and professional exam questions | 548 | regional knowledge |
| *planned* | AzerbaijaniMMLU, ARC_Azerbaijani, Azerbaijani_Hist_MC / Lang_MC (gated on HF) | | knowledge, science, history, language |
| *planned* | groundedness-az (SIBA) | | document-grounded answering |

```
pip install datasets
python -m azbench.run --models qwen/qwen3.8-27b,openai/gpt-oss-120b     # Groq
OPENAI_BASE_URL=http://localhost:11434/v1 python -m azbench.run --models meristem2   # Ollama
python -m azbench.table
```

Results are per-item JSON under `results/<provider>/`, resumable. Leaderboard: `LEADERBOARD.md`, later azbench.siba.az.

Aghasalim Mustafazada · SIBA, Baku · MIT
