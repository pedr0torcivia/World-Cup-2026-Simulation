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
- `full_report.md`

Ejemplo de interpretación:

- `champion_probabilities.csv` muestra cuántas veces salió campeón cada equipo y su probabilidad estimada.
- `qualification_probabilities.csv` muestra probabilidad por ronda.
- `group_probabilities.csv` muestra probabilidad de terminar 1°, 2°, 3° o 4° de grupo.
- `injuries_summary.csv` resume lesiones promedio y riesgo de lesiones moderadas o graves.

## Modelo

Cada partido calcula goles esperados con una variante de Poisson usando:

- fuerza ofensiva;
- debilidad defensiva rival;
- mediocampo;
- forma reciente;
- fatiga;
- impacto de lesiones;
- localía;
- sede y clima;
- matchup táctico.

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

## Ejemplo de Salida

Después de ejecutar:

```bash
python -m src.main --simulations 5 --seed 123
```

La consola muestra el top 5 de probabilidades de campeón y los archivos completos quedan en `outputs/`.
