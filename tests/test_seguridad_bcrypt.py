"""
Pruebas unitarias de Seguridad y Hashing de contraseñas con Bcrypt (RNF-SEG-001).
"""
import pytest
from app.core import security


def test_hashing_contrasena_genera_hash_distinto_al_texto_plano():
    password_plana = "ClaveSecretaHotel2026*"
    hash_resultado = security.get_password_hash(password_plana)

    assert hash_resultado != password_plana
    assert hash_resultado.startswith("$2b$") or hash_resultado.startswith("$2a$")


def test_verificacion_exitosa_contrasena_correcta():
    password_plana = "SuperPasswordSegura!"
    hash_resultado = security.get_password_hash(password_plana)

    es_valida = security.verify_password(password_plana, hash_resultado)
    assert es_valida is True


def test_verificacion_falla_con_contrasena_incorrecta():
    password_plana = "SuperPasswordSegura!"
    password_falsa = "PasswordEquivocada?"
    hash_resultado = security.get_password_hash(password_plana)

    es_valida = security.verify_password(password_falsa, hash_resultado)
    assert es_valida is False


def test_dos_hashes_de_la_misma_contrasena_son_diferentes_por_salt():
    password = "ClaveConSaltDinamico"
    hash_1 = security.get_password_hash(password)
    hash_2 = security.get_password_hash(password)

    assert hash_1 != hash_2
    assert security.verify_password(password, hash_1) is True
    assert security.verify_password(password, hash_2) is True
