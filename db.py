import json
import os

ARCHIVO_PERFILES = "perfiles.json"

# Rangos definidos con sus umbrales de puntos
RANGOS = [
    {"nombre": "Semilla Climática",  "emoji": "🌱", "puntos_min": 0},
    {"nombre": "Brote Verde",        "emoji": "🌿", "puntos_min": 50},
    {"nombre": "Árbol Protector",    "emoji": "🌳", "puntos_min": 150},
    {"nombre": "Bosque Sostenible",  "emoji": "🌲", "puntos_min": 300},
    {"nombre": "Guardián Climático", "emoji": "🌍", "puntos_min": 500},
]


def cargar_perfiles():
    """Lee el archivo JSON. Si no existe, devuelve un diccionario vacío."""
    if not os.path.exists(ARCHIVO_PERFILES):
        return {}
    try:
        with open(ARCHIVO_PERFILES, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def guardar_perfiles(datos):
    """Guarda el diccionario de perfiles en el archivo JSON."""
    with open(ARCHIVO_PERFILES, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)


def obtener_rango_por_puntos(puntos: int):
    """Devuelve la información del rango correspondiente a la cantidad de puntos."""
    rango_actual = RANGOS[0]
    for r in RANGOS:
        if puntos >= r["puntos_min"]:
            rango_actual = r
    return rango_actual


def sumar_puntos_usuario(user_id: int, puntos_ganados: int = 10):
    """
    Suma puntos al usuario, actualiza sus estadísticas y verifica si subió de nivel.
    Retorna un diccionario con la información del resultado.
    """
    str_id = str(user_id)
    perfiles = cargar_perfiles()

    # Si el usuario no existía en la base de datos, lo creamos
    if str_id not in perfiles:
        perfiles[str_id] = {
            "puntos": 0,
            "rango": "Semilla Climática",
            "quizzes_correctos": 0
        }

    puntos_anteriores = perfiles[str_id]["puntos"]
    rango_anterior = obtener_rango_por_puntos(puntos_anteriores)

    # Actualizamos los datos
    perfiles[str_id]["puntos"] += puntos_ganados
    perfiles[str_id]["quizzes_correctos"] += 1

    puntos_nuevos = perfiles[str_id]["puntos"]
    rango_nuevo = obtener_rango_por_puntos(puntos_nuevos)

    # Verificamos si subió de nivel (si cambió de rango)
    subio_de_nivel = rango_nuevo["nombre"] != rango_anterior["nombre"]
    perfiles[str_id]["rango"] = rango_nuevo["nombre"]

    # Guardamos los cambios
    guardar_perfiles(perfiles)

    return {
        "puntos_totales": puntos_nuevos,
        "puntos_ganados": puntos_ganados,
        "subio_de_nivel": subio_de_nivel,
        "rango_nuevo": rango_nuevo
    }


def obtener_leaderboard():
    """Devuelve una lista ordenada de usuarios con sus puntos y rangos."""
    perfiles = cargar_perfiles()
    # Ordenamos de mayor a menor cantidad de puntos
    usuarios_ordenados = sorted(
        perfiles.items(), 
        key=lambda item: item[1]["puntos"],
        reverse=True
    )
    return usuarios_ordenados
