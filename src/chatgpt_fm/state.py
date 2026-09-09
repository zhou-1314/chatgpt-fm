"""content/state.json 读写：记录每篇文章的流水线进度，保证幂等重跑。"""

import json
from typing import Any

from . import config

# state 结构：
# {
#   "next_episode": 1,
#   "articles": {
#     "<url>": {
#       "slug": "...", "source": "engineering", "title": "...",
#       "published": "2024-12-19", "episode": 3, "duration_sec": 1502.3,
#       "stages": {"fetched": true, "interpreted": true, "synthesized": true, "packaged": true}
#     }
#   }
# }


def load() -> dict[str, Any]:
    if config.STATE_FILE.exists():
        return json.loads(config.STATE_FILE.read_text(encoding="utf-8"))
    return {"next_episode": 1, "articles": {}}


def save(state: dict[str, Any]) -> None:
    """原子写入：先写同目录的临时文件再 rename。

    直接 write_text 的话，进程在写到一半时被杀（限额中断、Ctrl-C、OOM）会留下
    半截 JSON，几百集的进度就全毁了。rename 在同一文件系统上是原子的。

    注意：这挡不住两个流水线同时跑——各自持有内存副本，后 save 的会整个覆盖
    先 save 的。不要并发跑两个 autorun，也不要在流水线运行时手改 state.json。
    """
    config.CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    tmp = config.STATE_FILE.with_suffix(".json.tmp")
    tmp.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    tmp.replace(config.STATE_FILE)


def get_article(state: dict[str, Any], url: str) -> dict[str, Any]:
    return state["articles"].setdefault(url, {"stages": {}})


def assign_episode(state: dict[str, Any], url: str) -> int:
    art = get_article(state, url)
    if "episode" not in art:
        art["episode"] = state["next_episode"]
        state["next_episode"] += 1
    return art["episode"]
