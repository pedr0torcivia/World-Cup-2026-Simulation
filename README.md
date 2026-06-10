# World Cup 2026 Simulator

Simulador Monte Carlo configurable del Mundial FIFA 2026. Modela fase de grupos, mejores terceros, eliminatorias, goles con distribución Poisson, alargue, penales, lesiones, fatiga, tarjetas, localía, sedes y reportes probabilísticos.

La información deportiva vive en archivos editables dentro de `data/`. Los grupos, selecciones, fixture de fase de grupos y sedes están cargados con datos oficiales/publicados del Mundial 2026; los parámetros que FIFA no publica para este modelo quedan documentados en `data/sources.md`.

## Instalación

```bash
pip install -r requirements.txt
```

Requiere Python 3.11 o superior.

## Datos de Entrada

Los archivos principales están en `data/`:

- `teams.csv`: selecciones oficiales, grupo, confederación, ranking FIFA y parámetros de modelo.
- `players.csv`: schema oficial del proyecto; queda sin filas si no hay planteles oficiales con los campos requeridos.
- `fixtures.csv`: partidos oficiales de fase de grupos.
- `venues.csv`: sedes oficiales y parámetros de modelo de clima/viaje.
- `referees.csv`: schema preparado para extender la simulación de arbitraje.
- `config.yaml`: cantidad de simulaciones, seed y switches para activar o desactivar módulos.
- `sources.md`: fuentes y aclaración de qué campos son oficiales y cuáles son parámetros del simulador.

No hace falta modificar código para cambiar equipos, sedes, jugadores o parámetros del modelo.

## Ejecución

```bash
python -m src.main --simulations 1000 --seed 123
```

Para generar también sensibilidad de supuestos principales:

```bash
python -m src.main --simulations 1000 --seed 123 --sensitivity
```

Para abrir la consola interactiva al terminar la simulación:

```bash
python -m src.main --simulations 1000 --seed 123 --interactive
```

Para abrir solo el dashboard con outputs ya generados:

```bash
python -m src.main --interactive-only
python -m src.interactive_dashboard
```

Para una prueba rápida:

```bash
python -m src.main --simulations 5 --seed 123
```

## Salidas

El simulador escribe resultados en `outputs/`:

- `champion_probabilities.csv`
- `qualification_probabilities.csv`
- `knockout_probabilities.csv`
- `group_probabilities.csv`
- `injuries_summary.csv`
- `match_results_sample.csv`
- `data_quality_report.csv`
- `team_dashboard_stats.csv`
- `full_report.md`

Los CSV de probabilidades incluyen:

- `standard_error`
- `ci_low`
- `ci_high`
- `simulations_used`

Cuando se ejecuta sensibilidad, también se generan:

- `champion_probability_sensitivity.csv`
- `variable_importance.csv`
- `tornado_chart_data.csv`

Ejemplo de interpretación:

- `champion_probabilities.csv` muestra cuántas veces salió campeón cada equipo y su probabilidad estimada.
- `qualification_probabilities.csv` muestra probabilidad por ronda.
- `group_probabilities.csv` muestra probabilidad de terminar 1°, 2°, 3° o 4° de grupo.
- `injuries_summary.csv` resume lesiones promedio y riesgo de lesiones moderadas o graves.

## Modelo

Cada partido calcula goles esperados con un modelo Poisson modular en `src/simulation/expected_goals.py` usando:

- fuerza ofensiva;
- debilidad defensiva rival;
- mediocampo;
- forma reciente;
- fatiga;
- impacto de lesiones;
- localía;
- sede y clima;
- matchup táctico.

Además calcula matriz de marcador, probabilidad de victoria/empate/derrota a 90 minutos, over/under 2.5, ambos equipos convierten y marcador más probable.

Los pesos centrales están en `data/config.yaml`:

- `team_strength_weights`
- `expected_goals_weights`
- `home_advantage_cap`
- `finishing_shrinkage_k`
- límites de expected goals

En eliminatorias, si el partido termina empatado tras 90 minutos se simula alargue. Si continúa empatado, se simula una tanda de penales con muerte súbita.

## Bracket

Si existe `data/bracket_rules.csv`, el simulador lo usa para construir los cruces de 32avos. Si no existe, genera un bracket sembrado aproximado: mejor clasificado contra peor clasificado, segundo contra penúltimo, y así sucesivamente.

Ese comportamiento está documentado porque los cruces reales de mejores terceros dependen de reglas oficiales específicas. El código queda listo para reemplazar esa aproximación por reglas oficiales editables.

## Tests

```bash
python -m pytest -q
```

La suite cubre:

- ordenamiento de grupos;
- mejores terceros;
- partidos eliminatorios con resultado en 90 minutos;
- partidos con alargue;
- partidos con penales;
- lesiones;
- sanciones/tarjetas;
- fatiga;
- reproducibilidad con seed;
- generación de outputs.

## Limitaciones

- Las selecciones, grupos, fixtures y sedes están cargados con datos oficiales/publicados; los ratings internos no son datos oficiales de FIFA.
- El bracket por defecto es aproximado si no se carga `data/bracket_rules.csv`.
- El modelo de árbitros está preparado en datos, pero la primera versión usa principalmente disciplina de equipo y riesgo de jugador.
- `players.csv` no inventa jugadores: si se cargan planteles completos, el motor usa candidatos por equipo; si no, usa fallback agregado.
- La sensibilidad es Monte Carlo adicional y debe ejecutarse con suficientes simulaciones para interpretar diferencias pequeñas.

## Variables

Las variables importantes están documentadas en `docs/variable_catalog.md` con definición, escala, fuente esperada, default, fórmula, módulo, outputs y tests mínimos.

## Dashboard Interactivo

El dashboard lee `outputs/team_dashboard_stats.csv` si existe. Si no existe, intenta construirlo combinando los CSV disponibles en `outputs/`.

Comandos dentro de la consola:

- número de equipo, por ejemplo `1`: muestra estadísticas completas;
- `buscar argentina`: busca por coincidencia parcial, ignorando mayúsculas y tildes;
- `comparar 1 2`: compara dos equipos del ranking;
- `top campeon`, `top grupos`, `top lesiones`, `top sorpresa`, `top decepcion`, `top goles`, `top defensa`, `top penales`;
- `ranking` o `volver`: muestra el ranking principal;
- `0`, `q`, `quit` o `salir`: cierra la consola.

## Ejemplo de Salida

Después de ejecutar:

```bash
python -m src.main --simulations 5 --seed 123
```

La consola muestra el top 5 de probabilidades de campeón y los archivos completos quedan en `outputs/`.
