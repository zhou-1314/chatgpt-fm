# EP16 | OpenAI 如何用 PostgreSQL 撑起八亿用户：一份极限优化工程复盘

- 音频文件：`/workspace/algorithm/zhouwg_project/chatGPT-fm/chatgpt-fm/content/openai/engineering/audio/2026-01-22-Scaling PostgreSQL to power 800 million ChatGPT users.mp3`
- 时长：27 分 09 秒

## Shownotes（复制到小宇宙）

OpenAI 在 2026 年初公开了一个让业界大吃一惊的工程细节：支撑八亿 ChatGPT 用户的数据库，核心仍然是一套没有分片的 PostgreSQL，一个主节点加将近五十个读副本，每秒处理数百万次查询。这期节目我们完整拆解这背后的九大挑战与解法，以及对你日常工程工作的实际启示。

- 为什么单主 PostgreSQL 可以撑到八亿用户，以及他们为什么暂时不做分片
- MVCC 写放大的坑和 OpenAI 把写密集型业务迁到 CosmosDB 的决策逻辑
- 一个联查十二张表的查询如何多次引发 ChatGPT 全面故障，以及 ORM 的隐患
- PgBouncer 如何把连接建立时间从五十毫秒压到五毫秒，防住连接风暴
- 缓存锁机制如何把"一千次数据库查询"变成"一次查询"
- 六条可以直接带走的工程实践，附带作者对"推迟复杂性"这一哲学的点评

---

原文：Scaling PostgreSQL to power 800 million ChatGPT users
链接：https://openai.com/index/scaling-postgresql
发表时间：2026-01-22
本期解读由模型（claude-sonnet-4-6）生成，音频由 edge-tts 合成。
