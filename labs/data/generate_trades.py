#!/usr/bin/env python3
"""生成 48 小时合成成交数据（确定性：固定随机种子）。

三个实验室共用同一份数据 —— 目的是让读者体会：
变的是黑盒的"口径"，不变的是你的"方法"。

输出: ../data/trades.csv
列: timestamp, side, price, qty, quote
    - timestamp: 本地显示时间（无时区语义，游戏中无需换算）
    - side:      buy / sell（主动方向）
    - price:     成交价 (2 位小数)
    - qty:       数量 = quote / price（6 位小数）
    - quote:     成交额 USDT（2 位小数）

数据中故意"埋"了恰好落在档位边界上的成交（1000 / 3000 / 10000），
供 lab2 的区间约定陷阱使用。
"""
import csv
import datetime as dt
import math
import random
import pathlib

random.seed(20260920)

START = dt.datetime(2026, 9, 18, 0, 0, 0)
MINUTES = 48 * 60
OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "trades.csv"


def main():
    price = 100.0
    rows = []

    for m in range(MINUTES):
        minute_start = START + dt.timedelta(minutes=m)
        price *= math.exp(random.gauss(0, 0.0006))  # 每分钟一步的随机游走
        for _ in range(random.randint(3, 8)):
            ts = minute_start + dt.timedelta(
                seconds=random.randint(0, 59),
                microseconds=random.randint(0, 999) * 1000,
            )
            quote = math.exp(random.gauss(3.5, 1.6))
            if random.random() < 0.005:
                quote *= 8  # 鲸鱼单
            quote = min(max(quote, 10.0), 80000.0)
            side = "buy" if random.random() < 0.5 else "sell"
            rows.append(
                (
                    ts,
                    side,
                    round(price, 2),
                    round(quote / price, 6),
                    round(quote, 2),
                )
            )

    # 埋边界成交：恰好等于 1000 / 3000 / 10000 的 quote
    planted = 0
    for boundary in (1000, 3000, 10000):
        for k in range(15):
            m = random.randrange(MINUTES)
            ts = START + dt.timedelta(minutes=m, seconds=random.randint(0, 59))
            p = round(price * (1 + random.gauss(0, 0.001)), 2)
            side = "buy" if k % 2 == 0 else "sell"
            rows.append((ts, side, p, round(boundary / p, 6), float(boundary)))
            planted += 1

    rows.sort(key=lambda r: r[0])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["timestamp", "side", "price", "qty", "quote"])
        for ts, side, p, q, quote in rows:
            w.writerow([ts.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], side, p, q, quote])

    big = sum(1 for r in rows if r[4] >= 4000)
    print(f"trades={len(rows)}, >=4000 USDT: {big}, planted boundary: {planted}")
    print(f"price range: {min(r[2] for r in rows)} .. {max(r[2] for r in rows)}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
