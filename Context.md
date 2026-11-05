# Context — Automatización E2E de Cliente Frecuente (CF)

**Última actualización:** 23/09/2026
**Ámbito:** portal UAT de Providigital (`originacion-uat.providigital.com`), base `botDB`.
**Complementa a:** `ESPECIFICACIONES.md` (flujo CN y diseño CF) y `CODEBASE_ANALYSIS.md` (estructura del proyecto). Este documento reúne lo aprendido validando CF contra UAT: estado, reglas de negocio, decisiones técnicas y problemas conocidos.

---

## 1. Qué es el flujo CF

1. Se inserta una oferta preautorizada en `botDB.dbo.Ofertas` (`services/offer_repository.py`).
2. **Se verifica con un SELECT que la oferta quedó en la BD** (`OfferRepository.verify_offer_inserted`): conexión nueva, hasta 5 intentos con 2 s de espera, y compara `nombreCliente`, `agenciaCliente`, `branchOferta`, `montoOferta`, `idEstatusOferta`, `Customer_Id` y `descOferta`. Si no aparece o difiere, el ciclo falla con un mensaje claro **antes de abrir el navegador**. Antes del insert se ajusta `semana` a la más reciente de la tabla (ver §6.9), o el front no la listaría.
3. La oferta aparece en el listado del front ("Cliente frecuente").
4. Se busca al cliente por nombre y se hace click en su tarjeta ("Sin estatus").
5. Se completa la venta hasta la finalización.

Se ejecuta con `python -m pytest tests/test_login_cf.py -s -v` o con `python run.py` (menú de selección de agencia, método de entrega, celular, correo y ciclos).

---

## 2. Orden real del flujo CF (validado en UAT)

```
Listado offerpage → buscar nombre → click "Sin estatus"
  → Confirmar oferta (plazo y monto)
  → Método de entrega → botón según método → "Sí"
  → Iniciar Proceso de Identidad → celular → INE frente/reverso → facematch (Legalario)
  → Documentos (comprobante + fachada) → "Acepto"
  → Consentimiento de geolocalización (locationpage: "No Acepto"/"Acepto")   ← solo CF
  → Confirmar dirección → datos personales → datos laborales → dirección diferente
  → Consentimientos legales (beneficiario) → checks de contrato
  → Enviar SMS → OTP Legalario → "Estoy de acuerdo" x2 → firma → modal "Contrato exitoso"
  → Finalizar Venta → (pantallas finales, ver §5)
  → Cierre de sesión local
```

### CN vs CF

| Punto | CN | CF |
|---|---|---|
| Orden | identidad → docs → datos → OTP Provident → plazo/monto → método de entrega → beneficiario | oferta → método de entrega → identidad → docs → datos → beneficiario |
| Plazo/monto | tras OTP Provident | al confirmar la oferta preautorizada |
| OTP Provident (SMS) | sí | **no** |
| Consentimiento de geolocalización | no | **sí** (`locationpage`) |
| Modal "Aceptar" al finalizar | sí | **a veces** (ver §5) |

Código compartido en `tests/test_login.py`: `_flujo_metodo_entrega`, `_flujo_identidad_a_otp(incluir_otp_provident=…)` y `_flujo_beneficiario_a_finalizar`. `tests/test_login_cf.py` los orquesta en el orden CF.

---

## 3. Reglas de negocio y datos

- **Tijuana, CF: el monto que se entrega debe ser menor a 10,000** (10,000 exacto tampoco). Se aplica en la pantalla **"Oferta"** ("Confirma el monto que se le entregará al cliente"), donde hay dos selectores: plazo (p. ej. "32 Semanas") y monto (p. ej. "$13400"). El test tomaba siempre la opción 1 del monto, que en una corrida real dio **$13,400** y viola la regla. Ahora `PrestamoPersonalPage.seleccionar_plazo_y_monto(monto_maximo_exclusivo)` elige el monto **más alto estrictamente menor al límite** y, si el plazo elegido no ofrece ninguno, prueba los otros plazos; si ninguno cumple, falla mostrando las opciones disponibles. El límite viene de `Settings.MONTO_MAXIMO_CF_POR_AGENCIA` (prefijo del label de agencia; hoy solo `Tijuana: 10000`) vía `_limite_monto_agencia` en `tests/test_login_cf.py`. Sin límite (otras agencias, CN) se conserva la primera opción válida.
- **Monto guardado en la oferta (`montoOferta`):** aparte, `_monto_para_agencia` toma `monto` de `data/run_config.json` o uno aleatorio de 1,500–3,000, y rechaza en Tijuana valores >= 10,000. Ojo: los montos que ofrece la pantalla "Oferta" salen del texto `descOferta` ("TARIFA MÁX 2000 AGREGAR 14000/65 A", que hoy ofrece hasta $14,000), no de `montoOferta`; por eso el filtro se hace sobre el selector.
- **Métodos de entrega según agencia.** No todas las agencias ofrecen todos los métodos:

  | Agencia | Métodos observados en CF |
  |---|---|
  | Tijuana 0003 | Efectivo, Cheque, Orden de pago HSBC, Orden de Pago BBVA |
  | Tijuana 111 | Cheque, Orden de pago HSBC, Orden de Pago BBVA (sin Efectivo, sin Finabien) |
  | Otras (sonda) | ver §6: resultados incompletos |

