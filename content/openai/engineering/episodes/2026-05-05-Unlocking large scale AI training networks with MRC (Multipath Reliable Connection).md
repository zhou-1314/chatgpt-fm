# EP7 | 告别训练崩溃：OpenAI MRC 如何让超算网络故障变成背景噪音

- 音频文件：`/workspace/algorithm/zhouwg_project/chatGPT-fm/chatgpt-fm/content/openai/engineering/audio/2026-05-05-Unlocking large scale AI training networks with MRC (Multipath Reliable Connection).mp3`
- 时长：28 分 06 秒

## Shownotes（复制到小宇宙）

本期解析 OpenAI 在二〇二六年五月联合 AMD、Broadcom、Intel、微软和英伟达共同发布的超算网络协议 MRC（Multipath Reliable Connection，多路径可靠连接）。这套协议从拓扑设计、数据传输和路由控制三个维度，彻底解决了十万卡级别 AI 训练集群的网络拥塞和故障问题，并已通过开放计算项目向全行业开源。

- MRC 的诞生背景：十几万张 GPU 同步训练时，单次链路故障如何被"放大"成整个训练任务崩溃
- 多平面拓扑：把一个八百吉比特网卡接口拆成八个独立平面，两层交换机连通十三万张 GPU
- 自适应数据包喷洒：打破"一条流走一条路"的传统限制，将数据包散射到数百条路径
- 数据包裁剪：区分拥塞导致的丢包与路径故障，避免误判误停正常路径
- SRv6 静态源路由：完全禁用 BGP 动态路由协议，消除整类动态路由故障
- 实战效果：每分钟多次链路抖动不影响训练，重启四台核心交换机无需通知训练团队

---

原文：Unlocking large scale AI training networks with MRC (Multipath Reliable Connection)
链接：https://openai.com/index/mrc-supercomputer-networking
发表时间：2026-05-05
本期解读由模型（claude-sonnet-4-6）生成，音频由 edge-tts 合成。
