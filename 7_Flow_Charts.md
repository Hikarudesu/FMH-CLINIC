# Process Flow Charts
## FMH Animal Clinic System

---

## Overview

This document contains detailed flow charts for critical business processes in the FMH Animal Clinic system.

---

## 1. User Authentication Flow

```mermaid
flowchart TD
    START([Start]) --> A[User accesses login page]
    A --> B[User enters credentials]
    B --> C{Valid credentials?}
    
    C -->|No| D[Display error message]
    D --> B
    
    C -->|Yes| E{Account active?}
    E -->|No| F[Display "Account disabled" message]
    F --> END1([End])
    
    E -->|Yes| G[Create session]
    G --> H[Log login activity]
    H --> I{Check user role}
    
    I -->|Pet Owner| J[Redirect to Pet Owner Portal]
    I -->|Receptionist| K[Redirect to Reception Dashboard]
    I -->|Veterinarian| L[Redirect to Vet Dashboard]
    I -->|Vet Assistant| L
    I -->|Branch Admin| M[Redirect to Admin Dashboard]
    I -->|Superadmin| N[Redirect to System Admin]
    
    J --> END2([End])
    K --> END2
    L --> END2
    M --> END2
    N --> END2
```

---

## 2. Appointment Booking Flow (Online Portal)

```mermaid
flowchart TD
    START([Start]) --> A[Pet Owner logs in]
    A --> B[Select "Book Appointment"]
    B --> C[Choose Branch]
    C --> D[Select Pet from list]
    D --> E[Choose Service Type]
    E --> F[Select preferred Date]
    F --> G{Date has available slots?}
    
    G -->|No| H[Show "No slots available"]
    H --> F
    
    G -->|Yes| I[Display available time slots]
    I --> J[Select time slot]
    J --> K[Enter reason for visit]
    K --> L[Review appointment details]
    L --> M{Confirm booking?}
    
    M -->|No| C
    M -->|Yes| N[Create Appointment record]
    N --> O[Set status = PENDING]
    O --> P[Denormalize pet/owner data]
    P --> Q[Generate notification to staff]
    Q --> R[Send confirmation email to owner]
    R --> S[Display confirmation page]
    S --> END([End])
```

---

## 3. Walk-in Appointment Flow

```mermaid
flowchart TD
    START([Start]) --> A[Customer arrives at clinic]
    A --> B[Receptionist greets customer]
    B --> C{Registered pet owner?}
    
    C -->|Yes| D[Search customer in system]
    D --> E[Select existing pet profile]
    
    C -->|No| F{New or returning guest?}
    F -->|New| G[Enter guest owner details]
    G --> H[Register new pet]
    F -->|Returning| I[Search by phone/name]
    I --> J[Select existing guest record]
    J --> K[Select pet or add new]
    
    E --> L[Create walk-in appointment]
    H --> L
    K --> L
    
    L --> M[Set appointment type = WALK_IN]
    M --> N[Check vet availability]
    N --> O{Vet available now?}
    
    O -->|Yes| P[Assign to available vet]
    O -->|No| Q[Add to queue]
    Q --> R[Estimate wait time]
    R --> S[Inform customer of wait]
    S --> P
    
    P --> T[Update appointment status = CONFIRMED]
    T --> U[Direct to waiting area]
    U --> END([End])
```

---

## 4. Medical Consultation Flow

```mermaid
flowchart TD
    START([Start]) --> A[Vet receives patient]
    A --> B[Review pet history]
    B --> C[Open Medical Record]
    C --> D{Existing active record?}
    
    D -->|Yes| E[Continue existing record]
    D -->|No| F[Create new MedicalRecord]
    
    E --> G[Create new RecordEntry]
    F --> G
    
    G --> H[Record vital signs]
    H --> I[weight, temperature]
    I --> J[Document clinical signs]
    J --> K{Need AI assistance?}
    
    K -->|Yes| L[Request AI Diagnosis]
    L --> M[Review AI suggestions]
    M --> N[Accept/modify diagnosis]
    
    K -->|No| O[Enter diagnosis manually]
    N --> O
    
    O --> P[Record treatment plan - Tx]
    P --> Q[Enter prescription - Rx]
    Q --> R{Follow-up needed?}
    
    R -->|Yes| S[Set follow-up date]
    R -->|No| T[Set action_required]
    S --> T
    
    T --> U{action_required value}
    
    U -->|HEALTHY| V[Pet.status = HEALTHY]
    U -->|MONITOR| W[Pet.status = MONITOR]
    U -->|TREATMENT| X[Pet.status = TREATMENT]
    U -->|CRITICAL| Y[Pet.status = CRITICAL]
    
    V --> Z[Save RecordEntry]
    W --> Z
    X --> Z
    Y --> Z
    
    Z --> AA[Update appointment status]
    AA --> AB{Services/products rendered?}
    
    AB -->|Yes| AC[Create Sale linked to appointment]
    AB -->|No| AD[Complete consultation]
    AC --> AD
    
    AD --> AE[Notify owner of status change]
    AE --> END([End])
```