- **Finabien: aparece cuando el monto elegido es menor a 10,000.** Con montos altos ($13,400) la pantalla "Método de entrega" no lo mostraba en ninguna agencia; al aplicar la regla de monto < 10,000, en **Tijuana 0003** Finabien sí apareció (23/09 16:22) y el flujo pasó el método de entrega, el modal de oficina postal (Estado → Ciudad → Oficina → Confirmar) y llegó a generar el folio de tesorería (`tipoDePago: 4`) y el contrato. La sonda anterior (§6.4) no era concluyente justamente porque usaba montos altos. Pendiente: una corrida Finabien completa hasta "Finalizar Venta".
- **Oficina postal de Finabien según la agencia.** El modal pide Estado → Ciudad → Oficina; ya no va fijo en Puebla. `Settings.UBICACION_OFICINA_POSTAL_POR_AGENCIA` (por prefijo del label) define estado y ciudad: Tijuana → Baja California / Tijuana; Izcalli → Estado de México / Cuautitlán Izcalli; Zacatecas → Zacatecas / Zacatecas; Aguascalientes → Aguascalientes / Aguascalientes; San Luis → San Luis Potosí / San Luis Potosí; cualquier otra → Puebla / Puebla. La búsqueda ignora acentos y mayúsculas, prefiere coincidencia exacta y, si no encuentra el estado o la ciudad, **falla listando las opciones** (antes elegía la primera en silencio). Se toma la primera oficina disponible de esa ciudad. Los textos exactos del portal para estas ubicaciones no están verificados salvo Puebla; si algún nombre no coincide, el error muestra cómo se llama en el portal para ajustarlo.
- **Campos de `dbo.Ofertas` para CF/OF:** `tipoDeOferta` = `'RE'` si la oferta es REFIN, `'AD'` si es AGREGAR (elegido en el menú, panel "Oferta" → Tipo de oferta; `Settings.TIPO_OFERTA`); `seccionCliente` viene del catálogo local por agencia (`utils/catalog_db.py`, columna `seccion`; fallback `'R'` si la agencia no tiene sección confirmada — nivel de confianza por agencia en `config/Context/REGLAS_DE_NEGOCIO.md`); `Agreement_Num` solo para REFIN (`'510' + AA + últimos 4 dígitos de idOferta`, y el mismo número se repite en `descOferta` tras "REFIN!"; `NULL` para AGREGAR); `idEstatusOferta=1`. `idOferta` = `AAMM + persona(1) + consecutivo(3)` con `utils/offer_id_allocator.py`.
- **Nombres de cliente:** ahora se generan con `utils/mexican_names.py` (ya no llevan el prefijo `TEST DEVIN CF`). Para localizar una oferta de prueba hay que buscar por `idOferta` o `Customer_Id`, no por el prefijo antiguo.
- **Las ofertas insertadas NO se borran** (decisión del usuario, para revisarlas después). `OfferRepository.delete_offer` existe para limpieza manual.
- **Datos que identifican una venta:** `idOferta`, `Customer_Id`, `VendidaProvidigital = 1` en BD y el folio de finalización (request `useractivitylogger`: acción "Finalización", detalle `Exitoso <folio>`). El test guarda el folio en `data/run_results_cf.json`.

### Ventas de prueba generadas (referencia)

| idOferta | Método | Folio | Nota |
|---|---|---|---|
| 26090022 | BBVA | 240020865 | 13:01, `VendidaProvidigital=1` |
| 26090023 | HSBC | — | 14:28, `VendidaProvidigital=1` |
| 26090028 | HSBC | 240020872 | finalizó; el cierre por "Salir" se colgó |
| 26090029 | HSBC | 240020873 | ciclo completo, "1 passed" |

