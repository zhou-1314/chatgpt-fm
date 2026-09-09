---
title: Empowering teams to unlock insights faster at OpenAI
url: https://openai.com/index/openai-research-assistant
source: engineering
category: API
published: '2025-09-29'
fetched: 2026-09-09 16:05
---

*This is part of our series sharing internal examples of how OpenAI is using its own technology and APIs. These tools are being used internally, only at OpenAI, and are shared here as illustrative examples of how frontier AI is supporting use cases across our teams. We’re also sharing the internal tool names for a clearer look at how frontier AI helps our teams get work done.*

Millions of support tickets come in every year. Each one carries something valuable: a frustration, an idea, a request.

But until recently, those signals were difficult to understand. Dashboards hinted at trends but missed the why. Deep dives took weeks of work from a data scientist. A product leader might want to know how a new feature landed with a unique audience type. But answering required a data scientist to conduct a detailed analysis.

Curiosity was getting rationed.

“The process required deep technical expertise, and it was cutting off our curiosity,” says Molly Jackman, Head of Business Data.

We built a research assistant to unlock curiosity that scales. It combines two modes of exploration: dashboards for patterns and a conversational interface for digging deeper. You can start with a chart of trending issues, then ask follow-up questions in plain language.

We built it by blending what already worked. On one side, classifiers and charts that structured millions of tickets into product areas and themes. On the other, GPT‑5, which could summarize raw tickets and generate flexible reports in plain language. The combination gave us both speed and depth that was simple enough for anyone to use.

“What are healthcare customers saying about new integrations?”

“What’s driving support tickets this quarter?”

“What major features are hitting the mark?”

In minutes, the system returns a report sizing the problem, showing prevalence, and highlighting friction points. Leaders no longer have to borrow bandwidth or view static dashboards. Anyone can follow their own questions wherever they lead. For product teams, that means faster iteration on real feedback—knowing what’s working, what isn’t, and drawing clear insights to guide both product launches and long-term roadmaps.

“The magic is that you don’t have to predefine your questions, you can just follow your curiosity.”

Speed is meaningless without accuracy.

In the early days, ops teams ran manual classifications and data scientists wrote custom models to compare against the assistant. The results lined up.

Over time, confidence grew. Leaders began to cross-check findings against what they were already hearing in the field, and when it matched, they leaned in.

That cycle—ask, check, trust—turned the assistant into a daily habit for teams. What once took a week of SQL queries and classifiers now happens in a few clicks.

The payoff shows up everywhere.

- After GPT‑5 launched, product teams had feedback themes in days, not weeks.
- When the enterprise adoption of connectors slowed, the assistant quickly surfaced the root cause: a buggy onboarding flow. Engineers could then prioritize fixes.
- In Image generation, it highlighted both the creativity of marketing teams using it for mockups *and* the friction of rendering delays; two truths that directly shaped the roadmap.

When the cost of asking a question drops to minutes, more questions get asked. More issues surface. Teams move faster.

The tool doesn’t replace data scientists. It frees them to do different work. Instead of one off analyses, they have more time to build new classifiers and invest in automation and tooling. Ops teams now generate launch reports in minutes instead of days, freeing capacity to spend more time with customers. Product teams can learn in real time from customers, informing their roadmaps with faster feedback loops.

This transformation has shifted how we can listen. Instead of rationing scarce analytical cycles, every team can now pursue their questions freely. Curiosity compounds. A product lead spots a friction point, a sales lead sees the same theme in enterprise tickets, and together they create a faster path to action.

The hope is that customers feel it most. Issues will get resolved sooner. Features can evolve closer to their needs. Feedback that once sat buried in the backlog is now central to how we build.

“I think about it as customer UX research at scale. If we’re surfacing the voice of the customer in a way that proactively changes our products, policies, and practices—that’s success.”

What began as a tool for parsing millions of tickets is becoming part of the operating system for how we listen. And listening well is how we build well.
