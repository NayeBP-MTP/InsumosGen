# Mapeo Excel → Base de Datos (18 Ofertas)

## Catálogos de Referencia

### CatSaleType
- **F7049160-F367-438C-A0A8-0B63F6B03EBD** = Home Credit (Tradicional)
- **21BE783E-8B08-405D-A449-A21FABC8E113** = Negocio (Integral)

### CatCustomerType
- **D681D8CC-F364-499A-9322-F6AEDBBF24AE** = Cliente Nuevo
- **4819CA7D-5A32-4857-A6B2-12C99D5EA295** = Frecuente

### CatPaymentTerm
- **81C7FA1C-FFB3-4CF3-AEB7-BDDE1A8A4D6C** = 12 sem
- **403E89C5-B995-4AA1-8ADA-5B99E0267BB2** = 32 sem
- **E2741F66-A665-491E-84AB-EB0DECDA3E8A** = 42 sem
- **E1B43A01-C984-4D50-A468-A4E8FCDA1296** = 52 sem

### CatPaymentTermType
- **B771BFC0-D40A-49A7-8372-72F7776A6338** = N1 (ShouldDisplay=1)
- **44B1FFD7-F5E3-4B49-A771-E03C80627593** = N2 (ShouldDisplay=1)
- **0383C426-64C5-497E-9E90-779650EEF86C** = N3 (ShouldDisplay=1)

---

## Mapeo Escenario por Escenario

### Escenario 1 (Excel fila 1) → Ofertas 1-2

**Excel:**
- Monto Solicitado: $5,000
- Plazo 1: 12 semanas
- Monto Autorizado #2: (vacío - solo 1 oferta)
- Plazo 2: (vacío)
- Tipo Seguro: **Tradicional**
- Resultado: **Etiqueta N1 Visible**
- Tipo Usuario: **Nuevo**
- Cantidad: 2
- Sucursal: **SLP**

**BD Actual (Ofertas 1-2):**
| Oferta 1 | 25DCA8C7-560E-4025-AF7C-E56413FA1A48 | 85120 | Home Credit | Cliente Nuevo | 5000 | 12 sem | (eliminar) | (eliminar) | N1 | 1 | San Luis Potosi 2 |
| Oferta 2 | BC360B4B-D73A-460F-8240-6541C3531863 | 601022 | Home Credit | Cliente Nuevo | 5000 | 12 sem | (eliminar) | (eliminar) | N1 | 1 | San Luis Potosi 2 |

**Cambios Necesarios:**
- Oferta 1: Cambiar a SLP, ajustar montos/plazos, cambiar a N1
- Oferta 2: Ajustar montos/plazos, cambiar a N1

---

### Escenario 2 (Excel fila 2) → Ofertas 3-4

**Excel:**
- Monto: $4,500 / 12 sem
- Monto #2: $10,500 / 32 sem
- Tipo: **Tradicional**
- Resultado: **Etiqueta N1 Visible**
- Usuario: **Frecuente**
- Sucursal: **SLP**

**BD Actual:**
| Oferta 3 | 3F366374-2598-4D77-B4AE-7E9FF10600B1 | 85120 | Home Credit | Frecuente | 4500 | 12 sem | 10500 | 32 sem | N1 | 1 | San Luis Potosi 2 |
| Oferta 4 | 965756F8-F046-4F36-804A-02491C7BC89F | 601022 | Home Credit | Frecuente | 4500 | 12 sem | 10500 | 32 sem | N1 | 1 | San Luis Potosi 2 |

---

### Escenario 3 (Excel fila 3) → Ofertas 5-6

**Excel:**
- Monto: $3,500 / 12 sem
- Tipo: **Tradicional**
- Resultado: **Etiqueta N1 Visible**
- Usuario: **Nuevo**
- Sucursal: **SLP**

**BD Actual:**
| Oferta 5 | 91BDB477-89AE-455B-AA06-8F9CF3B3A530 | 85120 | Home Credit | Cliente Nuevo | 3500 | 12 sem | (eliminar) | (eliminar) | N1 | 1 | San Luis Potosi 2 |
| Oferta 6 | 771D10AC-677A-4EE4-836F-138AE0471EDF | 601022 | Home Credit | Cliente Nuevo | 3500 | 12 sem | (eliminar) | (eliminar) | N1 | 1 | San Luis Potosi 2 |

---

### Escenario 4 (Excel fila 4) → Ofertas 7-8

**Excel:**
- Monto: $10,500 / 42 sem
- Monto #2: $5,000 / 12 sem
- Tipo: **Integral**
- Resultado: **Etiqueta N1 Visible**
- Usuario: **Frecuente**
- Sucursal: **Zacatecas**

**BD Actual:**
| Oferta 7 | CC4B8A31-CE6A-40CD-8302-DA3C0658DBE2 | 85120 | Negocio | Frecuente | 10500 | 42 sem | 5000 | 12 sem | N1 | 1 | Zacatecas |
| Oferta 8 | 4AAB5567-AB50-4249-BCEC-5DF47AD69251 | 601022 | Negocio | Frecuente | 10500 | 42 sem | 5000 | 12 sem | N1 | 1 | Zacatecas |