---

## 4. Estado de validación

| Área | Estado |
|---|---|
| Insertar oferta, login, "Cliente frecuente", búsqueda, tarjeta | ✅ |
| Confirmar oferta, método de entrega | ✅ |
| Identidad Legalario (INE, facematch), documentos, datos personales | ✅ |
| Geolocalización, beneficiario, contrato, OTP y firma Legalario | ✅ |
| Finalizar venta | ✅ |
| CF con BBVA | ✅ (corrida del 23/09 13:01) |
| CF con HSBC | ✅ (ciclo completo del 23/09) |
| CF con Efectivo / Cheque | ⬜ sin probar |
| CF con Finabien | ✅ ciclo completo del 03/11 (Izcalli 335, monto $9,900, folio capturado). Con monto ≥ 10,000 el botón no aparece: el test elige monto < 10,000 si el método es Finabien |
| CN con BBVA / HSBC / Finabien | ✅ corridas del 03/11 (Izcalli 335) |
| Ciclos múltiples (≥2) | ⬜ sin corrida exitosa con el código final |
| Regla de Tijuana (monto < 10,000 en pantalla "Oferta") | ✅ implementada · ⬜ falta corrida end-to-end que la confirme |

---

## 5. Comportamientos del portal que el test debe tolerar

- **Modal de Legalario "Contrato exitoso":** pasa por estados; un click temprano cierra el estado equivocado. El test espera "Contrato exitoso" y reintenta "Continuar" hasta ver "Finalizar Venta".
- **"Enviar SMS" a veces no responde:** el click puede no disparar `send-code` si la pantalla aún recarga el expediente (`GET expedientecliente`). Síntoma: no aparece el cuadro del código y en las requests no hay `send-code`. El test espera 3 s y reintenta el click hasta 3 veces.
- **Casillas del contrato:** la casilla `confirm` a veces no registra el click y "Continuar" abre "¿Cancelar venta?". `marcar_checks_contrato` verifica y reintenta por JS.
- **Después de "Finalizar Venta":** unas veces aparece "¡Muchas felicidades! … pre-aprobado" con botón **Aceptar** y luego una pantalla con botón **Finalizar**; otras veces no aparece ninguno y solo se ve el contador de 2 minutos del contrato. El test trata "Aceptar" y "Finalizar" como opcionales y valida la finalización por la request `useractivitylogger` ("Finalización — Exitoso <folio>").
- **Facematch:** con el video de cámara fake el SDK termina y muestra "¡Proceso exitoso!" aunque el interceptor no capture la request. El test sale al ver esa pantalla y ya no espera 60 s ni dispara el fallback (que devolvía 400 de AWS Rekognition).
- **`IMPLICIT_WAIT=10`:** cada `find_elements` vacío espera hasta 10 s; los bucles de espera con `find_elements` avanzan más lento de lo que parece.

---

## 6. Problemas conocidos

