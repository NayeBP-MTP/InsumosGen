# Application Schemas — Customer App, Pesos Offer & Analytics

---

## Schema: CNFS_dbo

Reporting, analytics, and miscellaneous utility tables.

### AM_KPI
Weekly Area Manager KPI report. No formal PK defined.

| Column | Type | Notes |
|--------|------|-------|
| `Year` | int | |
| `Month_Code` | `T_Code` | |
| `Week` | int | Accounting week number |
| `Region` | varchar(11) | |
| `DOM` / `ROM` | `T_Short_Text` | District/Regional Operations Manager |
| `Branch_Name` | nvarchar(40) | |
| `SG` / `SR` | `T_Short_Text` | Sales Grade/Rep |
| `Branch_id` | bigint | |
| `Agency_Id` | bigint | |
| `ND` / `ND_Value` | int / numeric | New Disbursements count/value |
| `RES` / `RES_Value` | int / numeric | Resignations count/value |
| `Customers` | int | |
| `QC` | int | Qualified Customers |
| `Active` | int | Active count |
| `Collection_Value` | numeric(22,6) | |
| `Debit_value` | numeric(22,6) | |
| `AM_Role_Id` | `T_Id` | AM's role ID in NFS |
| `ventas_0` | int | Zero-sales count |
| `Vacant` | int | Vacant sections |
| `RI` / `RIIA` | int | Re-issue counts |
| `ND_RI` / `ND_RIIA` / `RES_RI` / `RES_RIIA` | int | |
| `Leavers` | float | |
| `Offers` | int | |
| `Stage12` | smallint | |
| `Prior_Yr_Cust` / `Prior_Yr_QC` | int | Prior year comparison |

---

### Branches_borrar
Temporary/staging table. Maps `Transfer_Db_Id` → `Full_Address`.

### CompetitorCP_borrar
Competitor data by postal code (CP). Contains competitor client counts by municipio.

### DDA_Import_File_Details
**PK:** `(Import_File_Id, Transfer_Partner_Id)`
Tracks DDA (Direct Debit Authority) import file processing times.

### Estructura_Branches
Maps branch names to BU and RSSM. No PK defined.

### MKT_Campaña_PUs_borrar / SA_GrupoControlPUs_borrar
Temporary marketing campaign and control group tables.

### TabAgreement_Freud_borrar
Temporary copy of agreement data. Contains the full agreement record structure with explicit SQL types (mirrors `Agreement_Table` + `Agreement_Table_DT_LOG`).

### Temp_GDSCategoryResult
GDS scoring category classification results per agency per week.

| Column | Type |
|--------|------|
| `classification_month_num` | varchar(7) |
| `classification_week_num` | int |
| `agency_id` | bigint |
| `agr_perc_25_payer_13wk` | numeric |
| `n_distinct_customers_cc_13wk` | int |
| `perc_consmiss_0_1_4wk` | numeric |
| `Points_*` columns | int — scoring points |
| `Final_Points` | int |

### Temp_Profil_borrar / Vacantes_borrar / prueba2 / stabilityscheme_borrar
Additional temporary/staging tables. `stabilityscheme_borrar` tracks agent section stability scheme data (scheme start/end week, section type, departure week, reason, vacancy flag).

### trace_st
**PK:** `RowNumber`
SQL Server Profiler trace data (EventClass, TextData, NTUserName, SPID, Duration, StartTime, Reads/Writes/CPU).

---

## Schema: CNFS_perezvma

User-specific reporting schema.

### Numeros_Diarios
Daily collection KPIs per branch (no PK). Spanish column names.
Collection, completed contacts, collected contacts, collected clients, new clients, etc.

### prueba3
Test/scratch table. `ID int`, `campo varchar(25)`.

---

## Schema: Customer_App_jwtprovident

JWT-based authentication and authorization framework for the Provident customer mobile app.
Contains two parallel sets of tables: `arq_*` (architecture/framework tables) and `jwt_*` (application-specific tables).

