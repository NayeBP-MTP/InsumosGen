# Plan de Implementaciones — Providigital_Ventas

> **Fecha:** Mayo 2026  
> **Objetivo:** Extender el framework de automatización E2E con 4 mejoras funcionales.

---

## Implementación 1 — Cerrar sesión al finalizar el flujo

**Objetivo:** Que el proceso automatizado cierre sesión correctamente en el portal antes de que el driver se destruya, en lugar de simplemente cerrar el navegador.

### Pasos

- [ ] **1.1** Identificar el elemento de cierre de sesión en el portal (botón, menú o enlace "Cerrar sesión" / "Salir").
- [ ] **1.2** Agregar el selector correspondiente en `pages/login_page.py` como constante de clase (ej. `BTN_CERRAR_SESION`).
- [ ] **1.3** Crear el método `cerrar_sesion()` en `LoginPage` que:
  - Espere a que el elemento sea clickable.
  - Haga click.
  - Espere a que la URL regrese a la pantalla de login como confirmación.
  - Tome screenshot del paso.
- [ ] **1.4** Agregar el paso al final de `tests/test_login.py`:
  ```python
  with allure.step("Cerrar sesión"):
      login_page.cerrar_sesion()
  ```
- [ ] **1.5** Verificar que el fixture `driver.quit()` en `conftest.py` siga ejecutándose después del logout (ya ocurre automáticamente por el `yield`).
- [ ] **1.6** Actualizar `CODEBASE_ANALYSIS.md` con el nuevo paso en el diagrama del flujo.

---

## Implementación 2 — Base de datos local de agencias y métodos de entrega

**Objetivo:** Crear una BD SQLite local que almacene catálogos de agencias y métodos de entrega, reutilizando el patrón ya establecido por `BirthdateAllocator`.

### Pasos

- [ ] **2.1** Definir el esquema de tablas:
  - `agencias (id INTEGER PK, nombre TEXT, codigo TEXT, activa INTEGER)`
  - `metodos_entrega (id INTEGER PK, nombre TEXT, activa INTEGER)`
- [ ] **2.2** Crear el archivo `utils/catalog_db.py` con la clase `CatalogDB` que incluya:
  - `init_db()` — crea las tablas si no existen y hace seed de datos iniciales.
  - `get_agencias()` — retorna lista de agencias activas.
  - `get_metodos_entrega()` — retorna lista de métodos de entrega activos.
  - `add_agencia(nombre, codigo)` — inserta nueva agencia.
  - `add_metodo_entrega(nombre)` — inserta nuevo método.
- [ ] **2.3** Hacer seed inicial con los datos conocidos de agencias Provident y métodos de entrega disponibles (Orden de Pago BBVA, etc.).
- [ ] **2.4** Ubicar la BD en `data/catalog.sqlite3` (mismo patrón que `generated_birthdates.sqlite3`).
- [ ] **2.5** Agregar prueba unitaria básica de `CatalogDB` o al menos un script de validación (`python utils/catalog_db.py`) que imprima los catálogos.

---

## Implementación 3 — Interfaz básica de selección (UI)

**Objetivo:** Crear una interfaz gráfica simple que permita al usuario seleccionar la agencia y el método de entrega antes de ejecutar el test, sin tocar el código.

### Pasos

- [ ] **3.1** Evaluar librería UI: usar `tkinter` (incluido en Python, sin instalación adicional) para mantener dependencias mínimas.
- [ ] **3.2** Crear el archivo `ui/selector_ui.py` con una ventana que contenga:
  - Dropdown / Listbox de **Agencia** (alimentado desde `CatalogDB.get_agencias()`).
  - Dropdown de **Método de entrega** (alimentado desde `CatalogDB.get_metodos_entrega()`).
  - Campo numérico **Número de ciclos** (ver Implementación 4).
  - Botón **"Iniciar automatización"**.
