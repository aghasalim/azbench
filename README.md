# azbench, the Azerbaijani LLM benchmark

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23003616.svg)](https://doi.org/10.5281/zenodo.23003616)

Zero-shot, multiple-choice, scored by exact letter, prompts in Azerbaijani. The questions are on Hugging Face as [aghasalim/azbench](https://huggingface.co/datasets/aghasalim/azbench), one config per source, rebuilt with `python -m azbench.export_hf`. Any OpenAI-compatible endpoint (Groq, OpenRouter, vLLM, Ollama).

| Task | Source | Items | What it measures |
|---|---|---|---|
| `belebele-az` | Meta Belebele, azj_Latn (human-translated) | 900 | reading comprehension |
| `include-az` | INCLUDE (Cohere/EPFL), real Azerbaijani academic and professional exam questions | 548 | regional knowledge |
| `tumlu-az` | TUMLU-mini (Isbarov et al. 2025), native Azerbaijani school-exam questions, 4-choice | 700 | school knowledge across subjects |
| *pending approval* | AzerbaijaniMMLU, ARC_Azerbaijani, Azerbaijani_Hist_MC / Lang_MC (gated on HF) | | knowledge, science, history, language |
| *planned* | groundedness-az (SIBA) | | document-grounded answering |

```
pip install datasets
python -m azbench.run --models qwen/qwen3.8-27b,openai/gpt-oss-120b     # Groq
OPENAI_BASE_URL=http://localhost:11434/v1 python -m azbench.run --models meristem2   # Ollama
python -m azbench.table
```

Results are per-item JSON under `results/<provider>/`, resumable. Leaderboard: `LEADERBOARD.md`. Chance is not 25 % everywhere: always answering D scores 42.7 % on tumlu-az.

First complete runs, both 3B models at Q4_K_M through Ollama ([`results/ollama/`](results/ollama/)): my SIBA Meristem 1.0.1 fine-tune scores 40.0 % on include-az against 36.9 % for its base model Qwen2.5-3B-Instruct, but 38.9 % on belebele-az against 45.2 %, so the fine-tune cost reading comprehension. On tumlu-az both sit below the 42.7 % of always answering D. The per-question files for these two runs were lost on the GPU pod, so only the totals are kept.

The three tasks also run on Kaggle Benchmarks, from the [Kaggle copy of the dataset](https://www.kaggle.com/datasets/aghasalimmustafazada/azbench) with the same prompts and scoring. Gemini 3.7 Flash ran three times there at temperature 0 and answered 835, 840 and 838 of 900 belebele-az; 473, 476 and 476 of 548 include-az; 660, 658 and 658 of 700 tumlu-az correctly. The largest spread is 5 of 900, about 0.6 points, so two models closer than that on one task are within what a single model does from run to run. The answers behind these counts are in [`results/kaggle/`](results/kaggle/), and `python -m azbench.kaggle_repeats check` recomputes them and fails if this paragraph disagrees.

Aghasalim Mustafazada · SIBA, Baku · MIT