### Auth Framework Tables (arq_*)

| Table | PK | Description |
|-------|----|-------------|
| `arq_cliente` | `id_arq_cliente` | Client app registrations |
| `arq_aplicacion` | `id_arq_aplicacion` | Applications per client |
| `arq_aplicacion_configuracion` | `id_arq_aplicacion_configuracion` | App configuration properties |
| `arq_modulo` | `id_arq_modulo` | Modules within an application (with IP, port, URI) |
| `arq_servicio_rest` | `id_arq_servicio_rest` | REST service endpoints per module |
| `arq_parametro_servicio_rest` | `id_arq_parametro_servicio_rest` | Parameters for REST services |
| `arq_rol` | `id_arq_rol` | Roles in the framework |
| `arq_usuario` | `id_arq_usuario` | Users (customer login, birth date, contract number, password, Firebase token) |
| `arq_usuario_rol` | `id_arq_usuario_rol` | User-role assignments |
| `arq_rol_permiso_servicio` | `id_arq_rol_permiso_servicio` | Role → service endpoint permissions |
| `arq_propiedad` | `id_arq_propiedad` | System property definitions |
| `arq_parametro_configuracion` | `id_arq_parametro_configuracion` | System configuration parameters |
| `arq_token_sesion` | `id_arq_token` | Active session tokens |

Key `arq_usuario` columns:
- `num_cliente_contrato` — NFS contract/customer number
- `fec_nacimiento` — birth date (used for auth)
- `acepto_termino` / `acepto_privacidad` — T&C acceptance flags
- `token_firebase` — push notification token

---

### App-Specific Tables (jwt_*)

| Table | PK | Description |
|-------|----|-------------|
| `jwt_cliente` | `id_jwt_cliente` | App client registrations |
| `jwt_aplicacion` | `id_jwt_aplicacion` | Applications |
| `jwt_aplicacion_configuracion` | `id_jwt_aplicacion_configuracion` | App configuration |
| `jwt_modulo` | `id_jwt_modulo` | App modules (IP, port, URI) |
| `jwt_servicio_rest` | `id_jwt_servicio_rest` | REST endpoints |
| `jwt_parametro_servicio_rest` | `id_jwt_parametro_servicio_rest` | Service parameters |
| `jwt_rol` | `id_jwt_rol` | Roles |
| `jwt_usuario` | `id_jwt_usuario` | Users (extended: email, nombre, apellido, num_cliente, Firebase token) |
| `jwt_usuario_rol` | `id_jwt_usuario_rol` | User-role links |
| `jwt_rol_permiso_servicio` | `id_jwt_rol_permiso_servicio` | Role permissions |
| `jwt_propiedad` | `id_jwt_propiedad` | Property definitions |
| `jwt_parametro_configuracion` | `id_jwt_parametro_configuracion` | Config parameters |
| `jwt_token_sesion` | `id_jwt_token` | Session tokens |
| `jwt_notificacion` | `id_jwt_notificacion` | Push notifications (title, message, data, status, read date, sent flag) |
| `jwt_tipo_bitacora` | `id_jwt_tipo_bitacora` | Log entry types |
| `jwt_bitacora` | `id_jwt_bitacora` | Activity log (user, contract, timestamp, type) |
| `jwt_metodo_servicio` | `codigo_metodo_servicio` | HTTP method codes for services |
| `jwt_ultimo_password` | `id_jwt_ultimo_password` | Password history for reset enforcement |

---

## Schema: Customer_App_master

SQL Server system tables — not application tables.

| Table | Notes |
|-------|-------|
| `spt_fallback_db` | Fallback DB registry |
| `spt_fallback_dev` | Fallback device registry |
| `spt_fallback_usg` | Fallback usage |
| `spt_monitor` | System monitor stats |

---

## Schema: Customer_App_pagosprovident

Payment receipt storage for the customer app.

