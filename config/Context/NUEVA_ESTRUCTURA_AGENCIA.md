# Nueva estructura de agencia — diseño e implementación

> Flujo "Crear una nueva estructura de agencia" — **implementado** (2026-10-01)
> tanto en `run.py` (UI de automatización) como en la skill `insumo-creator`.
> Este documento registra el análisis y las decisiones que llevaron al diseño
> final (sección 4 en adelante). Actualízalo si la regla de negocio cambia.

## 0. Dónde quedó cada pieza (mapa rápido)

- `config/sucursales.py` — catálogo de sucursales habilitadas (branch, prefijo de
  DM, texto de AM, ubicación).
- `utils/agency_id_allocator.py` — `AgencyIdAllocator` (Agency_Id nuevo esquema) y
  `AgencySectionAllocator` (siguiente letra de sección por sucursal).
- `services/agency_repository.py` — `ChallengerRepository` (Challenger_uat),
  `BotDbAgencyRepository` (botDB), `generar_persona`/`generar_dm_nuevo`/
  `generar_am_nuevo` (cálculo, sin insertar), `insertar_persona`/`crear_agencia`
  (insertan), `eliminar_agencia`/`eliminar_dm_am` (rollback).
- `tests/test_agencia_structure.py` — flujo pytest (sin Selenium) invocado por
  `run.py` cuando el insumo elegido es "Nueva estructura de agencia".
- `run.py`, `ui/selector_ui.py`, `ui/progress_ui.py`, `ui/results_ui.py` —
  integración en la UI/orquestador (tipo `AGENCIA`, panel con filas
  sucursal+modo, reutiliza el motor de slots/ronda/reintentos ya existente).
- `.claude/skills/insumo-creator/agents/agency-structure-creator.md` — agente de
  la skill de Claude Code (genera SQL insert/rollback usando los mismos
  helpers de Python, en modo solo-lectura + reserva local, sin ejecutar inserts
  directamente — ver ese archivo para el porqué).
- `.claude/skills/insumo-creator/references/agencies.md` — esquema nuevo de
  Agency_Id documentado junto al legado.

## 1. Qué existe hoy

### 1.1 Flujo manual actual (`config/Context/usuariosAgencias.md`)

Dar de alta una agencia nueva de cero requiere 5 inserts manuales, en dos bases:

| # | Tabla | Base | Contenido |
|---|-------|------|-----------|
| 1 | `AgencyStructure` | `Challenger_uat` | Agency_Id, Representative_Id (estrella), nombre, DM (texto+id+nombre), sección (letra), Branch (texto), AM (id+nombre) |
| 2 | `tblRepresentative_Table_AWS` | `Challenger_uat` | Alta de la estrella: Representative_Id, email, nombre, teléfono, tipo, Maintained_By_Db_Id, RFC |
| 3 | `P_ESTRELLAS_MENSUAL_CATEGORIAS` | `Challenger_uat` | Categoría mensual de la estrella (Avg_Collected_Cust, Sales_Volume, etc.) |
| 4 | `Agency_Representative_AWS` | `botDB` | Vincula Agency_Id + Representative_Id + prefijo de sucursal (4 dígitos) |
| 5 | `tblRepresentative_Table_AWS` | `botDB` | Mismo alta de representante, replicada en botDB |

`InsumosGen/generadores/agenciesGenerator.sql` ya envuelve esto en una transacción con
`DECLARE`s y rollback automático (`BEGIN TRY/CATCH`), pero sigue siendo un script de un
solo uso con IDs puestos a mano.

### 1.2 Esquema de IDs actual (13 dígitos, todos los tipos de ID)

Documentado en `.claude/skills/insumo-creator/references/agencies.md`:

```
[BBBB][000][SSSSSS]
 ^^^^  ^^^  ^^^^^^
 |     |    └─ sufijo aleatorio (3-6 dígitos, sin control de colisión)
 |     └────── siempre "000"
 └──────────── número de sucursal (4 dígitos)
```

Se usa igual para `Agency_Id`, `Representative_Id`, `DM_Id` y `AM_Id` — solo cambia el
sufijo aleatorio. **No hay un generador programático que garantice unicidad**: los IDs
de ejemplo en `agencies.md` fueron pegados a mano desde consultas reales.

Sucursales conocidas (número de sucursal = primeros 4 dígitos):

| Sucursal | Número |
|---|---|
| Izcalli | 2075 |
| Tijuana | 2093 |
| Zacatecas | 2060 |
| San Luis Potosí | 2049 |
| Aguascalientes | 2025 |

