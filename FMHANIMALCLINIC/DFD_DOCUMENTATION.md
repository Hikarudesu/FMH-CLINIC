# FMH Animal Clinic - Data Flow Diagram (DFD) Documentation

## System Overview

**FMH Animal Clinic** is a comprehensive veterinary clinic management system built with Django. It supports multi-branch operations, AI-powered diagnostics, point-of-sale transactions, staff management, and a complete patient/appointment lifecycle.

---

## External Entities

| Entity | Description |
|--------|-------------|
| **Pet Owner** | Clients who own pets - book appointments, view records, make payments |
| **Veterinarian** | Staff who examine and treat animals |
| **Receptionist/Cashier** | Front desk staff managing appointments and POS transactions |
| **Admin/Manager** | System administrators |
| **GROQ AI API** | External AI diagnostic service |

---

## Data Stores

| ID | Name | Description |
|----|------|-------------|
| D1 | Users | User accounts, roles, permissions |
| D2 | Patients | Pet profiles, owner info |
| D3 | Appointments | Bookings, schedules |
| D4 | Medical Records | Treatments, prescriptions |
| D5 | Inventory | Products, stock levels |
| D6 | Sales/POS | Transactions, payments, billing |
| D7 | Staff | Employee profiles, schedules, payroll |
| D8 | Analytic Reports | Generated reports data |
| D9 | AI Diagnosis | AI-generated diagnostics |

---

## Level 0 DFD - Context Diagram

```
                                    INBOUND DATA
                                    ────────────
                    ┌─────────────────────────────────────────────┐
                    │  • Registration/Login                       │
                    │  • Appointment Booking                      │
                    │  • Pet Information                          │
                    │  • Payment Details                          │
                    │  • Medical Records Input                    │
                    │  • AI Diagnosis Request                     │
                    └─────────────────────────────────────────────┘
                                         │
                                         ▼
┌──────────────┐              ┌─────────────────────┐              ┌──────────────┐
│  PET OWNER   │─────────────►│                     │◄─────────────│   GROQ AI    │
│              │◄─────────────│   FMH ANIMAL CLINIC │─────────────►│     API      │
└──────────────┘              │       SYSTEM        │              └──────────────┘
                              │        (0)          │
┌──────────────┐              │                     │              ┌──────────────┐
│ VETERINARIAN │─────────────►│                     │◄─────────────│    ADMIN     │
│              │◄─────────────│                     │─────────────►│              │
└──────────────┘              └─────────────────────┘              └──────────────┘
                                         │
                                         ▼
                    ┌─────────────────────────────────────────────┐
                    │  • Appointment Confirmation                 │
                    │  • Medical Updates                          │
                    │  • Receipts & Statements                    │
                    │  • AI Diagnosis Results                     │
                    │  • Reports                                  │
                    └─────────────────────────────────────────────┘
                                    OUTBOUND DATA
                                    ─────────────
```

### Level 0 Data Flows

| Flow | Data | Direction |
|------|------|-----------|
| Pet Owner → System | Registration, Login | INBOUND |
| Pet Owner → System | Appointment Request | INBOUND |
| Pet Owner → System | Pet Information | INBOUND |
| Pet Owner → System | Payment Details | INBOUND |
| Veterinarian → System | Symptoms, Diagnosis, Treatment | INBOUND |
| System → GROQ API | AI Diagnosis Request | INBOUND |
| Admin → System | Staff/Inventory Data | INBOUND |
| System → Pet Owner | Appointment Confirmation | OUTBOUND |
| System → Pet Owner | Medical Updates | OUTBOUND |
| System → Pet Owner | Receipts, Statements | OUTBOUND |
| GROQ API → System | AI Diagnosis Response | OUTBOUND |
| System → Admin/Staff | Reports | OUTBOUND |

---

## Level 1 DFD - Main Processes

