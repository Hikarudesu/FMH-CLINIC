# HIPO Charts (Hierarchy plus Input-Process-Output)
## FMH Animal Clinic System

---

## Overview

HIPO (Hierarchy plus Input-Process-Output) charts document the system's modular structure and the data transformations within each module.

---

## 1. System Hierarchy Chart

```mermaid
flowchart TB
    ROOT["FMH Animal Clinic<br/>Management System"]
    
    ROOT --> M1["1.0 User &<br/>Access Management"]
    ROOT --> M2["2.0 Patient<br/>Management"]
    ROOT --> M3["3.0 Appointment<br/>Management"]
    ROOT --> M4["4.0 Medical Records<br/>Management"]
    ROOT --> M5["5.0 AI Diagnostics"]
    ROOT --> M6["6.0 Point of Sale"]
    ROOT --> M7["7.0 Inventory<br/>Management"]
    ROOT --> M8["8.0 Employee<br/>Management"]
    ROOT --> M9["9.0 Payroll<br/>Management"]
    ROOT --> M10["10.0 Notifications"]
    ROOT --> M11["11.0 Reports &<br/>Analytics"]
    ROOT --> M12["12.0 System<br/>Administration"]
    
    M1 --> M1_1["1.1 User Registration"]
    M1 --> M1_2["1.2 Authentication"]
    M1 --> M1_3["1.3 Role Management"]
    M1 --> M1_4["1.4 Permission Control"]
    
    M2 --> M2_1["2.1 Pet Registration"]
    M2 --> M2_2["2.2 Pet Profile Mgmt"]
    M2 --> M2_3["2.3 Owner Management"]
    
    M3 --> M3_1["3.1 Appointment Booking"]
    M3 --> M3_2["3.2 Schedule Management"]
    M3 --> M3_3["3.3 Follow-up Scheduling"]
    
    M4 --> M4_1["4.1 Record Creation"]
    M4 --> M4_2["4.2 Consultation Entry"]
    M4 --> M4_3["4.3 Treatment Recording"]
    
    M5 --> M5_1["5.1 AI Request"]
    M5 --> M5_2["5.2 Diagnosis Review"]
    
    M6 --> M6_1["6.1 Sales Transaction"]
    M6 --> M6_2["6.2 Payment Processing"]
    M6 --> M6_3["6.3 Cash Drawer Mgmt"]
    M6 --> M6_4["6.4 Refund Processing"]
    
    M7 --> M7_1["7.1 Product Management"]
    M7 --> M7_2["7.2 Stock Adjustment"]
    M7 --> M7_3["7.3 Stock Transfer"]
    M7 --> M7_4["7.4 Reservation Mgmt"]
    
    M8 --> M8_1["8.1 Staff Management"]
    M8 --> M8_2["8.2 Schedule Management"]
    M8 --> M8_3["8.3 License Tracking"]
    
    M9 --> M9_1["9.1 Payroll Generation"]
    M9 --> M9_2["9.2 Payslip Management"]
    M9 --> M9_3["9.3 Payroll Release"]
    
    M10 --> M10_1["10.1 Notification Generation"]
    M10 --> M10_2["10.2 Email Delivery"]
    
    M11 --> M11_1["11.1 Sales Reports"]
    M11 --> M11_2["11.2 Inventory Reports"]
    M11 --> M11_3["11.3 Payroll Reports"]
    
    M12 --> M12_1["12.1 Branch Management"]
    M12 --> M12_2["12.2 System Settings"]
    M12 --> M12_3["12.3 Content Management"]
    M12 --> M12_4["12.4 Clinical Status Mgmt"]
    M12 --> M12_5["12.5 Reason for Visit Mgmt"]
```

---

## 2. IPO Charts by Module

### 2.1 User & Access Management (Module 1.0)

#### 1.1 User Registration

| Input | Process | Output |
|-------|---------|--------|
| Registration form data (username, email, password, phone, address) | 1. Validate form data<br/>2. Check username/email uniqueness<br/>3. Hash password<br/>4. Create User record<br/>5. Assign default role<br/>6. Log activity | User account created<br/>Confirmation message<br/>Activity log entry |