### 1.3 Dónde vive la lógica de "insumos" hoy

`.claude/skills/insumo-creator/` es la skill de Claude Code que orquesta la creación de
insumos de BD (hoy solo "Representatives", vía `agents/representative-creator.md`). Su
`SKILL.md` paso 1 dice literalmente "Ask the user what type of insumo they want to
create" y lista los tipos disponibles — este es, muy probablemente, el "desplegable del
inicio" al que se refiere el pedido, **no** el selector de `run.py`/`ui/selector_ui.py`
(ese es el flujo de automatización Selenium CN/CF/OF para vender, sin relación con dar
de alta agencias en BD).

Cada agente de insumo (ver `representative-creator.md`) genera dos archivos en
`InsumosGen/output/`: `<tipo>_insert_<timestamp>.sql` y `<tipo>_rollback_<timestamp>.sql`,
con transacciones por base de datos.

## 2. Propuesta del usuario: nuevo esquema de `Agency_Id` con consecutivos

En vez del sufijo aleatorio actual, generar el `Agency_Id` (13 dígitos) como:

```
[BBBB][YYMM][UU][CCC]
 ^^^^  ^^^^  ^^  ^^^
 |     |     |   └─ consecutivo (3 dígitos, sin repetirse)
 |     |     └───── "identificador único" (2 dígitos) — significado a confirmar
 |     └─────────── año-mes de creación (4 dígitos, YYMM)
 └───────────────── número de sucursal (4 dígitos, igual que hoy)
```

Ejemplo dado: Izcalli, año-mes 2609 (sep-2026), identificador `04`, consecutivo `001`
→ `2075 2609 04 001` = `2075260904001` (13 dígitos ✓).

Aplicaría igual a Zacatecas (2060), Aguascalientes (2025), San Luis Potosí (2049),
Tijuana (2093), y cualquier sucursal futura.

### 2.1 Qué resuelve esto

- Reemplaza el sufijo aleatorio (sin control de colisión) por un consecutivo
  determinista y legible: de un vistazo se sabe sucursal + mes de alta + orden.
- Es el mismo problema que ya resolvió `utils/offer_id_allocator.py` para `idOferta`
  en el framework de automatización (SQLite local con transacción `EXCLUSIVE` para
  evitar colisiones entre corridas, incluso en paralelo). El patrón es reutilizable
  aquí si este flujo también necesita ejecutarse en lote o en paralelo.

### 2.2 Lo que todavía no sé (ver preguntas abiertas)

- Si el nuevo esquema aplica **solo** a `Agency_Id`, o también a `Representative_Id`,
  `DM_Id` y `AM_Id` (hoy los 4 comparten el patrón `BBBB+000+sufijo`).
- Qué representa el campo de 2 dígitos "identificador único" (`04` en el ejemplo) —
  no corresponde a nada existente en el esquema actual (ni DM letter, ni tipo de
  representante, ni sucursal).
- Si el consecutivo (`CCC`) se reinicia cada año-mes por sucursal (001, 002... cada
  `YYMM` nuevo) o es un contador global que nunca se reinicia.
- Dónde debe vivir la fuente de verdad del consecutivo: ¿una tabla en alguna de las
  bases (Challenger_uat/botDB), o un allocator local tipo SQLite como los que ya
  existen en `utils/` para el framework de Selenium? Esto depende de si el flujo se
  ejecuta solo vía Claude Code (skill `insumo-creator`) o también necesita
  integrarse al framework de automatización.

## 3. Diseño propuesto (a validar, NO implementado)

Si se confirma que el flujo vive en la skill `insumo-creator`:

1. Nuevo agente `.claude/skills/insumo-creator/agents/agency-structure-creator.md`,
   análogo a `representative-creator.md`, que:
   - Genera el `Agency_Id` con el nuevo esquema `BBBB+YYMM+UU+CCC`.
   - Sigue generando `Representative_Id`/`DM_Id`/`AM_Id` con el esquema actual
     (`BBBB+000+sufijo`) salvo que se decida lo contrario (pregunta abierta arriba).
   - Genera los 5 inserts de la sección 1.1, en Challenger_uat y botDB, con
     transacción + rollback como ya hace `agenciesGenerator.sql`.
2. Actualizar `.claude/skills/insumo-creator/SKILL.md` para listar "Agency Structure"
   como tipo de insumo disponible (hoy solo lista "Representatives").
