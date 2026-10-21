# Switch Virtual Interactivo con Gestos de Mano

Este repositorio contiene el código fuente desarrollado como parte del proyecto de residencia profesional. Consiste en un sistema modular que integra visión artificial para simular la asignación de ancho de banda mediante gestos, comunicándose en tiempo real con un microcontrolador para reflejar los estados físicamente.

## Tecnologías Utilizadas

- **Python 3:** Lógica central y máquina de estados.
- **OpenCV & cvzone (MediaPipe):** Rastreo de los 21 puntos clave de la mano.
- **PySerial:** Enlace de comunicación bidireccional a 9600 baudios.
- **Arduino Uno:** Modulación PWM y corrección Gamma para la respuesta física (LEDs).

## Estructura del Sistema

El código está modularizado aplicando buenas prácticas de ingeniería:

- `config.py`: Variables globales y parámetros de calibración.
- `geometry.py`: Cálculo de distancias y trigonometría de falanges.
- `switch_logic.py`: Máquina de estados (Selección, Medición, Guardado).
- `ui_drawer.py`: Renderizado del menú inferior y gráficos en pantalla.
- `arduino_link.py`: Gestión del puerto serie.
- `main.py`: Bucle principal de ejecución.
