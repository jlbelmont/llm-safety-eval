# Prior Work on Jailbreaks and Safety

- **Wei et al. (2023) — "Jailbreak: How Does LLM Safety Training Fail"**: Analyzes prompt-based jailbreaks and shows that safety fine-tuning can be brittle under adversarially crafted inputs, motivating systematic evaluation grids like ours.
- **Zou et al. (2023) — "Universal and Transferable Adversarial Attacks on Aligned Language Models"**: Introduces input-agnostic jailbreak prompts that transfer across models, underscoring the need for multi-model experiments and shared prompt suites.
- **Perez et al. (2022) — "Red Teaming Language Models with Language Models"**: Uses LLMs to automatically generate adversarial prompts, inspiring automated expansion of prompt categories and transforms.
- **Bai et al. (2022) — Constitutional AI**: Demonstrates safety alignment through rule-based self-critique; informs our use of safety-prefix transforms and refusal metrics.
- **OpenAI (2023) — GPT-4 Technical Report**: Documents safety training and remaining risk areas, motivating benchmarks that track partial vs. unsafe compliance.

These works collectively highlight how adversarial prompting can bypass guardrails, and they motivate measuring refusal consistency, partial compliance, and unsafe compliance across diverse models and strategies.
