# Instrucciones para Actualizar las 18 Ofertas

## 📋 Resumen del Entregable

Este paquete contiene los scripts necesarios para ajustar **18 ofertas existentes** en la base de datos `AVTs` según las especificaciones del Excel proporcionado.

---

## 📁 Archivos Generados

| Archivo | Descripción |
|---------|-------------|
| `01_mapeo_excel_vs_bd.md` | Documentación del mapeo entre Excel y BD (referencia) |
| `02_UPDATE_18_ofertas.sql` | **Script principal de actualización** |
| `03_validacion_post_update.sql` | Query de validación post-cambios |
| `README_INSTRUCCIONES.md` | Este archivo (instrucciones de uso) |

---

## ⚠️ IMPORTANTE: Antes de Ejecutar

### 1. Hacer Backup
```sql
-- Backup de tablas críticas
SELECT * INTO Offer_BACKUP_20260216 FROM dbo.Offer;
SELECT * INTO AuthorizedAmountAndTerm_BACKUP_20260216 FROM dbo.AuthorizedAmountAndTerm;
SELECT * INTO Customer_BACKUP_20260216 FROM dbo.Customer;
```

### 2. Verificar Ambiente
- ✅ Confirmar que estás en **ambiente de QA/DEV** (NO producción)
- ✅ Verificar que tienes permisos de `UPDATE`, `INSERT`, `DELETE`
- ✅ Confirmar que DBeaver está conectado a la BD `AVTs`

---

## 🚀 Pasos de Ejecución

### Paso 1: Ejecutar el Script de Actualización

1. Abrir `02_UPDATE_18_ofertas.sql` en DBeaver
2. **Revisar** el script completo (son ~600 líneas)
3. Ejecutar el script completo (`Ctrl+Enter` o botón "Execute SQL Script")
4. Verificar que no haya errores en la consola de DBeaver

**Tiempo estimado:** 2-3 minutos

---

### Paso 2: Ejecutar la Validación

1. Abrir `03_validacion_post_update.sql` en DBeaver
2. Ejecutar el script completo
3. Revisar los resultados

**Resultados Esperados:**

#### Query Principal (18 filas)
Todas las ofertas deben mostrar:
- `CatPaymentTermTypeName` = **N1**
- `CatPaymentTermTypeShouldDisplay` = **1**
- Montos y plazos según Excel
- Sucursales correctas (SLP/Zacatecas/Aguascalientes)

#### Resumen de Distribución
```
Sucursal          | NivelPrecio | TipoSeguro  | TipoCliente | CantidadOfertas
------------------|-------------|-------------|-------------|----------------
SLP               | N1          | Home Credit | Nuevo       | 4
SLP               | N1          | Home Credit | Frecuente   | 2
Zacatecas         | N1          | Negocio     | Frecuente   | 4
Zacatecas         | N1          | Negocio     | Nuevo       | 2
Aguascalientes    | N1          | Home Credit | Nuevo       | 4
Aguascalientes    | N1          | Home Credit | Frecuente   | 2
Aguascalientes    | N1          | Negocio     | Nuevo       | 2
```

**Totales esperados:**
- **18 ofertas** en total
- **6 por sucursal** (SLP: 6, Zacatecas: 6, Aguascalientes: 6)
- **12 Tradicionales** (Home Credit) + **6 Integrales** (Negocio)
- **10 Nuevos** + **8 Frecuentes**
- **Todas con nivel N1**

---

## ✅ Checklist de Validación

Después de ejecutar los scripts, verifica:

- [ ] Las 18 ofertas tienen `CatPaymentTermTypeName = 'N1'`
- [ ] Todas tienen `ShouldDisplay = 1`
- [ ] Distribución por sucursal: 6 SLP, 6 Zacatecas, 6 Aguascalientes
- [ ] Distribución por tipo: 12 Tradicional, 6 Integral
- [ ] Distribución por cliente: 10 Nuevo, 8 Frecuente
- [ ] Montos y plazos coinciden con el Excel