### AgreementPayments
**PK:** `AgreementPaymentId`
**Indexes:** `(CustomerId, AgreementNumber)`, `(CustomerId, AgreementNumber, WeekNumber)`, `(CustomerId, AgreementNumber, WeekNumber, TransactionValue, ReceiptNumber)`

Stores payment receipt records generated from NFS transactions, including PDF content.

| Column | Type | Notes |
|--------|------|-------|
| `AgreementPaymentId` | bigint IDENTITY | |
| `CustomerId` | bigint | NFS Customer_Id |
| `CustomerName` | nvarchar(255) | |
| `CustomerAddress` | nvarchar(255) | |
| `AgreementId` | bigint | NFS Agreement_Id |
| `AgreementNumber` | bigint | NFS Agreement_Num |
| `Insurance` | bit | |
| `BranchNumber` | int | |
| `BranchAddress` | nvarchar(255) | |
| `RepresentativeId` | bigint | NFS Representative_Id |
| `RepresentativeName` | nvarchar(255) | |
| `WeekNumber` | int | Accounting week |
| `TransactionDate` | datetime | |
| `TransactionCreationDate` | datetime | |
| `TransactionType` | char(2) | Agreement_Transaction_Type_Code |
| `TransactionValue` | numeric(24,6) | |
| `ReceiptNumber` | nvarchar(255) | |
| `Sequence` | int | |
| `CreationDate` | datetime | |
| `ReceiptContentPdf` | varchar(MAX) | Receipt content |
| `ReceiptPdf` | varchar(MAX) | Full PDF |

Also present: `AgreementPayments_bk` and `AgreementPayments_tmp` — identical structure, used as backup and staging respectively.

---

## Schema: Customer_App_provident_app_customer

### FAQs
**PK:** `IdQuestion`
FAQ tree structure with `IdQuestionFather` for parent-child hierarchy.

### FAQsIResp
Same structure as `FAQs` but no PK — likely a staging/response table.

### Notifacion
**PK:** `IdNotifacion`
Push notification records sent to customers. Includes `TipoUsuario`, `CustomerId`, `Titulo`, `Mensaje`, `Data` (JSON payload).

---

## Schema: Pesos_Offer_CognitoRoleAuthorizations

AWS Cognito + Provident role authorization mapping.

### AppClients
**PK:** `id` | **UK:** `AppId`
Registered application clients. `AllowAll` flag and optional pre-auth URL.

### Roles
**PK:** `ProvidentRoleID`
Maps Provident role IDs to role names.

### AuthorizedRole
**PK:** `id`
Junction table: `AppID_FK` → `AppClients`, `ProvidentRole_FK` → `Roles`.

---

## Schema: Pesos_Offer_FloatControlDB

Cash float control and bank reference management.

| Table | PK | Description |
|-------|----|-------------|
| `bank` | `id` | Bank catalogue (name, status) |
| `branch_pilot` | `id` | Branches in pilot programme |
| `branch_activities` | `id` | Activity tracking (button clicks, events) |
| `branch_activities_permisions` | `id` | Which branches can perform which activities |
| `reference_type` | `id` | Types of bank references |
| `reference_status` | `id` | Statuses for references |
| `references_gen` | `id` | Bank reference records (bank, type, status, amount, voucher URL, section, agency) |
| `cash_assign` | no PK | Cash assignment between agents (assign_id → receive_id, amount, folio, status, geolocation) |
| `cash_assign_cp` | no PK | Cash assignment — star agent to DM flow |
| `Balancing_Transaction_Type_Desc` | `(Code, Lang)` | Multilingual descriptions for balancing transaction types |

---

## Schema: Pesos_Offer_LeadsDigitales

Digital lead capture and processing pipeline.

