# System Architecture Diagram
## FMH Animal Clinic System

---

## Overview

This document describes the technical architecture of the FMH Animal Clinic Management System, a Django-based web application with multi-branch support.

---

## 1. High-Level Architecture

```mermaid
flowchart TB
    subgraph Clients["Client Layer"]
        WEB["🌐 Web Browser<br/>(Chrome, Firefox, Safari)"]
        MOBILE["📱 Mobile Browser<br/>(Responsive Web)"]
    end
    
    subgraph Presentation["Presentation Layer"]
        LANDING["🏠 Landing Page<br/>(Public)"]
        PORTAL["👤 Customer Portal<br/>(Pet Owners)"]
        ADMIN["🔧 Admin Panel<br/>(Staff)"]
    end
    
    subgraph Application["Application Layer (Django)"]
        subgraph Django["Django Framework"]
            URLS["URL Router"]
            VIEWS["Views"]
            TEMPLATES["Templates<br/>(Jinja2)"]
            FORMS["Forms"]
            MIDDLEWARE["Middleware<br/>(Auth, CSRF, Session)"]
        end
        
        subgraph Apps["Django Apps"]
            APP_ACC["accounts"]
            APP_PAT["patients"]
            APP_APT["appointments"]
            APP_REC["records"]
            APP_DIA["diagnostics"]
            APP_INV["inventory"]
            APP_POS["pos"]
            APP_BIL["billing"]
            APP_EMP["employees"]
            APP_PAY["payroll"]
            APP_NOT["notifications"]
            APP_SET["settings"]
            APP_REP["reports"]
            APP_BRA["branches"]
        end
    end
    
    subgraph Business["Business Logic Layer"]
        RBAC["🔐 RBAC Engine"]
        SIGNALS["📡 Django Signals"]
        SERVICES["⚙️ Service Classes"]
        VALIDATORS["✅ Validators"]
    end
    
    subgraph Data["Data Layer"]
        ORM["Django ORM"]
        MODELS["Models"]
        MANAGERS["Custom Managers"]
        QUERYSETS["QuerySets"]
    end
    
    subgraph Storage["Storage Layer"]
        DB[("🗄️ SQLite<br/>(Development)<br/>PostgreSQL<br/>(Production)")]
        MEDIA[("📁 Media Storage<br/>(Images, Files)")]
        STATIC[("📦 Static Files<br/>(CSS, JS, Images)")]
    end
    
    subgraph External["External Services"]
        AI_API["🤖 AI Diagnostic API"]
        EMAIL_SVC["📧 Email Service<br/>(SMTP)"]
        PAYMENT["💳 Payment Gateway<br/>(GCash, Maya)"]
    end
    
    %% Connections
    WEB --> LANDING
    WEB --> PORTAL
    WEB --> ADMIN
    MOBILE --> LANDING
    MOBILE --> PORTAL
    
    LANDING --> URLS
    PORTAL --> URLS
    ADMIN --> URLS
    
    URLS --> VIEWS
    VIEWS --> TEMPLATES
    VIEWS --> FORMS
    VIEWS --> MIDDLEWARE
    
    VIEWS --> RBAC
    VIEWS --> SERVICES
    
    SERVICES --> ORM
    ORM --> MODELS
    MODELS --> MANAGERS
    
    ORM --> DB
    MODELS --> MEDIA
    TEMPLATES --> STATIC
    
    SERVICES --> AI_API
    SERVICES --> EMAIL_SVC
    SERVICES --> PAYMENT
    
    classDef client fill:#e3f2fd,stroke:#1565c0
    classDef presentation fill:#e8f5e9,stroke:#2e7d32
    classDef application fill:#fff3e0,stroke:#ef6c00
    classDef business fill:#fce4ec,stroke:#c2185b
    classDef data fill:#f3e5f5,stroke:#7b1fa2
    classDef storage fill:#e0e0e0,stroke:#424242
    classDef external fill:#e1f5fe,stroke:#0277bd
    
    class WEB,MOBILE client
    class LANDING,PORTAL,ADMIN presentation
    class URLS,VIEWS,TEMPLATES,FORMS,MIDDLEWARE,Django,Apps application
    class RBAC,SIGNALS,SERVICES,VALIDATORS business
    class ORM,MODELS,MANAGERS,QUERYSETS data
    class DB,MEDIA,STATIC storage
    class AI_API,EMAIL_SVC,PAYMENT external
```

