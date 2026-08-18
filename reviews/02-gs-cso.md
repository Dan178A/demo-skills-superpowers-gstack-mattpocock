# Demo: `gs-cso` (gstack) — auditoría de seguridad aplicada a `bolsa-valores-caracas-api`

**Skill:** `gs-cso` — auditoría estilo Chief Security Officer (OWASP Top 10 + STRIDE), con gate de confianza 8/10+ y escenario de exploit obligatorio por hallazgo.

---

## Hallazgo 1 — Secreto hardcodeado en texto plano (CONFIRMADO)
**Archivo:** `Analisis.py`, línea 6
**OWASP:** A05:2021 – Security Misconfiguration / A02:2021 – Cryptographic Failures (exposición de credenciales)
**STRIDE:** Information Disclosure, Elevation of Privilege (uso no autorizado de un servicio pago con la identidad del dueño de la cuenta)

```python
genai_client = genai.Client(api_key='AIzaSy************************') # API key de Google Gemini en texto plano
```

**Escenario de exploit concreto:** cualquier persona con acceso al repositorio (o que lo encuentre si se sube a GitHub, aunque sea en un repo "privado" que luego se hace público por error) puede copiar la key y usarla directamente contra la API de Gemini. Con eso puede: (a) generar consumo facturado a la cuenta de Google Cloud del dueño de la key hasta agotar la cuota o generar cargos, o (b) usar la key para sus propios proyectos sin que quede ningún rastro de quién la usó, porque la key sigue identificándose como el proyecto original.

**Impacto:** cargos no autorizados / agotamiento de cuota (DoS económico) + no hay forma de revocar el acceso de un atacante específico sin rotar la key para todos.

**Fix específico:** revocar esta key desde Google AI Studio / Google Cloud Console **ahora mismo** (ya quedó expuesta en este repo local), mover la key a una variable de entorno (`os.environ['GEMINI_API_KEY']`), y agregar `.env` al `.gitignore` si no está ya.

---

## Hallazgo 2 — Cookie de sesión hardcodeada
**Archivo:** `Analisis.py`, línea 43
**OWASP:** A05:2021 – Security Misconfiguration
**STRIDE:** Spoofing (si la sesión sigue viva, alguien podría reusarla para hacerse pasar por esa sesión ante bolsadecaracas.com)

```python
cookies = {'PHPSESSID': 'fe859ef36c3b3227345b58ee45a8a08f'}
```

**Escenario de exploit:** el impacto real depende de qué privilegios tenga esa sesión en el sitio de la Bolsa de Caracas — si es una sesión anónima de scraping, el riesgo es bajo (ya lo dice el propio comentario del código: "podrías necesitar actualizar el PHPSESSID", sugiriendo que ya se sabe que expira). No cumple el gate de confianza 8/10+ para tratarlo como vulnerabilidad crítica, pero sí como mala práctica: no debería viajar en el código fuente.

**Clasificación:** reportado como hallazgo de higiene, no como vulnerabilidad crítica confirmada (no se pudo construir un exploit de alto impacto sin saber qué protege esa sesión del lado del servidor).

---

## Revisado y descartado (para que quede constancia de que no es "reportar todo")
- **Selenium con `--headless` scrapeando un sitio público:** no hay input de usuario que llegue a un comando o query — no aplica inyección.
- **Endpoints de FastAPI (`main.py`):** son de solo lectura (`GET`), sin autenticación porque el dato es público (cotizaciones de bolsa). No hay broken access control que reportar porque no hay control de acceso que debiera existir.
- **Lectura de archivos JSON con `open()`:** las rutas son fijas en el código (`json/stocks.json`), no vienen de input del usuario — no hay path traversal.

## Resumen
- **1 hallazgo crítico confirmado:** API key de Gemini expuesta en texto plano — acción inmediata: rotar la key.
- **1 hallazgo de higiene:** cookie de sesión hardcodeada.
- **0 falsos positivos reportados** — se descartaron 3 candidatos que no pasaron el gate de exploit concreto.