| Table | PK | Description |
|-------|----|-------------|
| `tblLeadsDigitales` | `ID` | Main leads table — captures web/digital loan application leads |
| `EstatusOferta` | `IdEstatus` | Lead/offer status catalogue |
| `MedioContactacion` | `Id` | Contact channel catalogue |
| `tblMotivoRechazo` | `ID` | Rejection reason catalogue |
| `Cobertura_CP` | `Id` | Postal code coverage mapping to branches/regions |
| `WebPageLeadsControl` | `WebPageLeadsControlId` | Tracks web page lead processing |
| `EventSubscriptions` | `(topic, address)` | Pub/sub event subscriptions |
| `Sagas` | `id` | NServiceBus saga state storage |
| `SagaIndexes` | `(key, value, saga_type)` | Saga correlation indexes |
| `awsdms_truncation_safeguard` | `(task, guid, key)` | AWS DMS protection |
| `tblLogErrores` | `ID` | Error log entries |

### tblLeadsDigitales — Key Columns
| Column | Notes |
|--------|-------|
| `ALT_ID` | Alternative external ID |
| `TipoPrestamo` | Loan type |
| `Nombre` / `ApellidoPaterno` / `ApellidoMaterno` | Name |
| `FechaNacimiento` | Birth date |
| `Celular` / `TelefonoCasa` | Phone numbers |
| `CP` | Postal code |
| `CorreoElectronico` | Email |
| `CscApiStatusCode` | External credit API status |
| `GDSEstatusCliente` / `GDSDrEstatus` | GDS scoring results |
| `GDSIdCliente` | NFS Customer_Id if matched |
| `GdsMonto` / `GdsPlazo` | Approved offer amount/term |
| `IdEstatus` | FK → `EstatusOferta` |
| `BranchNumber` | Target branch |
| `SmsContactoEnviado` | SMS sent flag |
| `MedioContactacion` | FK → `MedioContactacion` |
| `Latitud/Longitud*` | Geolocation fields |
| Various `WebPage*` columns | Web analytics metadata |
| `PuntajeConversion` | Conversion score |

---

## Schema: Pesos_Offer_Originacion

Loan origination workflow. Manages the full digital origination process from lead to disbursement.

### Core Origination Tables

| Table | PK | Description |
|-------|----|-------------|
| `ExpedienteClienteVacio` | `IdExpedienteCliente` | **Main** case file — tracks each digital origination attempt |
| `ExpedienteClienteResp` | `IdExpedienteCliente` | Response/approved variant of case file |
| `ExpedienteClienteHistorial` | `IdExpedienteHistorial` | Audit history of case file state changes |
| `ExpedienteClienteLog` | no PK | Full log of all case file events |
| `ExpedienteCliente_BKPGDS` | `IdExpedienteCliente` | GDS processing backup |
| `ExpedienteCliente_respaldo` | `IdExpedienteCliente` | General backup snapshot |
| `DetalleContrato` | `Id` | Contract detail (generation date, signing date, expiry) |
| `DetalleKYC` | `ID` | KYC (Know Your Customer) verification data |
| `ExpedienteConsentimientoLegalario` | `IdExpedienteCliente` | Legal consent flags (caratula, protesta, conformidad, pagaré) |
| `ExpedienteDiff_Geo` | `idexpedienteCliente` | Geolocation comparison |
| `DocumentoTradicional` | `IdDocumento` | Uploaded documents (type, URL, KYC status) |

