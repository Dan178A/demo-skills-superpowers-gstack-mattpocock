# Demo: `gs-review` (gstack) aplicado a `bolsa-valores-caracas-api`

**Skill:** `gs-review` — "Staff-engineer style code review focused on bugs that pass CI but break production."
**Alcance:** `main.py`, `scrapper.py` (el repo no tiene tests ni CI, así que se revisó el código completo en vez de un diff).

---

## Lo que se rompería en producción (no lo agarraría un linter)

### 1. Silent failure — `scrape_and_save()` puede crashear sin avisar
**Archivo:** `scrapper.py`, líneas 21-31 y 147-166

`setup_driver()` captura cualquier excepción, loggea un warning y **retorna `None`**:

```python
except Exception as e:
    logger.warning(...)
    return None
```

Pero `scrape_and_save()` nunca verifica ese `None`:

```python
driver = setup_driver()
soup = scrapp_page(driver)   # driver.page_source con driver=None -> AttributeError
```

**Escenario concreto:** si Chrome no está disponible en el contenedor, o la página tarda en responder, el job programado (corre 2 veces al día vía APScheduler) truena con una excepción no manejada. APScheduler la loggea y sigue, pero el JSON servido por `/acciones` queda **congelado con datos viejos indefinidamente**, sin que nadie se entere hasta que un usuario reporte precios desactualizados.

**Clasificación:** Auto-fix — agregar `if driver is None: return` con log de error antes de seguir.

---

### 2. Bug real: falta un `return` — `main.py` línea 116
**Archivo:** `main.py`

```python
except:
    Response(content='Error al obtener la informacion', status_code=500)
```

Falta el `return`. El objeto `Response` se crea y se descarta; la función retorna `None`. Como el endpoint declara `-> StockDetail`, FastAPI lanza un `ResponseValidationError` (500 genérico) en vez del mensaje de error pensado para el usuario. Es el único de los 4 endpoints con este bug — los otros 3 sí tienen `return`.

**Clasificación:** Auto-fix — bug de una línea, sin ambigüedad.

---

### 3. Manejo de errores incompleto — `except:` desnudo en los 4 endpoints
**Archivo:** `main.py`, líneas 49, 64, 115, 133

Los 4 endpoints capturan **cualquier excepción** (incluyendo `KeyError`, `ValidationError` de Pydantic, `FileNotFoundError`) y las tratan todas igual, sin loggear qué fue lo que realmente falló. Si el scraper cambia el formato del JSON o un campo nuevo no matchea el modelo Pydantic, el error real queda invisible — solo se ve "Error al obtener la informacion" en los logs del cliente, nada en los logs del servidor.

**Clasificación:** Flag as gap — no es un bug que rompa hoy, pero es deuda que dificulta debuggear producción cuando algo falle.

---

### 4. Estado compartido mutado sin aislamiento — `os.chdir()` en el scraper
**Archivo:** `scrapper.py`, líneas 157-165

```python
os.chdir('json')
dump_json(...)
os.chdir('..')
```

`os.chdir` cambia el directorio de trabajo **del proceso entero**, no solo de esta función. Si en el futuro se agrega concurrencia (por ejemplo, otro job de APScheduler corriendo en paralelo, o un endpoint que lee/escribe archivos relativos durante la ventana en que el cwd está en `json/`), cualquier operación con rutas relativas en ese momento apunta al lugar equivocado. Hoy no truena porque solo hay un scraper corriendo secuencialmente, pero es exactamente el tipo de bug que "pasa el CI" y rompe producción el día que alguien agrega un segundo job.

**Clasificación:** Ask — no es urgente arreglarlo si nunca habrá concurrencia, pero vale la pena decidirlo explícitamente (reemplazar por rutas absolutas con `pathlib`).

---

### 5. Parsing frágil por posición — `get_stocks()`
**Archivo:** `scrapper.py`, líneas 84-109

El parser asume que la tabla siempre entrega exactamente múltiplos de 6 celdas por fila (`zip(keys, data[i:i+6])`, `i += 6`). Si el sitio web agrega o quita una columna, o una celda viene vacía y `row.string` es `None` (se filtra sin dejar rastro con `data = [x for x in data if x is not None]`), el resto de las filas se **desalinea silenciosamente**: el precio de una acción termina en el campo de otra.

**Clasificación:** Flag as gap — no hay validación de que `len(data) % 6 == 0` antes de hacer el zip.

---

## Resumen (formato gs-review)
- **Auto-fix (2):** falta `return` en línea 116 de `main.py`; verificación de `driver is None` en `scrape_and_save()`.
- **Ask (1):** `os.chdir` como estado global compartido.
- **Gaps (2):** manejo de errores que oculta la causa real; parsing posicional sin validación de longitud.

Nada de esto lo agarra un linter ni pytest (no hay tests en el repo) — es exactamente la categoría de bug que `gs-review` está diseñado para encontrar.
