# A股诊股与持仓跟踪 Skill

面向 Codex 的 A 股条件式研究 Skill，用于早盘筛选、午间复核、盘后预判、个股诊断及用户持仓跟踪。

> 本项目仅提供研究框架、条件触发与风险提示，不构成投资建议或买卖指令。

## 核心能力

| 模块 | 说明 |
|---|---|
| 09:55 晨报 | 核验正式热榜池、竞价/早盘量价、短均线、板块与公告 |
| 13:30 午间复盘 | 复核上午候选和用户持仓，更新技术角色 |
| 18:00 盘后复盘 | 核验收盘结构、盘后公告、市场情绪及次日观察标的 |
| 个股诊断 | 分析热度、量价、MA3/5/13、MA60、MACD、板块和催化 |
| 持仓跟踪 | 记录成本、相对收益、技术触发、公告风险与角色变化 |
| 隐私边界 | 仅向用户明确授权的行情端点发送持仓代码 |

## 正式筛选规则

### 热榜池

正式样本池为前一交易日：

- 同花顺可核验热榜 Top30
- 东方财富可核验人气榜 Top100
- 两者并集

仅前一交易日双榜交集标的可以进入 `priority_tracking`。单源、非交集、当日榜单或排名无法回溯的标的，最高为 `follow_observe`。

### 技术条件

进入优先跟踪需同时满足：

1. MA3、MA5、MA13分别较前一交易日上升。
2. `MA3 > MA5 > MA13`。
3. 最新价格位于MA3和MA5上方。
4. 量能、板块及公告完成确认。
5. 不存在ST/退市、重大负面、异常净资产、流动性或最新一期亏损风险。

MA60和日线MACD仅作为观察分层项，不负责样本准入；但未确认或走弱时，标的不能升级至最高优先级。

## 技术角色

| 角色 | 含义 |
|---|---|
| `priority_tracking` | 正式双榜、趋势、量能、板块和公告均完成确认 |
| `follow_observe` | 保留跟踪，仍有来源、MA60、MACD或催化等待确认 |
| `downgrade` | MA3下穿MA5，或趋势、量价、板块证据发生冲突 |
| `exit` | 价格有效跌破MA5，或重大负面破坏原研究逻辑 |

技术 `exit` 不等于用户已经卖出。只有用户明确报告平仓，`position_status` 才能改为 `closed`。

## 安装

### 使用 Git 克隆

```powershell
git clone https://github.com/LevRomeo/LevRo.git "$env:USERPROFILE\.codex\skills\a-share-open-auction-selector"
```

重新启动 Codex 后即可通过 `$a-share-open-auction-selector` 调用。

### 更新

```powershell
git -C "$env:USERPROFILE\.codex\skills\a-share-open-auction-selector" pull
```

## 使用示例

```text
使用 $a-share-open-auction-selector 生成今天09:55的A股晨报。
```

```text
使用 $a-share-open-auction-selector 复核我的持仓，并给出MA3/MA5触发条件。
```

```text
使用 $a-share-open-auction-selector 分析某只股票是否处于启动前期。
```

## 脚本

### 机械筛选

```powershell
python scripts/screen_candidates.py --input data/input.json --output data/screen.json
```

输入格式见 [references/data-contract.md](references/data-contract.md)。

### 状态合并

```powershell
python scripts/update_watchlist.py --screen data/screen.json --state state/watchlist.json
```

状态脚本会保留用户持仓、行情授权和自定义策略字段。状态格式见 [references/state-contract.md](references/state-contract.md)。

## 目录结构

```text
.
├── SKILL.md
├── agents/
│   └── openai.yaml
├── config/
│   └── strategy.json
├── references/
│   ├── data-contract.md
│   ├── report-template.md
│   ├── source-policy.md
│   └── state-contract.md
└── scripts/
    ├── screen_candidates.py
    └── update_watchlist.py
```

## 数据与限制

- 优先使用交易所、巨潮资讯、公司公告及监管/政府来源。
- 行情、热榜和第三方接口可能发生结构调整、限频或历史数据缺失。
- 当正式榜单无法回溯时，必须披露缺口，不得用当日热度冒充前一交易日正式样本。
- 盘中均线属于动态值；盘中成交量不能直接与完整交易日成交量机械比较。
- 仓库不应提交真实持仓成本、用户授权清单或私人报告。

## 许可证与责任

使用者应自行核验数据来源、接口使用条款及投资风险。本Skill不会保证收益，也不会替代持牌投资顾问。