1. **"Salir" tras finalizar congela el navegador.** El click dispara una recarga infinita del portal y chromedriver responde con `ReadTimeout` (120 s). Ocurrió repetidamente desde `documentcis`. Mitigación: `LoginPage.cerrar_sesion_local()` limpia cookies y storage y vuelve al login. La sesión termina en el navegador; no se verificó que el servidor la invalide. `LoginPage.cerrar_sesion()` (UI) se conserva para otras pantallas.
2. **Chrome y chromedriver huérfanos.** Corridas atascadas o abortadas dejaban ventanas abiertas. `conftest.py` ahora: cierra el driver en un hilo con límite de 15 s, mata el árbol de procesos siempre (fallo, Ctrl+C, terminación), y al iniciar limpia huérfanos de corridas anteriores (chromedriver y Chrome de automatización sin proceso padre). No toca el Chrome normal del usuario.
3. **Un fallo arrastraba a los ciclos siguientes.** `LoginPage.recuperar_sesion_tras_fallo()` (cerrar sesión, o limpiar cookies/storage) se ejecuta tras cada ciclo fallido, en CN y CF.
4. **Sonda de métodos por agencia: resultados incompletos.** Una sonda temporal (ya eliminada) listó los botones de "Método de entrega" en 11 agencias y solo vio Cheque y HSBC; leyó la lista apenas apareció el primer botón, así que faltan botones que cargan después. No es concluyente. Si se repite, esperar a que estabilice la lista.
5. **Video de cámara fake.** El generador recortaba una franja central de una foto vertical en un cuadro horizontal (a 2.5x solo quedaban ojos y nariz). Ahora `utils/generate_fake_camera_video.py` detecta la cara y la mantiene centrada: 0–4 s pequeña, 4–12 s acercamiento, 12–30 s fija. `data/selfie_old.y4m` es el video anterior (respaldo).
6. **Sesión concurrente con la misma estrella.** Dos ejecuciones simultáneas con el mismo usuario pueden interferir entre sí. Correr una a la vez.
7. **Acceso a `botDB`.** Solo con red/VPN corporativa (`BOTDB_SERVER:1433`). Sin acceso, el ciclo CF falla en el insert antes de abrir el navegador.
8. **`dbo.Ofertas` es una tabla compartida y las ofertas de prueba desaparecen.** Comprobado el 25/09: la tabla tiene ~2,100 filas y otras personas insertan en ella (p. ej. `idOferta` 2609 7xxx de la agencia 335, ese mismo día), y **ninguna** de las ofertas de prueba de las corridas del 23/09 (26090022, 26090023, 26090028, 26090029 y 26090053) sigue en la tabla, ni tampoco las anteriores a 26090060. Algo las borra (limpieza o recarga periódica de UAT, no identificada). Consecuencias: (a) la oferta insertada debe usarse enseguida, por eso se verifica con SELECT justo después del insert; (b) la BD **no** sirve como registro histórico de las ventas de prueba: guardar `idOferta`, `Customer_Id` y folio en `data/run_results_cf.json`; (c) posible colisión de `idOferta` con otras personas que insertan en la misma tabla, dado que `utils/offer_id_allocator.py` lleva su contador solo en SQLite local. Pendiente: confirmar con el equipo de BD qué borra las filas y con qué frecuencia.
9. **La oferta está en la BD pero no aparece en el listado del front (campo `semana`).** Comprobado el 25/09: el front pide el listado al endpoint `GET /v1/getpesosmsgs?...&agencias=<agencia>&cliente=<nombre>&semana=&...` (el parámetro `semana` del request va vacío y el backend lo ignora) y **solo devuelve las ofertas de la semana más reciente de la tabla**. Ese día había 104 ofertas con `semana=202639` (48 de la agencia 335) y una sola con `semana=202640` (insertada a mano a las 11:41); el listado mostraba únicamente esa, y buscar el nombre de la oferta de prueba (`semana=202639`, id 26090061) devolvía 0 filas aunque `SELECT` la encontraba. Causa: `utils/offer_id_allocator.py` calcula la semana por calendario (corte en miércoles) y ese valor quedó una semana por debajo de la que el backend usa. Corrección: `_ejecutar_venta_cf` usa `max(semana calculada, MAX(semana) de la tabla)` (`OfferRepository.get_max_semana`), y `semana` ahora también se compara en `verify_offer_inserted`. Verificado: una oferta insertada así (26090062, `semana=202640`) apareció en `getpesosmsgs` al buscarla por nombre, y la de `202639` no. Si la búsqueda en el front falla, el error ahora indica la semana de la oferta y la más reciente de la tabla. Pendiente de confirmar con el equipo: si el backend usa la máxima de la tabla o una semana calendario con corte distinto (la evidencia del 23/09 —ofertas con 202639 visibles en miércoles— apunta a la máxima de la tabla); cualquier fila con una semana mayor "esconde" todas las demás, incluidas las de otros usuarios.

---

## 7. Diagnóstico de fallas CF

Cuando un ciclo CF falla se guardan en `data/diagnostico_cf/`: `cicloN_falla.png`, `.html`, `_url.txt`, `_requests.json` (todas las requests capturadas) y `_otp_legalario.json`. Es lo primero que hay que revisar. Las capturas del test están en `screenshots/`.

Nota: un menú hamburguesa abierto en una captura de falla normalmente es la recuperación de sesión, no el flujo.

---

## 8. Pendientes

- [x] Completar una corrida **Finabien** hasta "Finalizar Venta" (hecha el 03/11 en CN y CF, Izcalli 335).
- [ ] Verificar los nombres de estado/ciudad de la oficina postal para Tijuana y para el resto de agencias (§3).
- [ ] Probar **Efectivo** y **Cheque** en CF.
- [ ] Corrida de **2 o más ciclos** consecutivos sin intervención.
- [ ] Verificar que el cierre de sesión local no deja sesión abierta en el servidor.
- [ ] Confirmar con negocio el template exacto de `descOferta` y las reglas de plazo/tasa.
- [ ] Confirmar en una corrida real que en Tijuana se elige un monto < 10,000 en la pantalla "Oferta" y que el resto del flujo lo acepta.
- [ ] Definir si el límite de monto aplica también a otras agencias (hoy solo Tijuana).

