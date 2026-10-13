# Saphire AOCS — Practical System Context & Comparative Case Study

## 1. Project Overview & Operational Context
* **System Name**: SAPHIRE AOCS (Airport Operations Coordination System)
* **Domain**: Aerodrome Operations & Airport Collaborative Decision Making (A-CDM)
* **Institutional Context**: SVKM's NMIMS MPSTME, Semester 5 Software Engineering (`702IT0C016`)
* **Student Engineering Team**:
  * **Krishna Solanki (I075)** — Database Architecture & Systems Integration Lead
  * **Chaitanya Tikku (I078)** — Documentation & Quality Lead
  * **Anuvrat Tripathi (I080)** — Frontend UI/UX Lead
  * **Anay Modi (I088)** — Backend API & Logic Lead

---

## 2. Technical Architecture & Implementation Stack
* **Backend**: Spring Boot 3.2.5 / Java 17, Spring Security 6, Hibernate JPA, RESTful API (18 Controllers).
* **Persistence & Database**: PostgreSQL 16/18 with 20 sequential Flyway versioned migrations (`V1` to `V20`).
  * 41 Normalized 3NF tables in the operational OLTP database.
  * Dedicated OLAP Data Warehouse star schema (`FACT_FLIGHT_TURNAROUND` with 10 dimensional tables).
  * 158,660+ seed records spanning 5,000 international and domestic flights and 500 role-based staff accounts.
* **Frontend**: React 19 + TypeScript + Vite + Material UI (MUI), featuring 16 web consoles (7 public passenger views, 9 role-based operational dashboards).
* **Quality Assurance**: 16 test suites with 109 automated JUnit 5 / Mockito unit and integration tests (100% pass rate).

---

## 3. Real-Time Event-Driven Subsystems in Saphire AOCS
1. **Airside Telemetry & Conflict Detection (`AirsideConflictController`, `AirsideTelemetryController`)**:
   * Evaluates active runway occupations, apron stand allocations, and taxiway bottlenecks in real time.
2. **Turnaround Task Workflow Orchestration (`TaskController`, `TurnaroundTaskService`)**:
   * Manages 4-phase concurrent turnaround tasks (deboarding, baggage unloading/loading, refueling, catering, cleaning, boarding).
3. **Baggage Reconciliation System (`BaggageController`)**:
   * Event-driven processing of barcode scanner telemetry from check-in through sorting, ramp transfer, and aircraft hold loading.
4. **State-Backed Session Engine (`AuthController`, `auth_sessions`)**:
   * Bridges stateless JWT tokens with database-level session tracking, allowing immediate revocation upon logout or concurrent logins.

---

## 4. Direct Architectural Parallels with AIAER-Mask

| Architectural Feature in AIAER-Mask | Implementation in Saphire AOCS |
|---|---|
| **Deterministic Capability Map $C(a, o)$** | **Role-Based Access Control (RBAC)**: Enforced via Spring Security `@PreAuthorize` annotations mapping exact user roles to operational endpoints (e.g., only `RAMP_AGENT` can trigger turnaround milestones; only `AOCC_CONTROLLER` can reallocate gates). |
| **Hard Action Mask $M_a(o) \in \{0, -\infty\}$** | **Domain Integrity Constraints**: Physical gate wingspan validation (preventing widebody A380/B777 aircraft from being assigned to narrowbody Code-C stands), and database-level `auth_sessions` revocation checks. |
| **Telemetry State Vector $s_t$** | **Operational Airport Telemetry**: Real-time runway queue depths, apron occupancy ratios, turnaround SLA deviation timers, and flight status state transitions. |
| **Neural Adaptive Layer (SAC)** | **Turnaround Dispatch & Resource Allocation**: Dynamic scheduling of ground staff, fueling trucks, and baggage baggage tugs based on real-time flight ETA delays. |
| **Separation of Safety and Adaptation** | **Decoupled Architecture**: Strict separation between transactional database consistency rules (3NF schema constraints) and dynamic real-time dashboard scheduling. |

---

## 5. Case Study Discussion Points for the Review Paper
In the final review paper (especially Chapter 6 / Case Study), the team can synthesize these practical insights:
1. **Why Safety Must Precede Adaptation**: In both cloud microservices (AIAER-Mask) and safety-critical airport software (Saphire AOCS), optimizing for throughput without hard semantic boundaries results in catastrophic state corruption.
2. **Deterministic Guards vs. Black-Box AI**: Both systems prove that safety constraints should remain deterministic and auditable (symbolic rule guards / database constraints), while AI/adaptive policies should be restricted strictly to performance optimization among valid choices.
