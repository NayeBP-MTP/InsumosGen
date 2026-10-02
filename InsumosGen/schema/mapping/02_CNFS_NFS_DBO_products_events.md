# CNFS_NFS_DBO — Products, Elements & Events

## Product_Table
**PK:** `(Product_Id, Product_Db_Id)`

Top-level product definition (loan product catalogue).

| Column | Type | Notes |
|--------|------|-------|
| `Product_Id` | `T_Id IDENTITY(1,1)` | |
| `Product_Db_Id` | `T_Db_Id` | |
| `Company_Code` | `T_Company_Code` | FK → `Company` |
| `Description` | `T_Text` | |
| `Maintained_By_Db_Id` | `T_Db_Id` | |
| `Term` | `T_Small_Num` | Number of repayment periods |
| `Product_Term_Type_Code` | `T_Code` | FK → `Product_Term_Type_Desc` (weekly/monthly) |
| `Product_Type_Code` | `T_Code` | |
| `Rapid_Product_Code` | `T_Number` | Legacy rapid system code |
| `Third_Party_Product_Retailer_Code` | `T_Code` | |
| `Third_Party_Retailer_Code` | `T_Code` | |
| `Deleted_Flag` | `T_Delete_Flag` | |
| *(+ audit columns)* | |

---

## Product_Version_Table
**PK:** `(Product_Version_Id, Product_Version_Db_Id)`

A product version defines the detailed financial and operational parameters for a product at a given time (start/end date). Multiple versions can exist per product.

| Column | Type | Notes |
|--------|------|-------|
| `Product_Version_Id` | `T_Id IDENTITY(1,1)` | |
| `Product_Version_Db_Id` | `T_Db_Id` | |
| `Product_Id` | `T_Id` | FK → `Product_Table` |
| `Product_Db_Id` | `T_Db_Id` | |
| `Apr` | `T_Large_Percentage` | Annual Percentage Rate |
| `Amendment_Period` | `T_Number` | |
| `Amount_Payable` | `T_Amount` | |
| `Annual_Interest_Rate` | `T_Large_Percentage` | |
| `Apply_Default_Charge_Bln` | `T_Boolean` | |
| `Calculate_Arrears_Bln` | `T_Boolean` | |
| `Cancellation_Date` | `T_Date` | |
| `Cancellation_Period` | `T_Number` | |
| `Catalogue_Bln` | `T_Boolean` | Whether shown in product catalogue |
| `Customer_Max_Age` | `T_Age` | |
| `Customer_Min_Age` | `T_Age` | |
| `Deferred_Revenue` | `T_Percentage` | |
| `End_Date` | `T_Date` | |
| `Start_Date` | `T_Date` NOT NULL | |
| `Factor_A` / `Factor_B` / `Factor_C` | `T_Large_Percentage` | Rate factors |
| `First_Payment_Due` | `T_Number` | Weeks until first payment |
| `Flat_Rate_Interest` | `T_Percentage` | |
| `Insurance_Rate` | `T_Percentage` | |
| `Max_Issue_Value` / `Min_Issue_Value` | `T_Amount` | Issue value bounds |
| `Payment_Card_Bln` | `T_Boolean` | |
| `Print_On_Collecting_List_Bln` | `T_Boolean` | |
| `Product_Insured_Bln` | `T_Boolean` | |
| `Rebate_Rule_Code` | `T_Code` | |
| `Repayment_Frequency_Code` | `T_Code` | |
| `ESR_Minimum_Settlement_Period_With_Quote` | `T_Small_Num` | Early settlement |
| `ESR_Minimum_Settlement_Period_Without_Quote` | `T_Small_Num` | |
| `Esr_Quote_Required_Bln` | `T_Boolean` | |
| `Esr_Charge` | `T_Amount` | |
| `Long_Term_Product_Indicator_Bln` | `T_Boolean` | |
| `Annual_Interest_Rate_Is_Capped_Bln` | `T_Boolean` | |
| `Electronic_Issue_Bln` | `T_Boolean` | |
| `Electronic_Collection_Bln` | `T_Boolean` | |
| `Repayment_Schedule_Bln` | `T_Boolean` | |
| `Cash_Flow_Product_Bln` | `T_Boolean` | |
| `Codebtor_Bln` | `T_Boolean` | |
| `Available_For_Sale_Bln` | `T_Boolean` | |
| `Interest_Percentage` | `T_Large_Percentage` | |
| `Insurance_Fee_Percentage` | `T_Large_Percentage` | |
| `Collection_Fee_Percentage` | `T_Large_Percentage` | |
| `Admin_Fee_Percentage` | `T_Large_Percentage` | |
| `Upfront_Fee_Percentage` | `T_Percentage` | |
| `Deleted_Flag` | `T_Delete_Flag` | |
| *(+ audit columns)* | |

