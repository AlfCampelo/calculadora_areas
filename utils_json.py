import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from functools import lru_cache
import threading

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.json import JSON
from rich import box

console = Console()

ARCHIVO_JSON = Path('areas.json')


##############################
###### SISTEMA DE CACHÉ ######
##############################

class CacheJSON:
    ''' Sistema de caché para evitar lecturas repetidas del archivo JSON '''

    def __init__(self):
        self._cache: Optional[List[Dict]] = None
        self._timestamp: Optional[float] = None
        self._file_mtime: Optional[float] = None
        self._lock = threading.Lock()
        self._cache_duration = 60 # segundo (ajustable)

    
    def invalidar(self):
        ''' Invalida el caché forzando una nueva lectura '''
        with self._lock:
            self._cache = None
            self._timestamp = None
            self._file_mtime = None


    def is_valid(self, ruta: Path) -> bool:
        ''' Verifica si el caché es válido '''
        if self._cache is None or self._timestamp is None:
            return False
        
        # Verificar si el archivo ha cambiado
        if ruta.exists():
            current_mtime = ruta.stat().st_mtime
            if self._file_mtime != current_mtime:
                return False
        
        # Verificar si el caché ha expirado
        tiempo_transcurrido = datetime.now().timestamp() - self._timestamp
        return tiempo_transcurrido < self._cache_duration
    

    def get(self, ruta: Path) -> Optional[List[Dict]]:
        ''' Obtiene datos del caché si es válido '''
        with self._lock:
            if self.is_valid(ruta):
                return self._cache.copy() if self._cache else None
            return None
        

    def set(self, ruta: Path, datos: List[Dict]):
        ''' Guarda datos en el caché '''
        with self._lock:
            self._cache = datos.copy() if datos else []
            self._timestamp = datetime.now().timestamp
            if ruta.exists():
                self._file_mtime = ruta.stat().st_mtime


# Instancia global del caché
_cache_global = CacheJSON()


################################
###### FUNCION DE LECTURA ######
################################

def cargar_json(ruta: Path=ARCHIVO_JSON, default=None, usar_cache: bool=True) -> List[Dict]:
    '''
    Carga datos desde un archivo JSON con sistema de caché.
    
    :param ruta: Ruta al archivo JSON
    :type ruta: Path
    :param default: Valor por defecto si el archivo no existe.
    :param usar_cache: Si True, usa el sistema de caché.
    :type usar_cache: bool
    :return: Lista de diccionarios con los datos.
    :rtype: List[Dict]
    '''

    # Intenta obtener del caché primero
    if usar_cache:
        datos_cache = _cache_global.get(ruta)
        if datos_cache is not None:
            return datos_cache
        
    # Si no hay caché válido, leer del archivo
    if ruta.exists():
        try:
            with ruta.open('r', encoding='utf-8') as f:
                datos = json.load(f)

                # Guardar en caché
                if usar_cache:
                    _cache_global.set(ruta, datos)
                
                return datos
        except json.JSONDecodeError as e:
            console.print(f'[red]Error al decodificar JSON: {e}[/red]')
            return default or []
        except Exception as e:
            console.print(f'[red]Error al leer el archivo: {e}[/red]')
            return default or []
    
    return default or []


##################################
###### FUNCION DE ESCRITURA ######
##################################

def guardar_json_append(dato: Dict, ruta: Path=ARCHIVO_JSON) -> bool:
    '''
    Agrega un registro al final del archivo sin reescribir todo.
    ADVERTENCIA: Requiere que el archivo JSON esté formateado como array.
    
    :param dato: Diccionario con los datos a guardar
    :type dato: Dict
    :param ruta: Ruta al archivo JSON
    :type ruta: Path
    :return: True si se guardo correctamente, False en caso contrario.
    :rtype: bool
    '''

    try:
        if not ruta.exists() or ruta.stat().st_size == 0:
            # Si no existe crear nuevo archivo
            with ruta.open('w', encoding='utf-8') as f:
                json.dump([dato], f, ensure_ascii=False, indent=4)
        else:
            # Leer el archivo y agregar al final
            with ruta.open('r+', encoding='utf-8') as f:
                # Ir al final del archivo y retroceder para quitar el ']'
                f.seek(0, 2) # Ir al final
                size = f.tell()

                # Retroceder hasta encontrar el ']'
                f.seek(size -1)
                while f.tell() > 0:
                    char = f.read(1)
                    if char == ']':
                        f.seek(f.tell() - 1)
                        break
                    f.seek(f.tell() - 2)

                # Determinar si necesitamos coma
                pos = f.tell()
                if pos > 1:
                    f.seek(pos -1)
                    prev_char = f.read(1)
                    f.seek(pos)

                    if prev_char != '[':
                        f.write(',\n')
                
                # Escribir el nuevo dato
                json_str = json.dumps(dato, ensure_ascii=False, indent=4)
                # Indentar correctamente
                lines = json_str.split('\n')
                indented = '\n'.join('    ' + line if line.strip() else line for line in lines)
                f.write(indented)
                f.write('\n')

            # Invalidar caché
            _cache_global.invalidar()
            return True
    except Exception as e:
        console.print(f'[red]Error en append: {e}[/red]')
        return False
    

