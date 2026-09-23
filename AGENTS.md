# AGENTS.md — how an AI agent should work in this repository

If you are an AI agent asked to "look at this repo", "walk me through the labs",
or "help me reconcile this indicator against mine", this file is the contract.

Everything stated here is drawn from the repository's own README, `docs/`, the
three lab worksheets, `labs/data/README.md`, the three `mystery.py` CLI sources
and `LICENSE`. Where the repository does not state something, this file says so
instead of guessing.

## 0. What this repository is

A hands-on method for reverse-engineering a **black-box market indicator**: a
number you can see, whose rule is documented nowhere. The flagship case is an
exchange-app "money flow" panel (Binance-style), and the failure that starts
everything is a hidden convention inside the black box's own pipeline. The
repository's answer is a procedure, not a lucky guess: a six-step method, four
iron laws, seven named traps, and three runnable labs where the *user* does the
reverse-engineering.

It is **documentation plus three runnable labs, and nothing else** — no package,
no data pipeline, no live data, no third-party dependency, nothing to install.
The content comes from one real reverse-engineering effort (2026-09), with the
instrument name and the details desensitised. Its audience includes people who
do not write code themselves and drive an AI to build the pipeline.

```
README.md                        entry point (English; README.zh-CN.md is the Chinese version)
LICENSE                          MIT, Copyright (c) 2026 Roy9608
docs/01-when-numbers-disagree.md four root causes for a mismatch
docs/02-the-method.md            the six-step method
docs/03-iron-laws.md             the four iron laws
docs/04-trap-table.md            seven named traps, ordered by cost of checking
docs/05-dynamic-thresholds.md    dynamic conventions + when to declare "unsolved"
docs/06-reporting.md             the reconciliation-report format
docs/07-real-case.md             the real Binance money-flow case, including what stayed unsolved
labs/data/trades.csv             one 48h synthetic dataset, fixed seed, shared by all three labs
labs/data/generate_trades.py     regenerates trades.csv byte-for-byte
labs/data/README.md              dataset generation parameters and column definitions
labs/lab1-static-threshold/      ★   the hidden convention is a ×2 multiplier
labs/lab2-aggregation-tiers/     ★★  the hidden convention is half-open tier edges [a, b)
labs/lab3-dynamic-threshold/     ★★★ the threshold is recomputed every 15 min from a trailing P90
```

Each lab directory holds the same four artefacts: `mystery.py` (the "app", a
runnable CLI), `params.lock` (the obfuscated ground truth), `worksheet.md` (the
exercise) and `solution/solution.md` (the worked answer, with real run numbers).

## 1. Prove it runs (no network, no keys, no install)

```bash
python labs/lab1-static-threshold/mystery.py 1h "2026-09-18 20:00"
```

Python 3.8+, standard library only. The script resolves its dataset relative to
its own location, so the working directory does not matter, and it writes
nothing.

Expected output — an app-style card. The card is reproduced in `README.md` and
in `labs/lab1-static-threshold/worksheet.md`; the excerpt below is the part that
is worth checking:

```
 加总净流入              +32,912.65 USDT
 大单净流入              +64,541.08 USDT
                    [大单: 单笔 >= 4,000 USDT]
 成交笔数                       321
 最新价                       99.09
```

Confirm the run by those four numbers. Do **not** confirm it by "the script
printed something and did not crash": plausible-looking output is exactly what
this repository exists to warn about.

The CLI has the same shape in all three labs:
`python mystery.py <15m|1h|4h> "YYYY-MM-DD HH:MM"`. With arguments that do not
match, `mystery.py` prints its own usage text instead of a card. An input time
that is not already on a window boundary is snapped to the enclosing window and
a line is printed to say so — that is normal, not an error.

The three `mystery.py` files are the same program. Read side by side, they
differ only in the module docstring — each names its own lab, and lab3's adds a
warning that its large-order threshold is not published. Every constant,
function and control-flow line is identical, so their argument handling is
identical too. What differs is `params.lock`: each CLI loads its own engine from
it, and therefore the card's numbers differ — and so does the card's shape.
lab2 renders a tier table followed by a `口径说明` legend line; lab1 and lab3
render two labelled lines instead.