---

## 2. Component Architecture

```mermaid
flowchart TB
    subgraph Frontend["Frontend Components"]
        HTML["HTML5 Templates"]
        CSS["CSS3 / TailwindCSS"]
        JS["JavaScript"]
        HTMX["HTMX<br/>(Dynamic Updates)"]
        ALPINE["Alpine.js<br/>(Reactivity)"]
    end
    
    subgraph Backend["Backend Components"]
        subgraph Core["Core Django"]
            DJANGO["Django 4.x"]
            DRF["Django REST Framework<br/>(API)"]
            AUTH["Django Auth"]
            ADMIN_SITE["Django Admin"]
        end
        
        subgraph CustomApps["Custom Applications"]
            direction TB
            ACC["accounts<br/>User & RBAC"]
            PAT["patients<br/>Pet Records"]
            APT["appointments<br/>Scheduling"]
            REC["records<br/>Medical Records"]
            DIA["diagnostics<br/>AI Integration"]
            INV["inventory<br/>Stock Mgmt"]
            POS_APP["pos<br/>Sales & Payments"]
            BIL["billing<br/>Services & SOA"]
            EMP["employees<br/>Staff Mgmt"]
            PAY["payroll<br/>Compensation"]
            NOT["notifications<br/>Alerts"]
            SET["settings<br/>Configuration"]
            BRA["branches<br/>Multi-location"]
            LAND["landing<br/>Public Site"]
            UTIL["utils<br/>Shared Code"]
        end
    end
    
    subgraph Infrastructure["Infrastructure"]
        WSGI["WSGI Server<br/>(Gunicorn)"]
        NGINX["Reverse Proxy<br/>(Nginx)"]
        CACHE["Cache<br/>(Redis/Memcached)"]
    end
    
    subgraph Database["Database"]
        SQLITE["SQLite<br/>(Dev)"]
        POSTGRES["PostgreSQL<br/>(Prod)"]
    end
    
    Frontend --> Backend
    Backend --> Infrastructure
    Infrastructure --> Database
    
    classDef frontend fill:#bbdefb,stroke:#1565c0
    classDef backend fill:#c8e6c9,stroke:#2e7d32
    classDef infra fill:#ffe0b2,stroke:#e65100
    classDef db fill:#d1c4e9,stroke:#512da8
    
    class HTML,CSS,JS,HTMX,ALPINE frontend
    class DJANGO,DRF,AUTH,ADMIN_SITE,ACC,PAT,APT,REC,DIA,INV,POS_APP,BIL,EMP,PAY,NOT,SET,BRA,LAND,UTIL backend
    class WSGI,NGINX,CACHE infra
    class SQLITE,POSTGRES db
```

---

## 3. Module Architecture (Django Apps)

