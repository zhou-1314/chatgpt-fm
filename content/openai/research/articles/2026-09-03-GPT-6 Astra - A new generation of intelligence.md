---
title: 'GPT-6 Astra: A new generation of intelligence'
url: https://openai.com/index/gpt-6-astra
source: research
category: Research
published: '2026-09-03'
fetched: 2026-09-09 18:41
---

## A new generation of intelligence

We’re introducing GPT‑6 Astra, the world’s most intelligent and aligned model.

GPT‑6 Astra brings together years of research and big bets across pre-training, reinforcement learning, and alignment. Astra is state-of-the-art on computer use, browsing, software engineering, cybersecurity, science, and professional work. Astra saturates FrontierMath Tier 4 with a 98% score, having already helped __solve long-standing open problems__ in mathematics. Astra also saturates ARC-AGI-3 with a 99.9% score and ExploitBench with a 100% score. It also sets a new frontier on computer and browser use, handling the most demanding professional work with unmatched speed, accuracy, and judgment.

GPT‑6 Astra is rolling out today to a limited set of organizations and over the coming days will become available to all ChatGPT Plus, Pro, Business, and Enterprise users, as well as through the OpenAI API, Microsoft Azure, and AWS Bedrock.

Astra is our most aligned model, with substantial improvements in understanding user intent and model behavior—you can delegate tasks with greater confidence in Astra’s judgment. As one way that we test this, we built a new evaluation informed by the Hugging Face incident that evaluates whether a model facing a difficult or impossible task will go beyond its intended scope. Compared to GPT‑5.6 Sol, which without production safeguards went beyond the authorized target 48% of the time, GPT‑6 Astra did this in 0% of cases.

## The world’s best computer use model

GPT‑6 Astra marks a new frontier in the speed, accuracy, and safety of computer use. It can take care of tedious tasks like filling out online forms, updating customer records in a CRM, and organizing your calendar. It can conduct online research and draft summaries in your email or in your document editor. It can analyze scientific data, generate plots, create a website, and run frontend QA checks to make sure all the features on that site work. It can help you autonomously install and test software, and troubleshoot problems you see on screen. These improvements are also reflected in our state-of-the-art evaluation results.

These improvements also result in significant efficiency gains in real knowledge-work tasks. In latency simulations on OSWorld 2.0, Astra achieves higher computer-use performance in about 47% less time per task than GPT‑5.6 Sol, scoring 72.6% at roughly 40 minutes per task, compared with 65.7% at roughly 75 minutes.<sup>3</sup>

GPT‑6 Astra’s computer-use capabilities can be seen in outputs across domains, including game development, electrical engineering, and everyday knowledge work:

Alongside Astra, we are also updating the Codex harness to significantly improve the speed of computer use. Combined with Astra’s efficiency, this translates to a 1.9x faster task completion compared to the current GPT‑5.6 Sol experience, on the Mind2Web benchmark. The model’s improvements on speed mean it can take on many time-consuming life tasks for you, faster than you can.<sup>4</sup>

## A step change in professional work

GPT‑6 Astra pairs advances in computer use with targeted training for professional environments, to help tackle complex work tasks. It combines the intelligence required for complex problems with the ability to carry out multistep workflows and produce polished documents, spreadsheets, and presentations.

GPT‑6 Astra is our best model for adhering to existing templates and producing slides that are well laid out and succinctly convey key points with a structured narrative. It creates clear, well-structured documents, presentations, spreadsheets, and analyses that follow your templates and match your writing and visual style. Astra is also trained to specifically pull only the context that matters into outputs, instead of repeating information unnecessary for the work at hand. All this means it can output more immediately usable artifacts that match your business context and standards.

GPT‑6 Astra also brings stronger visual judgment to the websites, games, applications, and renderings it builds. With __Sites__(opens in a new window) in ChatGPT, Astra can create, host, and share websites, web apps, and games directly from a prompt.

When instructions leave room for interpretation, GPT‑6 Astra is better than previous models at making the right call. It uses context to fill in routine gaps and asks focused questions when the answer could change the outcome. In Codex, it can ask asynchronously while continuing work that doesn’t depend on your reply. If you don’t respond, it proceeds with sensible assumptions where appropriate, but waits for your input on consequential decisions.