- [ ] **3.3** Al presionar el botón, la UI debe:
  - Validar que se haya seleccionado agencia y método de entrega.
  - Guardar la selección en un archivo temporal `data/run_config.json`.
  - Cerrar la ventana y disparar la ejecución de pytest programáticamente (usando `subprocess` o `pytest.main()`).
- [ ] **3.4** Crear el archivo `run.py` en la raíz del proyecto como punto de entrada único:
  ```bash
  python run.py
  ```
  Este script abre la UI, espera la confirmación del usuario y lanza pytest con los parámetros seleccionados.
- [ ] **3.5** Actualizar `config/settings.py` para leer `data/run_config.json` si existe, y usar sus valores (agencia, método de entrega, ciclos) en lugar de los hardcodeados.
- [ ] **3.6** Documentar el uso de `run.py` en el `README.md`.

---

## Implementación 4 — Ejecución en ciclos (N repeticiones)

**Objetivo:** Permitir que el flujo completo de venta se ejecute N veces consecutivas dentro de la misma sesión del navegador (sin cerrar y abrir el navegador entre cada ciclo).

### Pasos

- [ ] **4.1** Modificar el fixture `driver` en `conftest.py` para que tenga scope `"session"` en lugar de `"function"`, de modo que el navegador se mantenga abierto entre ciclos.
- [ ] **4.2** Refactorizar `tests/test_login.py`:
  - Extraer todo el flujo actual a una función reutilizable `ejecutar_venta(driver, config)`.
  - El método de prueba principal itera esa función `N` veces según el valor de `run_config.json`.
  - Incluir el paso de **cerrar sesión** (Impl. 1) al final de cada ciclo excepto el último, y volver a hacer login al inicio de cada ciclo siguiente.
- [ ] **4.3** Manejar el `BirthdateAllocator` dentro del ciclo para que cada iteración use una fecha de nacimiento diferente (ya funciona por diseño).
- [ ] **4.4** Agregar un contador de resultados por ciclo:
  - Ciclo exitoso: registrar número de solicitud o confirmación obtenida.
  - Ciclo fallido: registrar el paso donde falló y continuar con el siguiente ciclo (usar `try/except` por iteración).
- [ ] **4.5** Al finalizar todos los ciclos, guardar un resumen en `data/run_results.json`:
  ```json
  {
    "total": 3,
    "exitosos": 2,
    "fallidos": 1,
    "detalle": [
      { "ciclo": 1, "estado": "exitoso" },
      { "ciclo": 2, "estado": "fallido", "paso": "Validar requests facematch" },
      { "ciclo": 3, "estado": "exitoso" }
    ]
  }
  ```
- [ ] **4.6** Mostrar el resumen de resultados en la terminal al terminar la ejecución.

---

## Orden de implementación recomendado

```
Impl. 2 (BD) → Impl. 3 (UI) → Impl. 1 (Logout) → Impl. 4 (Ciclos)
```

> La BD debe existir antes que la UI (la UI la consume).  
> El logout debe estar listo antes de implementar los ciclos (cada ciclo necesita cerrar y reabrir sesión).

---

## Archivos nuevos que se crearán

| Archivo | Descripción |
|---|---|
| `utils/catalog_db.py` | Clase `CatalogDB` con acceso a SQLite de catálogos |
| `ui/selector_ui.py` | Interfaz tkinter para selección pre-ejecución |
| `run.py` | Punto de entrada único del proyecto |
| `data/catalog.sqlite3` | BD SQLite de agencias y métodos de entrega |
| `data/run_config.json` | Configuración generada por la UI para el test runner |
| `data/run_results.json` | Resumen de resultados por ciclo |

## Archivos que se modificarán

| Archivo | Cambio |
|---|---|
| `pages/login_page.py` | Agregar `BTN_CERRAR_SESION` y método `cerrar_sesion()` |
| `config/settings.py` | Leer `run_config.json` si existe |
| `conftest.py` | Cambiar scope del fixture `driver` a `"session"` |
| `tests/test_login.py` | Refactorizar flujo en función reutilizable + loop de ciclos |
| `README.md` | Documentar `python run.py` como nuevo punto de entrada |
