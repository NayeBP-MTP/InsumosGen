# Provipedia — Preparación de seguridad y datos personales

> Documento de trabajo para quien presenta el Gem. **No se sube al Knowledge del Gem.** Separa lo que está verificado en el repo de lo que hay que confirmar con TI / Seguridad de la Información / Legal.

## 1. Alcance del Gem (lo que puedes afirmar con seguridad)

- Es un asistente de **consulta de documentos**: responde con base en los archivos que se le cargan.
- **No** se conecta a bases de datos, **no** ejecuta SQL, **no** accede a MyProvi, Focus, Freud, Customer APP ni a ningún sistema, y **no** consulta datos de clientes.
- No escribe ni modifica nada en ningún sistema.
- Lo que sabe es exactamente lo que está en el Knowledge y en las instrucciones. Por eso **la principal medida de seguridad es controlar qué se sube**.

## 2. Inventario del Knowledge y resultado del escaneo

Escaneo hecho sobre los archivos del repo (búsqueda de contraseñas/tokens, IPs, correos, patrones de RFC/CURP y nombres de personas).

| Archivo | Contenido | Resultado del escaneo | Sensibilidad |
|---|---|---|---|
| `negocio/onboarding_po.md` | Roles, procesos, reglas de precios, umbrales (17 y 27 semanas), sucursales Unbundling | Sin credenciales, IPs, correos, RFC/CURP ni nombres de personas | **Interna / confidencial de negocio** |
| `negocio/gem_tecnico.md` | Esquema NFS, convenciones de ofertas | Sin credenciales/IPs. Único RFC es el genérico `XAXX010101000` | **Interna técnica** |
| `Conexión a BDD.docx` | Pasos para conectar con SSMS | ⚠️ **No está en el repo; no pude revisarlo** | **Potencialmente crítica** (ver §4, pendiente #1) |
| `schema/mapping/*.md` (opcional) | Nombres de tablas y columnas, incluidas tablas de autenticación (`arq_*`, `jwt_*`) | Solo esquema, sin datos. Muestran que existen columnas con datos personales (nombre, RFC, domicilio, etc.), no su contenido | **Interna técnica** (mapa del sistema) |

No se suben: `onboarding_po.txt` y `onboarding_po_call.txt` (contienen nombres de personas), scripts `.sql`, `CONTEXT.md`.

## 3. Datos personales: qué hay y qué no

- **No hay datos personales reales de clientes ni empleados** en los archivos que se suben (según el escaneo). Los ejemplos son ficticios (ej. "Juan Pérez García", RFC genérico).
- El Gem **no puede** consultar datos de clientes porque no tiene acceso a ningún sistema.
- **Riesgo residual**: que un usuario **pegue** datos reales en el chat. Mitigación: instrucción explícita en el prompt (bloque "SEGURIDAD Y DATOS PERSONALES"), reglas de uso para el equipo (§6) y pruebas #42-43 del set de pruebas.

## 4. Pendientes antes de presentar (verifica y marca)

- [ ] **#1 `Conexión a BDD.docx`**: ábrelo y confirma que **no contiene usuarios, contraseñas, IPs ni nombres de instancia reales**. El prompt lo describe como guía con "datos de conexión que le compartieron", lo que sugiere que esos datos se entregan aparte; confírmalo. Si contiene credenciales o IPs, **no lo subas** (o sube una versión sin ellos). Recuerda que cualquier usuario del Gem podría pedirle su contenido y un prompt no es una barrera fiable.
- [ ] **#2 Cuenta donde vive el Gem**: créalo en la cuenta **corporativa** de Google, no en una personal. Confirma con TI qué política de datos aplica a esa cuenta (ver §5, pregunta 2).
- [ ] **#3 Quién puede acceder al Gem**: comparte solo con personas o grupos concretos del equipo; evita "cualquiera con el enlace". Confirma con TI si Gems compartidos permiten a los usuarios ver las instrucciones o los archivos (no asumas que no).
- [ ] **#4 Clasificación de la información**: pregunta a Seguridad de la Información si el contenido de `onboarding_po.md` y del esquema técnico puede residir en una herramienta de IA aprobada. Deja la respuesta por escrito.
- [ ] **#5 Repositorio en GitHub**: el remoto es `github.com/NayeBenitezP/InsumosGen`, una **cuenta personal**. No pude comprobar si es público o privado. Verifícalo. Si contiene esquemas y scripts de Provident, confirma que tienes autorización para tenerlos ahí. Lo ya subido al remoto son solo los 12 scripts SQL de `Algorithms/`; el resto de tu trabajo está sin subir.
- [ ] **#6 Scripts SQL locales**: el escaneo encontró 41 coincidencias de patrón (IPs/correos/RFC-like) en scripts `.sql` de `generadores/`. No se suben al Gem, pero revísalos si vas a compartir el repo (probablemente son datos de prueba, pero no lo verifiqué).
- [ ] **#7 Enlace de Drive**: confirma que los permisos del documento de conexión son los intencionados (equipo, no público).
- [ ] **#8 Mapeos opcionales**: decide si los subes. Dan un mapa detallado del sistema (incluidas tablas de autenticación). Mi recomendación: **no subirlos** en la primera versión; `gem_tecnico.md` cubre lo básico.
- [ ] **#9 Pruebas de seguridad**: ejecuta las pruebas #39-48 de `PROVIPEDIA_TEST_SET.md` y anota el resultado.

## 5. Preguntas que te pueden hacer (y cómo responder)

**1. ¿Qué información sensible tiene el Gem?**
Documentación interna de procesos y reglas de negocio, y el esquema técnico (nombres de tablas y columnas). No tiene datos de clientes, credenciales ni datos de empleados, según la revisión del contenido. *(Confirma antes el docx de conexión, pendiente #1.)*

**2. ¿Google usa nuestra información para entrenar sus modelos?**
Depende del tipo de cuenta y del contrato. **No lo afirmes de memoria**: confirma con TI la política de la cuenta corporativa. Por eso el Gem debe crearse en la cuenta empresarial.

**3. ¿Puede el Gem acceder a datos de clientes o a nuestras bases de datos?**
No. Solo lee documentos cargados; no tiene conexión a ningún sistema.

**4. ¿Qué pasa si alguien pega datos reales de un cliente?**
El prompt le indica no usarlos ni repetirlos y avisar al usuario. Pero es una salvaguarda de comportamiento, no una barrera técnica: el texto ya salió hacia la herramienta. Por eso la regla de uso es no pegar datos reales, y hay que confirmar con TI cómo se retiene el historial de chats.

**5. ¿Se puede engañar al Gem para que revele instrucciones o archivos (prompt injection)?**
Se mitiga con instrucciones explícitas y con las pruebas #39-40 y #47, pero **ningún prompt es infalible**. Por eso lo que no debe conocer el Gem simplemente no se le carga: nada de credenciales, IPs ni datos personales.

**6. ¿Quién puede ver el Gem y sus archivos?**
Las personas con las que se comparta. Confirma con TI el comportamiento exacto de compartir Gems y si un usuario podría ver las instrucciones o los archivos (pendiente #3). No asumas que no.

**7. ¿Y si la información cambia o el Gem se equivoca (alucinación)?**
Instrucciones: no inventar, enumerar condiciones y marcar lo pendiente como "no confirmado". Hay 48 preguntas de prueba (varias trampa y 10 de seguridad) para validarlo. Aun así, para decisiones críticas debe verificarse con la fuente oficial. El Gem no cita fuentes por diseño; si el equipo lo requiere, puede reconsiderarse.

**8. ¿Cómo se actualiza y quién es responsable del contenido?**
El contenido se actualiza en `onboarding_po.md` y se vuelve a subir manualmente (Gemini no relee el repo). Propón un responsable nombrado y una cadencia de revisión.

**9. ¿Cumple con la ley de protección de datos personales (LFPDPPP) y las políticas internas?**
No des un dictamen. Responde: "No trata datos personales por diseño; el cumplimiento de la política de uso de IA lo valida Legal / Seguridad de la Información". Lleva la respuesta escrita de esos equipos si la tienes (pendiente #4).

**10. ¿Qué pasa si se filtra o se comparte fuera de la empresa?**
El contenido es interno y de sensibilidad media (procesos, reglas, esquema), sin datos personales ni credenciales. Aun así, el acceso se limita al equipo y se reporta cualquier uso indebido a Seguridad de la Información.

**11. ¿Puede usarse para saltarse controles o para acceder a sistemas?**
El Gem se niega a ayudar a eludir accesos. Además no tiene acceso a ningún sistema, y los accesos siguen solicitándose por el canal formal (DevOps/Base de Datos).

**12. ¿Por qué el Gem no cita archivos ni nombra a las personas que dieron la información?**
Es una decisión de diseño: privacidad de las personas y que responda como fuente interna unificada. Tiene el costo de menor trazabilidad, dilo abiertamente si te lo preguntan.

## 6. Reglas de uso para el equipo (para la diapositiva)

1. **Nunca** pegues datos reales de clientes, estrellas o empleados (nombre, RFC, CURP, INE, teléfono, domicilio, número de cliente o contrato).
2. Para insumos y pruebas usa **solo datos ficticios**.
3. No pidas ni compartas credenciales, IPs ni cadenas de conexión con el Gem.
4. La respuesta del Gem es una guía: **valida con Producto/Negocio** las decisiones críticas.
5. No compartas contenido del Gem fuera de la empresa.
6. Si sospechas una fuga o uso indebido, repórtalo a Seguridad de la Información.

## 7. Límites que conviene reconocer en la presentación

- Un system prompt **reduce** el riesgo pero no es un control de seguridad. El control real es **no cargar** información sensible.
- No sé qué registros de auditoría o retención de conversaciones existen para los Gems en la cuenta corporativa; pregúntalo a TI antes de que te lo pregunten a ti.
- No se ha sometido a una revisión formal de Seguridad de la Información. Si presentas antes de esa revisión, dilo como "piloto interno".