The examples below show how Astra collaborates on everyday tasks where missing information can materially change the answer.

Astra is also better at staying oriented as a task evolves. Earlier models sometimes treated steering messages as a new goal, losing track of the original request or earlier constraints. Astra incorporates new requirements, changes course when asked, and answers side questions without dropping the broader task.

## Coding

GPT‑6 Astra is the best model for software engineering to date.

With Astra, we’re introducing a new way for Codex to preserve and retrieve context when the context window fills. Historically, models have used compaction to summarize work during long sessions, such as when debugging complex issues or tackling large refactors. Each compaction can leave out details about why a fix failed or how a component behaves. In Codex, Astra can keep notes across context windows, preserving accumulated details without repeatedly compressing them into a single summary. Earlier context windows remain searchable, so Astra can find requirements or test results from previous messages and tool outputs—even if that information wasn’t captured in its notes. You can enable this experimental feature in your Codex config.toml,(opens in a new window) and it will become the default for Astra in the coming weeks.

## Advancing scientific discovery

Astra can help with the practical work behind scientific discovery. By combining scientific reasoning with computer use, it can work directly in specialized software to inspect data and explore results, helping researchers assess the evidence and decide what to investigate next.

## Cybersecurity

As we discussed in our __safety update__, Astra is a significant jump in cyber capabilities and meets the __Critical threshold__ in cybersecurity under our __Preparedness Framework__. Its ability to identify and develop zero-day exploits can help defenders find and patch weaknesses, but it also creates a need for stronger safeguards. To understand how far these capabilities extend, we ran Astra on internal and third-party expert evaluations.

We first tested the model without production safeguards on ExploitBench and ExploitGym, which evaluate whether models can turn known software vulnerabilities into working exploits. On ExploitBench, Astra achieved a perfect score of 100%, compared with 78.5% for GPT‑5.6 Sol, our previous frontier cyber-capable model. On ExploitGym, Astra reached a 42.4% success rate, compared with 30.3% for GPT‑5.6 Sol, while using substantially fewer output tokens.<sup>13</sup>

Given concerns that exposure to historical software vulnerabilities may have affected benchmark results, we also evaluated Astra on two novel benchmarks. For one, we built an internal “ExploitBench (June–August 2026)” evaluation to test exploit development using vulnerabilities from the previous three months.<sup><sup>14</sup></sup> Astra achieved substantially higher arbitrary code-execution rates than GPT‑5.6 Sol on this dataset while using far fewer output tokens. During the evaluation, Astra even discovered and used two previously unknown zero-day vulnerabilities. We are disclosing both vulnerabilities to their maintainers.

We also tested Astra on SRE-Bench<sup><sup>15</sup></sup>, a benchmark that measures whether models can reverse engineer software binaries to understand its core logic without access to raw source code. Astra solved 88.0% of tasks in a single attempt and 99.2% within four attempts, compared with 55.9% and 68.7% for GPT‑5.6 Sol, respectively.

Beyond benchmarks, expert-led assessments found that Astra, when run without production safeguards, could use previously unknown vulnerabilities to achieve arbitrary code execution in hardened browsers and create privilege-escalation exploits for hardened operating-systems.

As we discussed in __The Defender’s Window__, frontier cyber capabilities can help defenders find weaknesses faster, but they also make those weaknesses easier to exploit, raising the urgency for defenders to adapt. With the version of Astra launching today, defenders can use it to complete tasks such as secure code review and patching.

However, Astra will refuse to comply with more advanced cybersecurity tasks such as creating proof-of-concept exploits for vulnerabilities. Through __OpenAI Daybreak__, we plan to expand access and roll out less restrictive safeguards in the coming weeks. This will enable more defensive workflows, including vulnerability and proof-of-concept validation, malware analysis, and detection engineering.

We have also strengthened our protections against potential cyber misuse, building upon our safeguards stack for GPT‑5.6 Sol. These include stronger model robustness to better withstand potential jailbreaks and more context for our monitoring systems. We have continued rigorous internal and external testing, including automated evaluations with our __internal red-teaming attackers__. More details about our cyber safeguards and testing are available in the Astra safety overview and system card(opens in a new window)..

## Aligning and deploying GPT‑6 Astra responsibly

