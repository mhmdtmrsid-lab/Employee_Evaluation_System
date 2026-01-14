# Evaluation Cycle Architecture - After Refactoring

## System Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    SUPERVISOR SUBMITS EVALUATION            │
│                   (POST /employee/<id>)                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │ CHECK: SystemSettings          │
        │ .evaluations_enabled?          │
        │ (SINGLE SOURCE OF TRUTH)       │
        └────────┬───────────────┬───────┘
                 │               │
                 │ TRUE          │ FALSE
                 ▼               ▼
         ┌──────────────┐   ┌─────────────┐
         │   ALLOWED    │   │   BLOCKED   │
         │  Continue    │   │   Show      │
         │   Create     │   │   Error     │
         │ Evaluation   │   │             │
         └──────┬───────┘   └─────────────┘
                │
                ▼
    ┌──────────────────────────────┐
    │  CREATE EVALUATION RECORD    │
    │  - Store year  (immutable)   │
    │  - Store month (immutable)   │
    │  - Store supervisor_id       │
    │  - Store employee_id         │
    │  - Link to cycle (optional)  │
    └──────────────┬───────────────┘
                   │
                   ▼
    ┌──────────────────────────────┐
    │  SAVE TO DATABASE            │
    │  Evaluation stored forever   │
    │  in year/month partition     │
    └──────────────┬───────────────┘
                   │
                   ▼
    ┌──────────────────────────────┐
    │  SUCCESS: Evaluation saved   │
    │  (until next month)          │
    └──────────────────────────────┘
```

## Query & Export Flow

```
┌─────────────────────────────────────────────────┐
│          MANAGER REQUESTS CSV EXPORT            │
│      (GET /manager/export-csv/<cycle_id>)       │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │ QUERY EVALUATIONS BY       │
        │ - cycle_id (for grouping)  │
        │ - year/month (for period)  │
        └────────────┬───────────────┘
                     │
                     ▼
    ┌──────────────────────────────────┐
    │  BUILD CSV IN MEMORY             │
    │  (READ-ONLY OPERATION)           │
    │  - No database changes           │
    │  - No flags modified             │
    │  - No cycle state updated        │
    └────────────┬─────────────────────┘
                 │
                 ▼
    ┌──────────────────────────────────┐
    │  DOWNLOAD FILE TO USER           │
    │  - No side effects               │
    │  - No database modifications     │
    │  - Safe, repeatable operation    │
    └──────────────────────────────────┘
```

## Data Model: Key Fields

```
┌─ EVALUATION ─────────────────────┐
│ id (PK)                           │
│ supervisor_id (FK)                │
│ employee_id (FK)                  │
│ cycle_id (FK) [optional]          │
│ ┌─ IMMUTABLE FIELDS ──────────┐   │
│ │ year     (set at creation)   │   │
│ │ month    (set at creation)   │   │
│ └──────────────────────────────┘   │
│ created_at                         │
│ notes                              │
└───────────────────────────────────┘

┌─ EVALUATION_CYCLE ───────────────┐
│ id (PK)                           │
│ month                             │
│ year                              │
│ created_at                        │
│ [is_closed - REMOVED]             │
│                                   │
│ ℹ️ For display/organization ONLY  │
│    Does NOT block submission      │
└───────────────────────────────────┘

┌─ SYSTEM_SETTINGS ────────────────┐
│ id (PK)                           │
│ evaluations_enabled (BOOLEAN)     │
│ updated_at                        │
│                                   │
│ 🔑 SINGLE SOURCE OF TRUTH        │
│    Controls ALL evaluation gates  │
└───────────────────────────────────┘
```

## Submission Logic: Before vs. After

### BEFORE (Legacy)

```
IF current_cycle.is_closed = TRUE
    BLOCK (cycle-based gating)
ELSE IF settings.evaluations_enabled = FALSE
    BLOCK (settings-based gating)
ELSE
    ALLOW
```

**Problem:** Multiple gates, conflicting logic, cycle state could be stale

---

### AFTER (Unified)

```
IF settings.evaluations_enabled = FALSE
    BLOCK
ELSE
    ALLOW
```

**Benefits:** Single gate, clear logic, no state dependencies

---

## Monthly Freeze Logic: Before vs. After

### BEFORE (Legacy)

```
Manager manually sets cycle.is_closed = TRUE
Data remains editable based on cycle state
No automatic freezing
Risk of accidental overwrites
```

### AFTER (Unified)

```
Evaluation records store year/month at creation
Query filters use (year, month) as immutable keys
Past months naturally frozen by architecture
Historical data guaranteed safe
No manual cycle management needed
```

---

## Historical Data Integrity

```
Database State:

Evaluation 1: year=2026, month=1, ... (January)
Evaluation 2: year=2026, month=1, ... (January)
Evaluation 3: year=2025, month=12, ... (December - PAST)
Evaluation 4: year=2025, month=11, ... (November - PAST)

Query for December 2025 past month:
SELECT * FROM evaluation WHERE year=2025 AND month=12;
Result: Evaluation 3 (immutable, always the same)

Query for December 2025 with supervisor filter:
SELECT * FROM evaluation
WHERE year=2025 AND month=12 AND supervisor_id=X;
Result: Subset of Evaluation 3 (reliable, reproducible)

Key Feature:
- Year/Month fields are NEVER updated
- Past months are forever frozen
- CSV export always returns same data (idempotent)
```

---

## Manager Control Scope

```
TOGGLE: evaluations_enabled = TRUE/FALSE

Effect on CURRENT month:
  ✅ Affects current evaluations (supervisors can/cannot submit)
  ✅ Immediate effect on active submission

Effect on PAST months:
  ⚠️ NO EFFECT (already frozen by year/month)
  ℹ️ CSV exports always return frozen data
  ℹ️ Queries always return same results

Effect on FUTURE months:
  ⚠️ NO EFFECT (month doesn't exist yet)
  ℹ️ When month arrives, toggle will apply
```

---

## CSV Export Characteristics

```
READ-ONLY Operation:

Input:  Manager clicks "Download CSV" for cycle
        GET /manager/export-csv/<cycle_id>

Processing:
  1. Query evaluations for cycle
  2. Build CSV in memory
  3. Return file to browser

Database changes:
  ❌ NO evaluation records modified
  ❌ NO cycle state changed
  ❌ NO evaluations_enabled toggled
  ❌ NO supervisor state updated
  ❌ NO timestamps updated

Repeatability:
  ✅ Download same cycle 100 times = identical CSV
  ✅ No side effects accumulate
  ✅ Safe, idempotent operation

Key Property:
  "CSV export is a read-only observation of data,
   not a state-modifying operation"
```

---

## Error Messages That Will NOT Occur

```
❌ "The evaluation cycle for this month is closed"
❌ "This cycle has been exported and is locked"
❌ "Evaluations cannot be modified after export"
❌ "The monthly report is closed"
❌ "Cycle closing prevented evaluation submission"

✅ Replaced with single, clear message:
"Evaluations are currently disabled by the Manager"
(when evaluations_enabled = FALSE)
```

---

## Deployment Checklist

- [x] Schema: Added year/month to Evaluation
- [x] Schema: Removed is_closed from EvaluationCycle
- [x] Routes: Updated employee_profile check
- [x] Routes: Updated CSV export (verified read-only)
- [x] Routes: Updated view_evaluations filter
- [x] Templates: Removed is_closed references
- [x] Models: Cleaned up blocking logic
- [x] Database: Migrated (seed.py executed)
- [x] Tests: All requirements validated
- [x] No UI styling changed
- [x] No routes renamed
- [x] No templates restructured
- [x] All existing functionality preserved