```mermaid
flowchart LR
    subgraph Core["Core Modules"]
        ACC["accounts<br/>━━━━━━━━<br/>User<br/>Role<br/>Module<br/>Permission"]
        BRA["branches<br/>━━━━━━━━<br/>Branch"]
        SET["settings<br/>━━━━━━━━<br/>SystemSetting<br/>ClinicProfile<br/>CMS Models"]
        UTIL["utils<br/>━━━━━━━━<br/>SoftDeleteModel<br/>Base Classes"]
    end
    
    subgraph Clinical["Clinical Modules"]
        PAT["patients<br/>━━━━━━━━<br/>Pet"]
        APT["appointments<br/>━━━━━━━━<br/>Appointment"]
        REC["records<br/>━━━━━━━━<br/>MedicalRecord<br/>RecordEntry"]
        DIA["diagnostics<br/>━━━━━━━━<br/>AIDiagnosis"]
    end
    
    subgraph Business["Business Modules"]
        INV["inventory<br/>━━━━━━━━<br/>Product<br/>StockAdjustment<br/>StockTransfer<br/>Reservation"]
        BIL["billing<br/>━━━━━━━━<br/>Service<br/>CustomerStatement"]
        POS["pos<br/>━━━━━━━━<br/>Sale<br/>SaleItem<br/>Payment<br/>CashDrawer<br/>Refund"]
    end
    
    subgraph HR["HR Modules"]
        EMP["employees<br/>━━━━━━━━<br/>StaffMember<br/>VetSchedule<br/>RecurringSchedule"]
        PAY["payroll<br/>━━━━━━━━<br/>PayrollPeriod<br/>Payslip<br/>AuditLog"]
    end
    
    subgraph Support["Support Modules"]
        NOT["notifications<br/>━━━━━━━━<br/>Notification<br/>FollowUp"]
        REP["reports<br/>━━━━━━━━<br/>(Dynamic)"]
        LAND["landing<br/>━━━━━━━━<br/>(Views Only)"]
    end
    
    %% Dependencies
    ACC --> BRA
    PAT --> ACC
    APT --> PAT
    APT --> EMP
    APT --> BRA
    REC --> PAT
    REC --> EMP
    DIA --> PAT
    DIA --> EMP
    INV --> BRA
    BIL --> BRA
    POS --> INV
    POS --> BIL
    POS --> PAT
    EMP --> BRA
    EMP --> ACC
    PAY --> EMP
    NOT --> ACC
    NOT --> APT
```

---

## 4. Technology Stack

```mermaid
flowchart TB
    subgraph Stack["Technology Stack"]
        subgraph PL["Programming Languages"]
            PY["🐍 Python 3.10+"]
            JS_LANG["JavaScript ES6+"]
            HTML_LANG["HTML5"]
            CSS_LANG["CSS3"]
        end
        
        subgraph Frameworks["Frameworks & Libraries"]
            DJANGO_FW["Django 4.x"]
            TAILWIND["TailwindCSS"]
            HTMX_FW["HTMX"]
            ALPINE_FW["Alpine.js"]
            BOXICONS["Boxicons"]
        end
        
        subgraph DB_TECH["Database"]
            SQLITE_DB["SQLite (Dev)"]
            PG["PostgreSQL (Prod)"]
        end
        
        subgraph DevTools["Development Tools"]
            GIT["Git"]
            VENV["Python venv"]
            PIP["pip"]
            NPM["npm (Assets)"]
        end
        
        subgraph Deployment["Deployment"]
            GUNICORN["Gunicorn"]
            NGINX_DEP["Nginx"]
            DOCKER["Docker (Optional)"]
        end
    end
```

---

## 5. Deployment Architecture