---

## 5. POS Transaction Flow

```mermaid
flowchart TD
    START([Start]) --> A[Staff opens POS]
    A --> B{Cash drawer open?}
    
    B -->|No| C[Open cash drawer]
    C --> D[Enter opening amount]
    D --> E[Ready for transactions]
    
    B -->|Yes| E
    
    E --> F[Start new sale]
    F --> G{Customer type?}
    
    G -->|Registered| H[Search registered user]
    H --> I[Link sale to user]
    
    G -->|Walk-in| J[Enter guest info]
    J --> K[Sale with guest data]
    
    G -->|From Appointment| L[Select appointment]
    L --> M[Auto-populate customer info]
    M --> I
    
    I --> N[Add items to sale]
    K --> N
    
    N --> O{Add services?}
    O -->|Yes| P[Search/select services]
    P --> Q[Set quantity]
    Q --> N
    
    O -->|No| R{Add products?}
    R -->|Yes| S[Search/select products]
    S --> T[Set quantity]
    T --> U{Stock available?}
    U -->|Yes| N
    U -->|No| V[Show stock warning]
    V --> N
    
    R -->|No| W{Apply discount?}
    W -->|Yes| X[Select discount type]
    X --> Y[Enter discount value]
    Y --> Z[Calculate new total]
    
    W -->|No| AA[Calculate subtotal]
    Z --> AA
    
    AA --> AB[Calculate tax]
    AB --> AC[Display total amount]
    AC --> AD[Select payment method]
    AD --> AE{Payment method}
    
    AE -->|Cash| AF[Enter amount tendered]
    AF --> AG[Calculate change due]
    
    AE -->|Card| AH[Enter reference number]
    AE -->|E-wallet| AI[Enter reference number]
    AE -->|Split Payment| AJ[Enter multiple payments]
    
    AG --> AK[Create Payment record]
    AH --> AK
    AI --> AK
    AJ --> AK
    
    AK --> AL{Fully paid?}
    AL -->|No| AM[Record partial payment]
    AM --> AN[Customer statement updated]
    
    AL -->|Yes| AO[Complete sale]
    AO --> AP[Deduct product inventory]
    AP --> AQ[Generate receipt]
    AQ --> AR[Print receipt]
    AR --> END([End])
    
    AN --> END
```

---

## 6. Refund Processing Flow

```mermaid
flowchart TD
    START([Start]) --> A[Staff selects original sale]
    A --> B[Click "Process Refund"]
    B --> C{Refund type?}
    
    C -->|Full Refund| D[Select all items]
    C -->|Partial Refund| E[Select specific items]
    E --> F[Enter quantities to refund]
    
    D --> G[Enter refund reason]
    F --> G
    
    G --> H[Calculate refund amount]
    H --> I[Create Refund request]
    I --> J[Set status = PENDING_APPROVAL]
    J --> K[Notify approver]
    K --> L{Approval decision}
    
    L -->|Rejected| M[Set status = REJECTED]
    M --> N[Notify requestor]
    N --> END1([End])
    
    L -->|Approved| O[Set status = APPROVED]
    O --> P[Create RefundItem records]
    P --> Q{Contains products?}
    
    Q -->|Yes| R[Restore product inventory]
    R --> S[Create StockAdjustment - REFUND]
    
    Q -->|No| T[Process refund payment]
    S --> T
    
    T --> U[Update original Sale status]
    U --> V[Set refund status = PROCESSED]
    V --> W[Print refund receipt]
    W --> END2([End])
```

---

## 7. Inventory Stock Transfer Flow

