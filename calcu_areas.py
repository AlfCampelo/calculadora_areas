import math
from typing import Union, Dict, List
from utils_json import registrar_resultado, mostrar_estadisticas_resumidas


###############################
#### FUNCIONES DE ANALISIS ####
###############################

def calcular_area(figura: str, **kwargs: float) -> Union[float, str]:
    '''
   Calcula el área de distintas figuras geométricas según los argumentos pasados.

    Parámetros:
        figura (str): Tipo de figura ('rectangulo', 'triangulo', 'circulo', 'trapecio', 'cuadrado', 'poligono regular')
        **kwargs: Parámetros de cada figura (base, altura, radio, lado, etc.)

    Retorna:
        float: Área calculada redondeada a 2 decimales.
        str: Mensaje de error si falta un argumento o la figura no es válida.
    '''

    def area_rectangulo(base: float, altura: float) -> float:
        ''' Calcula el ára del rectángulo '''
        if base <= 0 or altura <= 0:
            raise ValueError('Base y altura deben ser mayores a cero.')
        return base * altura
    

    def area_triangulo(base: float, altura: float) -> float:
        ''' Calcula el área de un triángulo '''
        if base <= 0 or altura <= 0:
            raise ValueError('Base y altura deben ser mayores que cero.')
        return (base * altura) / 2
    

    def area_circulo(radio: float) -> float:
        ''' Calcula el área de un circulo '''
        if radio <= 0:
            raise ValueError('El radio debe ser mayor de cero.')
        return math.pi * (radio ** 2)
    

    def area_trapecio(base_mayor: float, base_menor: float, altura: float) -> float:
        ''' Calcula el área de un trapecio '''
        if base_mayor <= 0 or base_menor <= 0 or altura <= 0:
            raise ValueError('Las bases y la altura deben ser mayores que cero.')
        return ((base_mayor + base_menor) / 2) * altura
    

    def area_cuadrado(lado: float) -> float:
        ''' Calcula el área de un cuadrado '''
        if lado <= 0:
            raise ValueError('El lado debe ser mayor de cero.')
        return lado ** 2
    

    def area_poligono_regular(num_lados: int, lado: float, apotema: float) -> float:
        ''' Calcula el área de un poligono regular '''
        if num_lados <= 0 or lado <= 0 or apotema <= 0:
            raise ValueError('El número de lados, el lado y el apotema deben ser mayores que cero.')
        return num_lados * ((lado * apotema) / 2)
    

    def area_elipse(semi_eje_hor: float, semi_eje_ver: float) -> float:
        ''' Calcula el área de una elipse '''
        if semi_eje_hor <= 0 or semi_eje_ver <= 0:
            raise ValueError('El valor de los semiejes deben ser mayores que cero.')
        return math.pi * semi_eje_ver * semi_eje_hor
    

    def area_corona_circular(radio_mayor: float, radio_menor: float) -> float:
        ''' Calcula el área de una corona circular '''
        if radio_mayor <= 0 or radio_menor <= 0:
            raise ValueError('El valor de los radios deben ser mayores que cero.')
        return math.pi * ((radio_mayor ** 2) - (radio_menor ** 2))
    

    def area_cubo(lado: float) -> float:
        ''' Calcula el área de un cubo '''
        if lado <= 0 :
            raise ValueError('El lado debe ser mayor que cero.')
        return 6 * (lado ** 2)
    

    def area_cono(radio: float, generatriz: float) -> float:
        ''' Calcula el área de un cono '''
        if radio <= 0 or generatriz <= 0:
            raise ValueError('El radio y la generatriz deben ser mayores que cero.')
        return math.pi * radio * (radio + generatriz)


    figuras = {
        'rectangulo': area_rectangulo,
        'triangulo': area_triangulo,
        'circulo': area_circulo,
        'trapecio': area_trapecio,
        'cuadrado': area_cuadrado,
        'poligono_regular': area_poligono_regular,
        'elipse': area_elipse,
        'corona_circular': area_corona_circular,
        'cubo': area_cubo,
        'cono': area_cono
    }

    if figura not in figuras:
        raise ValueError(f'Figura {figura}, no valida. Usa: {", ".join(figuras.keys())}')

    try:
        area = round(figuras[figura](**kwargs), 2)
        datos = {
            'figura': figura,
            'area': area,
            'parametros': kwargs
        }

        registrar_resultado(**datos)
        return area
    except TypeError:
        return f'Argumentos incorrectos para la figura {figura}'