#####################################
###### FUNCIONES CON CACHÉ LRU ######
#####################################

@lru_cache(maxsize=128)
def obtener_figura_mas_frecuente_cached(datos_tuple) -> str:
    '''
    Versión cacheada de obtener_figura_mas_frecuente    
    :param datos_tuple: Usa tuple porque las listas no son hashables
    :return: Descripción
    :rtype: str
    '''
    from collections import Counter
    figuras = [dato['figura'] for dato in datos_tuple if 'figura' in dato]
    if not figuras:
        return 'ninguna'
    contador = Counter(figuras)
    return contador.most_common(1)[0][0]

@lru_cache(maxsize=128)
def calcular_estadisticas_cached(datos_tuple) -> Dict:
    ''' Calcula estadisticas con caché LRU '''
    datos = list(datos_tuple)

    areas = [
        d.get('area', 0)
        for d in datos 
        if isinstance(d.get('area'), (int, float))
    ]

    if not areas:
        return {
            'total_calculos': len(datos),
            'area_promedio': 0,
            'area_maxima': 0,
            'area_minima': 0,
            'figura_mas_calculada': 'ninguna'
        }
    
    return {
            'total_calculos': len(datos),
            'area_promedio': sum(areas) / len(areas),
            'area_maxima': max(areas),
            'area_minima': min(areas),
            'figura_mas_calculada': obtener_figura_mas_frecuente_cached(datos_tuple)
    }



##################################
###### FUNCIONES AUXILIARES ######
##################################

def obtener_fecha() -> str:
    ''' Retorna la fecha y la hora actual formateada '''
    return datetime.now().strftime('%d/%m/%Y %H:%M:%S')


def registrar_resultado(**kwargs):
    ''' Registra un resultado de cálcudo en el JSON '''
    dato = {'fecha': obtener_fecha(), **kwargs}
    return guardar_json_append(dato)


def datos_a_tuple(datos: List[dict]) -> tuple:
    ''' Convierte lista de diccionarios a tupla para usar con caché '''

    def dict_to_tuple(d):
        ''' Convierte un diccionario (inclucso con valores anidaddos) a tupla '''
        items = []
        for k, v in sorted(d.items()):
            if isinstance(v, dict):
                items.append((k, dict_to_tuple(v)))
            elif isinstance(v, list):
                items.append((k, tuple(v)))
            else:
                items.append((k, v))
        return tuple(items)
    
    try:
        return tuple(dict_to_tuple(d) for d in datos)
    except (TypeError, AttributeError):
        # Si falla la conversión, usar un hash simple basado en el JSON string
        import hashlib
        json_str = json.dumps(datos, sort_keys=True)
        return (hashlib.md5(json_str.encode()).hexdigest(),)
    


########################################
###### FUNCIONES DE VISUALIZACIÓN ######
########################################

def mostrar_json(limite: Optional[int]=None) -> None:
    '''
    Muestra todos los datos del JSON con Rich en formato tabla
    
    :param limite: Si se especifica, muestra solo los últimos n registros
    :type limite: Optional[int]
    '''

    datos = cargar_json()

    if not datos:
        console.print(Panel(
            '[yellow]📂 No hay datos guardados aún.[/yellow]',
            title='Historial vacío',
            border_style='yellow'
        ))
        return
    
    # Aplicar límite si se especifica
    if limite and len(datos) > limite:
        datos_mostrar = datos[-limite:]
        titulo = f'📊 ÚLTIMOS {limite} CÁLCULOS (de {len(datos)} totales)'
    else:
        datos_mostrar = datos
        titulos = f'📊 HISTORIAL DE CÁLCULOS ({len(datos)} registros)'

    # Crear tabla
    table = Table(
        title=titulo,
        title_style='bold cyan',
        box=box.ROUNDED,
        show_header=True,
        header_style='bold magenta',
        border_style='cyan',
        expand=False
    )

    # Añadir columnas
    table.add_column('#', style='yellow', justify='right', width=4)
    table.add_column('Fecha', style='cyan', width=17)
    table.add_column('Figura', style='green', width=20)
    table.add_column('Área', style='bold blue',justify='right', width=12)
    table.add_column('Parámetros', style='magenta', width=40)

    # Añadir filas
    inicio = len(datos) - len(datos_mostrar) + 1
    for i, registro in enumerate(datos_mostrar, inicio):
        fecha = registro.get('fecha', 'N/D')
        figura = registro.get('figura', 'desconocida')
        area = registro.get('area', 'N/D')
        params = registro.get('parametros', {})

        # Formatear parámetros
        if isinstance(params, dict):
            params_str = '\n'.join([f'{k}: {v}' for k, v in params.items()])
        else:
            params_str = str(params)

        # Formatear área
        area_str = f'{area:.2f}' if isinstance(area, (int, float)) else str(area)

        table.add_row(
            str(i),
            fecha,
            figura.replace('_', ' ').title(),
            area_str,
            params_str
        )
    
    console.print(table)

    # Mostrar estadísticas (usando caché)
    mostrar_estadisticas_resumidas(datos)


