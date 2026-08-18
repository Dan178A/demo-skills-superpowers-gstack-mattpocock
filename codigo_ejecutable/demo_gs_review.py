"""
Demo ejecutable: los 2 bugs "auto-fix" que encontró gs-review (gstack) en
bolsa-valores-caracas-api, reproducidos en una version minima y autocontenida
(sin FastAPI ni Selenium, solo Python estandar) para poder correrlos sin instalar nada.

Uso:
    python3 demo_gs_review.py

No requiere dependencias externas.
"""

# ---------------------------------------------------------------------------
# CASO 1 — main.py:116 — falta un `return` dentro de un except
# ---------------------------------------------------------------------------

def get_accion_detalle_BUGGY(cod_simbolo: str, stocks_db: dict) -> dict:
    """Version tal cual esta en el repo real: el except no tiene `return`."""
    try:
        stock = stocks_db[cod_simbolo]
        return {"status": 200, "data": stock}
    except KeyError:
        # BUG real (main.py linea 116): se construye la respuesta de error
        # pero nunca se retorna -> la funcion devuelve None.
        {"status": 404, "message": "Codigo de accion no encontrado"}


def get_accion_detalle_FIXED(cod_simbolo: str, stocks_db: dict) -> dict:
    """Mismo codigo con el auto-fix que propuso gs-review: agregar `return`."""
    try:
        stock = stocks_db[cod_simbolo]
        return {"status": 200, "data": stock}
    except KeyError:
        return {"status": 404, "message": "Codigo de accion no encontrado"}  # FIX


# ---------------------------------------------------------------------------
# CASO 2 — scrapper.py — silent failure: setup_driver() puede retornar None
# y scrape_and_save() nunca lo valida antes de usarlo.
# ---------------------------------------------------------------------------

def setup_driver_BUGGY(chrome_disponible: bool):
    """Simula setup_driver(): si Chrome/Selenium falla, retorna None (como en el repo real)."""
    if not chrome_disponible:
        print("   [setup_driver] Chrome no disponible -> logueando warning y retornando None")
        return None
    return {"page_source": "<html>...tabla de acciones...</html>"}


def scrapp_page_BUGGY(driver):
    # Igual que scrapper.py: usa driver.page_source sin chequear que exista.
    return driver["page_source"]


def scrape_and_save_BUGGY(chrome_disponible: bool):
    driver = setup_driver_BUGGY(chrome_disponible)
    soup = scrapp_page_BUGGY(driver)   # BUG real: si driver es None, esto truena
    return soup


def setup_driver_FIXED(chrome_disponible: bool):
    if not chrome_disponible:
        print("   [setup_driver] Chrome no disponible -> logueando warning y retornando None")
        return None
    return {"page_source": "<html>...tabla de acciones...</html>"}


def scrapp_page_FIXED(driver):
    return driver["page_source"]


def scrape_and_save_FIXED(chrome_disponible: bool):
    driver = setup_driver_FIXED(chrome_disponible)
    if driver is None:                 # FIX que propuso gs-review
        print("   [scrape_and_save] Aborting: no hay driver, se preserva el JSON anterior")
        return None
    return scrapp_page_FIXED(driver)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def separador(titulo):
    print("\n" + "=" * 70)
    print(titulo)
    print("=" * 70)


if __name__ == "__main__":
    stocks_db = {"TPG": {"nombre": "Telares de Palo Grande", "ultimo_precio": "1.20"}}

    separador("CASO 1 — main.py:116 (falta return) — codigo BUGGY (tal cual el repo)")
    resultado = get_accion_detalle_BUGGY("CODIGO_QUE_NO_EXISTE", stocks_db)
    print(f"Resultado para un codigo inexistente: {resultado!r}")
    print("-> El cliente de la API recibe None en vez de {'status': 404, ...}.")
    print("   FastAPI, al no poder validar None contra el modelo de respuesta,")
    print("   devuelve un 500 generico en vez del mensaje de error pensado.")

    separador("CASO 1 — misma llamada, codigo FIXED (con el auto-fix de gs-review)")
    resultado = get_accion_detalle_FIXED("CODIGO_QUE_NO_EXISTE", stocks_db)
    print(f"Resultado para un codigo inexistente: {resultado!r}")
    print("-> Ahora el cliente recibe el 404 con el mensaje correcto. Diferencia: 1 palabra (`return`).")

    separador("CASO 2 — scrapper.py — codigo BUGGY: Chrome falla, no se valida driver=None")
    try:
        resultado = scrape_and_save_BUGGY(chrome_disponible=False)
        print(f"Resultado: {resultado!r}")
    except Exception as e:
        print(f"CRASH no manejado: {type(e).__name__}: {e}")
        print("-> Este es el crash silencioso que describe gs-review: el job programado")
        print("   de APScheduler truena y el JSON servido por la API queda congelado")
        print("   con datos viejos, sin ninguna alerta visible para el equipo.")

    separador("CASO 2 — misma falla de Chrome, codigo FIXED (valida driver antes de usarlo)")
    resultado = scrape_and_save_FIXED(chrome_disponible=False)
    print(f"Resultado: {resultado!r}")
    print("-> No hay crash. Se loguea la falla, se aborta limpio y el JSON anterior")
    print("   se conserva intacto en vez de quedar en un estado indefinido.")

    separador("Resumen")
    print("Los 2 fixes de arriba son exactamente los que gs-review clasifico como")
    print("'auto-fix': bugs claros, de bajo riesgo, sin ambiguedad de negocio detras.")
    print("Corre este mismo archivo con pytest (test_demo_gs_review.py) para ver")
    print("los mismos casos como asserts automatizados.")