#### 1.2 Authentication

| Input | Process | Output |
|-------|---------|--------|
| Login credentials (username, password) | 1. Validate credentials<br/>2. Check user active status<br/>3. Verify password hash<br/>4. Create session<br/>5. Log login activity | Session token<br/>User dashboard redirect<br/>Login activity log |

#### 1.3 Role Management

| Input | Process | Output |
|-------|---------|--------|
| Role definition (name, code, hierarchy, permissions) | 1. Validate role data<br/>2. Create/Update Role record<br/>3. Set module permissions<br/>4. Set special permissions<br/>5. Log changes | Role record<br/>Permission mappings<br/>Audit log |

#### 1.4 Permission Control

| Input | Process | Output |
|-------|---------|--------|
| User request, Required permission | 1. Get user's role<br/>2. Check hierarchy level<br/>3. Query module permissions<br/>4. Evaluate branch restrictions<br/>5. Return access decision | Access granted/denied<br/>Filtered data (if branch-restricted) |

---

### 2.2 Patient Management (Module 2.0)

#### 2.1 Pet Registration

| Input | Process | Output |
|-------|---------|--------|
| Pet data (name, species, breed, DOB, sex, photo)<br/>Owner info (if walk-in) | 1. Validate pet data<br/>2. Upload photo (if provided)<br/>3. Create Pet record<br/>4. Link to owner (or set guest info)<br/>5. Set initial status to HEALTHY<br/>6. Log activity | Pet profile created<br/>Confirmation to owner<br/>Activity log |

#### 2.2 Pet Profile Management

| Input | Process | Output |
|-------|---------|--------|
| Updated pet info<br/>Pet ID | 1. Retrieve Pet record<br/>2. Validate updates<br/>3. Update Pet fields<br/>4. Sync to appointments (signal)<br/>5. Log changes | Updated Pet profile<br/>Synced appointment data<br/>Activity log |

---

### 2.3 Appointment Management (Module 3.0)

#### 3.1 Appointment Booking

| Input | Process | Output |
|-------|---------|--------|
| Booking request (date, time, branch, vet preference, reason)<br/>Pet/Owner info | 1. Validate date/time availability<br/>2. Check vet schedule<br/>3. Create Appointment record<br/>4. Denormalize pet/owner data<br/>5. Set status = PENDING<br/>6. Generate notification | Appointment record<br/>Confirmation message<br/>Notification to staff |

#### 3.2 Schedule Management

| Input | Process | Output |
|-------|---------|--------|
| Status update (CONFIRM, CANCEL, COMPLETE)<br/>Appointment ID | 1. Retrieve Appointment<br/>2. Validate status transition<br/>3. Update status<br/>4. Link to Sale (if COMPLETE)<br/>5. Generate notification | Updated appointment<br/>Notification to owner<br/>POS linkage (if completed) |

#### 3.3 Follow-up Scheduling

| Input | Process | Output |
|-------|---------|--------|
| Follow-up date(s)<br/>Reason<br/>Appointment ID | 1. Validate dates<br/>2. Create FollowUp record<br/>3. Link to appointment<br/>4. Generate notification | FollowUp record<br/>Owner notification<br/>Staff reminder |

---

### 2.4 Medical Records Management (Module 4.0)

#### 4.1 Record Creation

| Input | Process | Output |
|-------|---------|--------|
| Pet ID<br/>Vet ID<br/>Branch ID | 1. Retrieve Pet<br/>2. Check for existing active record<br/>3. Create MedicalRecord<br/>4. Set date_recorded | MedicalRecord created<br/>Ready for entries |

#### 4.2 Consultation Entry

| Input | Process | Output |
|-------|---------|--------|
| Vital signs (weight, temperature)<br/>Clinical signs<br/>Treatment (Tx)<br/>Prescription (Rx)<br/>Follow-up date<br/>Action required | 1. Validate entry data<br/>2. Create RecordEntry<br/>3. Link to MedicalRecord<br/>4. Update Pet.status (via signal)<br/>5. Notify owner (if status changed) | RecordEntry created<br/>Pet status updated<br/>Owner notification |

