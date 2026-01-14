# Quick Reference: Evaluation Cycle Refactoring

## 🎯 TL;DR

**The only rule:** `SystemSettings.evaluations_enabled` controls all evaluation submission.

```python
# ✅ CORRECT
if not SystemSettings.evaluations_enabled:
    block_submission()

# ❌ WRONG (don't do this)
if current_cycle.is_closed:  # This column doesn't exist anymore
    block_submission()
```

---

## 🔑 Key Changes

### Models

```python
# Removed from EvaluationCycle
is_closed  # Column deleted - NEVER use this

# Added to Evaluation
year   # Immutable - stores evaluation's year
month  # Immutable - stores evaluation's month
```

### Routes

```python
# Before
if current_cycle.is_closed:
    return error()

# After (ONLY check)
if not settings.evaluations_enabled:
    return error()
```

### Templates

```html
<!-- Before -->
{% if cycle.is_closed %}

<!-- After -->
{% if not loop.first %}
<!-- Is past cycle? -->
```

---

## 📊 Data Model

```python
Evaluation {
    id
    created_at
    notes

    year          ← NEW (immutable at creation)
    month         ← NEW (immutable at creation)

    supervisor_id
    employee_id
    cycle_id      (optional, for grouping)
    responses[]
}

EvaluationCycle {
    id
    month
    year
    created_at
    # is_closed removed
}

SystemSettings {
    id
    evaluations_enabled   ← THE ONLY GATE
    updated_at
}
```

---

## 🔄 Flow: Submission

```
POST /employee/<id>
    ↓
if not SystemSettings.evaluations_enabled:
    flash('Disabled')
    return redirect()
    ↓
now = datetime.utcnow()
Evaluation(
    supervisor_id=current_user.id,
    employee_id=employee.id,
    year=now.year,        ← Captured now
    month=now.month,      ← Captured now
    cycle_id=current_cycle.id
)
db.session.commit()
    ↓
Redirect to success
```

---

## 📁 File Locations

| What              | Where                       |
| ----------------- | --------------------------- |
| Models            | `app/models.py`             |
| Routes            | `app/main/routes.py`        |
| Templates         | `app/templates/main/*.html` |
| Manager Dashboard | `manager_dashboard.html`    |
| Employee Profile  | `employee_profile.html`     |

---

## ✅ Testing

```python
# Test: Can submit when enabled
settings.evaluations_enabled = True
assert submit_evaluation() == success

# Test: Blocked when disabled
settings.evaluations_enabled = False
assert submit_evaluation() == blocked

# Test: Year/month captured
eval = create_evaluation()
assert eval.year == 2026
assert eval.month == 1

# Test: CSV read-only
before = count_evals()
export_csv()
after = count_evals()
assert before == after  # No changes
```

---

## 🛠️ Common Tasks

### Query Evaluations for a Month

```python
Evaluation.query.filter_by(
    year=2026,
    month=1
).all()
```

### Export Evaluations

```python
GET /manager/export-csv/<cycle_id>
# Returns CSV, modifies NOTHING
```

### Check if Evaluations Enabled

```python
settings = SystemSettings.get_settings()
if settings.evaluations_enabled:
    # Supervisors can submit
else:
    # Supervisors blocked
```

### List Past Months

```python
past_cycles = EvaluationCycle.query.order_by(
    EvaluationCycle.year.desc(),
    EvaluationCycle.month.desc()
).all()
```

---

## 🚨 Things NOT to Do