---

## Product_Version_Valid_Issue_Table
**PK:** `(Product_Version_Id, Product_Version_Db_Id, Issue_Value)`

Valid issue amounts for a product version, with corresponding repayment schedule values.

| Column | Type |
|--------|------|
| `Issue_Value` | `T_Small_Amount` |
| `Total_Amount_Payable` | `T_Small_Amount` |
| `First_Instalment_Value` | `T_Small_Amount` |
| `Regular_Instalment_Value` | `T_Small_Amount` |
| `Final_Instalment_Value` | `T_Small_Amount` |
| `APR` | `T_Percentage` |
| `Non_Cashflow_Medical_Insurance_Value` | `T_Small_Amount` |
| *(+ audit columns)* | |

---

## Product_Version_Valid_Issue_Element_Table
**PK:** `(Product_Version_Id, Product_Version_Db_Id, Issue_Value, Product_Element_Id, Product_Element_Db_Id)`

Breaks down a valid issue amount into individual element contractual values.

---

## Product_Version_Package_Table
**PK:** `(Product_Version_Id, Product_Version_Db_Id, Package_Id)`

Links product versions to packages.

---

## Product_Element_Table
**PK:** `(Product_Element_Id, Product_Element_Db_Id)`
**UK:** `(Product_Version_Id, Product_Version_Db_Id, Element_Type_Code, Deleted_Flag)`

Defines the elements (components) of a product version.

| Column | Type | Notes |
|--------|------|-------|
| `Product_Element_Id` | `T_Id IDENTITY(1,1)` | |
| `Element` | `T_Short_Text` | Element name |
| `Element_Type_Code` | `T_Code` | FK → `Element_Type` |
| `Product_Version_Id` | `T_Id` | FK → `Product_Version_Table` |
| `Maintained_By_Db_Id` | `T_Db_Id` | |
| `Deleted_Flag` | `T_Delete_Flag` | |
| *(+ audit columns)* | |

---

## Product_Element_Attribute_Table
**PK:** `(Product_Element_Attribute_Id, Product_Element_Attribute_Db_Id)`
**UK:** `(Product_Element_Id, Product_Element_Db_Id, Element_Attribute_Type_Code, Element_Attribute_Sub_Type_Code, Element_Type_Code)`

Stores typed attribute values for product elements (flexible key-value store).

| Column | Type | Notes |
|--------|------|-------|
| `Element_Attribute_Type_Code` | `T_3CharCode` | |
| `Element_Attribute_Sub_Type_Code` | `T_Short_Text` | |
| `Data_Type_Code` | `T_Code` | Indicates which Value_* column to use |
| `Value_Amount` | `T_Amount` | |
| `Value_Boolean` | `T_Boolean` | |
| `Value_Datetime` | `T_Datetime` | |
| `Value_Large_Percentage` | `T_Large_Percentage` | |
| `Value_Small_Num` | `T_Small_Num` | |
| `Value_Number` | `T_Big_Id` | |
| `Value_Short_Text` | `T_Short_Text` | |
| `Element_Attribute_Value_Code` | `T_Code` | |
| *(+ audit columns)* | |

---

## Product_Element_Event_Type_Rule_Table
**PK:** `(Product_Element_Event_Type_Rule_Id, Product_Element_Event_Type_Rule_Db_Id)`
**UK:** `(Product_Element_Id, Product_Element_Db_Id, Event_Type_Code)`

Defines how each event type affects each product element (due, paid, accrued, contractual value, discount).

| Column | Type |
|--------|------|
| `Event_Type_Code` | `T_Code` |
| `Impacts_Due_Bln` | `T_Boolean` |
| `Impacts_Paid_Bln` | `T_Boolean` |
| `Impacts_Contractual_Value_Bln` | `T_Boolean` |
| `Impacts_Accrued_Bln` | `T_Boolean` |
| `Impacts_Discount_Bln` | `T_Boolean` |
| `Allocate_Overpayment_Bln` | `T_Boolean` |
| `Sequence` | `T_Small_Num` |
| *(+ audit columns)* | |

---

## Product_Role_Table
**PK:** `(Product_Role_Id, Product_Role_Db_Id)`