---

### 2.5 AI Diagnostics (Module 5.0)

#### 5.1 AI Request

| Input | Process | Output |
|-------|---------|--------|
| Symptoms<br/>Medical history<br/>Pet ID<br/>Requesting Vet ID | 1. Compile input data<br/>2. Send to AI API<br/>3. Parse AI response<br/>4. Create AIDiagnosis record<br/>5. Store differential diagnoses | AIDiagnosis record<br/>Primary diagnosis<br/>Recommended tests<br/>Warning signs |

#### 5.2 Diagnosis Review

| Input | Process | Output |
|-------|---------|--------|
| AIDiagnosis ID<br/>Review notes<br/>Reviewing Vet ID | 1. Retrieve AIDiagnosis<br/>2. Update review fields<br/>3. Set is_reviewed = True<br/>4. Record reviewed_at timestamp | Reviewed AIDiagnosis<br/>Audit trail |

---

### 2.6 Point of Sale (Module 6.0)

#### 6.1 Sales Transaction

| Input | Process | Output |
|-------|---------|--------|
| Customer info (registered or walk-in)<br/>Sale items (services, products)<br/>Discounts | 1. Create Sale record<br/>2. Add SaleItem records<br/>3. Calculate subtotal<br/>4. Apply discounts<br/>5. Calculate tax<br/>6. Compute total | Sale record<br/>Line items<br/>Calculated totals |

#### 6.2 Payment Processing

| Input | Process | Output |
|-------|---------|--------|
| Sale ID<br/>Payment method(s)<br/>Amount(s)<br/>Reference number(s) | 1. Validate payment amounts<br/>2. Create Payment record(s)<br/>3. Update Sale.amount_paid<br/>4. Calculate change_due<br/>5. Complete sale (if fully paid)<br/>6. Deduct inventory (via StockAdjustment) | Payment record(s)<br/>Updated Sale<br/>Inventory deducted<br/>Receipt data |

#### 6.3 Cash Drawer Management

| Input | Process | Output |
|-------|---------|--------|
| Opening amount<br/>Branch ID<br/>User ID | **Open:**<br/>1. Create CashDrawer<br/>2. Set status = OPEN<br/>3. Record opening_amount<br/><br/>**Close:**<br/>1. Count actual cash<br/>2. Calculate variance<br/>3. Set status = CLOSED | CashDrawer session<br/>Variance report<br/>Shift summary |

#### 6.4 Refund Processing

| Input | Process | Output |
|-------|---------|--------|
| Sale ID<br/>Refund type (FULL/PARTIAL)<br/>Refund items (if partial)<br/>Reason | 1. Create Refund record<br/>2. Create RefundItem records<br/>3. Request approval<br/>4. Process refund (restore inventory)<br/>5. Update Sale status | Refund record<br/>Restored inventory<br/>Updated Sale status |

---

### 2.7 Inventory Management (Module 7.0)

#### 7.1 Product Management

| Input | Process | Output |
|-------|---------|--------|
| Product data (name, type, price, cost, etc.)<br/>Branch ID | 1. Validate product data<br/>2. Auto-generate SKU<br/>3. Create/Update Product<br/>4. Set initial stock = 0 | Product record<br/>Unique SKU |

#### 7.2 Stock Adjustment

| Input | Process | Output |
|-------|---------|--------|
| Product ID<br/>Adjustment type<br/>Quantity<br/>Reference<br/>Reason | 1. Validate adjustment<br/>2. Create StockAdjustment<br/>3. Update Product.stock_quantity (atomic F())<br/>4. Check low stock threshold<br/>5. Generate alert (if low) | StockAdjustment record<br/>Updated stock level<br/>Low stock notification |

#### 7.3 Stock Transfer

| Input | Process | Output |
|-------|---------|--------|
| Source product ID<br/>Destination branch ID<br/>Quantity<br/>Requested by | 1. Validate quantity<br/>2. Create StockTransfer (PENDING)<br/>3. Await approval<br/>4. Complete transfer (creates StockAdjustments)<br/>5. Create/link destination Product | StockTransfer record<br/>Source stock reduced<br/>Destination stock increased |

