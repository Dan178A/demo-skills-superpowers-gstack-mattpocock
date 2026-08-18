"""
Suite de pytest que prueba, de forma automatizada, el antes/despues de los
2 bugs reales encontrados con gs-review en bolsa-valores-caracas-api.

Uso:
    pip install pytest --break-system-packages   # si no lo tienes
    pytest test_demo_gs_review.py -v
"""

import pytest
from demo_gs_review import (
    get_accion_detalle_BUGGY, get_accion_detalle_FIXED,
    scrape_and_save_BUGGY, scrape_and_save_FIXED,
)

stocks_db = {"TPG": {"nombre": "Telares de Palo Grande", "ultimo_precio": "1.20"}}


# --- Caso 1: falta return -----------------------------------------------

def test_caso1_buggy_devuelve_None_en_vez_de_error():
    """Reproduce el bug real: la version BUGGY devuelve None (no un 404)."""
    resultado = get_accion_detalle_BUGGY("NO_EXISTE", stocks_db)
    assert resultado is None  # <- esto es el bug: se pierde el mensaje de error


def test_caso1_fixed_devuelve_404_correcto():
    """La version FIXED sí retorna el error 404 esperado."""
    resultado = get_accion_detalle_FIXED("NO_EXISTE", stocks_db)
    assert resultado == {"status": 404, "message": "Codigo de accion no encontrado"}


def test_caso1_ambas_versiones_funcionan_igual_en_el_happy_path():
    """El bug solo afecta el camino de error; el caso feliz es identico."""
    buggy = get_accion_detalle_BUGGY("TPG", stocks_db)
    fixed = get_accion_detalle_FIXED("TPG", stocks_db)
    assert buggy == fixed == {"status": 200, "data": stocks_db["TPG"]}


# --- Caso 2: silent failure con driver=None ------------------------------

def test_caso2_buggy_crashea_si_chrome_no_esta_disponible():
    """Reproduce el crash real: TypeError al indexar un driver que es None."""
    with pytest.raises(TypeError):
        scrape_and_save_BUGGY(chrome_disponible=False)


def test_caso2_fixed_no_crashea_y_retorna_None_limpio():
    """La version FIXED valida driver antes de usarlo: falla controlada, no crash."""
    resultado = scrape_and_save_FIXED(chrome_disponible=False)
    assert resultado is None  # abortó limpio, no lanzó excepción


def test_caso2_ambas_versiones_funcionan_igual_si_chrome_si_esta_disponible():
    """El bug solo aparece cuando falla Chrome; con Chrome funcionando, ambas dan lo mismo."""
    buggy = scrape_and_save_BUGGY(chrome_disponible=True)
    fixed = scrape_and_save_FIXED(chrome_disponible=True)
    assert buggy == fixed == "<html>...tabla de acciones...</html>"
