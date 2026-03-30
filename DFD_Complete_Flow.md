# FMH Animal Clinic - Complete Data Flow Diagram (Level 0 → 2)

## Overview

This document presents the complete hierarchical Data Flow Diagram (DFD) for the FMH Animal Clinic Management System, showing the decomposition from the Context Diagram (Level 0) through to the detailed sub-processes (Level 2).

---

# 🔵 LEVEL 0: CONTEXT DIAGRAM

## System Overview

The Context Diagram shows the FMH Animal Clinic System as a **single process** interacting with **external entities**.

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              EXTERNAL ENTITIES                                       │
│                                                                                      │
│   👤 Pet Owner        👥 Walk-in Guest       🩺 Veterinarian       👩‍⚕️ Vet Assistant   │
│   💼 Receptionist     🔐 Superadmin          🤖 GROQ AI Service                      │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                      │
│                    ╔════════════════════════════════════════╗                       │
│                    ║     FMH ANIMAL CLINIC SYSTEM           ║                       │
│                    ║           (Process 0)                  ║                       │
│                    ╚════════════════════════════════════════╝                       │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                DATA STORES                                           │
│                                                                                      │
│   D1 Users    D2 Pets    D3 Appointments    D4 Medical Records    D5 AI Diagnoses   │
│   D6 Sales    D7 Inventory    D8 Employees                                          │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## External Entities (6)

| Entity | Role | Key Interactions |
|--------|------|------------------|
| **👤 Pet Owner** | Registered portal user | Register, book appointments, view records, pay bills |
| **👥 Walk-in Guest** | Unregistered visitor | Walk-in appointments, pay for services |
| **🩺 Veterinarian** | Licensed vet | Create medical records, request AI diagnosis, prescribe treatments |
| **👩‍⚕️ Vet Assistant** | Support staff | Assist with patient prep, record vitals |
| **💼 Receptionist** | Front desk | Manage appointments, process sales, handle inventory |
| **🔐 Superadmin** | System admin | Configure system, manage users/roles/branches, oversee all operations |
| **🤖 GROQ AI** | External service | Provide AI-powered diagnostic suggestions |

## Data Stores (8)

| ID | Name | Contains |
|----|------|----------|
| **D1** | Users | User accounts, roles, permissions, activity logs |
| **D2** | Pets | Pet profiles, owner info, clinical status |
| **D3** | Appointments | Bookings, schedules, follow-ups |
| **D4** | Medical Records | Consultations, treatments, prescriptions |
| **D5** | AI Diagnoses | AI-generated diagnoses, review status |
| **D6** | Sales & Payments | Transactions, payments, refunds, cash drawer |
| **D7** | Products & Inventory | Products, stock levels, adjustments, transfers |
| **D8** | Employees | Staff profiles, schedules, licenses |

## Major Data Flows

```
        ┌─────────────────────────────────────────────────────────────────┐
        │                     INBOUND DATA FLOWS                          │
        ├─────────────────────────────────────────────────────────────────┤
        │ Pet Owner → System                                              │
        │   • Registration data (username, email, password, phone)        │
        │   • Pet information (name, species, breed, DOB, photo)          │
        │   • Appointment requests (date, time, branch, reason)           │
        │   • Product reservations                                        │
        ├─────────────────────────────────────────────────────────────────┤
        │ Walk-in Guest → System                                          │
        │   • Walk-in appointment data                                    │
        │   • Guest info (name, phone, email)                             │
        │   • Payment for services                                        │
        ├─────────────────────────────────────────────────────────────────┤
        │ Veterinarian → System                                           │
        │   • Medical records (vitals, diagnosis, treatment, Rx)          │
        │   • AI diagnostic requests                                      │
        │   • Record signing/approval                                     │
        │   • Follow-up scheduling                                        │
        ├─────────────────────────────────────────────────────────────────┤
        │ Receptionist → System                                           │
        │   • Appointment management (confirm, cancel, reschedule)        │
        │   • Sales transactions (items, payments)                        │
        │   • Customer information                                        │
        │   • Cash drawer operations                                      │
        ├─────────────────────────────────────────────────────────────────┤
        │ Superadmin → System                                             │
        │   • System configuration                                        │
        │   • User/role management                                        │
        │   • Branch setup                                                │
        │   • Permission assignments                                      │
        └─────────────────────────────────────────────────────────────────┘

        ┌─────────────────────────────────────────────────────────────────┐
        │                    OUTBOUND DATA FLOWS                          │
        ├─────────────────────────────────────────────────────────────────┤
        │ System → Pet Owner                                              │
        │   • Appointment confirmations                                   │
        │   • Medical records access                                      │
        │   • Notifications & reminders                                   │
        │   • Receipts & statements                                       │
        ├─────────────────────────────────────────────────────────────────┤
        │ System → Walk-in Guest                                          │
        │   • Receipts                                                    │
        │   • Service information                                         │
        ├─────────────────────────────────────────────────────────────────┤
        │ System → Veterinarian                                           │
        │   • Patient information & history                               │
        │   • Daily schedule                                              │
        │   • AI diagnostic suggestions                                   │
        │   • Payslip                                                     │
        ├─────────────────────────────────────────────────────────────────┤
        │ System → Receptionist                                           │
        │   • Daily appointment schedule                                  │
        │   • Customer data                                               │
        │   • Inventory status & alerts                                   │
        │   • Receipts                                                    │
        ├─────────────────────────────────────────────────────────────────┤
        │ System → Superadmin                                             │
        │   • System-wide reports                                         │
        │   • All branch data                                             │
        │   • Audit logs                                                  │
        │   • Analytics dashboard                                         │
        └─────────────────────────────────────────────────────────────────┘

        ┌─────────────────────────────────────────────────────────────────┐
        │                   EXTERNAL SERVICE FLOWS                        │
        ├─────────────────────────────────────────────────────────────────┤
        │ System ↔ GROQ AI Service                                        │
        │   • OUT: Pet symptoms, medical history                          │
        │   • IN:  AI diagnosis, recommendations, warning signs           │
        └─────────────────────────────────────────────────────────────────┘
```

