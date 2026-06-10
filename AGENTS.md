# Proyecto

Este repositorio contiene una simulación Monte Carlo del Mundial FIFA 2026.

El objetivo es modelar el torneo completo con fase de grupos, mejores terceros, fase eliminatoria, lesiones, fatiga, tarjetas, penales, localía, sedes y reportes probabilísticos.

## Reglas de trabajo

- No hardcodear datos del torneo dentro del código.
- Usar archivos CSV/JSON/YAML dentro de `data/`.
- Mantener el código modular.
- Priorizar claridad antes que optimización extrema.
- Toda función importante debe tener nombres explícitos.
- Validar datos de entrada antes de simular.
- Usar seed reproducible.
- No eliminar archivos existentes sin justificarlo.
- No mezclar lógica de simulación con lógica de reportes.
- No meter impresión por consola dentro de funciones puras salvo que sea necesario.

## Comandos

Instalar dependencias:

```bash
pip install -r requirements.txt
```
