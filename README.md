# Demo: superpowers, gstack y mattpocock

Este repo acompaña el correo un correo de sugerencia sobre adoptar `superpowers`, `gstack` y `mattpocock` (mp-*) como herramientas fundamentales del equipo.

Contiene:

- `Demo_superpowers_gstack_mattpocock.docx` — documento comparativo: qué es cada herramienta, cuándo usar cada una, y un demo real (no simulado) de 3 skills (`gs-review`, `gs-cso`, `mp-code-review`) aplicadas sobre el repo [`bolsa-valores-caracas-api`](../bolsa-valores-caracas-api).
- `reviews/01-gs-review.md` — salida completa de `gs-review` (gstack).
- `reviews/02-gs-cso.md` — salida completa de `gs-cso` (gstack, auditoría de seguridad).
- `reviews/03-mp-code-review.md` — salida completa de `mp-code-review` (mattpocock).

## Nota de seguridad

Durante el demo (`gs-cso`) se encontró una **API key de Google Gemini expuesta en texto plano** en `Analisis.py` del repo `bolsa-valores-caracas-api`. Está redactada en los documentos de este demo, pero conviene rotarla cuanto antes en el repo original.

## Origen

Repos de las skills:
- superpowers: https://github.com/obra/superpowers
- gstack: https://github.com/garrytan/gstack
- mattpocock: https://github.com/mattpocock/skills