Links products to the roles that can sell/manage them.

---

## Product_Group_Item_Table
**PK:** `(Product_Group_Item_Id, Product_Group_Item_Db_Id)`

Groups products together under a product group code.

| Column | Type |
|--------|------|
| `Product_Id` | `T_Id` |
| `Product_Db_Id` | `T_Db_Id` |
| `Product_Group_Code` | `T_Code` |
| `Deleted_Flag` | `T_Delete_Flag` |
| *(+ audit columns)* | |

---

## Product_Term_Type_Desc
**PK:** `(Product_Term_Type_Code, User_Language_Code)`

Multilingual descriptions for term types (e.g. Weekly, Monthly).

| Column | Type |
|--------|------|
| `Product_Term_Type_Code` | `T_Code` NOT NULL |
| `User_Language_Code` | `T_Code` NOT NULL |
| `Description` | `T_Short_Text` |
| `Short_Desc` | `T_Short_Text` |

---

## Package_Table
**PK:** `Package_Id`

Defines packages that can be bundled with product versions (e.g. insurance packages).

| Column | Type |
|--------|------|
| `Package_Id` | `T_Big_Id` NOT NULL |
| `Package_Type` | `T_Short_Text` |
| `Package_Name` | `T_Short_Text` |
| `Can_Be_Resigned_Bln` | `T_Boolean` |
| `Parent_Package_Id` | `T_Big_Id` (nullable) |
| `Finance_Package_Reference` | `T_Short_Text` |
| `Deleted_Flag` | `T_Delete_Flag` |
| *(+ audit columns)* | |

---

## Element_Table
**PK:** `(Element_Id, Element_Db_Id)`

An instantiated element on a specific agreement.

| Column | Type | Notes |
|--------|------|-------|
| `Element_Id` | `T_Id IDENTITY(1,1)` | |
| `Agreement_Id` | `T_Id` | FK → `Agreement_Table` |
| `Product_Element_Id` | `T_Id` | FK → `Product_Element_Table` |
| `Due_Start_Date` | `T_Date` | |
| `Accrual_Start_Date` | `T_Date` | |
| `Invalid_Bln` | `T_Boolean` | |
| `Creation_Date` | `T_Datetime` | |
| `Creation_Week` | `T_Number` | |
| `Deleted_Flag` | `T_Delete_Flag` | |
| *(+ audit columns)* | |

---

## Element_Type
**PK:** `Element_Type_Code`

Lookup table for element type codes (e.g. Principal, Interest, Insurance, Collection Fee).

---

## Element_Type_Desc
**PK:** `(Element_Type_Code, User_Language_Code)`
Multilingual descriptions and customer-facing text for element types.

---

## Element_Event_Type_Rule_Table
**PK:** `Element_Event_Type_Rule_Id`

Agreement-level override of event type rules for elements (similar to `Product_Element_Event_Type_Rule_Table` but per-agreement).

| Column | Type |
|--------|------|
| `Agreement_Id` / `Agreement_Db_Id` | IDs |
| `Element_Type_Code` | `T_Code` |
| `Event_Type_Code` | `T_Code` |
| `Company_Code` | `T_Company_Code` |
| `Impacts_Due_Bln` | `T_Boolean` |
| `Impacts_Paid_Bln` | `T_Boolean` |
| `Impacts_Contractual_Value_Bln` | `T_Boolean` |
| `Impacts_Accrued_Bln` | `T_Boolean` |
| `Impacts_Discount_Bln` | `T_Boolean` |
| `Allocate_Overpayment_Bln` | `T_Boolean` |
| `Sequence` | `T_Small_Num` |
| `Active_Bln` | `T_Boolean` |
| *(+ audit columns)* | |

---

## Event_Table
**PK:** `(Event_Id, Event_Db_Id)`

Core event record. Events represent any occurrence that financially impacts an agreement (e.g. payment, charge, settlement, amendment).