#### 7.4 Reservation Management

| Input | Process | Output |
|-------|---------|--------|
| User ID<br/>Product ID<br/>Quantity<br/>Pickup date | 1. Check product availability<br/>2. Create Reservation (PENDING)<br/>3. Reserve stock (StockAdjustment)<br/>4. Notify staff<br/><br/>**Release:**<br/>1. Update status = RELEASED<br/>2. Notify customer | Reservation record<br/>Reserved stock<br/>Staff notification<br/>Customer notification |

---

### 2.8 Employee Management (Module 8.0)

#### 8.1 Staff Management

| Input | Process | Output |
|-------|---------|--------|
| Staff data (name, position, salary, license)<br/>Branch ID<br/>User account (optional) | 1. Validate staff data<br/>2. Create/Update StaffMember<br/>3. Link to User account (if provided)<br/>4. Set is_active | StaffMember record<br/>User link (if applicable) |

#### 8.2 Schedule Management

| Input | Process | Output |
|-------|---------|--------|
| Staff ID<br/>Schedule data (date, times, shift type)<br/>OR Recurring template | **Individual:**<br/>1. Create VetSchedule<br/><br/>**Recurring:**<br/>1. Create RecurringSchedule<br/>2. Auto-generate VetSchedule entries (30-day lookahead) | VetSchedule record(s)<br/>Staff availability |

---

### 2.9 Payroll Management (Module 9.0)

#### 9.1 Payroll Generation

| Input | Process | Output |
|-------|---------|--------|
| Month<br/>Year | 1. Create PayrollPeriod (DRAFT)<br/>2. Get all active employees<br/>3. Generate Payslip for each<br/>4. Auto-populate base salary, allowances<br/>5. Calculate statutory contributions<br/>6. Update period totals | PayrollPeriod (GENERATED)<br/>Payslips for all staff<br/>Audit log |

#### 9.2 Payslip Management

| Input | Process | Output |
|-------|---------|--------|
| Payslip ID<br/>Adjustments (overtime, bonus, deductions, etc.) | 1. Retrieve Payslip<br/>2. Update fields<br/>3. Recalculate totals<br/>4. Log changes | Updated Payslip<br/>Audit log |

#### 9.3 Payroll Release

| Input | Process | Output |
|-------|---------|--------|
| PayrollPeriod ID<br/>Release confirmation | 1. Validate all payslips approved<br/>2. Set period status = RELEASED<br/>3. Set payslip status = RELEASED<br/>4. Send email to each employee<br/>5. Log release action | Released PayrollPeriod<br/>Released Payslips<br/>Email notifications<br/>Audit log |

#### 9.4 Payslip Email Distribution

| Input | Process | Output |
|-------|---------|--------|
| Payslip ID or Period ID<br/>Recipient email | 1. Retrieve payslip data<br/>2. Compose email with payslip details<br/>3. Send via SMTP<br/>4. Log send status<br/>5. Create PayslipEmailLog | Email sent<br/>PayslipEmailLog record<br/>Status tracking |

---

### 2.10 Notifications (Module 10.0)

#### 10.1 Notification Generation

| Input | Process | Output |
|-------|---------|--------|
| Event trigger (appointment, status change, low stock)<br/>Recipient(s)<br/>Message data | 1. Determine notification type<br/>2. Format message<br/>3. Create Notification record(s)<br/>4. Set is_read = False | Notification record(s)<br/>Unread count updated |

#### 10.2 Email Delivery

| Input | Process | Output |
|-------|---------|--------|
| Recipient email<br/>Subject<br/>Message body<br/>Attachments (optional) | 1. Compose email<br/>2. Send via SMTP<br/>3. Log delivery status | Email sent<br/>Delivery log |

---

### 2.11 Reports & Analytics (Module 11.0)

#### 11.1 Sales Reports

| Input | Process | Output |
|-------|---------|--------|
| Date range<br/>Branch filter<br/>Report type | 1. Query Sales data<br/>2. Aggregate by period/category<br/>3. Calculate totals, averages<br/>4. Format for display/export | Sales report<br/>Charts/graphs<br/>Export (CSV/PDF) |

