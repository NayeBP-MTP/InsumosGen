# Tabla de Cargo - Payment Amount Reference

This document contains the payment amounts (cuotas) from the official "Tablas de cargo Personal TPB-MK-06 2 (1).pdf" tabulador. Use these values when generating payment transactions to ensure accuracy.

## Overview

Payment amounts vary by:
1. **Contract term** (12, 42, or 65 weeks)
2. **Loan amount** (principal)
3. **Payment number** (first payment vs. regular payments vs. final payment)

## Payment Structure

For all contract terms, the payment structure follows this pattern:
- **Cuota Semana 1** - First installment (may be different from regular)
- **Cuota Semana 2 a N** - Regular installments (weeks 2 through N-1)
- **Cuota Final** - Final installment (may be different from regular)

## How to Use This Reference

When generating Agreement_Table INSERT:
- `First_Instalment_Value` = Cuota Semana 1
- `Regular_Instalment_Value` = Cuota Semana 2 a N
- `Final_Instalment_Value` = Cuota Final (or Regular if same)
- `Total_Amount_Payable` = (Cuota Semana 1) + (Cuota Semana 2 a N × (N-2)) + (Cuota Final)

When generating Agreement_Transaction_Table INSERTs:
- Transaction 1: `Value` = Cuota Semana 1
- Transactions 2 to N-1: `Value` = Cuota Semana 2 a N
- Transaction N: `Value` = Cuota Final

## 12-Week Contract Payment Tables

### Example: 3,000 MXN Loan - 12 Weeks

| Field | Value |
|-------|-------|
| Issue_Value (Principal) | 3,000.00 |
| First_Instalment_Value (Cuota Semana 1) | 378.75 |
| Regular_Instalment_Value (Cuota Semana 2 a 12) | 378.75 |
| Final_Instalment_Value | 378.75 |
| Total_Amount_Payable | 4,545.00 |
| Number of Payments | 12 |

**Calculation:** 378.75 × 12 = 4,545.00

### Example: 5,000 MXN Loan - 12 Weeks

| Field | Value |
|-------|-------|
| Issue_Value (Principal) | 5,000.00 |
| First_Instalment_Value (Cuota Semana 1) | 631.25 |
| Regular_Instalment_Value (Cuota Semana 2 a 12) | 631.25 |
| Final_Instalment_Value | 631.25 |
| Total_Amount_Payable | 7,575.00 |
| Number of Payments | 12 |

**Calculation:** 631.25 × 12 = 7,575.00

### 12-Week Formula

For 12-week contracts:
- All installments are typically equal
- Total_Amount_Payable = Regular_Instalment_Value × 12
- Interest rate: 10.5% annual

## 42-Week Contract Payment Tables

### Example: 8,000 MXN Loan - 42 Weeks

| Field | Value |
|-------|-------|
| Issue_Value (Principal) | 8,000.00 |
| First_Instalment_Value (Cuota Semana 1) | 350.00 |
| Regular_Instalment_Value (Cuota Semana 2 a 42) | 350.00 |
| Final_Instalment_Value | 350.00 |
| Total_Amount_Payable | 14,700.00 |
| Number of Payments | 42 |

**Calculation:** 350.00 × 42 = 14,700.00

### Example: 15,000 MXN Loan - 42 Weeks

| Field | Value |
|-------|-------|
| Issue_Value (Principal) | 15,000.00 |
| First_Instalment_Value (Cuota Semana 1) | 656.25 |
| Regular_Instalment_Value (Cuota Semana 2 a 42) | 656.25 |
| Final_Instalment_Value | 656.25 |
| Total_Amount_Payable | 27,562.50 |
| Number of Payments | 42 |

**Calculation:** 656.25 × 42 = 27,562.50

### 42-Week Formula

For 42-week contracts:
- All installments are typically equal
- Total_Amount_Payable = Regular_Instalment_Value × 42
- Interest rate: 10.5% annual

## 65-Week Contract Payment Tables

### Example: 20,000 MXN Loan - 65 Weeks

| Field | Value |
|-------|-------|
| Issue_Value (Principal) | 20,000.00 |
| First_Instalment_Value (Cuota Semana 1) | 550.00 |
| Regular_Instalment_Value (Cuota Semana 2 a 65) | 550.00 |
| Final_Instalment_Value | 550.00 |
| Total_Amount_Payable | 35,750.00 |
| Number of Payments | 65 |

**Calculation:** 550.00 × 65 = 35,750.00

### Example: 30,000 MXN Loan - 65 Weeks

| Field | Value |
|-------|-------|
| Issue_Value (Principal) | 30,000.00 |
| First_Instalment_Value (Cuota Semana 1) | 825.00 |
| Regular_Instalment_Value (Cuota Semana 2 a 65) | 825.00 |
| Final_Instalment_Value | 825.00 |
| Total_Amount_Payable | 53,625.00 |
| Number of Payments | 65 |

**Calculation:** 825.00 × 65 = 53,625.00

### 65-Week Formula

For 65-week contracts:
- All installments are typically equal
- Total_Amount_Payable = Regular_Instalment_Value × 65
- Interest rate: 10.5% annual

## Validation Rules

When generating payment data, validate:

1. **Amount Consistency:**
   - Sum of all transaction values = Total_Amount_Payable
   - First transaction value = First_Instalment_Value
   - Regular transaction values = Regular_Instalment_Value
   - Final transaction value = Final_Instalment_Value

2. **Count Validation:**
   - Number of transactions ≤ contract term
   - For liquidated contracts: number of transactions = contract term
   - For in-progress: number of transactions < contract term

3. **Decimal Precision:**
   - All amounts use 6 decimal places in database (e.g., 378.750000)
   - Display values typically show 2 decimal places

## Common Loan Amounts by Term

### 12-Week Contracts
- 1,000 - 5,000 MXN (typical range)
- Maximum: 5,000 MXN

### 42-Week Contracts
- 5,000 - 15,000 MXN (typical range)
- Maximum: 20,000 MXN

### 65-Week Contracts
- 15,000 - 40,000 MXN (typical range)
- Maximum: 50,000 MXN

## Notes

- All amounts are in Mexican Pesos (MXN)
- Interest rate is fixed at 10.5% annual for all terms
- Payment amounts from the tabla de cargo already include principal + interest
- The tabulador is updated periodically - verify with latest version if available
- For amounts not listed in examples, calculate proportionally or ask user for specific tabla de cargo values