def mostrar_estadisticas_resumidas(datos: List[Dict]) -> None:
    ''' Muestras estadísticas resumidas usando caché '''
    if not datos:
        return
    
    try:
        # Convertir datos a tuple para usar caché
        datos_tuple = datos_a_tuple(datos)
        stats = calcular_estadisticas_cached(datos_tuple)
    except Exception as e:
        # Si falla el caché, calcular sin caché
        console.print(f'[dim yellow]Calculando sin caché...[/dim yellow]')
        stats = calcular_estadisticas_sin_cache(datos)

    # Crear tabla de estadísticas
    stats_table = Table(
        title='📈 Estadísticas',
        box=box.SIMPLE,
        show_header=False,
        border_style='green',
        expand=False
    )    

    stats_table.add_column(style='cyan')
    stats_table.add_column(style='yellow', justify='right')

    stats_table.add_row('Total de cálculos:', str(stats['total_calculos']))

    if stats['area_promedio'] > 0:
        stats_table.add_row('Área promedio:', f'{stats["area_promedio"]:.2f}')
        stats_table.add_row('Área máxima:', f'{stats["area_maxima"]:.2f}')
        stats_table.add_row('Área mínima:', f'{stats["area_minima"]:.2f}')

    stats_table.add_row(
        'Figura más calculada',
        stats['figura_mas_calculada'].replace('_', ' ').title()
    )
    console.print('\n')
    console.print(stats_table)


def calcular_estadisticas_sin_cache(datos: List[Dict]) -> Dict:
    ''' Calcular estadísticas sin usar caché '''
    from collections import Counter

    areas = [
        d.get('area', 0)
        for d in datos
        if isinstance(d.get('area'), (int, float))
    ]

    figuras = [d.get('figura', 'desconocida') for d in datos if 'figura' in d]

    if not areas:
        return {
            'total_calculos': 0,
            'area_promedio': 0,
            'area_maxima': 0,
            'area_minima': 0,
            'figura_mas_calculada': Counter(figuras).most_common(1)[0][0] if figuras else 'ninguna'
        }
    
    return {
            'total_calculos': len(datos),
            'area_promedio': sum(areas) / len(areas),
            'area_maxima': max(areas),
            'area_minima': min(areas),
            'figura_mas_calculada': Counter(figuras).most_common(1)[0][0] if figuras else 'ninguna'
        }


def mostrar_ultimos_calculos(n: int=5) -> None:
    ''' Muestra los últimos n cálculos realizados '''
    datos = cargar_json()

    if not datos:
        console.print(Panel(
            '[yellow]📂 No hay datos guardados aún.[/yellow]',
            title='Historial vacío',
            border_style='yellow'
        ))
        return
    
    # Tomar los últimos n registros
    ultimos = datos[-n:] if len(datos) >= n else datos

    table = Table(
        title=f'🕒 Últimos {len(ultimos)} cálculos (de {len(datos)} totales)',
        title_style='bold cyan',
        box=box.ROUNDED,
        show_header=True,
        header_style='bold magenta',
        border_style='cyan',
        expand=False
    )

    # Calcular el número inicial (para mostrar la posición real)
    inicio = len(datos) - len(ultimos) + 1

    for i, registro in enumerate(ultimos, inicio):
        fecha = registro.get('fecha', 'N/D'),
        figura = registro.get('figura', 'desconocida').replace('_', ' ').title(),
        area = registro.get('area', 'N/D'),
        params = registro.get('parametros', {})

        # Formatear parámetros
        if isinstance(params, dict):
            params_str = '\n'.join([f'{k}: {v}' for k, v in params.items()])
        else:
            params_str = str(params)

        # Formatear área
        area_str = f'{area:.2f}' if isinstance(area, (int, float)) else str(area)

        table.add_row(str(i), fecha, figura, area_str, params_str)
    
    console.print(table)


def limpiar_historial() -> bool:
    ''' Elimina todos los registros del historial '''
    try:
        if ARCHIVO_JSON.exists():
            ARCHIVO_JSON.unlink()
            _cache_global.invalidar()
            console.print(Panel(
                '[green]✅ Historial limpiado exitosamente[/green]',
                border_style='green'
            ))
            return True
        else:
            console.print(Panel(
                f'[yellow]⚠️ No hay historial para limpiar[/yellow]',
                border_style='yellow'
            ))
            return False
    except Exception as e:
        console.print(Panel(
                '[yellow]⚠️ No hay historial para limpiar[/yellow]',
                border_style='yellow'
            ))
        return False

    


    