```
                                     EXTERNAL ENTITIES
       ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
       │   Pet Owner   │  │  Veterinarian │  │ Receptionist/ │  │     Admin     │
       │               │  │               │  │    Cashier    │  │               │
       └───────┬───────┘  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘
               │                  │                  │                  │
               │ Login            │ Login            │ Login            │ Login
               │ credentials,     │ credentials,     │ credentials,     │ credentials,
               │ Registration     │ Registration     │ Registration     │ Registration
               ▼                  ▼                  ▼                  ▼
       ┌───────────────────────────────────────────────────────────────────────────┐
       │                         1.0 USER & ACCESS MANAGEMENT                      │
       │                                   ─────► D1                               │
       └───────────────────────────────────────────────────────────────────────────┘
               │                  │                  │                  │
               │ Session,         │ Session,         │ Session,         │ Session,
               │ Access token     │ Access token     │ Access token     │ Access token
               ▲                  ▲                  ▲                  ▲
               └─────────────────────────────────────────────────────────┘
                                    (returns to entities above)

               │                  │                  │                  │
               │ Booking          │ Symptoms,        │ Items,           │ Stock adj,
               │ request,         │ Diagnosis,       │ Payment          │ Employee info,
               │ Date/Time,       │ Treatment        │                  │ Query params
               │ Pet info         │                  │                  │
               ▼                  ▼                  ▼                  ▼
       ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
       │     2.0     │    │     4.0     │    │     6.0     │    │     7.0     │
       │ APPOINTMENT │    │   MEDICAL   │    │     POS     │    │  INVENTORY  │
       │ MANAGEMENT  │    │   RECORDS   │    │             │    │             │
       │   ─► D3     │    │   ─► D4     │    │   ─► D6     │    │   ─► D5     │
       └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
               │                  │                  │                  │
               │ Confirmation,    │ Medical history, │ Receipt,         │ Stock levels,
               │ Status           │ Follow-up        │ Invoice          │ Low stock alert
               ▲ to Pet Owner     ▲ to Pet Owner     ▲ to Pet Owner     ▲ to Admin
               └─────────────────────────────────────────────────────────┘
                                    (returns to entities above)

               │                  │                  │                  │
               │ Create Pet       │ Pet data,        │ Employee info,   │ Query
               │ (from 2.0)       │ Symptoms         │ Schedule, Payroll│ params
               ▼                  ▼                  ▼                  ▼
       ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
       │     3.0     │    │     5.0     │    │     8.0     │    │     9.0     │
       │   PATIENT   │    │     AI      │    │    STAFF    │    │  ANALYTIC   │
       │ MANAGEMENT  │    │ DIAGNOSTICS │    │ MANAGEMENT  │    │   REPORTS   │
       │   ─► D2     │    │   ─► D9     │    │   ─► D7     │    │   ─► D8     │
       └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
               │                  │                  │                  │
               │ Pet profile,     │ AI diagnosis,    │ Vet availability,│ Reports
               │ Clinical status  │ Recommendations  │ Payslips         │ (PDF/Excel)
               ▲ to Pet Owner     ▲ to Vet          ▲ to Vet/Staff     ▲ to Admin
               └─────────────────────────────────────────────────────────┘
                                    (returns to entities above)


       PROCESS CONNECTIONS:
       ─────────────────────
       2.0 ────────────► 3.0  (Create Pet from walk-in)
       4.0 ────────────► 3.0  (Clinical status signal)
       4.0 ────────────► 5.0  (Pet data for AI)
       5.0 ◄───────────► GROQ API (External)
       6.0 ────────────► 7.0  (Stock deduction signal)
       8.0 ────────────► 2.0  (Vet availability)
       8.0 ────────────► 9.0  (Staff data for reports)
```

### Level 1 Process Summary