| Column | Type | Notes |
|--------|------|-------|
| `Event_Id` | `T_Id IDENTITY(1,1)` | |
| `Agreement_Id` | `T_Id` | FK → `Agreement_Table` |
| `Agreement_Transaction_Id` | `T_Id` | Optional FK → `Agreement_Transaction_Table` |
| `Event_Type_Code` | `T_Code` | FK → `Event_Type` |
| `Business_Transaction_Id` | `T_Dt_Transaction_Id` | |
| `Invalid_Bln` | `T_Boolean` | Soft invalidation |
| `Indicative_Bln` | `T_Boolean` | Preview/what-if flag |
| `Was_Triggered_by_Early_Settlement_Bln` | `T_Boolean` | |
| `Value` | `T_Small_Amount` | Optional monetary value |
| `Creation_Date` | `T_Datetime` | |
| `Creation_Week` | `T_Number` | |
| `Parent_Event_Id` | `T_Id` | Self-reference for child events |
| `Contraing_Event_Id` | `T_Id` | Contra/reversal event |
| `Latest_Event_Version` | `T_Id` | |
| `Is_Contra_Pair_bln` | `T_Boolean` | |
| `Deleted_Flag` | `T_Delete_Flag` | |
| *(+ audit columns)* | |

---

## Event_Version_Table
**PK:** `(Event_Id, Event_Db_Id, Event_Version)`

Versioning for events — each reprocessing creates a new version.

| Column | Type | Notes |
|--------|------|-------|
| `Event_Version` | `T_Id` | Version number |
| `Effective_Date` | `T_Date` | |
| `Posting_Date` | `T_Date` | |
| `Processed_Datetime` | `T_Datetime` | |
| `Agreement_Status_Code` | `T_Code` | Status at time of processing |
| `Settlement_Balance` | `T_Small_Amount` | |
| `Triggered_Settlement_Bln` | `T_Boolean` | |
| `Processed_Bln` | `T_Boolean` | |
| `Is_Latest_Version_bln` | `T_Boolean` | |
| `Event_Priority` | `T_Number` | |
| `Deleted_Flag` | `T_Delete_Flag` | |
| *(+ audit columns)* | |

---

## Event_Type
**PK:** `Event_Type_Code`

Defines a type of event and its processing rules.

| Column | Type | Notes |
|--------|------|-------|
| `Event_Type_Code` | `T_Code` | |
| `Agreement_Transaction_Type_Code` | `T_Code` | |
| `Credit_Indicator_Bln` | `T_Boolean` | Credit or debit |
| `Event_Priority` | `T_Number` | Processing order |
| `Invalidate_On_Issue_Amendment_Bln` | `T_Boolean` | |
| `Recreate_Periodic_Events_Bln` | `T_Boolean` | |
| `Reprocessable_Bln` | `T_Boolean` | |
| `Triggers_Early_Settlement_Bln` | `T_Boolean` | |
| `Display_On_Customer_Statement_Bln` | `T_Boolean` | |
| `Event_Process_Rule` | `T_Short_Text` | Rule engine code |
| `Event_Process_Rule_SP` | `T_Long_Text` | Stored procedure name |
| `Contraing_Event_Type_Code` | `T_Code` | Contra event type |
| `Active_Bln` | `T_Boolean` | |
| `Create_Zero_Value_Event_Bln` | `T_Boolean` | |
| `Impacts_TAP_And_Rates` | `T_Boolean` | |
| *(+ audit columns)* | |

---

## Event_Type_Desc
**PK:** `(Event_Type_Code, Language_Code)`
Multilingual descriptions and customer-facing text for event types.

---

## Event_Impact_Table
**PK:** `(Event_Impact_Id, Event_Impact_Db_Id)`

The financial impact of an event version on a specific element.

| Column | Type | Notes |
|--------|------|-------|
| `Event_Id` / `Event_Db_Id` | IDs | FK → `Event_Table` |
| `Event_Version` | `T_Id` | |
| `Element_Id` / `Element_Db_Id` | IDs | FK → `Element_Table` |
| `Contractual_Value` | `T_Small_Amount` | |
| `Due` | `T_Small_Amount` | Amount due |
| `Contractual_Due` | `T_Large_Amount` | |
| `Accrued` | `T_Large_Amount` | |
| `Paid` | `T_Small_Amount` | |
| `Discount` | `T_Small_Amount` | |
| `Change_In_Due` | `T_Small_Amount` | Delta from previous version |
| `Change_In_Accrued` | `T_Large_Amount` | |
| `Change_In_Paid` | `T_Small_Amount` | |
| `Change_In_Contractual_Value` | `T_Small_Amount` | |
| `Change_in_Discount` | `T_Small_Amount` | |
| `Due_Rounding_Difference` | `T_Large_Amount` | |
| `Effective_Date` | `T_Date` | |
| `Event_Priority` | `T_Number` | |
| `Posting_Date` | `T_Date` | |
| `Deleted_Flag` | `T_Delete_Flag` | |
| *(+ audit columns)* | |

---

