
# main.py
"""
Punto de entrada principal de la aplicación
"""
import sys
from cad_system import CADSystem

def main():
    try:
        # Inicializar el sistema CAD
        cad = CADSystem()

        # Ejecutar el bucle principal
        cad.run()

    except Exception as e:
        print(f"Error en la aplicación: {e}")
        sys.exit(1)
    finally:
        print("Cerrando aplicación...")
        sys.exit(0)

if __name__ == "__main__":
    main()