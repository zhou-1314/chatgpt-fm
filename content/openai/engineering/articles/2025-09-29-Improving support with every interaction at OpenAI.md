---
title: Improving support with every interaction at OpenAI
url: https://openai.com/index/openai-support-model
source: engineering
category: API
published: '2025-09-29'
fetched: 2026-09-09 15:05
---

# Improving support with every interaction at OpenAI

*This is part of our series sharing internal examples of how OpenAI is using its own technology and APIs. These tools are being used internally, only at OpenAI, and are shared here as illustrative examples of how frontier AI is supporting use cases across our teams. We’re also sharing the internal tool names for a clearer look at how frontier AI helps our teams get work done.*

Support has historically meant queues, tickets, and throughput. But at OpenAI, that wasn’t enough. We serve hundreds of millions of users, handle millions of requests each year, and see that volume grow by multiples annually.

Lots of organizations deal with scale. Fewer deal with scale **and** hypergrowth. Almost none face both—while also building the very technology that could change the equation. That combination uniquely positioned us to rethink support from the ground up.

“Support has never really been about replying to just tickets. It’s about whether people get what they need, whether it actually serves them well.”

Support isn’t a volume challenge. It’s an engineering and operational design challenge. So we built something different: an operating model where every interaction improves the next.

The Ops team wanted to go well beyond using a chatbot to deflect support questions. The team has a vision: reimagine support as an AI operating model that continuously learns and improves.

At the center are three building blocks:

- **Surfaces.** Where support systems are interacted with. Chat, email, and phone, but increasingly, help embedded directly inside the product.
- **Knowledge.** Not just static docs, but living and continuously improving guidance drawn from real conversations, policies, and context.
- **Evals and classifiers.** Shared definitions of quality built by software and humans in unison, plus tools to measure, improve, and highlight feedback.

These pieces don’t sit in isolation. They form a loop. A pattern spotted in an enterprise conversation can inform a developer FAQ. An eval written for one case strengthens the model for thousands more. And because the same primitives power every surface - chat, email, voice—improvements scale across channels automatically.

The role of a support rep is changing. Our aim is to shift the model from primarily focusing on processing transactional work to being a part of the overall build. They’re empowered to contribute to the architecture itself, both directly through bottom up shipping of changes and indirectly through the natural motions of their day to day work.

Reps flag interactions that should become test cases, propose and ship classifiers when they see new patterns, and even prototype lightweight automations to close workflow gaps in days. Training shifts too, it’s not just about policies, but about evaluating interactions, identifying structural gaps, and feeding improvements back.

The new approach strives to ensure that support reps are builders as much as responders.

“Agents aren’t just responding to tickets. They’re informing our knowledge base and our policies. They have an ear to the ground that we don’t.”

The result is a support organization defined less by throughput and more by its capacity to evolve. Every person is not only serving users but also actively improving the machinery that serves *all* users.

Building support this way is only possible because we’re built on OpenAI’s stack.

- Agents SDK gives us step-level traces and observability by default. We can replay runs, inspect tool calls, and debug root causes instantly.
- Responses API powers classifiers for tone, correctness, and policy adherence.
- Realtime API makes voice support possible.
- OpenAI’s Evals dashboard makes quality measurable and easy to visualize over time.

Because the platform primitives come ready-made, we spend less time stitching systems together and more time focusing on the work that matters: defining what good looks like, measuring it, and improving it.

We started with a simple Q&A answerer that worked well. With Agents SDK, we quickly expanded into dynamic actions for things like refunds, invoices, incident lookups. As the models continue to improve with larger context windows, Deep Research, and stronger agentic capabilities, we can adopt those advances immediately.

Evals turn everyday conversations into production tests. They codify what “great” means—not just solving the issue, but doing it politely, clearly, and consistently. Reps play a direct role here, flagging strong and weak examples that become evals, and those evals run continuously in production to steer model behavior.

“Usually when you have a problem, you just want help as quickly as possible. By using our AI tools, we’re able to get those responses much more quickly—and just as importantly, we know when the model shouldn’t answer,” says Jay Patel, Software Engineer, Support Automation.

Learning doesn’t stop at resolution. Patterns feed back into knowledge, automation, and product design. The system compounds: faster answers for users, tighter feedback loops for builders, and a consistently higher bar for quality across every surface.

And it’s not just the AI that learns. The organization learns alongside it. Specialists see where models fall short, shape new classifiers, and contribute datasets for fine-tuning. Observability dashboards make quality measurable, showing how performance improves over time.

The most profound shift isn’t the tooling, it’s the people and how the organization measures success. Support specialists are recognized not just for solving problems, but for refining knowledge, improving models, and extending the system itself. Leaders look for a new kind of teammate: someone who pairs frontline empathy with design instincts, combining support craft with curiosity to improve the system.

“We’re starting to see this marriage between deep craft expertise and deep engineering expertise. That’s the future of how departments run.”

And our vision is support stops being a destination you go to. It becomes an action, woven into every product surface. Users don’t “open a ticket.” They simply get what they need, where they are.

What began as a response to scale has become a blueprint for how people and AI can work together: collaborative, adaptive, and continuously improving.