#### 11.2 Inventory Reports

| Input | Process | Output |
|-------|---------|--------|
| Branch filter<br/>Stock status filter | 1. Query Product data<br/>2. Calculate inventory value<br/>3. Identify low/out of stock<br/>4. Format report | Inventory report<br/>Stock alerts<br/>Value summary |

#### 11.3 Payroll Reports

| Input | Process | Output |
|-------|---------|--------|
| PayrollPeriod ID<br/>Report type | 1. Query Payslip data<br/>2. Aggregate totals<br/>3. Calculate statutory contributions<br/>4. Format for display/export | Payroll summary<br/>Contribution reports<br/>Export (CSV/PDF) |

---

### 2.12 System Administration (Module 12.0)

#### 12.1 Branch Management

| Input | Process | Output |
|-------|---------|--------|
| Branch data (name, address, contact, hours)<br/>Social media links<br/>Map URLs | 1. Validate branch data<br/>2. Create/Update Branch<br/>3. Set is_active<br/>4. Update landing page display | Branch record<br/>Updated landing page |

#### 12.2 System Settings

| Input | Process | Output |
|-------|---------|--------|
| Setting key<br/>Setting value<br/>Category | 1. Retrieve SystemSetting<br/>2. Update value<br/>3. Type-coerce value<br/>4. Log change | Updated setting<br/>Audit log |

#### 12.3 Content Management

| Input | Process | Output |
|-------|---------|--------|
| Section type (HERO, MISSION, etc.)<br/>Content (title, subtitle, description, image) | 1. Retrieve SectionContent<br/>2. Update fields<br/>3. Upload image (if changed)<br/>4. Set is_active | Updated landing page content |

#### 12.4 Clinical Status Management

| Input | Process | Output |
|-------|---------|--------|
| Status data (name, code, color, description)<br/>Order preference | 1. Validate unique code<br/>2. Create/Update ClinicalStatus<br/>3. Set color for UI display<br/>4. Set is_active flag | ClinicalStatus record<br/>Available in pet status dropdown |

#### 12.5 Reason for Visit Management

| Input | Process | Output |
|-------|---------|--------|
| Reason data (name, code, description)<br/>Order preference | 1. Validate unique code<br/>2. Create/Update ReasonForVisit<br/>3. Set display order<br/>4. Set is_active flag | ReasonForVisit record<br/>Available in appointment reason dropdown |

---

## 3. Summary Hierarchy Table

| Level 0 | Level 1 | Level 2 |
|---------|---------|---------|
| **FMH Animal Clinic System** | | |
| | 1.0 User & Access Mgmt | 1.1 Registration, 1.2 Auth, 1.3 Roles, 1.4 Permissions |
| | 2.0 Patient Mgmt | 2.1 Pet Registration, 2.2 Profile Mgmt, 2.3 Owner Mgmt |
| | 3.0 Appointment Mgmt | 3.1 Booking, 3.2 Schedule, 3.3 Follow-up |
| | 4.0 Medical Records | 4.1 Creation, 4.2 Consultation, 4.3 Treatment |
| | 5.0 AI Diagnostics | 5.1 AI Request, 5.2 Review |
| | 6.0 Point of Sale | 6.1 Sales, 6.2 Payment, 6.3 Drawer, 6.4 Refund |
| | 7.0 Inventory Mgmt | 7.1 Products, 7.2 Adjustment, 7.3 Transfer, 7.4 Reservation |
| | 8.0 Employee Mgmt | 8.1 Staff, 8.2 Schedule, 8.3 License |
| | 9.0 Payroll Mgmt | 9.1 Generation, 9.2 Payslip, 9.3 Release, 9.4 Email |
| | 10.0 Notifications | 10.1 Generation, 10.2 Email |
| | 11.0 Reports | 11.1 Sales, 11.2 Inventory, 11.3 Payroll |
| | 12.0 Administration | 12.1 Branches, 12.2 Settings, 12.3 CMS, 12.4 Clinical Status, 12.5 Reasons |