```mermaid
flowchart TB
    subgraph Internet["Internet"]
        USERS["👥 Users"]
        DNS["🌐 DNS"]
    end
    
    subgraph Server["Production Server"]
        subgraph WebLayer["Web Layer"]
            NGINX_SRV["Nginx<br/>━━━━━━━━<br/>• Reverse Proxy<br/>• SSL Termination<br/>• Static Files<br/>• Load Balancing"]
        end
        
        subgraph AppLayer["Application Layer"]
            GUNICORN_SRV["Gunicorn<br/>━━━━━━━━<br/>• WSGI Server<br/>• Worker Processes<br/>• Process Management"]
            DJANGO_APP["Django App<br/>━━━━━━━━<br/>• FMH Clinic<br/>• All Modules"]
        end
        
        subgraph DataLayer["Data Layer"]
            PG_DB[("PostgreSQL<br/>━━━━━━━━<br/>• Production DB<br/>• Backups")]
            REDIS["Redis<br/>━━━━━━━━<br/>• Session Cache<br/>• Task Queue"]
        end
        
        subgraph FileLayer["File Storage"]
            MEDIA_SRV["Media Files<br/>━━━━━━━━<br/>• Pet Photos<br/>• Profile Images<br/>• Documents"]
            STATIC_SRV["Static Files<br/>━━━━━━━━<br/>• CSS/JS<br/>• Images<br/>• Fonts"]
        end
    end
    
    subgraph External_SVC["External Services"]
        SMTP_EXT["📧 SMTP Server"]
        AI_EXT["🤖 AI API"]
        PAY_EXT["💳 Payment Gateway"]
    end
    
    USERS --> DNS
    DNS --> NGINX_SRV
    NGINX_SRV --> STATIC_SRV
    NGINX_SRV --> MEDIA_SRV
    NGINX_SRV --> GUNICORN_SRV
    GUNICORN_SRV --> DJANGO_APP
    DJANGO_APP --> PG_DB
    DJANGO_APP --> REDIS
    DJANGO_APP --> SMTP_EXT
    DJANGO_APP --> AI_EXT
    DJANGO_APP --> PAY_EXT
    
    classDef internet fill:#e3f2fd,stroke:#1565c0
    classDef web fill:#c8e6c9,stroke:#2e7d32
    classDef app fill:#fff3e0,stroke:#ef6c00
    classDef data fill:#f3e5f5,stroke:#7b1fa2
    classDef file fill:#e0e0e0,stroke:#616161
    classDef external fill:#ffecb3,stroke:#ff8f00
    
    class USERS,DNS internet
    class NGINX_SRV web
    class GUNICORN_SRV,DJANGO_APP app
    class PG_DB,REDIS data
    class MEDIA_SRV,STATIC_SRV file
    class SMTP_EXT,AI_EXT,PAY_EXT external
```

---

## 6. Security Architecture

```mermaid
flowchart TB
    subgraph Security["Security Layers"]
        subgraph Network["Network Security"]
            SSL["🔒 SSL/TLS<br/>HTTPS Only"]
            FIREWALL["🛡️ Firewall<br/>Port Restrictions"]
        end
        
        subgraph Application["Application Security"]
            CSRF["CSRF Protection<br/>(Django Built-in)"]
            XSS["XSS Prevention<br/>(Template Escaping)"]
            SQL_INJ["SQL Injection<br/>(ORM Protection)"]
            CORS["CORS Policy"]
        end
        
        subgraph Auth["Authentication & Authorization"]
            SESSION["Session Auth<br/>(Django Sessions)"]
            RBAC_SEC["RBAC Engine<br/>(Custom Roles)"]
            PERM["Permission Checks<br/>(Decorators)"]
        end
        
        subgraph Data["Data Security"]
            PWD_HASH["Password Hashing<br/>(PBKDF2)"]
            SENSITIVE["Sensitive Data<br/>Encryption"]
            AUDIT["Audit Logging"]
        end
    end
    
    Network --> Application
    Application --> Auth
    Auth --> Data
```

---

## 7. PlantUML - System Architecture

