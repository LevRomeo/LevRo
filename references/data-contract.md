# Screening data contract

Use UTF-8 JSON with top-level `as_of`, `market_trend`, and `candidates`.

```json
{
  "as_of": "2026-08-03T09:55:00+08:00",
  "market_trend": "weak",
  "candidates": [{
    "code": "000001",
    "name": "示例",
    "hot_ranks": {
      "tonghuashun": 12,
      "eastmoney": 31,
      "source_date": "2026-07-31",
      "retrieved_at": "2026-08-03T09:55:00+08:00"
    },
    "rank_scope": "formal_prior_day",
    "daily": [{"date":"2026-08-03","open":10.1,"high":10.4,"low":10.0,"close":10.3,"volume":1000000}],
    "sector_trend": "strong",
    "market_trend": "neutral",
    "liquid": true,
    "latest_period_profitable": true,
    "st_or_delisting_risk": false,
    "net_asset_abnormal": false,
    "major_negative_event": false,
    "one_day_narrative": false,
    "source_verified": true,
    "volume_confirmed": true,
    "sector_confirmed": true,
    "announcement_checked": true,
    "verified_catalyst": true,
    "intraday_macd_aligned": false
  }]
}
```

Requirements:

- Supply at least 61 daily bars in chronological order.
- Use `rank_scope`: `formal_prior_day`, `current_observation`, or `unverified`.
- Set `source_verified=true` only when the ranks, dates, and retrieval evidence are reproducible.
- Treat missing promotion booleans as false and report the missing evidence.
- Use `strong`, `neutral`, or `weak` for market and sector trend.
- Keep source URLs and timestamps in the report; the mechanical script does not invent them.