---

### Escenario 5 (Excel fila 5) → Ofertas 9-10

**Excel:**
- Monto: $7,500 / 32 sem
- Tipo: **Integral**
- Resultado: **Etiqueta N1 Visible**
- Usuario: **Nuevo**
- Sucursal: **Aguascalientes**

**BD Actual:**
| Oferta 9 | B3EA6615-AF47-435A-B783-AD424CB792E6 | 85120 | Negocio | Cliente Nuevo | 7500 | 32 sem | (eliminar) | (eliminar) | N1 | 1 | Aguascalientes 1 |
| Oferta 10 | 19EC9494-008E-4B70-B27F-87C5516157FB | 601022 | Negocio | Cliente Nuevo | 7500 | 32 sem | (eliminar) | (eliminar) | N1 | 1 | Aguascalientes 1 |

---

### Escenario 6 (Excel fila 6) → Ofertas 11-12

**Excel:**
- Monto: $5,500 / 32 sem
- Monto #2: $7,500 / 42 sem
- Tipo: **Integral**
- Resultado: **Etiqueta N1 Visible**
- Usuario: **Frecuente**
- Sucursal: **Zacatecas**

**BD Actual:**
| Oferta 11 | 23D24ADA-086D-4587-A335-499BB3E642FB | 85120 | Negocio | Frecuente | 5500 | 32 sem | 7500 | 42 sem | N1 | 1 | Zacatecas |
| Oferta 12 | 8385BEAD-EC91-4F5D-BC23-7896751FC341 | 601022 | Negocio | Frecuente | 5500 | 32 sem | 7500 | 42 sem | N1 | 1 | Zacatecas |

---

### Escenario 7 (Excel fila 7) → Ofertas 13-14

**Excel:**
- Monto: $4,000 / 12 sem
- Tipo: **Tradicional**
- Resultado: **Etiqueta N1 Visible**
- Usuario: **Nuevo**
- Sucursal: **Aguascalientes**

**BD Actual:**
| Oferta 13 | 907B8C9E-9026-47E2-88C4-6A80F107F36E | 85120 | Home Credit | Cliente Nuevo | 4000 | 12 sem | (eliminar) | (eliminar) | N1 | 1 | Aguascalientes 1 |
| Oferta 14 | D08987BA-89B2-430F-99D9-1E3E5C4A3BCD | 601022 | Home Credit | Cliente Nuevo | 4000 | 12 sem | (eliminar) | (eliminar) | N1 | 1 | Aguascalientes 1 |

---

### Escenario 8 (Excel fila 8) → Ofertas 15-16

**Excel:**
- Monto: $4,000 / 12 sem
- Monto #2: $10,500 / 32 sem
- Tipo: **Tradicional**
- Resultado: **Etiqueta N1 Visible**
- Usuario: **Frecuente**
- Sucursal: **Aguascalientes**

**BD Actual:**
| Oferta 15 | D2453662-E539-4C26-B980-3DB9A3A45664 | 85120 | Home Credit | Frecuente | 4000 | 12 sem | 10500 | 32 sem | N1 | 1 | Aguascalientes 1 |
| Oferta 16 | 802591C9-6455-44ED-938E-EBAC665EA38D | 601022 | Home Credit | Frecuente | 4000 | 12 sem | 10500 | 32 sem | N1 | 1 | Aguascalientes 1 |

---

### Escenario 9 (Excel fila 9) → Ofertas 17-18

**Excel:**
- Monto: $4,000 / 12 sem
- Tipo: **Tradicional**
- Resultado: **Etiqueta N1 Visible**
- Usuario: **Nuevo**
- Sucursal: **Aguascalientes**

**BD Actual:**
| Oferta 17 | 03BECF9D-205C-43D1-A70B-F10EF0610DA0 | 85120 | Home Credit | Cliente Nuevo | 4000 | 12 sem | (eliminar) | (eliminar) | N1 | 1 | Aguascalientes 1 |
| Oferta 18 | F845C707-7A22-4E26-AE8E-936390E2664E | 601022 | Home Credit | Cliente Nuevo | 4000 | 12 sem | (eliminar) | (eliminar) | N1 | 1 | Aguascalientes 1 |

---

## Resumen de Cambios Globales

**Todos los escenarios requieren:**
1. Cambiar `CatPaymentTermType` de **Normal** (ID actual desconocido) a **N1** (`B771BFC0-D40A-49A7-8372-72F7776A6338`)
2. Ajustar montos y plazos según Excel
3. Cambiar tipo de cliente según Excel (Nuevo/Frecuente)
4. Cambiar tipo de seguro según Excel (Tradicional=Home Credit / Integral=Negocio)
5. Ajustar sucursal según Excel

**Nota Crítica:** El Excel NO especifica "Monto Solicitado" completo en todas las filas. Asumo que:
- Si solo hay 1 monto/plazo en Excel → la oferta tiene 1 sola `AuthorizedAmountAndTerm`
- Si hay 2 montos/plazos → la oferta tiene 2 `AuthorizedAmountAndTerm`
