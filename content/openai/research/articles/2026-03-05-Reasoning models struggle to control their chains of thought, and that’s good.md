---
title: Reasoning models struggle to control their chains of thought, and that’s good
url: https://openai.com/index/reasoning-models-chain-of-thought-controllability
source: research
category: Research
published: '2026-03-05'
fetched: 2026-09-10 02:15
---

# Reasoning models struggle to control their chains of thought, and that’s good

Why a limitation of frontier models is reassuring for AI safety.

As AI agents become capable of carrying out increasingly complex and autonomous tasks, maintaining reliable oversight of their behavior becomes more important. Consistent with our principle of iterative deployment, we study how systems behave in real-world settings and continuously refine safeguards as capabilities advance. To support this, __our safety approach__ uses defense-in-depth, with multiple complementary layers of defense such as __safety training__, __behavioral testing__, __agentic code review__(opens in a new window), and  __chain-of-thought (CoT) monitoring__. CoT monitoring analyzes the reasoning steps agents generate while pursuing tasks. These reasoning traces can provide valuable signals during both training and deployment, helping monitoring systems identify when an agent’s behavior may be unsafe or inconsistent with the user’s intended goals.

Today, we find that models’ reasoning is generally interpretable and __easy to monitor__. However, in the future, monitorability may break down for __a variety of reasons__(opens in a new window). Here, we focus on one such path: if agents become capable of deliberately reshaping or obscuring their reasoning when they know they are being monitored, evaluations could overestimate a system’s alignment or safety, and monitoring systems could become less reliable.

In this work, we study whether current reasoning models are capable of controlling their chain of thought in ways that reduce monitorability. Understanding this capability is important for ensuring that CoT monitoring remains a robust safeguard as AI systems grow more capable. We find that current reasoning models struggle to control their CoTs, even when told they are being monitored. While controllability is higher for larger models, it decreases as models are asked to reason for longer and when they undergo additional post-training. Our results suggest that CoT controllability is unlikely to currently pose a major risk to CoT monitorability, though continued evaluation will be important as models advance.

Chain of thought refers to the intermediate reasoning steps an AI agent generates while solving a task. These reasoning traces can provide useful safety signals, helping monitoring systems assess whether an agent's behavior is safe or aligned.

CoT controllability is a reasoning model’s ability to control properties of its CoT in ways that reduce monitorability. Measuring this capability under the full breadth of realistic incentives to evade monitors we may expect in practice is challenging. Instead, we use a practical proxy: we measure the model's ability to follow user instructions about their CoT. For example, we test whether a model can follow instructions that affect its internal reasoning—such as using only lowercase letters, avoiding certain keywords, or adding specific phrases—rather than merely changing its visible output.

To study this, we introduce *CoT-Control*, an open-source evaluation suite for measuring CoT controllability of reasoning models. CoT-Control includes over 13,000 tasks built from established benchmarks:  GPQA, MMLU-Pro, HLE, BFCL and __SWE-Bench Verified__. Each task is created by pairing a benchmark problem with one CoT instruction such as avoiding certain problem-relevant keywords in CoT, using only lowercase letters, or appending a given word to each sentence.

We run evaluations on 13 reasoning models, and find that they all struggle to reliably control their CoTs. We measure controllability as a fraction of reasoning traces where the model successfully complies with our CoT instructions. Across frontier models, CoT controllability scores are low, ranging from 0.1% and not exceeding 15.4% for any current frontier model we tested.

This inability does not result from misunderstanding the task: models often recognize in their CoT that they’re failing to comply with the CoT instructions they were given and—even after this realization—still continue to fail. This surprisingly low performance is good news for CoT monitorability: it suggests models might similarly lack the ability to obfuscate their reasoning to evade our monitors.

### Examples of CoT controllability failures

Questions are paraphrased for brevity.

While we do see that controllability increases with model size, we also find that it quickly decreases with the amount of post-training and test-time compute. Looking across two families of open-weight models, larger models were somewhat better at controlling their chains of thought, though the effect tapered off at larger sizes. But when we let models think for longer, they became less able to control those chains of thought. We saw a similar trend for RL training of OLMo-3-7B-RL-Zero-Math: its controllability score dropped by more than a factor of ten over the course of training.

Controllability increases with scale in open-weight models but degrades with longer reasoning and more RL training.

To simulate realistic incentives to evade monitors, we measure controllability when models are told they’re being monitored or evaluated. This slightly (but noticeably) increases controllability. We also use automated prompt optimization to find prompts eliciting high controllability. While the optimizer can increase controllability on a training set, these gains transfer poorly to new instruction types (such as requiring no spaces between words).

The tasks in CoT-Control are practical proxies: an ideal CoT controllability evaluation would involve testing whether models that naturally pursue misaligned goals can control their CoT to evade monitoring. Instead, we estimate agents’ ability to control their CoTs by measuring their ability to follow instructions about their CoT. Moreover, models can control some features of their CoT better than others, and CoT-Control might be over- or underestimating controllability by measuring only a narrow set of controllability types.

Low CoT controllability is a feature, not a bug. Current reasoning models’ low controllability makes CoT monitoring more trustworthy as a safeguard. At the same time, we do not yet understand why current reasoning models’ controllability is low—or whether this property will persist as models become more capable. Therefore, CoT controllability evaluations can be seen as a canary eval: an early warning sign of whether models are getting better at shaping or hiding their reasoning.

Our results suggest that CoT controllability is unlikely to currently pose a major risk to CoT monitorability. However, low controllability is not sufficient on its own to guarantee high monitorability because monitorability could still degrade due to other mechanisms such as direct optimization pressure on CoTs.

To help track these dynamics over time, we are going to start reporting CoT controllability alongside __CoT monitorability__ in system cards for future frontier models, starting with GPT‑5.4 Thinking, building on our __ongoing commitment__ to not applying optimization pressure directly to the CoTs of frontier reasoning models.

## Authors

Tomek Korbak, Micah Carroll, Bowen Baker, Ian Kivlichan
