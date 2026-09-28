# azbench leaderboard

Zero-shot, Azerbaijani, multiple choice, exact-letter scoring. Always giving the most common answer scores 27.9 % on belebele-az, 26.3 % on include-az and 42.7 % on tumlu-az, so read each column against that, not against 25 %.

| Model | Provider | belebele-az | include-az | tumlu-az | Mean |
|---|---|---:|---:|---:|---:|
| `qwen2.5:3b-instruct` | ollama | 45.2% (900) | 36.9% (548) | 36.0% (700) | **39.4%** |
| `aghasalim/siba-meristem-1.0:1.0.1` | ollama | 38.9% (900) | 40.0% (548) | 37.7% (700) | **38.9%** |
| `openai/gpt-oss-120b` | groq | 83.3% (114) | n/a | n/a | partial |
| `openai/gpt-oss-20b` | groq | 83.2% (101) | n/a | n/a | partial |
| `allam-2-7b` | groq | 25.2% (254) | n/a | n/a | partial |
| `qwen/qwen3.8-27b` | groq | 86.0% (143) | n/a | n/a | partial |