#### 1.0 User & Access Management → D1
| Flow | Data |
|------|------|
| Pet Owner → 1.0 | Login credentials, Registration |
| Veterinarian → 1.0 | Login credentials, Registration |
| Receptionist/Cashier → 1.0 | Login credentials, Registration |
| Admin → 1.0 | Login credentials, Registration |
| 1.0 → Pet Owner | Session, Access token |
| 1.0 → Veterinarian | Session, Access token |
| 1.0 → Receptionist/Cashier | Session, Access token |
| 1.0 → Admin | Session, Access token |

#### 2.0 Appointment Management → D3
| Flow | Data |
|------|------|
| Pet Owner → 2.0 | Booking request, Date/Time |
| 2.0 → Pet Owner | Confirmation, Status |
| 2.0 → 3.0 | Create Pet (walk-in) |

#### 3.0 Patient Management → D2
| Flow | Data |
|------|------|
| Pet Owner → 3.0 | Pet info, Owner details |
| 3.0 → Pet Owner | Pet profile, Clinical status |
| 4.0 → 3.0 | Clinical status update (signal) |

#### 4.0 Medical Records → D4
| Flow | Data |
|------|------|
| Veterinarian → 4.0 | Symptoms, Diagnosis, Treatment, Prescription |
| 4.0 → Pet Owner | Medical history, Follow-up date |
| 4.0 → 3.0 | Clinical status update (signal) |
| 4.0 → 5.0 | Pet data, Symptoms |

#### 5.0 AI Diagnostics → D9
| Flow | Data |
|------|------|
| 4.0 → 5.0 | Pet history, Current symptoms |
| 5.0 → GROQ API | AI diagnosis request |
| GROQ API → 5.0 | AI diagnosis response |
| 5.0 → Veterinarian | Primary diagnosis, Differentials, Recommended tests |

#### 6.0 POS → D6
| Flow | Data |
|------|------|
| Receptionist/Cashier → 6.0 | Items/Services, Payment method, Payment amount |
| 6.0 → Pet Owner | Receipt, Invoice, Transaction ID |
| 6.0 → 7.0 | Stock deduction (signal) |

#### 7.0 Inventory Management → D5
| Flow | Data |
|------|------|
| Admin → 7.0 | Stock adjustment, Transfer request, Product info |
| 6.0 → 7.0 | Stock deduction (signal) |
| 7.0 → Admin | Stock levels, Low stock alert, Transfer status |

#### 8.0 Staff Management → D7
| Flow | Data |
|------|------|
| Admin → 8.0 | Employee info, Schedule data, Payroll period, Salary/Deductions |
| 8.0 → Veterinarian | Vet availability, Payslips |
| 8.0 → 2.0 | Vet availability |
| 8.0 → 9.0 | Staff data |

#### 9.0 Analytic Reports → D8
| Flow | Data |
|------|------|
| Admin → 9.0 | Query parameters, Date range, Report type |
| 9.0 → Admin | Generated reports (PDF/Excel) |

---

## Level 2 DFD - Detailed Process Breakdown

### 2.0 Appointment Management

```
┌───────────────┐                                              
│   Pet Owner   │                                              
└───────┬───────┘                                              
        │                                                      
        │ Booking request,                                     
        │ Date/Time,                                           
        │ Reason for visit                                     
        ▼                                                      
┌───────────────┐      ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│      2.1      │─────►│      2.2      │─────►│      2.3      │─────►│      2.4      │
│    BOOKING    │      │     CHECK     │      │    CREATE     │      │    STATUS     │
│    REQUEST    │      │  AVAILABILITY │      │  APPOINTMENT  │      │  MANAGEMENT   │
└───────────────┘      └───────┬───────┘      └───────┬───────┘      └───────┬───────┘
                               │                      │                      │
                               │ Vet schedules        │ Appointment data     │ Confirmation,
                               ▼                      ▼                      │ Status
                         ┌──────────┐           ┌──────────┐                 │
                         │    D7    │           │    D3    │                 │
                         │  Staff   │           │  Appts   │                 │
                         └──────────┘           └──────────┘                 │
                                                                             ▲
        │                                                                    │
        │ Create Pet (walk-in)                                               │
        ▼                                                      ┌─────────────┴─┐
┌───────────────┐                                              │   Pet Owner   │
│      3.0      │                                              └───────────────┘
│   PATIENTS    │
└───────────────┘
```