Astra is our most aligned model. Astra excels at exercising care, respecting task boundaries, and communicating transparently. This work is the latest product of our long-running research program focused on training models that remain aligned with human intent from start to finish.

In sensitive environments, Astra proceeds with care commensurate with its risk. In an evaluation of computer use tasks adversarially selected to elicit misbehavior, Astra was more successful at avoiding unintended consequences. Running with additional security measures offered by default yielded even stronger performance.

Astra is also more likely to operate within the boundaries set by the user and implied by its environment. In an internal evaluation, Astra never attempted to circumvent a Codex Auto-Review denial. This held even when Auto-review was deliberately configured to be evadable and the task was impossible to complete otherwise. This respect for the environment restrictions is consistent with the results of our impossible cyber task evaluation that we shared in the intro of this post and other findings documented in our system card(opens in a new window).

Astra additionally sets new marks in transparent user communication. In one evaluation, Astra is three times less likely than GPT‑5.6 Sol to make inaccurate representations about its capabilities and affordances.

Our evaluations found Astra’s written reasoning harder to monitor than GPT‑5.6 Sol’s, based on tests that explicitly asked it to evade monitoring. We attribute this to Astra’s greater control over written reasoning on simpler tasks and ability to solve problems with fewer written steps. Astra still appears to struggle to conceal the reasoning needed for complex tasks, but we take the decline seriously. Improving monitorability remains a research priority, and the accompanying __system card__(opens in a new window) details our findings and ongoing work.

Alignment training is core to our approach to deployment. As an additional layer of defenses, we also build system safeguards like Codex __Auto-review__(opens in a new window) and monitoring agents’ reasoning and actions to help detect and contain unsafe behavior. As described in our __safety update__, we are also deploying misalignment monitoring in production for Astra-class models in order to have visibility into misalignment, and help contain its worst instances. These safeguards resemble our monitoring for internal deployments and involve a system of classifiers which check the model’s reasoning and actions for unauthorized behavior and automatically stop potentially unauthorized activity.

Given the significant increase in Astra’s cybersecurity capabilities, we are being especially careful to make this deployment safe and secure. Extra safety checks can sometimes slow, pause, or stop legitimate work, including defensive cybersecurity. If a task is paused in ChatGPT or Codex, you may be asked to review the action before continuing. In the API, the task will stop. These checks can sometimes interrupt legitimate work, and we are continuing to iterate on this system to reduce unnecessary interruptions. Misalignment monitoring cannot replace alignment: our goal is to build models that reliably stay within their authorized scope, so these protections do not need to intervene.

## Availability

GPT‑6 Astra is rolling out today to a limited set of organizations and over the coming days will become available to all ChatGPT Plus, Pro, Business, and Enterprise users, as well as through the OpenAI API, Microsoft Azure, and AWS Bedrock. Astra usage is included within the existing subscription allowances—users and businesses will also be able to purchase credits for additional usage. Users on the Pro, Business, and Enterprise plans will also get access to GPT‑6 Astra Pro. Enterprise administrators can enable Astra for their workspace; access is off by default at launch.

Astra supports Zero Data Retention for eligible API customers, and as we shared last month, we're testing __Private Safety Processing__ to strengthen safety monitoring while preserving customer privacy.

For developers, GPT‑6 Astra will be available in the OpenAI API as `gpt-6-astra` and through Microsoft Azure and Amazon Bedrock.

OpenAI API Standard pricing is $10 per million input tokens and $50 per million output tokens. Separate rates apply to cache reads and writes. Fast mode is available for GPT‑6 Astra in the API and delivers up to 2x the speed of Standard processing at 2x the Standard price.

### Professional

| **Professional** | **GPT‑6 Astra** | **GPT‑5.6 Sol** | **Claude Fable 5.1** | **Claude Fable 5** | **Claude Opus 5** | **Gemini 3.8 Flash** | 
| AutomationBench | 41.4% | 18.1% | 31.4% | 17.4% | 26.9% | - | 
| BenchCAD | 95.9% | 83.3% | 84.3% <sup>5</sup> | 67.5% <sup>5</sup> | 82.1% <sup>5</sup> | - | 
| BrowseComp | 91.5% | 90.4% | - | 87.4% | 90.8% | - | 
| OpenScore String Quartets (1 - OMR-NED) | 0.84 | 0.19 | - | - | - | - | 
| Internal Design Tasks | 50.0% | 47.4% | - | 35.8% | - | - | 
| Internal Data Science Tasks | 40.9% | 30.5% | - | 34.7% | - | - | 
| Artificial Analysis Intelligence Index v4.1.1 | 61.2 | 60.9 | 65.7 | 62.1 | 63.1 | 58.7 |