---

# 🟢 LEVEL 1: MAIN PROCESSES

## Process Decomposition

Level 0 (single system) decomposes into **9 main processes**:

```
                        ┌────────────────────────────────┐
                        │   LEVEL 0: FMH CLINIC SYSTEM   │
                        └────────────────────────────────┘
                                       │
        ┌──────────────────────────────┼───────────────────────────────┐
        │                              │                               │
        ▼                              ▼                               ▼
┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐
│ 1.0 User & Access │  │ 2.0 Patient Mgmt  │  │ 3.0 Appointments  │
│   Management      │  │                   │  │   Management      │
└───────────────────┘  └───────────────────┘  └───────────────────┘
        │                              │                               │
        ▼                              ▼                               ▼
┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐
│ 4.0 Medical       │  │ 5.0 AI            │  │ 6.0 Point of      │
│   Records Mgmt    │  │   Diagnostics     │  │   Sale (POS)      │
└───────────────────┘  └───────────────────┘  └───────────────────┘
        │                              │                               │
        ▼                              ▼                               ▼
┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐
│ 7.0 Inventory     │  │ 8.0 Employee      │  │ 10.0 Reports &    │
│   Management      │  │   Management      │  │   Analytics       │
└───────────────────┘  └───────────────────┘  └───────────────────┘
```

## Process Flow Diagram

```
                              ┌─────────────┐
                              │  👤 Users   │
                              │ (All Roles) │
                              └──────┬──────┘
                                     │
                                     ▼
                        ╔═══════════════════════════╗
                        ║  1.0 USER & ACCESS MGMT   ║
                        ║  ─────────────────────    ║
                        ║  • Registration           ║
                        ║  • Authentication         ║
                        ║  • Role Management        ║
                        ║  • Permission Control     ║
                        ╚═══════════════════════════╝
                                     │
                                     │ Authenticated User
                                     ▼
         ┌───────────────────────────┴───────────────────────────┐
         │                                                       │
         ▼                                                       ▼
╔═══════════════════════════╗                       ╔═══════════════════════════╗
║   2.0 PATIENT MGMT        ║                       ║   8.0 EMPLOYEE MGMT       ║
║   ────────────────────    ║                       ║   ──────────────────      ║
║   • Pet Registration      ║                       ║   • Staff Management      ║
║   • Pet Profile Mgmt      ║                       ║   • Schedule Mgmt         ║
║   • Owner Management      ║                       ║   • License Tracking      ║
╚═══════════════════════════╝                       ╚═══════════════════════════╝
         │                                                       │
         │ Pet Data                                   Vet Schedules
         ▼                                                       │
╔═══════════════════════════╗                                    │
║   3.0 APPOINTMENT MGMT    ║ ◄──────────────────────────────────┘
║   ────────────────────    ║
║   • Appointment Booking   ║
║   • Schedule Management   ║
║   • Follow-up Scheduling  ║
╚═══════════════════════════╝
         │
         │ Appointment Data
         ▼
╔═══════════════════════════╗          ╔═══════════════════════════╗
║   4.0 MEDICAL RECORDS     ║ ───────► ║   5.0 AI DIAGNOSTICS      ║
║   ────────────────────    ║ Symptoms ║   ──────────────────      ║
║   • Record Creation       ║          ║   • Request Preparation   ║
║   • Consultation Entry    ║ ◄─────── ║   • AI Communication      ║
║   • Treatment Recording   ║ AI Rec   ║   • Diagnosis Review      ║
║   • Record Signing        ║          ╚═══════════════════════════╝
╚═══════════════════════════╝                      │
         │                                         │
         │ Treatment Data                          │ AI Integration
         ▼                                         ▼
╔═══════════════════════════╗          ┌───────────────────────────┐
║   6.0 POINT OF SALE       ║          │       🤖 GROQ AI          │
║   ────────────────────    ║          │    (External Service)     │
║   • Sales Transaction     ║          └───────────────────────────┘
║   • Payment Processing    ║
║   • Cash Drawer Mgmt      ║
║   • Refund Processing     ║
╚═══════════════════════════╝
         │
         │ Stock Deduction
         ▼
╔═══════════════════════════╗
║   7.0 INVENTORY MGMT      ║
║   ────────────────────    ║
║   • Product Management    ║
║   • Stock Adjustment      ║
║   • Stock Transfer        ║
║   • Reservation Mgmt      ║
╚═══════════════════════════╝
         │
         │ All Data
         ▼
╔═══════════════════════════╗
║   10.0 REPORTS & ANALYTICS║
║   ────────────────────    ║
║   • Superadmin Reports    ║
║   • Inventory Reports     ║
║   • Operational Reports   ║
╚═══════════════════════════╝
```