---

### 3.0 Patient Management

```
┌───────────────┐                                              
│   Pet Owner   │                                              
└───────┬───────┘                                              
        │                                                      
        │ Pet Name/Species,                                    
        │ Owner Info                                           
        ▼                                                      
┌───────────────┐      ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│      3.1      │─────►│      3.2      │─────►│      3.3      │─────►│      3.4      │
│   REGISTER    │      │     STORE     │      │    UPDATE     │      │   CLINICAL    │
│      PET      │      │    PROFILE    │      │     INFO      │      │    STATUS     │
└───────────────┘      └───────┬───────┘      └───────────────┘      └───────┬───────┘
                               │                                             │
                               │ Pet profile                                 │ Pet profile,
                               ▼                                             │ Clinical status
                         ┌──────────┐                                        │
                         │    D2    │◄───────────────────────────────────────┘
                         │ Patients │                                        
                         └──────────┘                                        ▲
                               ▲                                             │
                               │ Clinical status update (signal)             │
                               │                                   ┌─────────┴─────┐
                         ┌──────────┐                              │   Pet Owner   │
                         │   4.0    │                              └───────────────┘
                         │ MEDICAL  │
                         │ RECORDS  │
                         └──────────┘
```

---

### 4.0 Medical Records

```
┌───────────────┐                                              
│  Veterinarian │                                              
└───────┬───────┘                                              
        │                                                      
        │ Symptoms,                                            
        │ Diagnosis,                                           
        │ Treatment/Rx,                                        
        │ Follow-up Date                                       
        ▼                                                      
┌───────────────┐      ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│      4.1      │─────►│      4.2      │─────►│      4.3      │─────►│      4.4      │
│    CREATE     │      │      ADD      │      │      SET      │      │    UPDATE     │
│    RECORD     │      │     ENTRY     │      │   FOLLOW-UP   │      │    STATUS     │
└───────────────┘      └───────┬───────┘      └───────────────┘      └───────┬───────┘
                               │                                             │
                               │ Medical record                              │ Medical history,
                               ▼                                             │ Follow-up date
                         ┌──────────┐    Signal    ┌──────────┐              │
                         │    D4    │─────────────►│    D2    │              │
                         │ Medical  │  Clinical    │ Patients │              │
                         │ Records  │  status      └──────────┘              ▲
                         └──────────┘                                        │
                                                                   ┌─────────┴─────┐
        │                                                          │   Pet Owner   │
        │ Pet data, Symptoms                                       └───────────────┘
        ▼
┌───────────────┐
│      5.0      │
│      AI       │
│  DIAGNOSTICS  │
└───────────────┘
```

---

### 5.0 AI Diagnostics

```
┌───────────────┐      ┌───────────────┐
│      3.0      │      │      4.0      │
│   PATIENTS    │      │   MEDICAL     │
└───────┬───────┘      └───────┬───────┘
        │                      │
        │ Pet Profile          │ Medical History,
        │                      │ Current Symptoms
        ▼                      ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│      5.1      │─────►│      5.2      │─────►│      5.3      │─────►│      5.4      │
│    COLLECT    │      │     BUILD     │      │     CALL      │      │     STORE     │
│   PET DATA    │      │   AI PROMPT   │      │   GROQ API    │      │   DIAGNOSIS   │
└───────────────┘      └───────────────┘      └───────┬───────┘      └───────┬───────┘
                                                      │                      │
                                      AI prompt       │                      │ AI diagnosis
                                      request         ▼                      │
                                              ┌──────────────┐               │
                                              │   GROQ AI    │               │
                                              │     API      │               │
                                              │  (External)  │               │
                                              └──────┬───────┘               │
                                                     │                       │
                                      AI diagnosis   │                       │ Store diagnosis
                                      response       │                       ▼
                                                     │                 ┌──────────┐
                                                     │                 │    D9    │
                                                     │                 │ AI Diag. │
                                                     │                 └──────────┘
                                                     │
                                                     │ Primary Diagnosis,
                                                     │ Differentials,
                                                     │ Recommended Tests
                                                     ▲
                                                     │
                                              ┌──────┴───────┐
                                              │ Veterinarian │
                                              └──────────────┘
```

