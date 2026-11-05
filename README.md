# Semáforo de Medicamentos

Página pública para que los pacientes consulten si hay stock de su medicamento en la farmacia.
Cada medicamento muestra un semáforo:

- **Verde (Disponible):** cubre 10 días o más de consumo.
- **Amarillo (Stock bajo):** cubre menos de 10 días.
- **Rojo (Sin stock):** stock en cero.
- **Gris (Sin disponibilidad actual):** está en el vademécum de Nivel 1 pero no hay stock ni movimientos.

La página no muestra cantidades. La página no muestra el listado completo: el paciente busca su medicamento y ve solo el estado de lo que consultó, acumulando hasta 6 consultas (quedan guardadas en su celular; la séptima reemplaza a la más vieja).

## Cómo se actualiza

Un agente programado, de lunes a viernes, cada hora entre las 8 y las 12:

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
- `vademecum.json`: listado oficial de medicamentos de Nivel 1 (CeSAC) versión 2026. Todo lo del listado aparece en la página; lo que no tiene stock ni movimientos se muestra en gris ("Sin disponibilidad actual"). Se regenera con `vademecum_build.py <archivo.xlsx>`.
- `cruce.py`: cruza los nombres de SIGEHOS con el vademécum (con una tabla de ajustes manuales).
- `nombres.py`: simplifica los nombres de SIGEHOS a droga + concentración + forma.
- `generar_semaforo.py`: lee los reportes y genera `index.html`. Los umbrales y las palabras para excluir descartables se configuran al principio del archivo.