### ExpedienteClienteVacio — Key Columns
| Column | Notes |
|--------|-------|
| `IdKiban` | Kiban (external) customer ID |
| `IdOriginacion` | Origination system ID |
| `IdOferta` | Offer ID |
| `IdPaso` | Current step in workflow |
| `Agencia` | Agency ID |
| `Cliente` | NFS Customer_Id |
| `NombreCliente` | Customer name |
| `RFCCliente` | Tax ID |
| `SemanaVigenciaMsgPesos` | Offer validity week |
| `AprobadoVenta` | Sales approval flag |
| `AprobadoRegistro` | Registration approval flag |
| `OfertaAutorizada` | Authorized offer amount |
| `MontoDispersar` | Amount to disburse |
| `referencia` | Payment reference |
| `folioContrato` / `numeroContrato` | Contract folio and number |
| `IdTipoPago` | Payment method type |
| `IdTipoCliente` / `IdTipoProducto` | Customer and product type |
| `Cheque` | Cheque number |
| `IdEstatusCheque` | FK → `EstatusCheque` |
| `idEstatusOfertaEspecial` | FK → `EstatusOfertaEspecial` |
| `FicoScore` / `RazonesFicoScore` | Credit score |
| `PuntajeConversion` | Conversion score |
| `CancelaOrdenPago` / `CancelaContrato` | Cancellation flags |
| `PasoPrevCC` | Previous step before customer service |

---

### Catalogue / Reference Tables

| Table | PK | Description |
|-------|----|-------------|
| `CatBranches` | `Number` | Branch catalogue (name, company, status) |
| `CatCompanias` | `CompanyId` | Company catalogue (RFC, address, email) |
| `CatTiposRechazosAutomaticos` | `Id` | Automatic rejection types |
| `EstatusCheque` | `Id` | Cheque status codes |
| `EstatusOfertaSS` | `Id` | Offer status for SS (social security) flow |
| `EstatusOfertaEspecial` | `idEstatusOfertaEspecial` | Special offer status codes |
| `BackOfficeCatSubOfferType` | `SubOfferType` | Sub-offer type catalogue |
| `BackOfficeCatErrores` | `IdError` | Error catalogue |
| `BackOfficeTiposMovimiento` | `BackOfficeTipoMovimientoId` | Movement types for backoffice |
| `BackofficeTipoObjeto` | `BackofficeTipoObjetoId` | Object types for backoffice |
| `CorreoTemplate` | `CorreoTemplateId` | Email templates (subject, body, HTML flag) |

---

### Operational / Process Tables

| Table | PK | Description |
|-------|----|-------------|
| `Accounting_Week` | `(Accounting_Week_Num, Company_Code)` | Week calendar (start/end date, month code) |
| `AgenciaVacante` | `AgenciaVacanteId` | Vacant agency/section assignments |
| `AgencyStructure` | no PK | Agency organisational structure snapshot |
| `ArchivoEmpleados` | `Id` | Uploaded employee files log |
| `AvisoLegalUsuario` | no PK | Legal notice acceptance per FocusId |
| `BackOfficeArchivosCargados` | `IdArchivo` | Backoffice uploaded files log |
| `BackofficeUsuarios` | `BackofficeUsuarioId` | Backoffice user access management |
| `Bitacota` | `IdBitacora` | Activity log (action, detail, file name, count) |
| `CdcLog` | `IdCdcLog` | Credit bureau (CDC) consultation log |
| `Clientes_TelefonosRepetidos` | no PK | Customers with duplicate phone numbers |
| `Concilacion_ProviDigital_focus` | `id` | Reconciliation between digital origination and NFS Focus data |
| `DiaInhabilTelecomm` | `id` | Non-business days for Telecomm disbursements |
| `EstadoAsignacionExpDT_CS` | `Id` | CS assignment state catalogue |
| `EstructuraAgencia_SC` | `Id` | CS (Customer Service) agency structure mapping |
| `ArticuloModelos` | no PK | Product article models (for merchandise loans) |
| `ConcilacionProviDigital_focus` | `id` | See above |

### Concilacion_ProviDigital_focus — Purpose
Compares fields between the digital origination system and NFS Focus for each contract:
- `*_Digital` vs `*_Focus` columns for: RFC, Name, Surname, Birth Date, Gender, Mobile, Contract Number, Contract Type, Term, Product Type, Amount, TAP, First Payment, Subsequent Payment, Registration Date, Address, Marketing source
- `*_Comparacion` tinyint flag (0=match, 1=mismatch)
