# blackbox-indicator-reverse

**English** · [中文](README.zh-CN.md)

> **When your numbers and the app's numbers disagree — a hands-on method for
> reverse-engineering black-box market indicators.**
>
> Flagship case: exchange-app "money flow" panels (Binance-style).
> Reverse-engineering · data reconciliation · market-data algorithms.

---

## 1. What this is

A repeatable discipline for a situation you cannot look up: an indicator whose
number you can see, and whose rule is documented nowhere.

It ships the method, the traps, and three runnable labs — and the labs are the
point, because *you* do the reverse-engineering. Each lab is a black box you can
question but not read, and its answer is locked until you ask for it.

Most people's first attempt fails on the same thing: **they miss the factor
of 2.** This repo teaches you how to find it — systematically, not by luck.

It is written for anyone who holds trade-level data of their own and has a
black-box number to reconcile against it — including people who do not write
code themselves and drive an AI to build the pipeline.

## 2. The problem — and the answer, up front

**The answer, first:** when every check you can make passes and the number is
still wrong, you are missing a **hidden convention** — a rule inside their
pipeline that was never documented. It is not noise, so it leaves a fingerprint
in the residual, and the fingerprint says what kind of rule it is. Reading that
fingerprint is a procedure, and this repository is the procedure.

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

## 3. How to use it

### Run it yourself — the 60-second demo (lab 1)

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

No keys, no network, nothing to install. The script reads the dataset that ships
with the repo (`labs/data/trades.csv`), and its command shape is the same in all
three labs: `python mystery.py <15m|1h|4h> "YYYY-MM-DD HH:MM"`.

The app says one whale buy (+32,270.54) counts as **+64,541.08**.
Threshold is public (≥ 4,000 USDT). Reconcile twelve 4-hour windows
against your own baseline and the ratio is **exactly 2.0000** — eleven
times out of eleven. That stability is a fingerprint: additive errors
never produce a constant ratio. Something multiplies. What, and why,
is the lab.

### Path A — you just want to use it

Work the three labs, and read `docs/` in order — `01` through `07`. If you are
reproducing a real indicator of your own, read `01`, `02` and `03` before you
touch anything, and keep `04-trap-table.md` open as the index while you
reconcile: it is ordered by how cheap each check is.

### Path B — you want to change it

Plain Markdown plus Python: no build step, no dependencies, no configuration.

If you are an **AI agent** asked to work in this repository, read
[`AGENTS.md`](AGENTS.md) first — it is the contract for what you may and may not
do here.

## 4. What's inside

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

## 5. The method (docs/)

Six steps: anchor samples → time calibration → source reconciliation →
parameter-free baseline → parameter sweep → held-out cross-validation.

The order is the point: steps 1–3 are the foundation. While the data source is
unreconciled and the clock is unaligned, every later conclusion is an analysis
of noise — which is why you never use a later step to paper over an earlier one.

Four iron laws: reconcile the data source first · every value gets a
point-by-point reconciliation table · before blaming their data, suspect
your assumptions · half-open intervals everywhere.

They are not a parallel list but rising gates: pass law 1 or the tables from
law 2 mean nothing; skip law 2 and the cleverness of laws 3 and 4 has nowhere
to land.

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

## 6. The real case (docs/07)

Binance app "money flow" panel, a perpetual-futures symbol (name omitted).
Outcome: the "total" tier reproduced to 0.005% error — including the
coefficient 2 that survived three releases unnoticed; the "large order"
threshold reverse-engineered to 0.095 BTC (0.1–4.2% error on long
windows). Still unsolved, honestly documented: the 30-minute window
(13.2% error) and a one-sided sell-direction discrepancy (21–34%).

## 7. Requirements

Python 3.8+, standard library only. No install, no dependencies.
Every number shown in the READMEs and solutions is from an actual run.

## 8. Boundaries and non-applicability

What this repository deliberately does **not** do:

- **It is not a library.** It is a method plus three labs. There is nothing to
  install and nothing to import into a pipeline.
- **It will not tell you the mechanism, only the behaviour.** Reconciliation can
  lock down *what* the black box does (a ×2 factor); *why* it does it — which of
  two equivalent implementations is really running — is not recoverable from the
  numbers. A report must say so instead of picking the more flattering story.
- **It does not promise a solution.** The flagship real case is still partly
  unsolved, and that is documented rather than papered over. The repository also
  states, in `docs/05`, when "unsolved" is the honest answer: when the finest
  available granularity is still coarser than the black box's own refresh
  interval, when you cannot obtain the full data the algorithm consumes, or when
  the residual shows two parameters tangled together.
- **It does not work without your own data.** The whole method is a
  reconciliation between your trade-level data and the target's numbers. If you
  cannot get the data — the real case could not get market-wide ticks — some
  questions stay unanswerable, and no amount of method fixes that.
- **The demo data is synthetic.** `labs/data/trades.csv` is generated, not
  market data from any real exchange. It exists so that the labs are
  reproducible to the byte for everyone.

The repository's own acceptance test is worth applying to yourself, not just to
it: hand your report to someone who was not involved, and see whether they can
recompute every one of your numbers from the report alone. If they cannot, the
report is not finished.

## Language note

Docs and lab materials are written in Chinese; the two READMEs are
bilingual (this file, and [README.zh-CN.md](README.zh-CN.md)).
Code comments are Chinese where they carry teaching intent.

## License

MIT

## More from this author

- [live-trading-bot-reliability](https://github.com/Roy9608/live-trading-bot-reliability)
- [backtest-honesty](https://github.com/Roy9608/backtest-honesty)
- [macro-radar](https://github.com/Roy9608/macro-radar)

More at [@Roy9608](https://github.com/Roy9608).