---

### 6.0 Point of Sale (POS)

```
┌─────────────────────┐
│ Receptionist/Cashier│
└──────────┬──────────┘
           │
           │ Items/Services,
           │ Payment Method,
           │ Payment Amount
           ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│      6.1      │─────►│      6.2      │─────►│      6.3      │─────►│      6.4      │
│    CREATE     │      │      ADD      │      │    PROCESS    │      │   COMPLETE    │
│     SALE      │      │     ITEMS     │      │    PAYMENT    │      │     SALE      │
└───────────────┘      └───────┬───────┘      └───────────────┘      └───────┬───────┘
                               │                                             │
                               │ Product info                                │ Transaction,
                               ▼                                             │ Receipt, Invoice
                         ┌──────────┐                                        │
                         │    D5    │                                        │
                         │ Products │                                        │
                         └──────────┘                                        │
                                                                             ▼
                         ┌──────────┐    Stock deduction    ┌──────────┐
                         │    D5    │◄──────────────────────│    D6    │
                         │ Inventory│       (signal)        │  Sales   │
                         └──────────┘                       └──────────┘
                                                                             │
                                                                             │ Receipt,
                                                                             │ Invoice
                                                                             ▲
                                                                             │
                                                                   ┌─────────┴─────┐
                                                                   │   Pet Owner   │
                                                                   └───────────────┘
```

---

### 7.0 Inventory Management

```
┌───────────────┐      ┌───────────────┐
│     Admin     │      │     6.0       │
└───────┬───────┘      │     POS       │
        │              └───────┬───────┘
        │ Stock Adjustment,           │
        │ Transfer Request,           │ Stock deduction
        │ Product Info                │ (signal)
        ▼                             ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│      7.1      │─────►│      7.2      │─────►│      7.3      │─────►│      7.4      │
│    PRODUCT    │      │     STOCK     │      │     STOCK     │      │   LOW STOCK   │
│  MANAGEMENT   │      │  ADJUSTMENT   │      │   TRANSFER    │      │     ALERT     │
└───────────────┘      └───────┬───────┘      └───────────────┘      └───────┬───────┘
                               │                                             │
                               │ Update stock                                │
                               ▼                                             │
                         ┌──────────┐                                        │
                         │    D5    │                                        │
                         │ Inventory│                                        │
                         └──────────┘                                        │
                                                                             │
                                                                             │ Stock Levels,
                                                                             │ Low Stock Alert,
                                                                             │ Transfer Status
                                                                             ▲
                                                                             │
                                                                     ┌───────┴───────┐
                                                                     │     Admin     │
                                                                     └───────────────┘
```

---

### 8.0 Staff Management