```mermaid
flowchart TD
    START([Start]) --> A[Branch Admin initiates transfer]
    A --> B[Select source branch]
    B --> C[Select product to transfer]
    C --> D[Enter quantity]
    D --> E{Quantity <= available stock?}
    
    E -->|No| F[Display error - insufficient stock]
    F --> D
    
    E -->|Yes| G[Select destination branch]
    G --> H[Add transfer notes]
    H --> I[Create StockTransfer request]
    I --> J[Set status = PENDING]
    J --> K[Notify destination branch]
    K --> L{Destination approves?}
    
    L -->|Rejected| M[Set status = REJECTED]
    M --> N[Notify source branch]
    N --> END1([End])
    
    L -->|Approved| O[Set status = APPROVED]
    O --> P[Deduct from source stock]
    P --> Q[Create StockAdjustment - OUT]
    Q --> R{Product exists at destination?}
    
    R -->|Yes| S[Add to existing product stock]
    R -->|No| T[Create new product at destination]
    T --> U[Copy product details]
    U --> S
    
    S --> V[Create StockAdjustment - IN]
    V --> W[Set transfer status = COMPLETED]
    W --> X[Log transfer in audit]
    X --> Y[Notify both branches]
    Y --> END2([End])
```

---

## 8. Payroll Processing Flow

```mermaid
flowchart TD
    START([Start]) --> A[Admin opens Payroll module]
    A --> B[Select month and year]
    B --> C{PayrollPeriod exists?}
    
    C -->|Yes| D[Load existing period]
    C -->|No| E[Create new PayrollPeriod]
    E --> F[Set status = DRAFT]
    F --> D
    
    D --> G{Period status?}
    
    G -->|RELEASED| H[View-only mode]
    H --> END1([End])
    
    G -->|DRAFT| I[Click "Generate Payroll"]
    I --> J[Get all active StaffMembers]
    J --> K[Loop: For each staff member]
    
    K --> L[Create Payslip]
    L --> M[Set base salary from StaffMember]
    M --> N{Is 15th payout?}
    
    N -->|Yes| O[Add ₱1000 allowance]
    N -->|No| P{Is 30th payout?}
    P -->|Yes| O
    P -->|No| Q[No allowance split]
    
    O --> R[Calculate statutory deductions]
    Q --> R
    
    R --> S[SSS contribution]
    S --> T[PhilHealth contribution]
    T --> U[PAG-IBIG contribution]
    U --> V[Calculate withholding tax]
    V --> W[Compute net pay]
    W --> X{More staff?}
    
    X -->|Yes| K
    X -->|No| Y[Update PayrollPeriod totals]
    
    Y --> Z[Set status = GENERATED]
    Z --> AA[Log generation in audit]
    AA --> AB[Review payslips]
    
    AB --> AC{Need adjustments?}
    AC -->|Yes| AD[Modify individual payslips]
    AD --> AE[Overtime, bonus, deductions]
    AE --> AF[Recalculate net pay]
    AF --> AB
    
    AC -->|No| AG[Click "Release Payroll"]
    AG --> AH{All payslips approved?}
    
    AH -->|No| AI[Approve pending payslips]
    AI --> AG
    
    AH -->|Yes| AJ[Set period status = RELEASED]
    AJ --> AK[Set all payslips status = RELEASED]
    AK --> AL[Send email to each employee]
    AL --> AM[Log release in audit]
    AM --> END2([End])
```

---

## 9. Pet Status Monitoring Flow

```mermaid
flowchart TD
    START([Start]) --> A[RecordEntry saved with action_required]
    A --> B[Django signal triggered]
    B --> C{action_required value?}
    
    C -->|HEALTHY| D[Pet.status = HEALTHY]
    C -->|MONITOR| E[Pet.status = MONITOR]
    C -->|TREATMENT| F[Pet.status = TREATMENT]
    C -->|SURGERY| G[Pet.status = SURGERY]
    C -->|DIAGNOSTICS| H[Pet.status = DIAGNOSTICS]
    C -->|CRITICAL| I[Pet.status = CRITICAL]
    
    D --> J[Save Pet status]
    E --> J
    F --> J
    G --> J
    H --> J
    I --> J
    
    J --> K{Status changed from previous?}
    K -->|No| END1([End])
    
    K -->|Yes| L[Create notification for owner]
    L --> M{Status is CRITICAL?}
    
    M -->|Yes| N[Send urgent notification]
    N --> O[Alert staff dashboard]
    O --> P[Log status change]
    
    M -->|No| Q[Send standard notification]
    Q --> P
    
    P --> END2([End])
```

