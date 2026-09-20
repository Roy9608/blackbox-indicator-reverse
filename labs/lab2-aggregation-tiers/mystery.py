#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mystery.py —— 「某交易所 App · 资金流向分析」模拟黑盒（lab2: 分档口径）。

你只能看到卡片里的数值，看不到算法。
你的任务：用 ../data/trades.csv 复现卡片上每一档的净流入；对不上，就查出为什么。

规则（先做再看）：
  1. 只把 mystery.py 当"App"用：运行它、看卡片，不要读它的引擎；
  2. 不要解码 params.lock —— 里面有剧透，做完练习再看；
  3. "对不上"是这门课的素材，不是事故。方法见 docs/。

用法:
    python mystery.py <15m|1h|4h> "YYYY-MM-DD HH:MM"
例子:
    python mystery.py 1h "2026-09-19 12:00"
"""

import base64
import csv
import json
import sys
from bisect import bisect_left
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA_FILE = HERE.parent / "data" / "trades.csv"
WINDOW_MIN = {"15m": 15, "1h": 60, "4h": 240}


def load_params():
    outer = base64.b64decode((HERE / "params.lock").read_text(encoding="ascii"))
    raw = json.loads(outer.decode("utf-8"))
    engine_src = base64.b64decode(raw["engine_b64"]).decode("utf-8")
    ns = {}
    exec(compile(engine_src, "<engine>", "exec"), ns)  # 教学黑盒：口径在锁里
    return raw, ns["compute"]


def load_trades(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for rec in csv.DictReader(f):
            rows.append(
                (
                    datetime.strptime(rec["timestamp"], "%Y-%m-%d %H:%M:%S.%f"),
                    rec["side"],
                    float(rec["quote"]),
                    float(rec["price"]),
                )
            )
    rows.sort(key=lambda r: r[0])
    return rows


def window_bounds(gran, anchor):
    size = WINDOW_MIN[gran]
    mins = anchor.hour * 60 + anchor.minute
    t0 = anchor.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(
        minutes=mins - mins % size
    )
    return t0, t0 + timedelta(minutes=size)


def render(res, t0, t1, gran, n_trades, last_price):
    out = []
    out.append("=" * 62)
    out.append(" 资金流向分析 · SIM/USDT            （模拟教学数据）")
    out.append(f" 窗口: {t0:%Y-%m-%d %H:%M} ~ {t1:%Y-%m-%d %H:%M}  ({gran})")
    out.append("-" * 62)
    if "tiers" in res:
        out.append("  档位        净流入(USDT)      笔数")
        for t in res["tiers"]:
            out.append(f"  {t['name']}    {t['net']:+16,.2f}  {t['count']:>6}")
        out.append("-" * 62)
        out.append(f" 口径说明: {res['legend']}")
    else:
        out.append(f" 加总净流入        {res['total_net']:+16,.2f} USDT")
        out.append(f" 大单净流入        {res['big_net']:+16,.2f} USDT")
        out.append(f"                    [{res['big_label']}]")
    out.append("-" * 62)
    out.append(f" 成交笔数          {n_trades:>16}")
    out.append(f" 最新价            {last_price:>16}")
    out.append("=" * 62)
    out.append(" * 本工具为教学模拟，非真实交易所数据。")
    return "\n".join(out)


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in WINDOW_MIN:
        print(__doc__)
        sys.exit(2)
    try:
        anchor = datetime.strptime(sys.argv[2], "%Y-%m-%d %H:%M")
    except ValueError:
        sys.exit('时间格式应为 "YYYY-MM-DD HH:MM"，例如 "2026-09-19 12:00"')
    if not DATA_FILE.exists():
        sys.exit(f"找不到数据文件: {DATA_FILE}")

    gran = sys.argv[1]
    t0, t1 = window_bounds(gran, anchor)
    if (anchor.hour * 60 + anchor.minute) % WINDOW_MIN[gran]:
        print(f"* 输入时刻已对齐到窗口边界: {t0:%Y-%m-%d %H:%M}")

    _raw, compute = load_params()
    trades = load_trades(DATA_FILE)
    ts_list = [row[0] for row in trades]
    win = trades[bisect_left(ts_list, t0) : bisect_left(ts_list, t1)]

    res = compute(win, trades, _raw)
    last_price = f"{win[-1][3]:.2f}" if win else "未获取"
    if not win:
        print("* 该窗口无成交数据")
    print(render(res, t0, t1, gran, len(win), last_price))


if __name__ == "__main__":
    main()