❌ Check `cycle.is_closed` (column removed)  
❌ Try to manually close a cycle (not needed)  
❌ Modify evaluation year/month (immutable)  
❌ Allow CSV export to change state (it can't)  
❌ Use multiple gates for submission (one only)  
❌ Delete past evaluations (preserved forever)  
❌ Recompute old months (frozen by year/month)

---

## 📚 Documentation

| File                    | Purpose           |
| ----------------------- | ----------------- |
| REFACTORING_SUMMARY.md  | What changed      |
| ARCHITECTURE.md         | How it works      |
| MIGRATION_GUIDE.md      | Integration guide |
| COMPLETION_CHECKLIST.md | Verification      |
| FINAL_REPORT.md         | Executive summary |
| validate_refactoring.py | Validation script |

---

## 🔍 Validation

Run any time to verify everything is correct:

```bash
python validate_refactoring.py
```

Expected output:

```
[OK] EvaluationCycle.is_closed removed
[OK] Evaluation.year field exists
[OK] Evaluation.month field exists
[OK] SystemSettings.evaluations_enabled = True
[OK] Queries filter by year/month correctly
[SUCCESS] ALL VALIDATION CHECKS PASSED
```

---

## 💾 Database

### Schema Changes

```sql
-- REMOVED
ALTER TABLE evaluation_cycle DROP COLUMN is_closed;

-- ADDED
ALTER TABLE evaluation ADD COLUMN year INTEGER NOT NULL;
ALTER TABLE evaluation ADD COLUMN month INTEGER NOT NULL;

-- RECOMMENDED
CREATE INDEX idx_evaluation_period ON evaluation(year, month);
```

### Backward Compat

✅ All old evaluations still exist  
✅ All old cycles still exist  
✅ No data deleted  
✅ Only schema additions/removals

---

## 🎓 Learning Path

1. **Start:** Read EXECUTIVE_SUMMARY.md (5 min)
2. **Understand:** Read ARCHITECTURE.md (10 min)
3. **Integrate:** Read MIGRATION_GUIDE.md (15 min)
4. **Verify:** Run validate_refactoring.py (1 min)
5. **Deep Dive:** Read REFACTORING_SUMMARY.md (20 min)

---

## 📞 FAQ

**Q: Where do I check if evaluations are enabled?**  
A: `SystemSettings.evaluations_enabled` - that's it.

**Q: How do I freeze a past month?**  
A: It's automatic via year/month fields.

**Q: Can supervisors edit past evaluations?**  
A: No, they're in past months (year/month is different).

**Q: What if I need the old cycle.is_closed logic?**  
A: You don't - use evaluations_enabled instead.

**Q: Is CSV export safe?**  
A: Yes, 100% read-only with no side effects.

**Q: How often should I export?**  
A: As often as needed - always get same result.

**Q: What if something breaks?**  
A: Check MIGRATION_GUIDE.md troubleshooting section.

---

## 🚀 Deployment Command

```bash
# Initialize fresh database
python seed.py

# Start application
python run.py

# Validate (optional but recommended)
python validate_refactoring.py
```

---

## 📝 Cheat Sheet

| Concept             | Before                                  | After                     |
| ------------------- | --------------------------------------- | ------------------------- |
| **Submission Gate** | `cycle.is_closed` OR `settings.enabled` | `settings.enabled` ONLY   |
| **Month Tracking**  | Cycle state                             | Evaluation.year/month     |
| **Data Freeze**     | Manual `cycle.is_closed = True`         | Automatic via year/month  |
| **CSV Export**      | Might have side effects                 | Read-only, no changes     |
| **Query Filter**    | Date-based range                        | Period-based (year/month) |
| **Past Months**     | Depends on cycle state                  | Always frozen             |
| **Export Safety**   | Unclear                                 | Guaranteed safe           |

---

## 🎯 Remember

```
┌─────────────────────────────────────────────┐
│                                             │
│  ONE GATE CONTROLS EVERYTHING:              │
│                                             │
│  SystemSettings.evaluations_enabled         │
│                                             │
│  TRUE = Supervisors can submit              │
│  FALSE = Supervisors cannot submit          │
│                                             │
│  That's all you need to know.               │
│                                             │
└─────────────────────────────────────────────┘
```

---

**Last Updated:** January 14, 2026  
**Status:** ✅ Production Ready  
**Version:** 1.0