Argument handling and exit codes, read from that source (no Markdown in the
repository states them):

| Invocation | What happens | Exit code |
|---|---|---|
| `<15m\|1h\|4h> "YYYY-MM-DD HH:MM"` | card printed to stdout | 0 |
| wrong argument count, or a window other than `15m` / `1h` / `4h` | the module docstring is printed to **stdout** as usage text; no card | 2 |
| a time that does not parse as `YYYY-MM-DD HH:MM` | one-line message on **stderr**; no card | 1 |
| `labs/data/trades.csv` missing | one-line message naming the expected path on **stderr**; no card | 1 |

The CLI takes no stdin input and needs no environment variable; its only inputs
are `argv`, `params.lock` and `labs/data/trades.csv`. A window containing no
trades still renders a card, preceded by a notice line, with the latest price
shown as `未获取`.

If the user only asked to "look at the repo", stop after this step.

Not documented in the source repository — do not assert these: what any lab's
engine computes, and therefore the numbers of any window you have not run
yourself (that engine is `params.lock`, and rule 3 below forbids decoding it).
The CLI hands the window to that engine and prints whatever it returns, so the
tier numbers the engine produces for an empty window, and whether it has any
side effect, are not verifiable from the CLI source alone. And do not describe
the three labs as behaving identically: only their CLI shell is identical.

## 2. Ask the user before going further

Do not guess any of these. Each one changes what you should recommend or write.

| # | Question | Why it matters |
|---|---|---|
| 1 | Do you want to **learn** (work the labs) or **apply** the method to a real indicator of your own? | If it is the labs, do not hand over answers or open `params.lock` — see rule 3. If it is a real indicator, start at `docs/01`. |
| 2 | (applied) What is the target system, and which windows and tiers does it expose? | Step 1 needs anchor samples. One window's worth of numbers cannot pin down a convention — a single set of constraints fits infinitely many rules. |
| 3 | (applied) Do you have your own trade-level data for the same instrument and period, and at what granularity? | Iron law 1 is "reconcile the data source before discussing the algorithm". Without the data, some questions stay unanswerable — the real case is unsolved partly for exactly this reason. |
| 4 | (applied) What does the target's own ⓘ / help text say, word for word? | Those few words are the only ground truth you get (lab1's "≥ 4,000 USDT" comes from there), and they are also what makes the *undocumented* part visible by contrast. |
| 5 | (applied) What clock and time base are the target's numbers on, versus your data? | Step 2 calibrates the axis against price. While the axes are misaligned, everything downstream is an analysis of noise. |
| 6 | (applied) What is your acceptance criterion, and who will consume the result? | The repository accepts only "per-point zero on held-out samples". A downstream consumer needs the "not usable" list as much as the formula. |
| 7 | Do you want to **use** the repository or **change** it? | If "use", edit nothing — walk them through the labs and `docs/`. If "change", the rules in section 4 apply. |

Never invent the user's threshold, granularity, sign convention, window set or
data source. Ask.

## 3. Failure modes → meaning

