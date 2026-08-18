# Demo: `mp-code-review` (mattpocock) aplicado a `bolsa-valores-caracas-api`

**Skill:** `mp-code-review` — revisión en dos ejes (Standards / Spec) de un diff entre un punto fijo y `HEAD`, usando sub-agentes en paralelo.

**Nota sobre la adaptación para este demo:** este repo no tiene un PR abierto, ni un issue/spec de origen, ni un `CODING_STANDARDS.md`. La skill real pide justo eso (un diff + una spec) — aquí no hay ninguno de los dos, así que:
- El **eje Spec se omite** (tal como indica la skill cuando no hay spec disponible: "Spec sub-agent skips and reports 'no spec available'").
- El **eje Standards** se aplicó igual, usando el baseline de "code smells" de Fowler que la skill trae por defecto cuando el repo no documenta sus propios estándares — y se aplicó sobre el archivo completo en vez de un diff, ya que no hay un punto de comparación.

Esto es justo la diferencia práctica entre `mp-code-review` y `gs-review`: mattpocock exige contexto explícito (spec + estándares) antes de opinar, mientras que gstack revisa directo buscando bugs de producción. En un repo real con PRs e issues, `mp-code-review` es más preciso porque valida contra la intención declarada, no solo contra "esto se ve raro".

---

## Standards (baseline de smells de Fowler)

### Duplicated Code — `main.py`
Los 4 endpoints repiten el mismo patrón `try: ... except: return Response(error, 500)`. Es candidato a extraer un decorador o un `try/except` compartido, para que el bug del hallazgo #2 de `gs-review` (falta `return`) no pueda repetirse en el próximo endpoint que se agregue.

### Primitive Obsession — `models.py`
Todos los campos son `str`, incluyendo valores que son inherentemente numéricos: `ultimo_precio`, `monto_efectivo`, `variacion`, `capitalizacion_en_mill`. En una API de datos financieros, esto empuja el parsing/validación de números al cliente de la API en vez de garantizarlo en el modelo. Fix sugerido: tipos `Decimal` con un `validator` de Pydantic que limpie el formato (`remove_dots`/`remove_quotes` ya existen en `utils.py` — deberían vivir como validators del modelo, no como funciones sueltas aplicadas a mano en el scraper).

### Mysterious Name — `main.py`
`trigger` y `trigger2` (líneas 15-18) no comunican qué representa cada uno (scrape de las 14:00 UTC vs. las 21:00 UTC). Nombres como `trigger_scrape_midday` / `trigger_scrape_evening` costarían cero y evitarían tener que leer el `CronTrigger` para saber qué hace cada uno.

### Divergent Change — `Analisis.py`
El archivo mezcla tres responsabilidades sin relación directa: configuración de credenciales de Gemini, un cliente HTTP a mano para la API de la Bolsa de Caracas, y un script ejecutable de prueba (`if __name__ == '__main__'`). Cualquier razón para cambiar una de las tres (rotar la key, cambiar el endpoint de la Bolsa, ajustar el script de prueba) toca el mismo archivo — señal de que debería dividirse.

---

## Resumen
- **Standards:** 4 hallazgos (1 duplicación, 1 obsesión primitiva, 1 nombre confuso, 1 archivo con responsabilidades mezcladas). Ninguno es una violación de un estándar documentado (el repo no tiene ninguno) — todos son juicios contra el baseline de Fowler.
- **Spec:** omitido — no hay spec de origen para este código.

Para que `mp-code-review` rinda su valor completo en el equipo, el prerrequisito real no es la skill en sí — es tener specs/issues por feature y un `CODING_STANDARDS.md` mínimo. Sin eso, la skill funciona pero a media capacidad (como en este demo).
