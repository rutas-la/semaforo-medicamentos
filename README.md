# Semáforo de Medicamentos

Página pública para que los pacientes consulten si hay stock de su medicamento en la farmacia.
Cada medicamento muestra un semáforo:

- **Verde (Disponible):** cubre 15 días o más de consumo.
- **Amarillo (Stock bajo):** cubre menos de 15 días.
- **Rojo (Sin stock):** stock en cero.

La página no muestra cantidades. Cada paciente puede guardar hasta 6 medicamentos en "Mis medicamentos" (queda guardado en su celular).

## Cómo se actualiza

Un agente programado, de lunes a viernes dos veces por día:

1. Exporta de SIGEHOS el **Listado de Stock** y la **Consulta de movimientos** (últimos 90 días).
2. Ejecuta:
   ```
   python generar_semaforo.py --stock "Listado de Stock.xlsx" --movimientos "Consulta de movimientos.xlsx" --salida index.html
   ```
3. Sube el `index.html` nuevo a este repositorio. GitHub Pages lo publica en uno o dos minutos.

Los reportes del sistema **nunca** se suben al repositorio (están en `.gitignore`).

## Archivos

- `index.html`: la página publicada (generada, no editar a mano).
- `template.html`: diseño de la página; los datos se insertan en `/*__DATA__*/`.
- `generar_semaforo.py`: lee los reportes y genera `index.html`. Los umbrales y las palabras para excluir descartables se configuran al principio del archivo.
