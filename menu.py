from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

from calcu_areas import calcular_area
from utils_json import mostrar_json, mostrar_ultimos_calculos, limpiar_historial, buscar_por_figura

console = Console()


##################################
#### CONFIGURACIÓN DE FIGURAS ####
##################################

FIGURAS_CONFIG = {
    '1': {
        'nombre': 'rectangulo',
        'titulo': 'Rectángulo',
        'params': [
            ('base', 'Introduce la base', 'float'),
            ('altura', 'Introduce la altura', 'float')
        ]
    },
    '2': {
        'nombre': 'triangulo',
        'titulo': 'Triángulo',
        'params': [
            ('base', 'Introduce la base', 'float'),
            ('altura', 'Introduce la altura', 'float')
        ]
    },
    '3': {
        'nombre': 'circulo',
        'titulo': 'Circulo',
        'params': [
            ('radio', 'Introduce el radio', 'float')
        ]
    },
    '4': {
        'nombre': 'trapecio',
        'titulo': 'Trapecio',
        'params': [
            ('base_mayor', 'Introduce la base mayor', 'float'),
            ('base_menor', 'Introduce la base menor', 'float'),
            ('altura', 'Introduce la altura', 'float')
        ]
    },
    '5': {
        'nombre': 'cuadrado',
        'titulo': 'Cuadrado',
        'params': [
            ('lado', 'Introduce el lado', 'float')
        ]
    },
    '6': {
        'nombre': 'poligono_regular',
        'titulo': 'Poligono regular',
        'params': [
            ('num_lados', 'Introduce el número de lados', 'int'),
            ('lado', 'Introduce el lado', 'float'),
            ('apotema', 'Introduce el apotema', 'float')
        ]
    },
    '7': {
        'nombre': 'elipse',
        'titulo': 'Elipse',
        'params': [
            ('semi_eje_hor', 'Introduce el semieje horizontal', 'float'),
            ('semi_eje_ver', 'Introduce el semieje vertical', 'float')
        ]
    },
    '8': {
        'nombre': 'corona_circular',
        'titulo': 'Corona circular',
        'params': [
            ('radio_mayor', 'Introduce el radio mayor', 'float'),
            ('radio_menor', 'Introduce el radio menor', 'float')
        ]
    },
    '9': {
        'nombre': 'cubo',
        'titulo': 'Cubo',
        'params': [
            ('lado', 'Introduce el lado', 'float')
        ]
    },
    '10': {
        'nombre': 'cono',
        'titulo': 'Cono',
        'params': [
            ('radio', 'Introduce el radio', 'float'),
            ('generatriz', 'Introduce la generatriz', 'float')
        ]
    }
}


##############################
#### FUNCIONES AUXILIARES ####
##############################

def pedir_float(mensaje: str) -> float:
    ''' Solicita un número float positivo al usuario '''
    while True:
        try:
            valor = float(Prompt.ask(mensaje))
            if valor <= 0:
                raise ValueError
            return valor
        except ValueError:
            console.print('[red]Ingresa un número válido mayor que cero.')


def pedir_int(mensaje: str) -> int:
    ''' Solicita un número entero positivo al usuario '''
    while True:
        try:
            valor = int(Prompt.ask(mensaje))
            if valor <= 0:
                raise ValueError
            return valor
        except ValueError:
            console.print('[red]Ingresa un número entero válido mayor que cero.')


def procesar_figura(config: dict) -> None:
    '''
        Procesa el cálculo del área para cualquier figura según su configuración.

        Args:
            config: Diccionario con la configuración de la figura
                (nombre, titulo, params)
    '''
    try:
        # Recopilar parámetros dinámicamente
        parametros = {}
        for param_name, mensaje, tipo in config['params']:
            if tipo == 'int':
                parametros[param_name] = pedir_int(mensaje)
            elif tipo == 'float':
                parametros[param_name] = pedir_float(mensaje)
        
        # Calcular área
        area = calcular_area(config['nombre'], **parametros)

        # Mostrar resultado
        mostrar_resultado(config['titulo'], area=area)
    
    except ValueError as e:
        console.print(Panel(
            f'[bold red]⚠️ Error: {e}[/bold red],',
            border_style='red'
        ))
    except Exception as e:
        console.print(Panel(
            f'[bold red]❌ Error inesperado: {e}[/bold red],',
            border_style='red'
        ))