## Level 1 Process Details

### Process 1.0: User & Access Management
- **Purpose**: Handle user authentication, registration, and role-based access control
- **Data Stores**: D1 (Users)
- **External Entities**: All users (login), Pet Owner (registration), Superadmin (role management)

### Process 2.0: Patient Management
- **Purpose**: Manage pet profiles and owner information
- **Data Stores**: D1 (Users), D2 (Pets)
- **External Entities**: Pet Owner, Walk-in Guest, Receptionist

### Process 3.0: Appointment Management
- **Purpose**: Handle appointment booking, scheduling, and follow-ups
- **Data Stores**: D2 (Pets), D3 (Appointments), D8 (Employees - for vet availability)
- **External Entities**: Pet Owner, Walk-in Guest, Receptionist, Veterinarian

### Process 4.0: Medical Records Management
- **Purpose**: Create and manage medical consultation records
- **Data Stores**: D2 (Pets), D3 (Appointments), D4 (Medical Records)
- **External Entities**: Veterinarian, Vet Assistant, Pet Owner (view only)

### Process 5.0: AI Diagnostics
- **Purpose**: Provide AI-powered diagnostic assistance
- **Data Stores**: D2 (Pets), D4 (Medical Records), D5 (AI Diagnoses)
- **External Entities**: Veterinarian, GROQ AI Service

### Process 6.0: Point of Sale
- **Purpose**: Handle sales transactions, payments, and refunds
- **Data Stores**: D6 (Sales & Payments), D7 (Inventory)
- **External Entities**: Receptionist, Pet Owner, Walk-in Guest

### Process 7.0: Inventory Management
- **Purpose**: Manage products, stock levels, and transfers
- **Data Stores**: D7 (Products & Inventory)
- **External Entities**: Receptionist, Pet Owner (reservations)

### Process 8.0: Employee Management
- **Purpose**: Manage staff profiles, schedules, and licenses
- **Data Stores**: D1 (Users), D8 (Employees)
- **External Entities**: Superadmin

### Process 10.0: Reports & Analytics
- **Purpose**: Generate business intelligence and reports
- **Data Stores**: ALL (D1-D8)
- **External Entities**: Superadmin

---

# 🟡 LEVEL 2: SUB-PROCESSES

## Level 1 → Level 2 Decomposition

```
┌────────────────────────────────────────────────────────────────────────────┐
│                      LEVEL 1 → LEVEL 2 MAPPING                              │
├────────────────────────────────────────────────────────────────────────────┤
│  LEVEL 1 PROCESS               LEVEL 2 SUB-PROCESSES                       │
│  ════════════════════════════════════════════════════════════════════════  │
│  1.0 User & Access Mgmt    →   1.1, 1.2, 1.3, 1.4                          │
│  2.0 Patient Management    →   2.1, 2.2, 2.3                               │
│  3.0 Appointment Mgmt      →   3.1, 3.2, 3.3                               │
│  4.0 Medical Records       →   4.1, 4.2, 4.3, 4.4                          │
│  5.0 AI Diagnostics        →   5.1, 5.2, 5.3                               │
│  6.0 Point of Sale         →   6.1, 6.2, 6.3, 6.4                          │
│  7.0 Inventory Mgmt        →   7.1, 7.2, 7.3, 7.4                          │
│  8.0 Employee Mgmt         →   8.1, 8.2, 8.3                               │
│  10.0 Reports & Analytics  →   10.1, 10.2, 10.3                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 1.0 USER & ACCESS MANAGEMENT

```
                         ┌───────────────────────┐
                         │  1.0 USER & ACCESS    │
                         │      MANAGEMENT       │
                         └───────────┬───────────┘
                                     │
         ┌───────────┬───────────────┼───────────────┬───────────┐
         ▼           ▼               ▼               ▼           │
    ┌─────────┐ ┌─────────┐    ┌─────────┐    ┌─────────┐       │
    │   1.1   │ │   1.2   │    │   1.3   │    │   1.4   │       │
    │  User   │ │ Authen- │    │  Role   │    │ Permis- │       │
    │ Regist. │ │ tication│    │  Mgmt   │    │  sion   │       │
    └────┬────┘ └────┬────┘    └────┬────┘    └────┬────┘       │
         │           │              │              │             │
         └───────────┴──────────────┴──────────────┘             │
                                │                                │
                                ▼                                │
                         ═══════════════                         │
                         │  D1 USERS   │                         │
                         ═══════════════                         │

INBOUND:  👤 Pet Owner → Registration Data
          👤 All Users → Login Credentials
          🔐 Superadmin → Role Definitions

OUTBOUND: → 👤 Pet Owner: Account Confirmation
          → 👤 All Users: Session/Dashboard Access
          → 🔐 Superadmin: Role Confirmation
