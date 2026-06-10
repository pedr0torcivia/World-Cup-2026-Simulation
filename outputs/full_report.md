# World Cup 2026 Monte Carlo Report

- Simulations: 5
- Random seed: 123
- Most likely champion: Paraguay (20.00%)
- Average goals per match: 2.58
- Average injuries per simulation: 52.60
- Penalty shootout rate: 5.00%
- Average team data quality score: 0.63

## Top 10 Candidates

- Paraguay: 20.00%
- Senegal: 20.00%
- Spain: 20.00%
- Curacao: 20.00%
- France: 20.00%
- Mexico: 0.00%
- Korea Republic: 0.00%
- South Africa: 0.00%
- Switzerland: 0.00%
- Brazil: 0.00%

## Early Exit Risk

- Uruguay: 80.00%
- Ecuador: 80.00%
- South Africa: 60.00%
- Bosnia and Herzegovina: 60.00%
- Tunisia: 60.00%
- Ghana: 60.00%
- Paraguay: 60.00%
- IR Iran: 60.00%
- France: 60.00%
- Norway: 60.00%

## Injuries

- Czechia: 2.20 average injuries
- England: 2.20 average injuries
- Senegal: 2.00 average injuries
- Algeria: 2.00 average injuries
- Ivory Coast: 1.80 average injuries
- United States: 1.80 average injuries
- Iraq: 1.80 average injuries
- Canada: 1.60 average injuries
- DR Congo: 1.60 average injuries
- South Africa: 1.60 average injuries

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