def mostrar_resultado(nombre_figura: str, area: float) -> None:
    ''' Muestra el resultado del cálculo de forma atractiva '''

    console.print(Panel.fit(
        f'[bold cyan]Área del {nombre_figura.lower()}[/bold cyan]'
        f'[bold green]📏{area} unidades[/bold green]',
        border_style='green' 
    ))
    


def mostrar_menu() -> None:
    ''' Muestra el menú principal con todas las opciones '''

    table = Table(title='MENÚ ÁREA', style='bold blue')

    table.add_column('Opción', style='yellow', justify='center')
    table.add_column('Descripción')

    # Agregar figuras desde la configuración
    for opcion, config in FIGURAS_CONFIG.items():
        table.add_row(opcion, config['titulo'])
    
    # Agregar opciones adicionales
    table.add_row('11', 'Mostrar JSON')
    table.add_row('12', 'Buscar historial por figura')
    table.add_row('13', 'Últimos cálculos')
    table.add_row('14', 'Limpiar historial')
    table.add_row('15', 'Salir')

    console.print(table)


def buscar_historial() -> None:
    ''' Permite al usuario buscar en el historial por figura '''
    # Crear lista de figuras para búsqueda
    figuras_busqueda = [
        (str(i), config['nombre'], config['titulo'])
        for i, (_, config) in enumerate(FIGURAS_CONFIG.items(), 1)
    ]
    
    # Mostrar tabla de opciones
    table = Table(title='Buscar en el historial', style='bold blue')
    table.add_column('Opción', style='yellow', justify='center')

    for opcion, _, titulo in figuras_busqueda:
        table.add_row(opcion, titulo)

    console.print(table)

    # Solicitar opción
    try:
        index_str = Prompt.ask(
            'Introduce el número de la figura a buscar',
            choices=[str(i) for i in range(1, len(figuras_busqueda) + 1)]
        )
        index = int(index_str) -1
        nombre_figura = figuras_busqueda[index][1]
        buscar_por_figura(figura=nombre_figura)
    except(ValueError, IndexError) as e:
        console.print(Panel(f'[bold red]Error: {e}[/bold red]', border_style='red'))



########################
#### MENÚ PRINCIPAL ####
########################

def menu() -> None:
    ''' Menú principal de la aplicación '''
    while True:
        try:
            mostrar_menu()

            opcion = Prompt.ask(
                '\n[bold cyan]Elige una opción[/bold cyan]',
                choices=[str(i) for i in range(1, 16)]
            )

            # Procesar figuras geometricas (opciones 1-10)
            if opcion in FIGURAS_CONFIG:
                procesar_figura(FIGURAS_CONFIG[opcion])

            # Mostrar JSON (opción 11)
            elif opcion == '11':
                console.print('\n[bold cyan]=== HISTORIAL DE CÁLCULOS ===[/bold cyan]\n')
                mostrar_json()
            
            # Buscar historial (opción 12)
            elif opcion == '12':
                buscar_historial()

            # Mostrar últimos n cálculos (opción 13)
            elif opcion == '13':
                while True:
                    try:
                        n = int(Prompt.ask(
                            '\n[bold cyan]¿Cuantos calculos deseas buscar?[/bold cyan]'
                        ))
                        mostrar_ultimos_calculos(n)
                        break
                    except ValueError:
                            console.print(Panel(
                                '[bold red]⚠️ Error: Debes introducir un número entero válido.[/bold red]'
                            ))
            
            # Limpiar historial (opción 14)
            elif opcion == '14':
                confirmacion = Prompt.ask(
                    '[bold yellow]⚠️ ¿Estás seguro de que deseas limpiar todo el historial? (s/n)[/bold yellow]',
                    choices=['s','n','S','N'],
                    default='n'
                )
                if confirmacion.lower() == 's':
                    limpiar_historial()
            
            # Salir (opción 15)
            elif opcion == '15':
                console.print(Panel(
                    '[bold green]✋ Hasta pronto[/bold green]',
                    border_style='green'
                ))
                break

            # Pausa antes de mostrar el menú nuevamente
            if opcion != '15':
                console.print('\n[dim]Presiona ENTER para continuar...[/dim]')
                input()
                console.clear()
                            
        except KeyboardInterrupt:
            console.print('\n')
            console.print(Panel(
                '[bold yellow]⚠️ Operación cancelada por el usuario[/bold yellow]',
                border_style='yellow'
            ))
            break
        except Exception as e:
            console.print(Panel(
                f'[bold red]❌ Error inesperado: {e}[/bold red]',
                border_style='red'
            ))

