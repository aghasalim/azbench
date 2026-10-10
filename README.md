# azbench, the Azerbaijani LLM benchmark

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23003616.svg)](https://doi.org/10.5281/zenodo.23003616)

I wanted a simple way to check how well LLMs handle Azerbaijani, so I put this together. Every task is zero-shot multiple choice with the prompt in Azerbaijani, and I score the answer by its exact letter. The questions are on Hugging Face as [aghasalim/azbench](https://huggingface.co/datasets/aghasalim/azbench), one config per source, and `python -m azbench.export_hf` rebuilds them. It runs against any OpenAI-compatible endpoint, so Groq, OpenRouter, vLLM and Ollama all work.

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

Results go to per-item JSON under `results/<provider>/`, so a run can pick up where it stopped. The leaderboard is in `LEADERBOARD.md`. Watch out for the chance level. It isn't 25 % on every task, and on tumlu-az you get 42.7 % just by always answering D.

My first complete runs compared two 3B models at Q4_K_M through Ollama ([`results/ollama/`](results/ollama/)). One is my SIBA Meristem 1.0.1 fine-tune and the other is its base model, Qwen2.5-3B-Instruct. On include-az the fine-tune got 40.0 % and the base got 36.9 %. On belebele-az it went the other way, 38.9 % against 45.2 %, so my fine-tuning hurt reading comprehension. Neither model beat always answering D on tumlu-az (42.7 %). I lost the per-question files for these two runs on the GPU pod, so I only have the totals.

The three tasks also run on Kaggle Benchmarks. They use the [Kaggle copy of the dataset](https://www.kaggle.com/datasets/aghasalimmustafazada/azbench) with the same prompts and scoring. I wanted to know how much a score moves between runs, so I ran Gemini 3.7 Flash three times there at temperature 0. Across the three runs it got 835, 840 and 838 of 900 belebele-az; 473, 476 and 476 of 548 include-az; 660, 658 and 658 of 700 tumlu-az right. The largest spread is 5 of 900, which is about 0.6 points. If two models are closer than that on a task, I wouldn't call either one better. The answers behind these counts are in [`results/kaggle/`](results/kaggle/). Running `python -m azbench.kaggle_repeats check` recomputes them and fails if this paragraph disagrees.

Aghasalim Mustafazada · SIBA, Baku · MIT