```

---

## 2.0 PATIENT MANAGEMENT

```
                         ┌───────────────────────┐
                         │  2.0 PATIENT MGMT     │
                         └───────────┬───────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              ▼                      ▼                      ▼
         ┌─────────┐            ┌─────────┐            ┌─────────┐
         │   2.1   │            │   2.2   │            │   2.3   │
         │   Pet   │            │   Pet   │            │  Owner  │
         │ Regist. │            │ Profile │            │  Mgmt   │
         └────┬────┘            └────┬────┘            └────┬────┘
              │                      │                      │
              └──────────────────────┼──────────────────────┘
                                     ▼
                              ═══════════════
                              │  D2 PETS    │
                              ═══════════════

INBOUND:  👤 Pet Owner → Pet Information (name, species, breed)
          👥 Walk-in Guest → Guest Pet Info
          💼 Receptionist → Customer Updates

OUTBOUND: → 👤 Pet Owner: Registration Confirmation
          → D3: Auto-sync owner info (via signal)
```

---

## 3.0 APPOINTMENT MANAGEMENT

```
                         ┌───────────────────────┐
                         │  3.0 APPOINTMENT MGMT │
                         └───────────┬───────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              ▼                      ▼                      ▼
         ┌─────────┐            ┌─────────┐            ┌─────────┐
         │   3.1   │            │   3.2   │            │   3.3   │
         │Appoint- │            │Schedule │            │Follow-up│
         │ Booking │            │  Mgmt   │            │Schedule │
         └────┬────┘            └────┬────┘            └────┬────┘
              │                      │                      │
              ▼                      ▼                      ▼
       ═══════════════        ═══════════════        ═══════════════
       │D8 EMPLOYEES │        │D3 APPTS     │        │D4 RECORDS   │
       │(availability)│       │(bookings)   │        │(follow-up)  │
       ═══════════════        ═══════════════        ═══════════════

INBOUND:  👤 Pet Owner → Appointment Request
          👥 Walk-in Guest → Walk-in Request
          💼 Receptionist → Status Updates
          🩺 Veterinarian → Follow-up Request

OUTBOUND: → 👤 Pet Owner: Confirmation Email
          → 🩺 Veterinarian: Daily Schedule
          → 💼 Receptionist: Updated Schedule
```

---

## 4.0 MEDICAL RECORDS MANAGEMENT

```
                         ┌───────────────────────┐
                         │  4.0 MEDICAL RECORDS  │
                         └───────────┬───────────┘
                                     │
        ┌────────────┬───────────────┼───────────────┬────────────┐
        ▼            ▼               ▼               ▼            │
   ┌─────────┐  ┌─────────┐    ┌─────────┐    ┌─────────┐        │
   │   4.1   │  │   4.2   │    │   4.3   │    │   4.4   │        │
   │ Record  │  │ Consult │    │Treatment│    │ Record  │        │
   │Creation │  │  Entry  │    │Recording│    │Signing⚠️│        │
   └────┬────┘  └────┬────┘    └────┬────┘    └────┬────┘        │
        │            │              │              │              │
        └────────────┴──────────────┴──────────────┘              │
                                │                                 │
                                ▼                                 │
                     ═══════════════════════                      │
                     │   D4 MEDICAL RECORDS │                     │
                     ═══════════════════════                      │

INBOUND:  🩺 Veterinarian → Consultation Data (vitals, diagnosis)
          🩺 Veterinarian → Treatment Data (Tx, Rx)
          👩‍⚕️ Vet Assistant → Patient Prep Data

OUTBOUND: → 5.0 AI Diagnostics: Patient Symptoms
          → 👤 Pet Owner: Medical Records Access (view)
          → D7: Inventory impact (via POS)
```

---

## 5.0 AI DIAGNOSTICS

```
                         ┌───────────────────────┐
                         │   5.0 AI DIAGNOSTICS  │
                         └───────────┬───────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              ▼                      ▼                      ▼
         ┌─────────┐            ┌─────────┐            ┌─────────┐
         │   5.1   │   ────►    │   5.2   │   ────►    │   5.3   │
         │   AI    │            │  AI API │            │Diagnosis│
         │ Request │            │  Comm   │            │ Review  │
         └────┬────┘            └────┬────┘            └────┬────┘
              │                      │                      │
              ▼                      ▼                      ▼
       D2 + D4                 🤖 GROQ AI             ═══════════════
       (Pet + History)         (External)             │D5 AI DIAG   │
                                                      ═══════════════

INBOUND:  🩺 Veterinarian → AI Diagnostic Request
          D2 → Pet Info (species, breed, age)
          D4 → Medical History

OUTBOUND: → 🤖 GROQ AI: Formatted Request
          → 🩺 Veterinarian: AI Suggestions
          → D5: Stored AI Diagnosis
```

---

## 6.0 POINT OF SALE

```
                         ┌───────────────────────┐
                         │   6.0 POINT OF SALE   │
                         └───────────┬───────────┘
                                     │
        ┌────────────┬───────────────┼───────────────┬────────────┐
        ▼            ▼               ▼               ▼            │
   ┌─────────┐  ┌─────────┐    ┌─────────┐    ┌─────────┐        │
   │   6.1   │  │   6.2   │    │   6.3   │    │   6.4   │        │
   │  Sales  │  │ Payment │    │  Cash   │    │ Refund  │        │
   │  Trans  │  │Processing│   │ Drawer  │    │Processing│       │
   └────┬────┘  └────┬────┘    └────┬────┘    └────┬────┘        │
        │            │              │              │              │
        └────────────┴──────────────┴──────────────┘              │
                                │                                 │
                                ▼                                 │
                     ═══════════════════════                      │
                     │  D6 SALES & PAYMENTS │──► D7 (Stock)       │
                     ═══════════════════════                      │