## Event_Impact_Status_Table
**PK:** `(Event_Impact_Status_Id, Event_Impact_Status_Db_Id)`

Status of element-level impact (active flags for payment holiday, payment freeze, HCS accrual).

| Column | Type |
|--------|------|
| `Element_Active_Bln` | `T_Boolean` |
| `Payment_Holiday_Active_Bln` | `T_Boolean` |
| `Payment_Holiday_Count` | `T_Number` |
| `Payment_Freeze_Active_Bln` | `T_Boolean` |
| `Payment_Freeze_Count` | `T_Number` |
| `Accrue_HCS_This_Week_Bln` | `T_Boolean` |
| `Accure_HCS_Count` | `T_Number` |
| *(+ audit columns)* | |

---

## Event_Impact_TAP_And_Rates_Table
**PK:** `(Event_Impact_TAP_And_Rates_Id, Event_Impact_TAP_And_Rates_Db_Id)`

TAP (Total Amount Payable) and instalment rate impacts at the agreement level per event version.

| Column | Type |
|--------|------|
| `Total_Amount_Payable` | `T_Amount` |
| `First_Instalment_Value` | `T_Amount` |
| `Regular_Instalment_Value` | `T_Amount` |
| `Final_Instalment_Value` | `T_Amount` |
| *(+ audit columns)* | |

---

## Payment_Flexibility_Request_Table
**PK:** `(Payment_Flexibility_Request_Id, Payment_Flexibility_Request_Db_Id)`

Records customer requests for payment flexibility (holiday or freeze).

| Column | Type | Notes |
|--------|------|-------|
| `Agreement_Id` / `Agreement_Db_Id` | IDs | FK → `Agreement_Table` |
| `Payment_Flexibility_Reason_Code` | `T_Code` | |
| `Effective_Date` | `T_Date` | |
| `Event_Id` / `Event_Db_Id` | IDs | Resulting event |
| `Payment_Holiday_Bln` | `T_Boolean` | |
| `Payment_Freeze_Bln` | `T_Boolean` | |
| `Accrue_HCS_Bln` | `T_Boolean` | |
| `Cancellation_Requested_Bln` | `T_Boolean` | |
| `Cancellation_Processed_Bln` | `T_Boolean` | |
| `Deleted_Flag` | `T_Delete_Flag` | |
| *(+ audit columns)* | |

---

## Payment_Flexibility_Reason
**PK:** `Payment_Flexibility_Reason_Code`

## Payment_Flexibility_Reason_Desc
**PK:** `(Payment_Flexibility_Reason_Code, User_Language_Code)`

---

## Suppress_PI_Request_Table
**PK:** `(Suppress_PI_Request_Id, Suppress_PI_Request_Db_Id)`

Requests to suppress periodic instalments for an agreement.

---

## Property
**PK:** `Property_ID`
**UK:** `(Property_Name, Property_Extension_Name)`

Dynamic property/attribute definition system — used for flexible custom fields.

| Column | Type | Notes |
|--------|------|-------|
| `Property_ID` | `T_Id IDENTITY(1,1)` | |
| `Property_Name` | `T_Text` | |
| `Property_Extension_Name` | `T_Text` | Disambiguator |
| `Company_Code` | `T_Company_Code` | |
| `Tab_Name` | `T_Short_Text` | UI tab grouping |
| `Data_Type_Code` | `T_Code` | Type of stored value |
| `Active_Bln` | `T_Boolean` | |
| `Is_Mandatory_Bln` | `T_Boolean` | |
| `Property_Abbreviation` | `T_3CharCode` | |
| `Property_Code_Selected_From_Code` | `T_Code` | FK → `Property_Code_Selected_From` |
| Various `Default_*_Value` columns | | One per data type |
| *(+ audit columns)* | |

---

## Property_Desc
**PK:** `(Property_ID, User_Language_Code)`
**UK:** `(Property_Name, Property_Extension_Name, User_Language_Code)`

---

## Property_Impact
**PK:** `(Impacting_Property_ID, Impacted_Property_ID, Impacting_Property_Number)`

Rules that define how changing one property value affects another property's appearance or value.

---

## Property_Value
**PK:** `(Property_Code_Selected_From_Code, Property_Value_Code)`

Valid selectable values for a property that has a code list.

---

## Property_Value_Desc
**PK:** `(Property_Code_Selected_From_Code, Property_Value_Code, User_Language_Code)`

---

## Property_Code_Selected_From
**PK:** `Property_Code_Selected_From_Code`

Registry of code list sources for property values.
