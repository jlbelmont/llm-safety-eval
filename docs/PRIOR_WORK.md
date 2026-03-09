# Prior Work on Jailbreaks and Safety Evaluation

This repository is positioned as evaluation infrastructure, not as a new alignment method. The local references already collected for the project are useful for understanding why that distinction matters.

## Jailbreak and Adversarial Prompting

- **Wei et al. (2023), "Jailbreak: How Does LLM Safety Training Fail"** analyzes prompt-based failures in safety-trained systems and shows that alignment can be brittle under adversarially structured inputs. That result motivates keeping multiple prompt families in the evaluation suite instead of relying on a single attack template.
- **Zou et al. (2023), "Universal and Transferable Adversarial Attacks on Aligned Language Models"** demonstrates that some jailbreak prompts transfer across models. This is one reason the framework keeps model IDs, providers, and prompt categories separate in the experiment matrix: the same prompt family can be tested across heterogeneous backends.
- **Perez et al. (2022), "Red Teaming Language Models with Language Models"** motivates automated prompt expansion. The repository's prompt-generation support is intentionally simple for now, but it is designed to leave room for this style of automated adversarial input generation later.

## Alignment and Refusal Behavior

- **Bai et al. (2022), Constitutional AI** is relevant because it treats safety as behavior that can be shaped by explicit principles and self-critique. In this repository, transforms such as `safety_prefix` are not presented as a new defense, but they are useful experimental conditions for testing whether prompt framing changes refusal behavior.
- **OpenAI (2023), GPT-4 Technical Report** is relevant because it documents safety mitigations while still acknowledging residual risk. That is close to the motivation here: models may refuse some direct prompts while still partially complying under adversarial variants.

## Relevance to This Project

The common thread in these references is that safety evaluation needs to look beyond simple binary pass/fail outcomes. A model that refuses a direct request may still be vulnerable to decomposition, roleplay, or obfuscation. This repository focuses on measuring those shifts systematically. It does so by separating the prompt suite, experiment matrix, backend configuration, transforms, logging, human labels, and summary metrics into explicit components that can be inspected and reproduced.

The project therefore fits most naturally alongside jailbreak evaluation, red teaming, and safety benchmarking work. It is not claiming a new defense, a new alignment objective, or a new model architecture. Its contribution is the experimental framework needed to measure refusal, partial compliance, and unsafe compliance under controlled prompt variations.