INBOUND:  💼 Receptionist → Sales Items, Payment Info
          D7 → Product Prices, Stock Availability

OUTBOUND: → 👤 Pet Owner: Receipt
          → 👥 Walk-in Guest: Receipt
          → D7: Stock Deduction/Restoration
```

---

## 7.0 INVENTORY MANAGEMENT

```
                         ┌───────────────────────┐
                         │  7.0 INVENTORY MGMT   │
                         └───────────┬───────────┘
                                     │
        ┌────────────┬───────────────┼───────────────┬────────────┐
        ▼            ▼               ▼               ▼            │
   ┌─────────┐  ┌─────────┐    ┌─────────┐    ┌─────────┐        │
   │   7.1   │  │   7.2   │    │   7.3   │    │   7.4   │        │
   │ Product │  │  Stock  │    │  Stock  │    │ Reserv- │        │
   │  Mgmt   │  │ Adjust  │    │Transfer │    │  ation  │        │
   └────┬────┘  └────┬────┘    └────┬────┘    └────┬────┘        │
        │            │              │              │              │
        └────────────┴──────────────┴──────────────┘              │
                                │                                 │
                                ▼                                 │
                     ═══════════════════════                      │
                     │  D7 INVENTORY        │                     │
                     ═══════════════════════                      │

INBOUND:  💼 Receptionist → Product Data, Stock Adjustments
          🔐 Superadmin → Stock Transfer Request
          👤 Pet Owner → Reservation Request
          6.0 POS → Stock Deduction/Restoration

OUTBOUND: → 💼 Receptionist: Low Stock Alerts
          → 🔐 Superadmin: Transfer Notifications
          → 👤 Pet Owner: Reservation Confirmation
```

---

## 8.0 EMPLOYEE MANAGEMENT

```
                         ┌───────────────────────┐
                         │  8.0 EMPLOYEE MGMT    │
                         └───────────┬───────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              ▼                      ▼                      ▼
         ┌─────────┐            ┌─────────┐            ┌─────────┐
         │   8.1   │            │   8.2   │            │   8.3   │
         │  Staff  │            │Schedule │            │ License │
         │  Mgmt   │            │  Mgmt   │            │Tracking │
         └────┬────┘            └────┬────┘            └────┬────┘
              │                      │                      │
              └──────────────────────┼──────────────────────┘
                                     ▼
                              ═══════════════
                              │D8 EMPLOYEES │──► 3.1 (vet availability)
                              ═══════════════

INBOUND:  🔐 Superadmin → Staff Data, Schedule Data, License Info

OUTBOUND: → 🩺 Veterinarian: Work Schedule
          → 👩‍⚕️ Vet Assistant: Work Schedule
          → 3.1: Vet Availability
          → 🔐 Superadmin: License Expiry Alerts
```

---

## 10.0 REPORTS & ANALYTICS

```
                         ┌───────────────────────┐
                         │ 10.0 REPORTS          │
                         └───────────┬───────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              ▼                      ▼                      ▼
         ┌─────────┐            ┌─────────┐            ┌─────────┐
         │  10.1   │            │  10.2   │            │  10.3   │
         │Superadm │            │Inventory│            │Operatl. │
         │ Reports │            │ Reports │            │ Reports │
         └────┬────┘            └────┬────┘            └────┬────┘
              │                      │                      │
              ▼                      ▼                      ▼
           D1-D8                    D7                  D3, D4, D6
         (All Data)             (Inventory)           (Operations)

INBOUND:  🔐 Superadmin → Report Request (date range, filters)
          D1-D8 → All Data Stores