```
┌───────────────┐
│     Admin     │
└───────┬───────┘
        │
        │ Employee Info,
        │ Schedule Data,
        │ Payroll Period,
        │ Salary/Deductions
        ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│      8.1      │─────►│      8.2      │─────►│      8.3      │─────►│      8.4      │
│   EMPLOYEE    │      │   SCHEDULE    │      │   GENERATE    │      │   RELEASE     │
│   PROFILE     │      │  MANAGEMENT   │      │   PAYSLIPS    │      │   PAYROLL     │
└───────┬───────┘      └───────┬───────┘      └───────────────┘      └───────┬───────┘
        │                      │                                             │
        │ Store profile        │ Store schedule                              │
        ▼                      ▼                                             │
  ┌──────────┐           ┌──────────┐                                        │
  │    D7    │           │    D7    │                                        │
  │  Staff   │           │  Staff   │                                        │
  └──────────┘           └──────────┘                                        │
                                                                             │
        Vet availability ────────────────────────► 2.0 Appointments          │
        Staff data ──────────────────────────────► 9.0 Analytic Reports      │
                                                                             │
                                                                             │ Staff Profiles,
                                                                             │ Vet Availability,
                                                                             │ Payslips
                                                                             ▲
                                                                             │
                                                           ┌─────────────────┴──────────────────┐
                                                           │         Veterinarian/Staff         │
                                                           └────────────────────────────────────┘
```

---

## Complete Data Flow Summary

### Process Interconnections

```
    ┌──────────────────────────────────────────────────────────────────┐
    │                        CLINICAL FLOW                             │
    │  2.0 Appointments ──► 3.0 Patients ◄──► 4.0 Medical ──► 5.0 AI  │
    └──────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │                     OPERATIONS FLOW                              │
    │           6.0 POS ◄──► 7.0 Inventory ◄──► 8.0 Staff             │
    └──────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │                   ANALYTIC REPORTS FLOW                         │
    │   9.0 Analytic Reports ◄── Data from ALL processes             │
    └──────────────────────────────────────────────────────────────────┘
```

### Inbound/Outbound Summary Table

#### INBOUND Flows (Source → Process)
| Source | Process | Data |
|--------|---------|------|
| Pet Owner | 1.0 | Login credentials, Registration |
| Veterinarian | 1.0 | Login credentials, Registration |
| Receptionist/Cashier | 1.0 | Login credentials, Registration |
| Admin | 1.0 | Login credentials, Registration |
| Pet Owner | 2.0 | Booking request, Date/Time |
| Pet Owner | 3.0 | Pet info, Owner details |
| Veterinarian | 4.0 | Symptoms, Diagnosis, Treatment |
| 4.0 | 5.0 | Pet data, Symptoms |
| Receptionist/Cashier | 6.0 | Items, Payment |
| Admin | 7.0 | Stock adjustments |
| 6.0 | 7.0 | Stock deduction (signal) |
| Admin | 8.0 | Employee info, Payroll data |
| Admin | 9.0 | Query parameters |

#### OUTBOUND Flows (Process → Destination)
| Process | Destination | Data |
|---------|-------------|------|
| 1.0 | Pet Owner | Session, Access token |
| 1.0 | Veterinarian | Session, Access token |
| 1.0 | Receptionist/Cashier | Session, Access token |
| 1.0 | Admin | Session, Access token |
| 2.0 | Pet Owner | Confirmation, Status |
| 3.0 | Pet Owner | Pet profile, Clinical status |
| 4.0 | Pet Owner | Medical history, Follow-up |
| 4.0 | 3.0 | Clinical status (signal) |
| 5.0 | Veterinarian | AI Diagnosis, Recommendations |
| 6.0 | Pet Owner | Receipt, Invoice |
| 7.0 | Admin | Stock levels, Alerts |
| 8.0 | Veterinarian | Schedules, Payslips |
| 9.0 | Admin | PDF/Excel Reports |

---

## Legend

| Symbol | Meaning |
|--------|---------|
| **Rectangle** | Process |
| **D1, D2, etc.** | Data Store |
| **Arrow →** | Data Flow Direction |
| **INBOUND** | Data entering the process |
| **OUTBOUND** | Data leaving the process |

---

## Document Information

| Attribute | Value |
|-----------|-------|
| System | FMH Animal Clinic |
| Framework | Django 6.0.3 |
| Database | SQLite |
| AI Integration | GROQ API |
| Multi-Branch | Yes |
