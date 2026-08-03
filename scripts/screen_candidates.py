#!/usr/bin/env python3
"""Mechanically assign A-share research roles from normalized UTF-8 JSON."""
import argparse
import json
from pathlib import Path


def sma(values, period, offset=0):
    end = len(values) - offset if offset else len(values)
    return sum(values[end - period:end]) / period


def ema_series(values, period):
    multiplier = 2 / (period + 1)
    result = [values[0]]
    for value in values[1:]:
        result.append(value * multiplier + result[-1] * (1 - multiplier))
    return result


def macd(values):
    fast = ema_series(values, 12)
    slow = ema_series(values, 26)
    dif = [a - b for a, b in zip(fast, slow)]
    dea = ema_series(dif, 9)
    hist = [(a - b) * 2 for a, b in zip(dif, dea)]
    return dif[-1], dea[-1], hist[-1], hist[-2]


def base_result(item, role, reasons, metrics=None, flags=None, score=0):
    return {
        "code": item.get("code"),
        "name": item.get("name"),
        "role": role,
        "status": role,
        "score": score,
        "reasons": reasons,
        "flags": flags or [],
        "metrics": metrics or {},
    }


def evaluate(item):
    bars = item.get("daily", [])
    if len(bars) < 61:
        return base_result(item, "downgrade", ["日线数据不足61根，不能升级"])

    closes = [float(bar["close"]) for bar in bars]
    volumes = [float(bar["volume"]) for bar in bars]
    current = {p: sma(closes, p) for p in (3, 5, 13, 20, 60)}
    previous = {p: sma(closes, p, 1) for p in (3, 5, 13, 20, 60)}
    price = closes[-1]
    dif, dea, histogram, prior_histogram = macd(closes)
    ranks = item.get("hot_ranks", {})

    rising_short = all(current[p] > previous[p] for p in (3, 5, 13))
    ma_stack = current[3] > current[5] > current[13]
    above_ma3 = price >= current[3]
    above_ma5 = price >= current[5]
    ma60_support = current[60] > previous[60] and price >= current[60]
    macd_support = dif >= 0 and (dif >= dea or histogram > prior_histogram)
    formal_dual = (
        item.get("rank_scope") == "formal_prior_day"
        and item.get("source_verified", False)
        and ranks.get("tonghuashun") is not None
        and ranks.get("eastmoney") is not None
    )
    confirmations = all(item.get(key, False) for key in (
        "volume_confirmed", "sector_confirmed", "announcement_checked"
    ))

    metrics = {
        "latest_price": price,
        "ma3": current[3], "ma5": current[5], "ma13": current[13],
        "ma20": current[20], "ma60": current[60],
        "ma3_previous": previous[3], "ma5_previous": previous[5],
        "ma13_previous": previous[13], "ma60_previous": previous[60],
        "dif": dif, "dea": dea, "macd_histogram": histogram,
        "volume_vs_prior_5d": volumes[-1] / sma(volumes, 5, 1),
        "formal_dual_source": formal_dual,
    }
    reasons, flags = [], []

    if price < current[5]:
        return base_result(item, "exit", ["价格有效跌破MA5"], metrics)
    if current[3] < current[5]:
        return base_result(item, "downgrade", ["MA3低于MA5"], metrics)
    if not above_ma3:
        return base_result(item, "downgrade", ["价格跌破MA3，停止升级"], metrics)
    if not rising_short or not ma_stack:
        return base_result(item, "downgrade", ["MA3/5/13未同时向上或未形成多头排列"], metrics)

    severe_risk = any(item.get(key, False) for key in (
        "st_or_delisting_risk", "net_asset_abnormal", "major_negative_event"
    )) or not item.get("liquid", False)
    if severe_risk:
        return base_result(item, "exit", ["存在ST/退市、净资产、流动性或重大负面风险"], metrics)
    if not item.get("latest_period_profitable", False):
        flags.append("最近一期盈利未确认或为亏损")
    if item.get("one_day_narrative", False):
        flags.append("单日叙事或孤立脉冲")
    if not formal_dual:
        flags.append("非前一交易日已核验双榜交集，最高跟随观察")
    if not confirmations:
        flags.append("量能、板块或公告确认不完整")
    if item.get("market_trend") == "weak" or item.get("sector_trend") == "weak":
        flags.append("市场或板块偏弱")
    if not ma60_support:
        flags.append("MA60趋势或价格站位未确认")
    if not macd_support:
        flags.append("日线MACD零轴或动能未确认")

    max_bar = max(bars[-20:], key=lambda bar: float(bar["volume"]))
    if float(max_bar["close"]) < float(max_bar["open"]):
        flags.append("近20日最大量能为阴线")

    score = 2 if formal_dual else 0
    score += 2 if confirmations else 0
    score += 1 if ma60_support else 0
    score += 1 if macd_support else 0
    score += 1 if item.get("intraday_macd_aligned", False) else 0
    score += 1 if volumes[-1] > sma(volumes, 5, 1) else 0
    score += 1 if price > max(closes[-21:-1]) else 0

    priority_ok = (
        formal_dual and confirmations and ma60_support and macd_support
        and item.get("latest_period_profitable", False)
        and not item.get("one_day_narrative", False)
        and item.get("market_trend") != "weak"
        and item.get("sector_trend") != "weak"
        and not any("最大量能为阴线" in flag for flag in flags)
    )
    role = "priority_tracking" if priority_ok else "follow_observe"
    reasons.append("短均线多头且价格位于MA3/MA5上方")
    if formal_dual:
        reasons.append("前一交易日双榜交集已核验")
    return base_result(item, role, reasons, metrics, flags, score)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    results = [evaluate(item) for item in payload.get("candidates", [])]
    groups = {role: [x for x in results if x["role"] == role] for role in (
        "priority_tracking", "follow_observe", "downgrade", "exit"
    )}
    groups["priority_tracking"] = sorted(
        groups["priority_tracking"], key=lambda x: x["score"], reverse=True
    )[:3]
    output = {"as_of": payload.get("as_of"), **groups}
    output["focus"] = groups["priority_tracking"]
    output["observe"] = groups["follow_observe"]
    output["exclude"] = groups["downgrade"] + groups["exit"]
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

