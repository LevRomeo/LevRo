---
name: a-share-open-auction-selector
description: Screen, diagnose, and track A-share stocks at 09:55, 13:30, and 18:00 Beijing time using verified Tonghuashun Top30 and Eastmoney Top100 popularity ranks, opening and intraday price-volume behaviour, MA3/5/13, observation-only MA60 and daily MACD, sector strength, announcements, catalysts, and user-position roles. Use for A-share morning selection, midday review, evening outlook, individual stock diagnosis, position tracking, conditional triggers, or maintaining the Stock report/state files.
---

# A股筛选、诊股与持仓跟踪

Use this skill only for conditional research. Never promise returns or issue mandatory buy/sell instructions.

## Required workflow

1. Confirm the Beijing time, normal A-share trading day, and report node: 09:55, 13:30, or 18:00. Stay silent for automation triggers outside these nodes.
2. Read `state/watchlist.json` when it exists. Treat `position_status` as user-reported truth. Never infer that a technical `exit` means the user sold.
3. Build the formal universe from the previous trading day's verified Tonghuashun Top30 and Eastmoney Top100 union. Preserve both ranks, source date, retrieval time, and intersection status.
4. If the previous-day snapshot cannot be reproduced, state the exact missing evidence. Use current-day rankings only as `current_observation`; never substitute them for the formal universe.
5. Cross-check quotes, daily bars, market/sector conditions, announcements, and catalysts. Do not promote a name when key evidence conflicts or is unavailable.
6. Normalize data using `references/data-contract.md`, then run `scripts/screen_candidates.py`.
7. Run `scripts/update_watchlist.py` to merge roles without deleting policies, authorizations, or user positions.
8. Produce the relevant report using `references/report-template.md`. Include 1–3 named market samples even when none reaches priority, clearly labeled as follow/downgrade/exit.

## Ranking rules

- Only a verified previous-day intersection may become `priority_tracking`.
- A single-source, non-intersection, current-day-only, or rank-unverified name is at most `follow_observe`.
- Always separate formal-universe evidence from current popularity.

## Technical rules

Require all of the following before priority:

- MA3, MA5, and MA13 each rise versus the previous session.
- `MA3 > MA5 > MA13`.
- Latest price is above MA3 and MA5.
- Volume, sector, and announcement checks confirm the move.
- No verified ST/delisting, net-asset, liquidity, major-negative, or latest-period loss risk.

Apply role changes mechanically:

- MA3 below MA5: `downgrade`.
- Price below MA3: stop upgrades.
- Effective price break below MA5: technical `exit`.
- Keep the actual user position open until the user explicitly reports closure.

Treat MA60 and daily MACD as observation layers, not universe admission gates. Good MA60/MACD supports priority. Falling/unconfirmed MA60, price below MA60, or MACD below zero keeps the name at most `follow_observe` and requires a stated risk.

## Quality checks

- Reward verified 5–10 day platforms, 20-day highs, relative strength, and sustainable volume.
- Reject isolated narrative spikes, maximum-volume bearish bars, failed surges, or unverified rumours.
- For policy, project, order, or “国产算力替代 / Token工厂” themes, verify direct business relevance and potential revenue/profit linkage. Concept association alone cannot upgrade a stock.
- Review official announcements for earnings, reductions, pledges, guarantees, investigations, abnormal-volatility notices, and project progress.

## Position and privacy rules

- Review every open position alongside market candidates at each report node.
- Show entry-relative performance, MA3/MA5 triggers, volume, announcements, and role changes.
- Do not treat a position as a recommendation merely because the user owns it.
- Query a user-position code only through endpoints explicitly authorized in `quote_query_authorization`. Public indices and public ranking lists do not disclose the user's holdings.

## Resources

- Read `references/data-contract.md` before running the scripts.
- Read `references/state-contract.md` before creating or updating state.
- Read `references/source-policy.md` when selecting or documenting data sources.
- Read `references/report-template.md` for 09:55, 13:30, and 18:00 output.
- Adjust documented defaults only in `config/strategy.json`.