OUTBOUND: → 🔐 Superadmin: Dashboard, Metrics, Alerts
```

---

## Level 2 Summary Table

| Process | Sub-Processes | Data Stores | Key External Entities |
|---------|--------------|-------------|----------------------|
| **1.0** User & Access | 1.1 Registration, 1.2 Auth, 1.3 Role, 1.4 Permission | D1 | Pet Owner, Superadmin |
| **2.0** Patient | 2.1 Pet Reg, 2.2 Profile, 2.3 Owner | D2, D1, D3 | Pet Owner, Walk-in, Receptionist |
| **3.0** Appointment | 3.1 Booking, 3.2 Schedule, 3.3 Follow-up | D3, D8, D4 | Pet Owner, Walk-in, Receptionist, Vet |
| **4.0** Medical Records | 4.1 Create, 4.2 Consult, 4.3 Treat, 4.4 Sign⚠️ | D4, D2, D3 | Veterinarian, Vet Assistant |
| **5.0** AI Diagnostics | 5.1 Prep, 5.2 API, 5.3 Review | D5, D2, D4 | Veterinarian, 🤖 GROQ AI |
| **6.0** POS | 6.1 Sales, 6.2 Payment, 6.3 Drawer, 6.4 Refund | D6, D7 | Receptionist, Pet Owner, Walk-in |
| **7.0** Inventory | 7.1 Product, 7.2 Adjust, 7.3 Transfer, 7.4 Reserve | D7 | Receptionist, Superadmin, Pet Owner |
| **8.0** Employee | 8.1 Staff, 8.2 Schedule, 8.3 License | D8, D1 | Superadmin |
| **10.0** Reports | 10.1 Admin, 10.2 Inventory, 10.3 Operations | D1-D8 | Superadmin |

---

# 📊 COMPLETE DATA FLOW MATRIX

## Sub-Process → Data Store Mapping

| Process | Sub-Process | Input Data Stores | Output Data Stores |
|---------|-------------|-------------------|-------------------|
| **1.0** | 1.1 User Registration | - | D1 (Users) |
| | 1.2 Authentication | D1 (Users) | D1 (Session) |
| | 1.3 Role Management | D1 (Roles) | D1 (Roles) |
| | 1.4 Permission Control | D1 (Permissions) | - (Allow/Deny) |
| **2.0** | 2.1 Pet Registration | D1 (Owner) | D2 (Pets) |
| | 2.2 Pet Profile Mgmt | D2 (Pets) | D2 (Pets) |
| | 2.3 Owner Management | D1 (Users) | D1 (Users), D3 (sync) |
| **3.0** | 3.1 Appointment Booking | D2 (Pets), D8 (Vets) | D3 (Appointments) |
| | 3.2 Schedule Management | D3 (Appointments) | D3 (Appointments) |
| | 3.3 Follow-up Scheduling | D4 (Records) | D3 (Appointments), Notifications |
| **4.0** | 4.1 Record Creation | D2 (Pets), D3 (Appointments) | D4 (Records) |
| | 4.2 Consultation Entry | D2 (Pets) | D4 (Records) |
| | 4.3 Treatment Recording | D4 (Records) | D4 (Records), D7 (implicit) |
| | 4.4 Record Signing | D4 (Records) | D4 (Records) ⚠️ |
| **5.0** | 5.1 AI Request Prep | D2 (Pets), D4 (Records) | - (formatted request) |
| | 5.2 AI API Communication | - (request) | - (AI response) |
| | 5.3 Diagnosis Review | D5 (AI Diagnoses) | D5 (AI Diagnoses) |
| **6.0** | 6.1 Sales Transaction | D7 (Products) | D6 (Sales) |
| | 6.2 Payment Processing | D6 (Sales) | D6 (Payments) |
| | 6.3 Cash Drawer Mgmt | D6 (Drawer) | D6 (Drawer) |
| | 6.4 Refund Processing | D6 (Sales) | D6 (Refunds), D7 (Stock restore) |
| **7.0** | 7.1 Product Management | - | D7 (Products) |
| | 7.2 Stock Adjustment | D7 (Products) | D7 (Products) |
| | 7.3 Stock Transfer | D7 (Products) | D7 (Products - both branches) |
| | 7.4 Reservation Mgmt | D7 (Products) | D7 (Reservations) |
| **8.0** | 8.1 Staff Management | D1 (Users) | D8 (Staff) |
| | 8.2 Schedule Management | D8 (Staff) | D8 (Schedules) |
| | 8.3 License Tracking | D8 (Staff) | D8 (Licenses) |
| **10.0** | 10.1 Superadmin Reports | D1-D8 (All) | - (Reports) |
| | 10.2 Inventory Reports | D7 (Inventory) | - (Reports) |
| | 10.3 Operational Reports | D3, D4, D6 | - (Reports) |

---

# 🔄 END-TO-END WORKFLOW FLOWS

## Flow 1: Pet Owner Registration & First Appointment

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  WORKFLOW: PET OWNER REGISTRATION → APPOINTMENT BOOKING → CONSULTATION          │
└──────────────────────────────────────────────────────────────────────────────────┘

👤 Pet Owner
     │
     │ (1) Registration form data
     ▼
┌─────────────────┐
│ 1.1 User        │ ──────► D1 (User Account Created)
│   Registration  │
└─────────────────┘
     │
     │ (2) Login credentials
     ▼
┌─────────────────┐
│ 1.2 Authenti-   │ ◄────── D1 (Validate credentials)
│   cation        │ ──────► Session created
└─────────────────┘
     │
     │ (3) Pet information
     ▼
┌─────────────────┐
│ 2.1 Pet         │ ──────► D2 (Pet Profile Created)
│   Registration  │
└─────────────────┘
     │
     │ (4) Appointment request
     ▼
┌─────────────────┐
│ 3.1 Appointment │ ◄────── D8 (Check vet availability)
│   Booking       │ ──────► D3 (Appointment Created)
└─────────────────┘         │
     │                      ▼
     │                 📧 Confirmation Email
     │
     │ (5) Visit clinic - check-in
     ▼
┌─────────────────┐
│ 4.1 Record      │ ◄────── D3 (Get Appointment)
│   Creation      │ ──────► D4 (Medical Record Created)
└─────────────────┘
     │
     │ (6) Consultation
     ▼
┌─────────────────┐
│ 4.2 Consultation│ ──────► D4 (Vitals, Clinical Signs)
│   Entry         │
└─────────────────┘
     │
     │ (7) Request AI assistance
     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ 5.1 AI Request  │──│ 5.2 AI API      │──│ 5.3 Diagnosis   │
│   Preparation   │  │ Communication   │  │   Review        │
└─────────────────┘  └─────────────────┘  └─────────────────┘
     │                      │                      │
     ▼                      ▼                      ▼
  D2 + D4              🤖 GROQ AI             D5 (Save Diagnosis)
  (History)            (API Call)
     │
     │ (8) Treatment
     ▼
┌─────────────────┐
│ 4.3 Treatment   │ ──────► D4 (Treatment, Rx)
│   Recording     │
└─────────────────┘
     │
     │ (9) Payment
     ▼
┌─────────────────┐  ┌─────────────────┐
│ 6.1 Sales       │──│ 6.2 Payment     │──────► D6 (Sale + Payment)
│   Transaction   │  │   Processing    │
└─────────────────┘  └─────────────────┘
     │                                           │
     │                                           ▼
     │                                      D7 (Stock Deduction)
     │
     │ (10) Follow-up
     ▼
┌─────────────────┐
│ 3.3 Follow-up   │ ──────► D3 (Follow-up Created)
│   Scheduling    │ ──────► 📧 Notification
└─────────────────┘
```