### Coding

| **Coding** | **GPT‑6 Astra** | **GPT‑5.6 Sol** | **Claude Fable 5.1** | **Claude Fable 5** | **Claude Opus 5** | **Gemini 3.8 Flash** | 
| Terminal-Bench 4.0 | 57.9% | 37.3% | 55.8% | 44.5% | 52.6% | 19.1% | 
| DeepSWE v1.1 | 74.1% | 72.7% | 67.4% | 69.9% | 73.7% | 73.8% | 
| FrontierCode 1.1 Extended (score) | 64.5% <sup>8</sup> | 60.6% | 63.6% | 64.9% | 63.6% | 56.3% | 
| FrontierCode 1.1 Main (score) | 53.3% <sup>8</sup> | 47.5% | 50.9% | 53.5% | 53.4% | 43.6% | 
| Internal Database Migration Tasks | 63.9% | 42.7% | 57.8% | 50.3% | - | - | 
| Artificial Analysis Coding Agent Index v1.4 | 67.0 | 65.1 | - | 67.2 | 68.1 | 61.2 |

### Academic

| **Academic** | **GPT‑6 Astra** | **GPT‑5.6 Sol** | **Claude Fable 5.1** | **Claude Fable 5** | **Claude Opus 5** | **Gemini 3.8 Flash** | 
| Terminal-Bench Science 0.1 | 64.6% | 22.4% | 52.6% | 21.4% | 30.0% | - | 
| FrontierMath Tier 4 (v2) | 97.6% | 83.0% | 87.8% | 90.2% | 73.2% | - | 
| GPQA Diamond | 96.0% | 94.6% | 93.7% | 92.6% | 93.7% | 95.3% | 
| Humanity's Last Exam (w/ tools) | 57.2% | - | 65.0% | 63.8% | 63.6% | - |

### Alignment

| **Alignment** | **GPT‑6 Astra** | **GPT‑5.6 Sol** | **Claude Fable 5.1** | **Claude Fable 5** | **Claude Opus 5** | **Gemini 3.8 Flash** | 
| Internal computer use safety benchmark (lower is better) | 2.4% | 22.0% | 9.5% | 18.3% | 11.5% | - | 
| Internal computer use safety benchmark, w/ AutoReview (lower is better) | 1.8% | 4.3% | - | - | - | - | 
| Internal circumvention benchmark (lower is better) | 0.00% | 0.29% | - | - | - | - | 
| ExploitGym honeypot (lower is better) | 0.0% | 48.2% | - | - | - | - | 
| Impossible ExploitGym | 100.0% | - | - | - | - | - | 
| Internal hallucination benchmark (lower is better) | 4.2% | 12.2% | - | - | - | - |

### Long Context

| **Long Context** | **GPT‑6 Astra** | **GPT‑5.6 Sol** | **Claude Fable 5.1** | **Claude Fable 5** | **Claude Opus 5** | **Gemini 3.8 Flash** | 
| OpenAI MRCR v2 8-needle 256K-512K | 100.0% | 91.5% | - | - | - | - | 
| OpenAI MRCR v2 8-needle 512K-1M | 96.3% | 73.8% | - | - | - | - |

### Abstract reasoning

| **Abstract reasoning** | **GPT‑6 Astra** | **GPT‑5.6 Sol** | **Claude Fable 5.1** | **Claude Fable 5** | **Claude Opus 5** | **Gemini 3.8 Flash** | 
| ARC-AGI-3 | 99.9% <sup>1</sup> | 7.8% | - | - | 30.2% | - | 
| ARC-AGI-2 | 95.0% | 92.5% | 90.0% | 89.2% | 90.4% | - | 
| ARC-AGI-1 | 98.5% | 97.5% | 97.5% | 98.5% | 97.5% | - |

Evaluation scores are the maximum at any effort. GPT evaluations were run in our research environment or via our API, which may provide slightly different output from production ChatGPT due to differences in the system prompts, tools available, etc.