---

## 🔧 Troubleshooting

### Error: "Cannot update identity column"
**Solución:** Ignorar, el script no actualiza columnas de identidad.

### Error: "Violation of PRIMARY KEY constraint"
**Solución:** Revisar que no haya duplicados en `AuthorizedAmountAndTerm`. Ejecutar:
```sql
SELECT OfferId, COUNT(*) 
FROM AuthorizedAmountAndTerm 
WHERE OfferId IN ('25DCA8C7-560E-4025-AF7C-E56413FA1A48', ...)
GROUP BY OfferId 
HAVING COUNT(*) > 2;
```

### Error: "The UPDATE statement conflicted with the FOREIGN KEY constraint"
**Solución:** Verificar que los IDs de catálogos existen:
```sql
SELECT * FROM CatPaymentTermType WHERE Name = 'N1';
SELECT * FROM CatSaleType WHERE Name IN ('Home Credit', 'Negocio');
SELECT * FROM CatCustomerType WHERE Name IN ('Cliente Nuevo', 'Frecuente');
```

### Algunos registros no se actualizaron
**Solución:** Revisar la sección específica del script que falló y ejecutarla manualmente.

---

## 📊 Mapeo Excel → Base de Datos

### Escenarios del Excel (9 filas × 2 ofertas c/u = 18 total)

| Escenario | Ofertas | Monto/Plazo | Tipo | Cliente | Sucursal |
|-----------|---------|-------------|------|---------|----------|
| 1 | 1-2 | $5,000/12sem | Tradicional | Nuevo | SLP |
| 2 | 3-4 | $4,500/12sem + $10,500/32sem | Tradicional | Frecuente | SLP |
| 3 | 5-6 | $3,500/12sem | Tradicional | Nuevo | SLP |
| 4 | 7-8 | $10,500/42sem + $5,000/12sem | Integral | Frecuente | Zacatecas |
| 5 | 9-10 | $7,500/32sem | Integral | Nuevo | Aguascalientes |
| 6 | 11-12 | $5,500/32sem + $7,500/42sem | Integral | Frecuente | Zacatecas |
| 7 | 13-14 | $4,000/12sem | Tradicional | Nuevo | Aguascalientes |
| 8 | 15-16 | $4,000/12sem + $10,500/32sem | Tradicional | Frecuente | Aguascalientes |
| 9 | 17-18 | $4,000/12sem | Tradicional | Nuevo | Aguascalientes |

---

## 🔄 Rollback (Si algo sale mal)

Si necesitas revertir los cambios:

```sql
-- Restaurar desde backup
TRUNCATE TABLE dbo.Offer;
INSERT INTO dbo.Offer SELECT * FROM Offer_BACKUP_20260216;

TRUNCATE TABLE dbo.AuthorizedAmountAndTerm;
INSERT INTO dbo.AuthorizedAmountAndTerm SELECT * FROM AuthorizedAmountAndTerm_BACKUP_20260216;

TRUNCATE TABLE dbo.Customer;
INSERT INTO dbo.Customer SELECT * FROM Customer_BACKUP_20260216;
```

---

## 📞 Soporte

Si encuentras algún problema:

1. Revisar la sección de **Troubleshooting** arriba
2. Ejecutar el query de validación para identificar qué falló
3. Revisar el archivo `01_mapeo_excel_vs_bd.md` para entender el mapeo
4. Contactar al equipo de desarrollo con el error específico

---

## ✨ Siguiente Paso

Una vez validado que todo está correcto, el frontend (usando `spCustomerSearch`) debería mostrar las 18 ofertas con:
- **Etiqueta "N1" visible**
- **Montos y plazos** según Excel
- **Tipo de seguro** correcto (Tradicional/Integral)
- **Tipo de cliente** correcto (Nuevo/Frecuente)

**¡Listo para pruebas funcionales!** 🎉
