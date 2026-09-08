"""统一的 HTTP 抓取：httpx → curl → curl_cffi 三级回退。

openai.com 的静态资源（sitemap.xml、news/rss.xml）普通请求就能拿；但文章页
（/index/<slug>）挂着 Cloudflare 的机器人校验，会按 TLS 指纹判定，httpx 和
系统 curl 一律吃 403。curl_cffi 用真实 Chrome 的指纹发请求，才拿得到正文。

顺序上先便宜后贵：能用 httpx 就不启 curl_cffi。
"""

import os
import subprocess
import time

import httpx

from . import config


def _proxy() -> str | None:
    return (
        os.environ.get("HTTPS_PROXY")
        or os.environ.get("https_proxy")
        or os.environ.get("HTTP_PROXY")
        or os.environ.get("http_proxy")
    )


def client(timeout: int = 30) -> httpx.Client:
    return httpx.Client(
        headers={"User-Agent": config.USER_AGENT},
        timeout=timeout,
        follow_redirects=True,
    )


def _curl(url: str) -> str:
    cmd = ["curl", "-fsSL", "--retry", "3", "--retry-all-errors",
           "--retry-max-time", "30", "--max-time", "60",
           "-A", config.USER_AGENT]
    proxy = _proxy()
    if proxy:
        cmd += ["--proxy", proxy]
    cmd.append(url)
    # 失败由 get_text 统一兜底，curl 自己的报错不用打到终端上吓人
    return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)


def _curl_cffi(url: str, attempts: int = 3) -> str:
    """Chrome TLS 指纹请求。curl_cffi 是 openai.com 正文抓取的必需依赖，
    但装不上时也不该让 sitemap/RSS 这类能走 httpx 的请求跟着失败，所以延迟导入。

    这一级是文章正文唯一走得通的路，前面几级失败后没有别的兜底了，所以它
    自己要扛住偶发的连接中断（SSL_ERROR_SYSCALL 之类），退避重试几次。
    """
    from curl_cffi import requests as cffi_requests

    proxies = {"https": _proxy(), "http": _proxy()} if _proxy() else None
    last_err: Exception | None = None
    for attempt in range(attempts):
        try:
            resp = cffi_requests.get(
                url,
                impersonate=config.IMPERSONATE,
                timeout=60,
                proxies=proxies,
            )
            if resp.status_code == 200:
                return resp.text
            # 403 再试也是同样的指纹，没意义；5xx/429 值得等一下
            if resp.status_code in {403, 404}:
                raise RuntimeError(f"curl_cffi HTTP {resp.status_code}")
            last_err = RuntimeError(f"curl_cffi HTTP {resp.status_code}")
        except RuntimeError:
            raise
        except Exception as exc:  # noqa: BLE001 — 连接层抖动，退避重试
            last_err = exc
        if attempt < attempts - 1:
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"curl_cffi 失败（{attempts} 次）: {str(last_err)[:200]}")


def get_text(url: str, attempts: int = 3, timeout: int = 30) -> str:
    """取回 url 的文本内容，逐级回退；全部失败抛 RuntimeError。"""
    errors: list[str] = []
    blocked = False  # httpx 拿到 403/429 → 判定为机器人校验

    # httpx 这一级整段兜住：连 Client 都建不起来时（比如环境里设了 ALL_PROXY=socks5
    # 但没装 socksio），也要落到 curl / curl_cffi，而不是直接崩掉。
    try:
        with client(timeout) as c:
            for attempt in range(attempts):
                try:
                    resp = c.get(url)
                    resp.raise_for_status()
                    return resp.text
                except httpx.HTTPError as exc:
                    errors.append(f"httpx: {exc}")
                    status = getattr(getattr(exc, "response", None), "status_code", None)
                    blocked = blocked or status in {403, 429}
                    # 403/404 是稳定拒绝，重试同一条路没意义
                    if status in {403, 404} or attempt == attempts - 1:
                        break
                    time.sleep(min(10, 2 * (attempt + 1)))
    except Exception as exc:  # noqa: BLE001 — 客户端本身不可用，交给下一级
        errors.append(f"httpx client: {str(exc)[:200]}")

    # 403/429 是 Cloudflare 按 TLS 指纹拦的，系统 curl 的指纹和 httpx 一样会被拦，
    # 试它纯属浪费时间（每次还要走完重试），直接跳到 curl_cffi。
    fallbacks = [("curl", _curl), ("curl_cffi", _curl_cffi)]
    if blocked:
        fallbacks = fallbacks[1:]

    for name, fn in fallbacks:
        try:
            return fn(url)
        except Exception as exc:  # noqa: BLE001 — 每一级失败都只记录并继续兜底
            errors.append(f"{name}: {str(exc)[:200]}")

    raise RuntimeError(f"抓取失败 {url}\n  " + "\n  ".join(errors))