## Flow 2: Walk-in Guest Flow

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  WORKFLOW: WALK-IN GUEST → APPOINTMENT → TREATMENT → PAYMENT                     │
└──────────────────────────────────────────────────────────────────────────────────┘

👥 Walk-in Guest
     │
     │ (1) Walk-in request (no account)
     ▼
┌─────────────────┐
│ 3.1 Appointment │ ──────► D3 (Walk-in Appointment)
│   Booking       │         │ guest_name, guest_phone stored
└─────────────────┘         │ source='WALKIN'
     │                      │
     │                      ▼
     │              D2 (Pet Created with guest_owner_* fields)
     │
     │ (2) Consultation
     ▼
┌─────────────────┐  ┌─────────────────┐
│ 4.1 Record      │──│ 4.2 Consultation│──────► D4 (Medical Record)
│   Creation      │  │   Entry         │
└─────────────────┘  └─────────────────┘
     │
     │ (3) Treatment & Payment
     ▼
┌─────────────────┐  ┌─────────────────┐
│ 6.1 Sales       │──│ 6.2 Payment     │──────► D6 (Sale)
│   Transaction   │  │   Processing    │        customer_type='WALKIN'
└─────────────────┘  └─────────────────┘
     │
     ▼
🧾 Receipt Printed
```

## Flow 3: Inventory & Stock Transfer

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  WORKFLOW: STOCK TRANSFER BETWEEN BRANCHES                                        │
└──────────────────────────────────────────────────────────────────────────────────┘

💼 Receptionist / 🔐 Superadmin (Branch A)
     │
     │ (1) Initiate transfer request
     ▼
┌─────────────────┐
│ 7.3 Stock       │ ──────► D7 (Transfer Record: PENDING)
│   Transfer      │         │ source_branch: A
└─────────────────┘         │ dest_branch: B
     │                      │ quantity: X
     │                      │
     ▼                      ▼
📧 Notification ───────► 🔐 Superadmin (Approval)
                              │
                              │ (2) Approve transfer
                              ▼
                        ┌─────────────────┐
                        │ 7.3 Stock       │ ──────► D7 (Transfer: APPROVED)
                        │   Transfer      │
                        └─────────────────┘
                              │
                              │ (3) Complete transfer
                              ▼
                        ┌─────────────────┐
                        │ 7.2 Stock       │ ──────► D7 (Branch A: -X stock)
                        │   Adjustment    │ ──────► D7 (Branch B: +X stock)
                        └─────────────────┘         │
                              │                     │ StockAdjustment records:
                              ▼                     │ - TRF-OUT (Branch A)
                        D7 (Transfer: COMPLETED)    │ - TRF-IN (Branch B)
                                                    ▼
                                              📋 ActivityLog Entry
```

## Flow 4: POS with Refund

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  WORKFLOW: SALE → PAYMENT → REFUND                                                │
└──────────────────────────────────────────────────────────────────────────────────┘

💼 Receptionist
     │
     │ (1) Open cash drawer
     ▼
┌─────────────────┐
│ 6.3 Cash Drawer │ ──────► D6 (CashDrawer: OPEN)
│   Management    │         │ opening_amount: $XXX
└─────────────────┘         │ opened_by: Receptionist
     │
     │ (2) Create sale
     ▼
┌─────────────────┐
│ 6.1 Sales       │ ◄────── D7 (Product prices, availability)
│   Transaction   │ ──────► D6 (Sale: PENDING)
└─────────────────┘         │ SaleItems added
     │
     │ (3) Process payment
     ▼
┌─────────────────┐
│ 6.2 Payment     │ ──────► D6 (Payment record)
│   Processing    │ ──────► D6 (Sale: COMPLETED)
└─────────────────┘ ──────► D7 (Stock deducted via signal)
     │
     │ 🧾 Receipt generated
     │
     │ (4) Customer returns - refund needed
     ▼
┌─────────────────┐
│ 6.4 Refund      │ ──────► D6 (Refund record)
│   Processing    │ ──────► D6 (Sale: REFUNDED)
└─────────────────┘ ──────► D7 (Stock restored)
     │
     │ (5) End of day - close drawer
     ▼
