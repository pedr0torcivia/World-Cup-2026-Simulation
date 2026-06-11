# World Cup 2026 Monte Carlo Report

- Simulations: 50
- Random seed: system_entropy
- Most likely champion: Germany (10.00%)
- Average goals per match: 2.69
- Average injuries per simulation: 51.38
- Penalty shootout rate: 5.35%
- Average team data quality score: 0.63
- Most likely match scores are written to `match_predictions.csv`.

## Top 10 Candidates

- Germany: 10.00%
- Senegal: 8.00%
- United States: 6.00%
- France: 6.00%
- Japan: 6.00%
- Belgium: 6.00%
- Argentina: 6.00%
- Croatia: 6.00%
- Spain: 4.00%
- Morocco: 4.00%

## Early Exit Risk

- Iraq: 68.00%
- New Zealand: 66.00%
- Bosnia and Herzegovina: 58.00%
- Haiti: 58.00%
- Curacao: 58.00%
- Cape Verde: 58.00%
- Saudi Arabia: 56.00%
- Jordan: 54.00%
- DR Congo: 54.00%
- Ghana: 52.00%

## Injuries

- Brazil: 1.46 average injuries
- Argentina: 1.40 average injuries
- Belgium: 1.38 average injuries
- France: 1.38 average injuries
- England: 1.36 average injuries
- Colombia: 1.30 average injuries
- Germany: 1.30 average injuries
- Portugal: 1.30 average injuries
- Japan: 1.28 average injuries
- IR Iran: 1.28 average injuries

## Data Quality

- Mexico: player-level data missing; using team-level fallback (score 0.63)
- South Africa: player-level data missing; using team-level fallback (score 0.63)
- Korea Republic: player-level data missing; using team-level fallback (score 0.63)
- Czechia: player-level data missing; using team-level fallback (score 0.63)
- Canada: player-level data missing; using team-level fallback (score 0.63)
- Bosnia and Herzegovina: player-level data missing; using team-level fallback (score 0.63)
- Qatar: player-level data missing; using team-level fallback (score 0.63)
- Switzerland: player-level data missing; using team-level fallback (score 0.63)

## Sensitivity

Sensitivity CSVs can be generated with `run_sensitivity_analysis`; they report champion probability deltas when core assumptions move by +/-10%.

## Model Notes

The simulator uses editable CSV/YAML inputs, Poisson goals, fatigue, injuries, cards, venue effects, penalties, group tie-breakers and a configurable knockout bracket.
If `data/bracket_rules.csv` is absent, the round-of-32 bracket is an approximate seeded bracket that can be replaced when official mapping rules are loaded.