---

## 9. Archivos relevantes

| Archivo | Rol |
|---|---|
| `tests/test_login_cf.py` | Test CF, generador de oferta, límite de monto por agencia, diagnóstico de fallas |
| `tests/test_login.py` | Test CN y tramos compartidos CN/CF |
| `pages/ofertas_listado_page.py` | Búsqueda y selección de la tarjeta |
| `pages/login_page.py` | Login, `cerrar_sesion`, `cerrar_sesion_local`, `recuperar_sesion_tras_fallo` |
| `pages/prestamo_personal_page.py` | Pantallas del préstamo (checks de contrato, finalizar, etc.) |
| `services/offer_repository.py` | Conexión e insert en `botDB` |
| `utils/offer_id_allocator.py`, `utils/mexican_names.py`, `utils/catalog_db.py` | Ids, nombres y catálogo de agencias |
| `utils/generate_fake_camera_video.py` | Genera `data/selfie.y4m` |
| `conftest.py` | Driver, cierre garantizado de Chrome |
| `config/settings.py` | Configuración; lee `data/run_config.json` (incluye `monto` y topes) |

## 9. Cámara fake y facematch de Legalario (observado el 03/11/2026)

- El facematch lo debe completar **el SDK** con la cámara fake. El fallback `force_facematch_request` **no sirve**: Legalario/Rekognition lo rechaza siempre con 400 `CompareFaces InvalidParameterException` (envía la INE completa como `front`, un JPEG etiquetado como mp4 y no lleva `organization_id`/`requested_by`; la request real del SDK trae un recorte de cara de ~37 KB y un video webm real).
- **No usar un video de cara fija** (`HOLD_ONLY=True` en `utils/generate_fake_camera_video.py`, probado con 0.58 y 0.68): el SDK se queda en "Ajusta tu cara dentro del óvalo" y nunca valida, incluso donde el video original pasaba. El SDK necesita ver el acercamiento progresivo (cara pequeña → grande).
- Chrome comparte un solo dispositivo fake durante la sesión y el video se repite cada 30 s, así que la fase en que arranca el facematch es arbitraria. Con el video original la tasa de éxito observada fue ~2/3; los fallos restantes siguen sin causa confirmada.
- Modos de fallo vistos: (a) "Inicializando la cámara" colgado con el stream `ended` (causa probable: pulsar "Comenzar a grabar" antes de que termine la inicialización; corregido esperando a que desaparezca el overlay), (b) SDK en "Ajusta tu cara" sin completar, (c) SDK sin mensaje tras detectar. El diagnóstico `>>> CÁMARA t=…` en consola y la captura `facematch_atascado_30s` ayudan a distinguirlos.
- Finabien solo aparece con monto < 10,000: en CF el test ya elige un monto menor cuando el método es Finabien.
- Con `run.py` en paralelo (CN 334 + CF 335) fallaron ambas. El fallo de facematch de la CN se reproduce también en secuencial, así que ese no se debe al paralelismo. El de la CF (OTP de Legalario con 3 clicks en "Enviar SMS" y luego `legalarioButtonDocumentAccept` no clickable) **no se reprodujo en secuencial pero tampoco se repitió en paralelo**: causa sin determinar.
- **OTP de Legalario ("Enviar SMS").** El SMS puede tardar más de 25 s. Volver a pulsar "Enviar SMS" genera un código nuevo e invalida el anterior: el 03/11 se tecleó un código expirado (pantalla con campos vacíos y "El código expirará en: 00:00") y `legalarioButtonDocumentAccept` nunca fue clickable. El test solo re-pulsa si no salió ninguna request `/sdk/invites/send-code` (a los 10 s); si salió, espera hasta 90 s los inputs (`OTP_ESPERA_INPUTS`, `OTP_CLICK_PERDIDO_TRAS` en `tests/test_login.py`). Una corrida CF/HSBC pasó con esto; falta más muestra.
- **Video fake de 12 s** (`DURATION_SECONDS=12` en `utils/generate_fake_camera_video.py`; respaldo del de 30 s en `data/selfie_phased.y4m`): 3 de 3 CN y 1 CF sin fallos de cámara, frente a ~2/3 con el de 30 s. Muestra pequeña: no es una mejora demostrada.