```plantuml
@startuml FMH_System_Architecture

!define ICONURL https://raw.githubusercontent.com/tupadr3/plantuml-icon-font-sprites/v2.4.0

skinparam componentStyle rectangle
skinparam linetype ortho

' Client Layer
package "Client Layer" #E3F2FD {
    [Web Browser] as WEB
    [Mobile Browser] as MOBILE
}

' Presentation Layer
package "Presentation Layer" #E8F5E9 {
    [Landing Page\n(Public)] as LANDING
    [Customer Portal\n(Pet Owners)] as PORTAL
    [Admin Panel\n(Staff)] as ADMIN
}

' Application Layer
package "Application Layer" #FFF3E0 {
    package "Django Framework" {
        [URL Router] as URLS
        [Views] as VIEWS
        [Templates] as TEMPLATES
        [Middleware] as MW
    }
    
    package "Django Apps" {
        [accounts] as ACC
        [patients] as PAT
        [appointments] as APT
        [records] as REC
        [diagnostics] as DIA
        [inventory] as INV
        [pos] as POS
        [billing] as BIL
        [employees] as EMP
        [payroll] as PAY
        [notifications] as NOT
        [settings] as SET
        [branches] as BRA
    }
}

' Business Layer
package "Business Logic" #FCE4EC {
    [RBAC Engine] as RBAC
    [Django Signals] as SIG
    [Services] as SVC
}

' Data Layer
package "Data Layer" #F3E5F5 {
    [Django ORM] as ORM
    [Models] as MDL
    [Managers] as MGR
}

' Storage Layer
database "Storage" #E0E0E0 {
    [SQLite / PostgreSQL] as DB
    [Media Storage] as MEDIA
    [Static Files] as STATIC
}

' External Services
cloud "External Services" #E1F5FE {
    [AI Diagnostic API] as AI
    [Email Service] as EMAIL
    [Payment Gateway] as PAY_GW
}

' Connections
WEB --> LANDING
WEB --> PORTAL
WEB --> ADMIN
MOBILE --> PORTAL

LANDING --> URLS
PORTAL --> URLS
ADMIN --> URLS

URLS --> VIEWS
VIEWS --> TEMPLATES
VIEWS --> MW
MW --> RBAC

VIEWS --> SVC
SVC --> ORM
ORM --> MDL
MDL --> MGR
MGR --> DB

TEMPLATES --> STATIC
MDL --> MEDIA

SVC --> AI
SVC --> EMAIL
SVC --> PAY_GW

@enduml
```

---

## 8. Technology Stack Summary

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| **Language** | Python | 3.10+ | Backend development |
| **Framework** | Django | 4.x | Web framework |
| **Database** | SQLite/PostgreSQL | - | Data storage |
| **Frontend** | HTML5, CSS3, JS | - | User interface |
| **CSS Framework** | TailwindCSS | 3.x | Styling |
| **Dynamic UI** | HTMX | 1.x | AJAX without JS |
| **Reactivity** | Alpine.js | 3.x | Lightweight reactivity |
| **Icons** | Boxicons | 2.x | Icon library |
| **WSGI** | Gunicorn | - | Production server |
| **Proxy** | Nginx | - | Reverse proxy, SSL |
| **Cache** | Redis | - | Session cache, queues |

---

## 9. Directory Structure

```
FMHANIMALCLINIC/
├── FMHANIMALCLINIC/          # Django project settings
│   ├── settings.py           # Configuration
│   ├── urls.py               # Root URL patterns
│   └── wsgi.py               # WSGI config
│
├── accounts/                  # User & RBAC
├── appointments/              # Scheduling
├── billing/                   # Services & SOA
├── branches/                  # Multi-location
├── diagnostics/               # AI integration
├── employees/                 # Staff management
├── inventory/                 # Stock management
├── landing/                   # Public website
├── notifications/             # Alerts
├── patients/                  # Pet records
├── payroll/                   # Compensation
├── pos/                       # Point of sale
├── records/                   # Medical records
├── reports/                   # Analytics
├── settings/                  # System config
├── utils/                     # Shared utilities
│
├── static/                    # Static files
│   ├── css/
│   ├── js/
│   └── image/
│
├── templates/                 # HTML templates
│   ├── base.html
│   ├── landing/
│   ├── portal/
│   └── admin/
│
├── media/                     # User uploads
│   ├── pet_photos/
│   └── profiles/
│
├── manage.py                  # Django CLI
├── requirements.txt           # Dependencies
└── .env                       # Environment variables
```

---

## 10. Key Architectural Decisions

| Decision | Rationale |
|----------|-----------|
| **Django Monolith** | Simpler deployment, shared ORM, integrated auth |
| **HTMX over React** | Less complexity, server-rendered, progressive enhancement |
| **Custom RBAC** | Fine-grained permissions beyond Django groups |
| **Soft Delete** | Preserve audit trail, allow data recovery |
| **Multi-Branch Design** | Branch-scoped data, independent operations |
| **Signal-Based Events** | Loose coupling, automatic sync (e.g., pet status updates) |
| **SQLite for Dev** | Zero-config development, easy reset |
| **PostgreSQL for Prod** | Robust, scalable, ACID compliance |