┌─────────────────┐
│ 6.3 Cash Drawer │ ──────► D6 (CashDrawer: CLOSED)
│   Management    │         │ actual_cash: $XXX
└─────────────────┘         │ variance calculated
                            │ closed_by: Receptionist
```

---

# 📈 PROCESS INTEGRATION DIAGRAM

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         HOW PROCESSES CONNECT                                        │
└─────────────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────┐
                              │ 1.0 USER &      │
                              │ ACCESS MGMT     │
                              └────────┬────────┘
                                       │ Authentication
                                       │ & Authorization
         ┌───────────────────┬─────────┴─────────┬───────────────────┐
         │                   │                   │                   │
         ▼                   ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ 2.0 PATIENT     │ │ 3.0 APPOINTMENT │ │ 6.0 POINT OF    │ │ 8.0 EMPLOYEE    │
│    MGMT         │ │    MGMT         │ │    SALE         │ │    MGMT         │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │                   │
         │ Pet Data          │ Schedules         │                   │ Staff Schedules
         │                   │                   │                   │
         └─────────┬─────────┘                   │                   │
                   │                             │                   │
                   ▼                             │                   │
         ┌─────────────────┐                     │                   │
         │ 4.0 MEDICAL     │                     │                   │
         │    RECORDS      │                     │                   │
         └────────┬────────┘                     │                   │
                  │                              │                   │
                  │ Symptoms                     │                   │
                  ▼                              │                   │
         ┌─────────────────┐                     │                   │
         │ 5.0 AI          │                     │                   │
         │    DIAGNOSTICS  │                     │                   │
         └────────┬────────┘                     │                   │
                  │                              │                   │
                  │ Treatment Data               │                   │
                  └──────────────────────────────┤                   │
                                                 │                   │
                                                 ▼                   │
                                        ┌─────────────────┐          │
                                        │ 7.0 INVENTORY   │          │
                                        │    MGMT         │          │
                                        └────────┬────────┘          │
                                                 │                   │
                                                 │                   │
                  ┌──────────────────────────────┴───────────────────┘
                  │
                  ▼
         ╔═════════════════════╗
         ║ 10.0 REPORTS &      ║
         ║    ANALYTICS        ║
         ║                     ║
         ║ Aggregates from:    ║
         ║ D1, D2, D3, D4,     ║
         ║ D5, D6, D7, D8      ║
         ╚═════════════════════╝
```

---

# ✅ VERIFICATION SUMMARY

## Implementation Status by Level

| Level | Total Items | Implemented | Match % | Status |
|-------|-------------|-------------|---------|--------|
| **Level 0** | 7 entities + 8 stores | 7 + 8 | 100% | ✅ COMPLETE |
| **Level 1** | 9 processes | 9 | 100% | ✅ COMPLETE |
| **Level 2** | 31 sub-processes | 30 | 96.77% | ✅ SUBSTANTIAL |

## Sub-Process Implementation Detail

| Process | Sub-Processes | Implemented | Status |
|---------|---------------|-------------|--------|
| 1.0 User & Access | 4 | 4 | ✅ 100% |
| 2.0 Patient Mgmt | 3 | 3 | ✅ 100% |
| 3.0 Appointments | 3 | 3 | ✅ 100% |
| 4.0 Medical Records | 4 | 3 | ⚠️ 75% |
| 5.0 AI Diagnostics | 3 | 3 | ✅ 100% |
| 6.0 Point of Sale | 4 | 4 | ✅ 100% |
| 7.0 Inventory | 4 | 4 | ✅ 100% |
| 8.0 Employee Mgmt | 3 | 3 | ✅ 100% |
| 10.0 Reports | 3 | 3 | ✅ 100% |
| **TOTAL** | **31** | **30** | **96.77%** |

## Identified Gap

| Sub-Process | Status | Description |
|-------------|--------|-------------|
| **4.4 Record Signing** | ⚠️ MISSING | Medical record finalization and vet signature not implemented |

---

# 🔑 KEY DATA SYNCHRONIZATION MECHANISMS

The system maintains data consistency through:

1. **Django Signals**
   - `post_save(User)` → Sync to appointments
   - `post_save(Pet)` → Sync denormalized fields to appointments
   - `post_save(RecordEntry)` → Update pet clinical status
   - `post_save(StockAdjustment)` → Log to ActivityLog

2. **Atomic Transactions**
   - `Sale.complete_sale()` → Atomic POS + Inventory update
   - `StockTransfer.complete_transfer()` → Atomic dual-branch update
   - `StockAdjustment.save()` → F() expressions for race prevention

3. **Foreign Key Constraints**
   - Referential integrity between all models
   - Cascade deletes where appropriate
   - Soft delete pattern for critical data

---

# 📝 NOTES

1. **Process 9.0** is skipped in numbering (reserved for future use)
2. **Walk-in guests** don't require user accounts (guest_owner_* fields)
3. **Multi-branch support** is built into every process
4. **RBAC** controls access at every process level
5. **ActivityLog** provides audit trail for compliance

---

*Document generated: 2026-03-30*
*System: FMH Animal Clinic Management System - Django 6.0.2*
*DFD Verification Status: 96.77% Match with Implementation*
