---
title: Turning contracts into searchable data at OpenAI
url: https://openai.com/index/openai-contract-data-agent
source: engineering
category: API
published: '2025-09-29'
fetched: 2026-09-09 10:45
---

# Turning contracts into searchable data at OpenAI

*This is part of our series sharing internal examples of how OpenAI is using its own technology and APIs. These tools are being used internally, only at OpenAI, and are shared here as illustrative examples of how frontier AI is supporting use cases across our teams. We’re also sharing the internal tool names for a clearer look at how frontier AI helps our teams get work done.*

Every enterprise deal comes with a signed contract. Each one has start dates, billing terms, renewal clauses.

At first, the process was manageable: read line by line, retype into a spreadsheet, move on. But when volume doubled and doubled again, this manual approach broke.

“In less than six months, the team went from reviewing hundreds of contracts each month to more than a thousand. And yet we’d only hired one new person. It was obvious that the process wasn’t going to scale,” says Wei An Lee, AI Engineer.

Instead of throwing more people at the problem, our finance and engineering teams built a contract data agent. The design principle was simple: take the repetition out of contract review, keep experts firmly in control.

The Agent works in three steps:

- **Ingest data:** PDFs, scanned copies, even phone photos marked up with handwritten edits. What used to be dozens of inconsistent files now flow into one pipeline.
- **Inference with prompting:** Using retrieval-augmented prompting, the system parses contracts into structured data. It doesn’t dump a thousand pages into context; it pulls only what’s relevant, reasons against it, and shows its work.
- **Review:** Finance experts review the structured output, complete with annotations and references for any non-standard terms. The agent highlights what’s unusual; humans are then looped in to review.

“We’re not just parsing, we’re reasoning—showing why a term is considered non-standard, citing the reference material, and letting the reviewer confirm the ASC 606 classification.”

The output is a dataset that’s immediately useful across finance workflows. What once took hours arrives overnight, annotated and ready for validation. Experts remain in the loop, but their role shifts from manual entry to judgment.

“The amazing thing is that the heavy lifting happens with AI—and then our teams wake up in the morning to data that’s ready for them to review.”

This design ensures confidence: professionals get structured, reasoned data at scale, but their expertise drives the outcome.

The results:

- **Faster turnaround** . Reviews cut in half, ready overnight.
- **Higher capacity** . Thousands of contracts processed without expanding headcount in lockstep.
- **Smarter context** . Non-standard terms flagged with reasoning and references.
- **Queryable results** . Tabular output in the data warehouse allows for easier data analysis.

Each cycle of human feedback sharpens the Agent, making every review faster and more accurate.

“The only way we can scale as OpenAI scales is through this,” Wei An said. “Without it, you’d have to grow your team linearly in lockstep with contract volume. This lets us keep the team lean while handling hypergrowth.”

This architecture now supports procurement, compliance, even month-end close. The same principle applies: automate the rote work, keep humans in charge of judgment.

Engineers describe it as “manual work already done,” not decisions replaced. Finance teams still write the story of the numbers; the Agent ensures they don’t spend their day doing painstaking work.

What started as a fix for contracts has become a new way of working in finance. Data parsing runs overnight. Professionals focus on analysis and strategy. Leaders scale confidently with growth, without growing teams in lockstep.

The contract data Agent is a blueprint for how AI can responsibly transform regulated, high-stakes work. It shows what becomes possible when experts partner with intelligent systems: more leverage, more confidence, and more time spent on what matters most.