---

## 10. Product Reservation Flow

```mermaid
flowchart TD
    START([Start]) --> A[Staff creates reservation]
    A --> B[Select customer]
    B --> C[Select product]
    C --> D[Enter quantity]
    D --> E{Quantity <= available?}
    
    E -->|No| F[Display insufficient stock warning]
    F --> D
    
    E -->|Yes| G[Enter pickup date]
    G --> H[Add notes optional]
    H --> I[Create Reservation]
    I --> J[Set status = PENDING]
    J --> K[Create StockAdjustment - RESERVE]
    K --> L[Reduce available stock]
    L --> M[Notify customer]
    M --> N[Wait for pickup]
    
    N --> O{Customer action?}
    
    O -->|Pickup| P[Staff processes sale]
    P --> Q[Apply reservation to sale]
    Q --> R[Set status = RELEASED]
    R --> S[Finalize transaction]
    S --> END1([End])
    
    O -->|Cancel| T[Customer requests cancellation]
    T --> U[Set status = CANCELLED]
    U --> V[Create StockAdjustment - UNRESERVE]
    V --> W[Restore available stock]
    W --> END2([End])
    
    O -->|Expired| X[Pickup date passed]
    X --> Y[Set status = EXPIRED]
    Y --> Z[Admin reviews]
    Z --> AA{Release stock?}
    
    AA -->|Yes| V
    AA -->|No| AB[Extend reservation]
    AB --> G
```

---

## 11. User Activity Logging Flow

```mermaid
flowchart TD
    START([Start]) --> A[User performs action]
    A --> B{Action type?}
    
    B -->|Login| C[Log LOGIN event]
    B -->|Logout| D[Log LOGOUT event]
    B -->|Create| E[Log CREATE event]
    B -->|Update| F[Log UPDATE event]
    B -->|Delete| G[Log DELETE event]
    B -->|View| H[Log VIEW event]
    B -->|Export| I[Log EXPORT event]
    
    C --> J[Capture metadata]
    D --> J
    E --> J
    F --> J
    G --> J
    H --> J
    I --> J
    
    J --> K[Record timestamp]
    K --> L[Record user ID]
    L --> M[Record IP address]
    M --> N[Record user agent]
    N --> O[Record affected model]
    O --> P[Record object ID]
    P --> Q[Record field changes - JSON]
    Q --> R[Create ActivityLog entry]
    R --> END([End])
```

---

## 12. Branch Permission Check Flow

```mermaid
flowchart TD
    START([Start]) --> A[User makes request]
    A --> B[Get user's Role]
    B --> C[Get role hierarchy level]
    C --> D{Level >= 10 Superadmin?}
    
    D -->|Yes| E[Full access - all branches]
    E --> END1([End - GRANTED])
    
    D -->|No| F[Get required module]
    F --> G[Query ModulePermission]
    G --> H{Permission found?}
    
    H -->|No| I[Access Denied]
    I --> END2([End - DENIED])
    
    H -->|Yes| J[Check action permission]
    J --> K{Can perform action?}
    
    K -->|No| I
    K -->|Yes| L{Data involves branch?}
    
    L -->|No| M[Grant access]
    M --> END1
    
    L -->|Yes| N[Get user's assigned branch]
    N --> O[Get data's branch]
    O --> P{Same branch?}
    
    P -->|Yes| M
    P -->|No| Q{Cross-branch permission?}
    
    Q -->|Yes| M
    Q -->|No| I
```

---

## Summary

These flow charts cover the critical business processes:

| # | Process | Purpose |
|---|---------|---------|
| 1 | User Authentication | Login and role-based redirect |
| 2 | Online Appointment Booking | Pet owner portal booking |
| 3 | Walk-in Appointment | Reception handling of walk-ins |
| 4 | Medical Consultation | Full vet consultation workflow |
| 5 | POS Transaction | Complete sales process |
| 6 | Refund Processing | Handling returns and refunds |
| 7 | Stock Transfer | Inter-branch inventory movement |
| 8 | Payroll Processing | Monthly payroll generation and release |
| 9 | Pet Status Monitoring | Automatic status sync from records |
| 10 | Product Reservation | Reserve and release workflow |
| 11 | Activity Logging | Audit trail capture |
| 12 | Branch Permission Check | RBAC enforcement |
