# DFD Level 2 - FMH Animal Clinic System

## Gemini Image Generation Prompt

```
Generate a professional DFD Level 2 diagram image for the FMH Animal Clinic Management System. This diagram expands each Level 1 process into detailed sub-processes.

**EXTERNAL ENTITIES (Draw as rectangles on the edges):**

1. **Pet Owner** - Left side
2. **Walk-in Guest** - Left side
3. **Veterinarian** - Top
4. **Vet Assistant** - Top right
5. **Receptionist** - Right side
6. **Superadmin** - Bottom right
7. **GROQ AI Service** - Bottom left (draw as a cloud)

**DATA STORES (Draw as open-ended rectangles):**

D1 **Users** - User accounts, roles, permissions
D2 **Pets** - Pet profiles, owner info, medical history
D3 **Appointments** - Bookings, schedules, follow-ups
D4 **Medical Records** - Consultations, treatments, prescriptions
D5 **AI Diagnoses** - AI diagnostic results, recommendations
D6 **Sales & Payments** - Transactions, payments, refunds, cash drawer
D7 **Products & Inventory** - Products, stock levels, adjustments
D8 **Employees** - Staff profiles, schedules, licenses

---

**PROCESS 1.0 - USER & ACCESS MANAGEMENT (Sub-processes):**

1.1 **User Registration**
    - Input: Registration form data (username, email, password, phone)
    - Output: User account created, confirmation message

1.2 **Authentication**
    - Input: Login credentials (username, password)
    - Output: Session token, dashboard redirect

1.3 **Role Management**
    - Input: Role definition (name, code, hierarchy, permissions)
    - Output: Role record, permission mappings

1.4 **Permission Control**
    - Input: User request, required permission
    - Output: Access granted/denied

Data Flows:
- Pet Owner → 1.1: Registration Data
- 1.1 → Pet Owner: Account Confirmation
- All Users → 1.2: Login Credentials
- 1.2 → All Users: Authentication Response
- Superadmin → 1.3: Role Definitions
- 1.1, 1.2, 1.3, 1.4 ↔ D1: User Data

---

**PROCESS 2.0 - PATIENT MANAGEMENT (Sub-processes):**

2.1 **Pet Registration**
    - Input: Pet data (name, species, breed, DOB, sex, photo)
    - Output: Pet profile created

2.2 **Pet Profile Management**
    - Input: Updated pet info, pet ID
    - Output: Updated pet profile

2.3 **Owner Management**
    - Input: Owner contact info, preferences
    - Output: Updated owner data

Data Flows:
- Pet Owner → 2.1: Pet Information
- Walk-in Guest → 2.1: Guest Pet Info
- Pet Owner → 2.2: Profile Updates
- Receptionist → 2.3: Customer Information
- 2.1, 2.2, 2.3 ↔ D2: Pet Data

---

**PROCESS 3.0 - APPOINTMENT MANAGEMENT (Sub-processes):**

3.1 **Appointment Booking**
    - Input: Booking request (date, time, branch, vet, reason)
    - Output: Appointment record, confirmation

3.2 **Schedule Management**
    - Input: Status updates (confirm, cancel, complete)
    - Output: Updated appointment

3.3 **Follow-up Scheduling**
    - Input: Follow-up dates, reason
    - Output: Follow-up record

Data Flows:
- Pet Owner → 3.1: Appointment Request
- Walk-in Guest → 3.1: Walk-in Request
- 3.1 → Pet Owner: Confirmation
- Receptionist → 3.2: Appointment Updates
- 3.2 → Veterinarian: Daily Schedule
- 3.2 → Receptionist: Daily Schedule
- Veterinarian → 3.3: Follow-up Request
- D8 → 3.1: Vet Availability
- 3.1, 3.2, 3.3 ↔ D3: Appointment Data

---

**PROCESS 4.0 - MEDICAL RECORDS MANAGEMENT (Sub-processes):**

4.1 **Record Creation**
    - Input: Pet ID, Vet ID, Branch ID
    - Output: New medical record

4.2 **Consultation Entry**
    - Input: Vital signs, clinical signs, symptoms
    - Output: Consultation record

4.3 **Treatment Recording**
    - Input: Treatment (Tx), Prescription (Rx)
    - Output: Treatment record

4.4 **Record Signing**
    - Input: Vet signature, approval
    - Output: Signed/finalized record

Data Flows:
- D3 → 4.1: Appointment Info
- Veterinarian → 4.2: Consultation Data
- D2 → 4.2: Patient History
- Veterinarian → 4.3: Treatment & Rx Data
- Vet Assistant → 4.2: Patient Prep Data
- Veterinarian → 4.4: Signature
- D4 → Pet Owner: Medical Records Access
- 4.2 → 5.0: Patient Symptoms
- 4.1, 4.2, 4.3, 4.4 ↔ D4: Medical Record Data

---

**PROCESS 5.0 - AI DIAGNOSTICS (Sub-processes):**

5.1 **AI Request Preparation**
    - Input: Symptoms, medical history, pet info
    - Output: Formatted AI request

5.2 **AI API Communication**
    - Input: Formatted request
    - Output: AI response (diagnoses, recommendations)

5.3 **Diagnosis Review**
    - Input: AI diagnosis ID, review notes
    - Output: Reviewed/approved diagnosis

Data Flows:
- Veterinarian → 5.1: AI Diagnostic Request
- D4 → 5.1: Patient Symptoms
- D2 → 5.1: Pet Medical History
- 5.2 ↔ GROQ AI: Symptoms & Recommendations
- Veterinarian → 5.3: Review Notes
- 5.3 → Veterinarian: AI Suggestions
- 5.3 → 4.3: AI Recommendations
- 5.1, 5.2, 5.3 ↔ D5: AI Diagnosis Data

---

**PROCESS 6.0 - POINT OF SALE (Sub-processes):**

6.1 **Sales Transaction**
    - Input: Customer info, sale items, discounts
    - Output: Sale record with totals

6.2 **Payment Processing**
    - Input: Sale ID, payment method(s), amounts
    - Output: Payment record, receipt

6.3 **Cash Drawer Management**
    - Input: Opening amount, closing count
    - Output: Cash drawer session, variance

6.4 **Refund Processing**
    - Input: Sale ID, refund type, reason
    - Output: Refund record

Data Flows:
- Receptionist → 6.1: Sales Items
- D7 → 6.1: Product Prices
- Receptionist → 6.2: Payment Info
- 6.2 → Walk-in Guest: Receipt
- 6.2 → Pet Owner: Receipt
- 6.2 → Receptionist: Receipt
- Receptionist → 6.3: Drawer Operations
- Receptionist → 6.4: Refund Request
- 6.4 → 7.2: Stock Restoration
- 6.1, 6.2, 6.3, 6.4 ↔ D6: Transaction Data

---

**PROCESS 7.0 - INVENTORY MANAGEMENT (Sub-processes):**

7.1 **Product Management**
    - Input: Product data (name, type, price, cost)
    - Output: Product record with SKU

7.2 **Stock Adjustment**
    - Input: Product ID, adjustment type, quantity
    - Output: Updated stock quantity

7.3 **Stock Transfer**
    - Input: Source product, destination branch, quantity
    - Output: Transfer record

7.4 **Reservation Management**
    - Input: User ID, product ID, quantity, pickup date
    - Output: Reservation record

Data Flows:
- 6.2 → 7.2: Stock Deduction
- 7.2 → Receptionist: Low Stock Alert
- Pet Owner → 7.4: Reservation Request
- D7 → Receptionist: Inventory Status
- D7 → Veterinarian: Product/Medicine Info
- 7.1, 7.2, 7.3, 7.4 ↔ D7: Inventory Data

---

**PROCESS 8.0 - EMPLOYEE MANAGEMENT (Sub-processes):**

8.1 **Staff Management**
    - Input: Staff data (name, position, salary, license)
    - Output: Staff member record

8.2 **Schedule Management**
    - Input: Staff ID, schedule data (dates, times, shifts)
    - Output: Schedule records

8.3 **License Tracking**
    - Input: License info, expiration dates
    - Output: License records, expiry alerts

Data Flows:
- D8 → Veterinarian: Work Schedule
- D8 → Vet Assistant: Work Schedule
- D8 → 3.1: Vet Availability
- 8.1, 8.2, 8.3 ↔ D8: Employee Data

---

**PROCESS 10.0 - REPORTS & ANALYTICS (Sub-processes):**

10.1 **Sales Reports**
    - Input: Date range, branch filter
    - Output: Sales summary, charts

10.2 **Inventory Reports**
    - Input: Branch filter, stock status
    - Output: Inventory report

10.3 **Operational Reports**
    - Input: Report parameters
    - Output: Appointment, medical reports

Data Flows:
- D6 → 10.1: Transaction Data
- D7 → 10.2: Inventory Data
- D3, D4, D8 → 10.3: Operational Data
- 10.1, 10.2, 10.3 → Superadmin: Reports

---

**VISUAL LAYOUT:**

TOP ROW (Clinical):
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ 2.0 Patient Mgmt│  │3.0 Appointment  │  │4.0 Medical Rec  │  │5.0 AI Diagnostics│
│ [2.1][2.2][2.3] │  │ [3.1][3.2][3.3] │  │[4.1][4.2][4.3][4.4]│ │ [5.1][5.2][5.3] │
└─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘

MIDDLE ROW (Business):
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ 6.0 Point of Sale│  │7.0 Inventory Mgmt│  │8.0 Employee Mgmt│
│[6.1][6.2][6.3][6.4]│ │[7.1][7.2][7.3][7.4]│ │ [8.1][8.2][8.3] │
└─────────────────┘  └─────────────────┘  └─────────────────┘

BOTTOM ROW (Support):
┌─────────────────┐  ┌─────────────────┐
│1.0 User & Access│  │10.0 Reports     │
│[1.1][1.2][1.3][1.4]│ │[10.1][10.2][10.3]│
└─────────────────┘  └─────────────────┘

**COLOR SCHEME:**
- External entities: Light blue (#E1F5FE) with dark blue border (#01579B)
- External services (AI): Light purple (#F3E5F5) with purple border (#7B1FA2)
- Parent processes: Light orange (#FFF3E0) with dark orange border (#E65100)
- Sub-processes: Lighter orange (#FFF8E1) with orange border (#FF9800)
- Data stores: Light green (#E8F5E9) with dark green border (#2E7D32)
- Data flow arrows: Dark gray (#424242)

**SIZE & RESOLUTION:**
- Very high resolution (at least 3840x2160 pixels)
- Landscape orientation
- Clear, readable sans-serif font
- Labeled data flow arrows
```

---

## DFD Level 2 Summary

| Parent Process | Sub-Processes |
|----------------|---------------|
| 1.0 User & Access | 1.1 Registration, 1.2 Auth, 1.3 Roles, 1.4 Permissions |
| 2.0 Patient Mgmt | 2.1 Pet Registration, 2.2 Profile Mgmt, 2.3 Owner Mgmt |
| 3.0 Appointment | 3.1 Booking, 3.2 Schedule Mgmt, 3.3 Follow-up |
| 4.0 Medical Records | 4.1 Creation, 4.2 Consultation, 4.3 Treatment, 4.4 Signing |
| 5.0 AI Diagnostics | 5.1 Request Prep, 5.2 API Comm, 5.3 Review |
| 6.0 Point of Sale | 6.1 Sales, 6.2 Payment, 6.3 Cash Drawer, 6.4 Refund |
| 7.0 Inventory | 7.1 Products, 7.2 Stock Adj, 7.3 Transfer, 7.4 Reservation |
| 8.0 Employee Mgmt | 8.1 Staff, 8.2 Schedule, 8.3 License |
| 10.0 Reports | 10.1 Sales, 10.2 Inventory, 10.3 Operational |
