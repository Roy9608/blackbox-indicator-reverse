# blackbox-indicator-reverse

**When your numbers and the app's numbers disagree — a hands-on method for
reverse-engineering black-box market indicators.**
Flagship case: exchange-app "money flow" panels (Binance-style).
Reverse-engineering · data reconciliation · market-data algorithms.

Most people's first attempt fails on the same thing: **they miss the factor
of 2.** This repo teaches you how to find it — systematically, not by luck.

## The problem

You reproduce an indicator that you can only *see*, not *read*:

```
App shows:   large-order net flow   -6,392.77
You compute: large-order net flow  -10,000.00
```

The threshold is **publicly documented**. Your data source checks out.
Your timestamps are aligned. And the number is still wrong.
That is not a bug in your code — it is a hidden convention in theirs.

This repo turns that situation into a repeatable discipline:
a six-step method, four iron laws, seven named traps,
and three runnable labs where *you* do the reverse-engineering.

## 60-second demo (lab 1)

```bash
python labs/lab1-static-threshold/mystery.py 1h "2026-09-18 20:00"
```

```
==============================================================
 资金流向分析 · SIM/USDT            （模拟教学数据）
 窗口: 2026-09-18 20:00 ~ 2026-09-18 21:00  (1h)
--------------------------------------------------------------
 加总净流入              +32,912.65 USDT
 大单净流入              +64,541.08 USDT
                    [大单: 单笔 >= 4,000 USDT]
--------------------------------------------------------------
 成交笔数                       321
 最新价                       99.09
==============================================================
```

The app says one whale buy (+32,270.54) counts as **+64,541.08**.
Threshold is public (≥ 4,000 USDT). Reconcile twelve 4-hour windows
against your own baseline and the ratio is **exactly 2.0000** — eleven
times out of eleven. That stability is a fingerprint: additive errors
never produce a constant ratio. Something multiplies. What, and why,
is the lab.

## What's inside

| Lab | The hidden convention | Failure mode it teaches |
|---|---|---|
| [lab1 · static threshold](labs/lab1-static-threshold/worksheet.md) | a hidden ×2 multiplier | documented threshold, undocumented semantics (★) |
| [lab2 · aggregation tiers](labs/lab2-aggregation-tiers/worksheet.md) | half-open intervals `[a, b)` at tier edges | documented ranges, undocumented boundaries (★★) |
| [lab3 · dynamic threshold](labs/lab3-dynamic-threshold/worksheet.md) | threshold recomputed every 15 min from a trailing P90 | nothing documented at all (★★★) |

All three labs share one 48-hour synthetic trade dataset (fixed seed,
fully regenerable — see `labs/data/`). **The black box changes;
your method doesn't.**

Each lab ships: `mystery.py` (the "app", runnable CLI), `params.lock`
(the obfuscated ground truth — decode = cheating), `worksheet.md`
(the exercise), `solution/solution.md` (full worked solution with real
run numbers).

## The method (docs/)

Six steps: anchor samples → time calibration → source reconciliation →
parameter-free baseline → parameter sweep → held-out cross-validation.

Four iron laws: reconcile the data source first · every value gets a
point-by-point reconciliation table · before blaming their data, suspect
your assumptions · half-open intervals everywhere (`bisect_left` for
slices, `bisect_right` for tiering).

Seven named traps with symptoms and counter-moves — plus a full chapter
on dynamic conventions (the hardest class, including when to declare a
problem **unsolved** and why that is a deliverable, not a defeat).

| Doc | Content |
|---|---|
| [01](docs/01-when-numbers-disagree.md) | when numbers disagree: four root causes |
| [02](docs/02-the-method.md) | the six-step method |
| [03](docs/03-iron-laws.md) | the four iron laws |
| [04](docs/04-trap-table.md) | seven traps quick reference |
| [05](docs/05-dynamic-thresholds.md) | dynamic thresholds & the scaling-factor method |
| [06](docs/06-reporting.md) | how to write a reconciliation report |
| [07](docs/07-real-case.md) | the real Binance money-flow case (2026-09) |

## The real case (docs/07)

Binance app "money flow" panel, a perpetual-futures symbol (name omitted).
Outcome: the "total" tier reproduced to 0.005% error — including the
coefficient 2 that survived three releases unnoticed; the "large order"
threshold reverse-engineered to 0.095 BTC (0.1–4.2% error on long
windows). Still unsolved, honestly documented: the 30-minute window
(13.2% error) and a one-sided sell-direction discrepancy (21–34%).

## Requirements

Python 3.8+, standard library only. No install, no dependencies.
Every number shown in the READMEs and solutions is from an actual run.

## Language note

Docs and lab materials are written in Chinese; the two READMEs are
bilingual (this file, and [README.zh-CN.md](README.zh-CN.md)).
Code comments are Chinese where they carry teaching intent.

## License

MIT
