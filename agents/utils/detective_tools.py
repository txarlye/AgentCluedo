from langchain_core.tools import tool

# de momento sólo devuelve texto, luego ya se implementará

@tool
def interrogar(sospechoso: str, pregunta:str) ->str:
    """
    Usa esta herramienta para interrogar a un sospechoso.
    Especifica el nombre del sospechoso(ej: 'Mayordomo','Heredera') y la pregunta exacta.
    """
    print(f"DEBUG: [Herramienta 'interrogar' llamada] -> {sospechoso}, {pregunta}")
    
    return f"Respuesta (simulada) de {sospechoso}: No recuerdo nada sobre eso"

@tool
def buscar_pista(ubicacion: str) -> str:
    """
    Usa esta herramienta para buscar pistas en una ubicación específica de la mansión.
    Especifica la ubicación (el: 'biblioteca', 'cocina', 'habitacion de la víctima').
    """
    print(f"DEBUG: [Herramienta 'buscar pista' llamada] -> {ubicacion}")
    return f" Al buscar en {ubicacion} encuentras (simulado): un pañuelo manchado"
@tool
def acusar(sospechoso: str)->str:
    """
    Usa esta herramienta SÓLO cuando estés 100% seguro de quién es el asesino.
    Esto termina el juego. Especifica el nombre del sospechoso y si no es el asesino entonces pierdes.
    """
    print(f"DEBUG: [Herramienta 'acusar' llamada] -> {sospechoso}")
    return f"Has acusado a {sospechoso}. (simulado) has resuelto el caso !"
    