When the user describes a symptom, this is what it most likely means. (The
pairings come from the repository's own trap table and iron laws.)

| Symptom | What it means | What to do |
|---|---|---|
| The residual is a constant ratio (×2, ×10, ×0.001) | **Coefficient error** — a multiplier the docs never mention. Trap 1, and the flagship case | Do step 4 first: reproduce the parameter-free figure (the "total" tier) to prove the frame is right, then look at the ratio |
| Zero triggers, or the magnitude is completely wrong | The target tiers **aggregated** flow per window, while you were testing **individual** trades. Trap 2 | Check whether tiering happens after window aggregation, not before |
| Error is large in some windows and near zero in others | A **static threshold** where the target uses a **dynamic** one. Trap 3 | Watch whether error varies systematically with the window (the scaling-factor method, `docs/05`) |
| A whole column is shifted by one bucket (bucket N equals the previous raw bucket) | **Timestamp misalignment**, usually a `bisect` direction bug. Trap 4 | Iron law 4: `bisect_left` for slicing, `bisect_right` for tiering — do not mix them |
| The newest bucket's number keeps changing | **Unclosed data** — you are reading a bucket that has not finished. Trap 5 | Use only closed buckets |
| Everything is off by a price multiple | **Unit confusion** — base quantity versus quote amount. Trap 6 | Confirm for every field whether it is a coin amount or a money amount |
| Short windows are badly off, long windows are fine | **Window-boundary truncation** — the screenshot was not taken on the hour. Trap 7, and it is normal | Align the window before drawing conclusions |
| Totals match but the tiers do not | A **structural attribution error** — it passes the total-level acceptance check and then contaminates every downstream per-tier analysis. The repository calls this more dangerous than a wrong total | Treat as urgent; find the specific trades that landed in the wrong tier |
| The residual looks random with no structure | Not a convention problem. Go back to **iron law 1** (data source) or look for your own bug | Fix the data or the bug before touching parameters |
| "It is close" (e.g. a static threshold within 1.4%) | The **most dangerous state**, not a near-success. A wrong convention does not average out with more data | Reject it. Acceptance is per-point zero on held-out samples |
| You are about to write "their data is wrong" | **Iron law 3.** Count your own assumptions before accusing the other side | List the alternatives you ruled out, with evidence |
| A factor of 2, or a similar constant, survived several releases | **Iron law 2.** Nobody ever put the computed value and the target value side by side in one table | Build the point-by-point reconciliation table; that is what finds it |
| The user asks you to help them work the labs | The labs are an exercise, and the answer is locked in `params.lock` on purpose | Help with the method, the data and the debugging. Do not decode `params.lock` or read `mystery.py`'s engine for them — point at the worksheet's hints instead |

## 4. Iron rules for an agent working in this repository

1. **Never invent facts, numbers, thresholds, file paths, commands or
   mechanisms.** Every number in the READMEs, worksheets and solutions comes
   from an actual run, and the readers rely on that. If a figure is not in the
   repository, write that it is not provided rather than producing a plausible
   one.
2. **Never remove or soften the honesty statements.** The "unsolved" section of
   the real case, the "residual small ≠ close to correct" warning, and the
   behaviour-versus-mechanism limit are the product, not boilerplate. Do not
   rewrite them into a cleaner success story, and do not tidy them away.
3. **While someone is working the labs, do not decode `params.lock`, and do not
   present the answer before the worksheet is done.** The worksheets say
   decoding it is cheating; the reasoning is the deliverable, not the number.
   Help with the method, the data, and the debugging.
4. **Never report "reproduced" without a held-out sample at exactly zero.** "80%
   reproduced" is not reproduced, and a single window that matches is not
   evidence — a single window can be satisfied by many different parameters.
5. **Never promote behaviour into mechanism.** Reconciliation can lock down
   *what* the black box does; *why* it does it is not recoverable from the
   numbers. Write "there is a stable ×2 factor", never "it counts each trade
   twice", unless a source confirms it.
6. **Never renumber or rename the six steps, four iron laws or seven traps.**
   They are cited by number across `docs/`, the worksheets and the solutions, so
   renumbering silently breaks the cross-references. Adding a new trap at the
   end is fine if it comes from a real case; reordering is not.
7. **Never skip a step in the six-step method, and never use a later step to
   cover an earlier debt.** If a reconciliation is failing, find the first step
   that is not established and fix that.
8. **Never introduce secrets or identifying data.** No tokens, API keys, email
   addresses, server IPs or host paths, account or holding information, or
   instrument names that were deliberately omitted. The repository desensitises
   the real case on purpose — keep it desensitised. If the user pastes real
   values, replace them with placeholders before writing anything.
9. **Never add a claimed trading edge, signal, or performance number.** The
   repository's subject is reconciliation, not profit; it deliberately contains
   no strategy and no returns.
10. **Do not state a mechanism problem as a data problem, or the reverse.** A
    residual shape of "random scatter, no structure" means data source or your
    own bug; a residual shape with structure (constant ratio, edges only, short
    windows only) means a convention in the black box. Getting this backwards
    sends the user into the wrong half of the repository.
11. **Keep both READMEs complete.** `README.md` (English) and `README.zh-CN.md`
    (Chinese) must each be readable on their own. `docs/` and the lab material
    are Chinese-only by design — that is stated in the READMEs' language note,
    not a defect to "fix" by translating half of it.