3. Actualizar `.claude/skills/insumo-creator/references/agencies.md` con el nuevo
   esquema de `Agency_Id` (sección "Agency_Id Construction Rules") sin perder el
   esquema viejo documentado (las agencias existentes ya creadas conservan su ID
   viejo; solo las nuevas usan el esquema nuevo).
4. Necesita un mecanismo de consecutivo sin colisión (sección 2.2) — pendiente de
   decidir dónde vive antes de construirlo.

## 4. Decisiones (confirmadas por el usuario, 2026-09-30)

1. **Dónde vive el flujo: ambos.**
   - Skill `insumo-creator` (Claude Code): nuevo tipo de insumo "Agency Structure",
     con agente dedicado que genera SQL de insert/rollback, igual que
     `representative-creator.md`.
   - `run.py`: nueva fase/tipo en el asistente interactivo (`ui/selector_ui.py`),
     separada de `OF/CF/CN` (es alta de catálogo en BD, no venta ni Selenium),
     que ejecuta el alta directamente contra las bases (no genera un .sql a mano).
   - Ambas rutas deben compartir el mismo generador de `Agency_Id` (ver punto 2),
     para que no se dupliquen consecutivos entre una vía y la otra.

2. **Alcance del esquema nuevo: solo `Agency_Id`.**
   `Representative_Id`, `DM_Id` y `AM_Id` siguen con el esquema actual
   (`BBBB+000+sufijo`).

3. **"Identificador único" (2 dígitos) = `11`, fijo.**
   No varía por tipo de estructura ni por persona: es una marca fija que identifica
   cualquier insumo (de cualquier tipo, no solo agencias) creado con esta
   herramienta. Es decir, el campo no es específico de "agencia" — es el sello de
   "creado por la herramienta de insumos". Se reutilizará tal cual si en el futuro
   se generan otros tipos de ID con este mismo esquema.

4. **Consecutivo (`CCC`, 3 dígitos): reinicia cada año-mes, por sucursal.**
   Izcalli en `2609` (sep-2026) empieza en `001`; al llegar `2610` (oct-2026)
   vuelve a `001` para Izcalli, independientemente del consecutivo de otras
   sucursales en ese mismo mes.

### Esquema final de `Agency_Id`

```
[BBBB][YYMM][11][CCC]   (13 dígitos)
 ^^^^  ^^^^  ^^  ^^^
 |     |     |   └─ consecutivo 001-999, reinicia cada (sucursal, YYMM)
 |     |     └───── fijo "11" (sello de herramienta de insumos)
 |     └─────────── año-mes de creación (YYMM, 2 dígitos año + 2 dígitos mes)
 └───────────────── número de sucursal (igual que el esquema actual)
```

Ejemplo: Izcalli, sep-2026, primera agencia del mes → `2075` + `2609` + `11` + `001`
= `2075260911001`.

## 5. Decisiones adicionales (confirmadas, 2026-10-01)

- **DM/AM nuevos**: el usuario decide caso por caso (no hay regla automática de
  "crear si no existe"). Cada agencia del lote elige independientemente
  "reutilizar" (de una lista con combos reales vigentes en Challenger_uat) o
  "crear equipo nuevo" — igual que cada fila del panel "Oferta" ya es
  independiente en `run.py`.
- **Número de DM/AM nuevo**: siempre el máximo real encontrado en vivo en
  `Challenger_uat.AgencyStructure` + 1 (nunca un contador local ciego), porque la
  data legada ya iba muy por delante de lo que el usuario recordaba (Izcalli
  AM ya iba en 4350, no 530).
- **Formato del código de DM**: se respeta el formato propio de cada sucursal
  (Tijuana sigue usando "BRM" en vez de "DM") — ver `config/sucursales.py`
  (`dm_prefix`).
- **Letra de sección para equipos nuevos**: secuencia propia de la herramienta,
  empieza en "C", nunca se reinicia ni se reutiliza por sucursal — independiente
  del desorden de letras ya usadas históricamente.

## 6. Verificación

Probado de punta a punta contra las bases reales (Challenger_uat + botDB, VPN
corporativa), insertando y luego revirtiendo con `eliminar_agencia`/
`eliminar_dm_am`:
- Alta reutilizando un DM/AM existente (Izcalli, Zacatecas).
- Alta creando un DM/AM nuevo, con 2 agencias compartiéndolo en el mismo lote
  (confirmó número de DM 63→64, AM 4350→4351, letra de sección C→D→E según el
  estado ya reservado localmente).
- Flujo completo vía `pytest tests/test_agencia_structure.py` (como lo invoca
  `run.py`), con `data/run_config.json` simulando lo que escribe
  `ui/selector_ui.py`.
