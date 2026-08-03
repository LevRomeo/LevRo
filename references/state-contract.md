# State contract

Keep UTF-8 JSON at `state/watchlist.json`. Preserve unknown top-level fields during updates.

```json
{
  "as_of": "2026-08-03T09:55:00+08:00",
  "quote_query_authorization": {
    "authorized_codes": [],
    "authorized_endpoints": [],
    "purpose": "Daily position review"
  },
  "daily_review_policy": {},
  "user_positions": [{
    "code": "000001",
    "name": "示例",
    "entry_price": 10.0,
    "opened_date": "2026-08-03",
    "position_status": "open",
    "tracking_status": "active",
    "role": "follow_observe",
    "note": "Technical role is not a user-reported sale."
  }],
  "watchlist": [],
  "prior_roles": []
}
```

Rules:

- Change `position_status` to `closed` only after an explicit user statement.
- Store technical `exit` in `role`; never reinterpret it as a sale.
- Keep closed positions as history unless the user asks to remove them.
- Deduplicate codes within each collection.
- Never publish a real state file, entry price, authorization list, or report as part of the reusable skill.

