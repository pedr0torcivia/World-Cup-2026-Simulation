# Data Sources

Dataset updated on 2026-06-10.

## Official / Tournament Data

- Teams and groups: FIFA World Cup 2026 Final Draw / group pages. FIFA confirms Group A as Mexico, South Africa, Korea Republic and Czechia, and the final draw pages list the group structure.
- Fixture and venues: FIFA match schedule as reflected in published fixture lists. FourFourTwo's fixture table was used as a readable tabular source for the 72 group-stage matches and stadium mapping.
- Format: 48 teams, 12 groups of four, top two plus eight best third-place teams.

## Ranking Data

- `fifa_ranking` and `elo_rating` use FIFA/Coca-Cola Men's World Ranking values from the latest official ranking available on 2026-06-10: last official update 2026-04-01, next official update 2026-06-11.
- `elo_rating` stores FIFA ranking points because FIFA's current ranking method is Elo-based.

## Model Parameters

The following columns are required by the simulator but are not official FIFA tournament data:

- `attack_rating`
- `defense_rating`
- `midfield_rating`
- `goalkeeper_rating`
- `squad_depth`
- `recent_form`
- `experience`
- `penalty_rating`
- `discipline_rating`
- `pressing_intensity`
- `tactical_style`
- `travel_fatigue_base`
- `expected_temperature`
- `expected_humidity`
- `travel_difficulty`
- `home_team_bonus`

They are deterministic model defaults derived from ranking strength, confederation and host context. Replace them with a scouting/rating provider if you want fully externalized team-strength data.

## Players

`players.csv` intentionally contains only the schema header. FIFA does not publish the simulator-specific player fields such as stamina, injury proneness, card risk and penalty skill as official CSV data. When no player rows are present, the simulator uses team-level fallback estimates for injuries and cards.

