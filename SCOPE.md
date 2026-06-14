# SCOPE.md — Anomaly Log & Database Schema

## Project: SplitLedger - Shared Expense Tracking Application

**Date:** June 14-15, 2026  
**Developer:** Afaque HK  
**Repository:** https://github.com/afaquehk/expense-analyzer

---

## 📊 **CSV Data Problems & Handling**

### **Anomaly Detection System**

The application detects **15+ types of data anomalies** during CSV import. Every issue is flagged for user review—nothing is silently fixed or deleted.

---

## 🔍 **Detected Anomalies & Handling**

### **1. Duplicate Rows**

**Problem:**
- Same expense appears multiple times in CSV
- Common when merging multiple sheets
- Risk of double-counting expenses

**Detection:**
```python
row_signature = f"{date}_{description}_{amount}"
if row_signature in seen_rows:
    flag_as_duplicate()
```

**Handling:**
- ✅ Flagged with anomaly type: `duplicate`
- ✅ Shows original row data
- ✅ User decides: Skip or import anyway
- ❌ Never auto-deleted

**Example:**
```csv
2026-06-01,Groceries,1500,INR,john  # Row 5
2026-06-01,Groceries,1500,INR,john  # Row 12 - DUPLICATE!
```

---

### **2. Settlement Recorded as Expense**

**Problem:**
- Direct payments between members mixed with expenses
- Should be in settlements table, not expenses
- Affects balance calculations if treated as expense

**Detection:**
- Description contains: "settlement", "paid back", "reimbursement"
- Amount matches typical payment patterns

**Handling:**
- ✅ Flagged with anomaly type: `settlement_as_expense`
- ✅ Suggestion: "Record as settlement instead"
- ✅ User can approve to create settlement entry
- ✅ Or reject and import as regular expense

---

### **3. Negative Amounts**

**Problem:**
- Expenses with negative values (e.g., -500)
- Usually indicates refunds or data entry errors
- Can distort balance calculations

**Detection:**
```python
if Decimal(amount) < 0:
    flag_as_negative_amount()
```

**Handling:**
- ✅ Flagged with anomaly type: `negative_amount`
- ✅ Suggestion: "Possible refund or error"
- ✅ User reviews and decides
- ⚠️ Can import if legitimate (e.g., refund scenario)

**Example:**
```csv
2026-06-10,Electricity Refund,-200,INR,john
```

---

### **4. Zero Amounts**

**Problem:**
- Expenses with ₹0 amount
- No financial impact but clutters records
- Usually data entry mistake

**Detection:**
```python
if amount == 0:
    flag_as_zero_amount()
```

**Handling:**
- ✅ Flagged with anomaly type: `zero_amount`
- ✅ Suggestion: "Verify or skip"
- ✅ User can choose to import or reject

---

### **5. Currency Mismatches**

**Problem:**
- Unsupported currencies (EUR, GBP, etc.)
- Missing currency field
- Mixed currency notation

**Detection:**
```python
if currency not in ['INR', 'USD']:
    flag_as_currency_mismatch()
```

**Handling:**
- ✅ Flagged with anomaly type: `currency_mismatch`
- ✅ Shows unsupported currency
- ✅ Suggestion: "Only INR and USD supported"
- ❌ Cannot import until fixed

**Example:**
```csv
2026-06-05,Hotel,500,EUR,jane  # EUR not supported!
```

---

### **6. Post-Moveout Expenses**

**Problem:**
- Expense dated after member left group
- Member shouldn't be included in split
- Causes incorrect balance calculations

**Detection:**
```python
if expense.date > membership.date_left:
    flag_as_post_moveout()
```

**Handling:**
- ✅ Flagged with anomaly type: `post_moveout`
- ✅ Shows expense date vs. leave date
- ✅ Suggestion: "Member not in group on this date"
- ⚠️ Member automatically excluded from split

**Example:**
```
Sam left: April 10, 2026
Expense: April 20, 2026 - "Electricity"
Sam NOT included in split for this expense
```

---

### **7. Missing Required Fields**

**Problem:**
- CSV rows missing critical data
- Date, description, amount, or paid_by empty
- Cannot create valid expense

**Detection:**
```python
if not row.get('date') or not row.get('description'):
    flag_as_missing_field()
```

**Handling:**
- ✅ Flagged with anomaly type: `missing_field`
- ✅ Shows which field is missing
- ✅ Suggestion: "Add missing data"
- ❌ Cannot import until fixed

---

### **8. Name Inconsistencies**

**Problem:**
- Same person spelled differently: "john", "John", "jhon"
- Causes split issues
- User not recognized

**Detection:**
- Username lookup fails
- Similar names detected (Levenshtein distance)

**Handling:**
- ✅ Flagged with anomaly type: `name_inconsistency`
- ✅ Shows similar existing usernames
- ✅ Suggestion: "Use exact username: john"
- ❌ Cannot import until corrected

**Example:**
```csv
2026-06-01,Groceries,1500,INR,jhon  # Should be "john"
```

---

### **9. Percentage Sum ≠ 100%**

**Problem:**
- Percentage splits don't add to 100%
- Example: 40% + 40% + 40% = 120%
- Mathematical inconsistency

**Detection:**
```python
if split_type == 'percentage':
    if sum(percentages) != 100:
        flag_as_percentage_sum()
```

**Handling:**
- ✅ Flagged with anomaly type: `percentage_sum`
- ✅ Shows total percentage (e.g., 120%)
- ⚠️ App calculates proportionally anyway
- ✅ User can accept or fix

---

### **10. Exact Sum ≠ Total**

**Problem:**
- Exact splits don't match expense total
- Example: Total ₹1,000 but splits sum to ₹950
- ₹50 discrepancy

**Detection:**
```python
if split_type == 'exact':
    if sum(exact_amounts) != total_amount:
        flag_as_exact_sum()
```

**Handling:**
- ✅ Flagged with anomaly type: `exact_sum`
- ✅ Shows difference amount
- ⚠️ User must decide how to handle difference
- ✅ Can accept anyway

---

### **11. Unknown Members**

**Problem:**
- Username doesn't exist in system
- Cannot assign expense or split
- Typo or user not registered

**Detection:**
```python
try:
    User.objects.get(username=paid_by)
except User.DoesNotExist:
    flag_as_unknown_member()
```

**Handling:**
- ✅ Flagged with anomaly type: `unknown_member`
- ✅ Shows username that doesn't exist
- ✅ Suggestion: "Register this user first"
- ❌ Cannot import until user exists

---

### **12. Future-Dated Expenses**

**Problem:**
- Expense date is in the future
- Example: Today is June 15, expense is June 20
- Usually data entry error

**Detection:**
```python
if expense_date > today:
    flag_as_future_date()
```

**Handling:**
- ✅ Flagged with anomaly type: `future_date`
- ✅ Shows expense date
- ✅ Suggestion: "Verify date is correct"
- ⚠️ Can import if intentional (planned expense)

---

### **13. Ambiguous Date Formats**

**Problem:**
- Date not in YYYY-MM-DD format
- Example: "06/01/2026" (US vs. DD/MM/YYYY)
- Parsing ambiguity

**Detection:**
```python
try:
    datetime.strptime(date, '%Y-%m-%d')
except ValueError:
    flag_as_ambiguous_date()
```

**Handling:**
- ✅ Flagged with anomaly type: `ambiguous_date`
- ✅ Shows problematic date
- ✅ Requires YYYY-MM-DD format
- ❌ Cannot import until fixed

---

### **14. Format Inconsistencies**

**Problem:**
- Invalid number formats
- Example: "1,500.00" (comma separator)
- Decimal parsing errors

**Detection:**
```python
try:
    Decimal(amount.replace(',', ''))
except InvalidOperation:
    flag_as_format_error()
```

**Handling:**
- ✅ Flagged with anomaly type: `format_error`
- ✅ Shows invalid value
- ✅ Suggestion: "Use decimal format: 1500.00"
- ❌ Cannot import until fixed

---

### **15. Split Type Conflicts**

**Problem:**
- Split type specified but required columns missing
- Example: `split_type=percentage` but no percentage columns
- Data inconsistency

**Detection:**
```python
if split_type == 'percentage' and not has_percentage_columns():
    flag_as_split_conflict()
```

**Handling:**
- ✅ Flagged with anomaly type: `split_conflict`
- ⚠️ Falls back to equal split
- ✅ User can add split columns or accept equal split

---

### **16. Amount Precision Issues**

**Problem:**
- Too many decimal places (e.g., 1500.123456)
- Can cause rounding errors in calculations
- Unusual for currency

**Detection:**
```python
if len(str(amount).split('.')[-1]) > 2:
    flag_as_amount_precision()
```

**Handling:**
- ✅ Flagged with anomaly type: `amount_precision`
- ⚠️ Rounds to 2 decimal places
- ✅ User notified of rounding

---

## 🔄 **Anomaly Workflow**

### **Import Process:**

```
1. Upload CSV
   ↓
2. Parse & Validate
   ↓
3. Detect Anomalies (15+ types)
   ↓
4. Create ImportSession record
   ↓
5. Flag anomalies in ImportAnomaly table
   ↓
6. Show Review Screen
   ↓
7. User Reviews Each Anomaly
   ↓
8. User Decides: Approve / Modify / Reject
   ↓
9. Import Clean Rows Only
   ↓
10. Generate Import Report
```

### **Resolution Options:**

| Resolution | Description |
|------------|-------------|
| `pending` | Awaiting user decision |
| `approved` | Import as-is |
| `modified` | Fix data then import |
| `rejected` | Skip this row |
| `auto_fixed` | System corrected (with user notification) |

---

## 🗄️ **Database Schema**

### **Complete Entity-Relationship Diagram**

```
┌─────────────────────┐
│   auth_user         │ (Django built-in)
│─────────────────────│
│ id (PK)             │
│ username            │
│ email               │
│ password            │
│ first_name          │
│ last_name           │
│ is_active           │
│ date_joined         │
└──────────┬──────────┘
           │
           │ creates
           ↓
┌─────────────────────┐
│  expense_groups     │
│─────────────────────│
│ id (PK)             │
│ name                │
│ description         │
│ created_by (FK) ────→ auth_user
│ created_at          │
│ updated_at          │
└──────────┬──────────┘
           │
           │ has many
           ↓
┌─────────────────────┐
│  group_members      │
│─────────────────────│
│ id (PK)             │
│ group_id (FK) ──────→ expense_groups
│ user_id (FK) ───────→ auth_user
│ date_joined         │ ⭐ Time-bounded
│ date_left (NULL)    │ ⭐ NULL = still active
└─────────────────────┘

┌─────────────────────┐
│     expenses        │
│─────────────────────│
│ id (PK)             │
│ group_id (FK) ──────→ expense_groups
│ paid_by (FK) ───────→ auth_user
│ date                │
│ description         │
│ amount_original     │ ⭐ Original amount
│ currency            │ ⭐ INR or USD
│ amount_inr          │ ⭐ Converted to INR
│ conversion_rate     │ ⭐ Rate used
│ split_type          │ ⭐ equal/percentage/exact/shares
│ is_settlement       │
│ notes               │
│ created_at          │
│ updated_at          │
└──────────┬──────────┘
           │
           │ has many
           ↓
┌─────────────────────┐
│  expense_splits     │
│─────────────────────│
│ id (PK)             │
│ expense_id (FK) ────→ expenses
│ user_id (FK) ───────→ auth_user
│ share_amount        │ ⭐ Always in INR
│ raw_value           │ ⭐ Original percentage/shares
└─────────────────────┘

┌─────────────────────┐
│    settlements      │
│─────────────────────│
│ id (PK)             │
│ group_id (FK) ──────→ expense_groups
│ paid_by (FK) ───────→ auth_user
│ paid_to (FK) ───────→ auth_user
│ amount              │
│ currency            │
│ amount_inr          │
│ date                │
│ note                │
│ created_at          │
└─────────────────────┘

┌─────────────────────┐
│  import_sessions    │
│─────────────────────│
│ id (PK)             │
│ group_id (FK) ──────→ expense_groups
│ uploaded_by (FK) ───→ auth_user
│ file_name           │
│ file                │ ⭐ Stored file
│ uploaded_at         │
│ status              │ ⭐ pending/reviewed/completed
│ total_rows          │
│ clean_rows          │
│ flagged_rows        │
│ imported_rows       │
│ skipped_rows        │
│ report_summary      │ ⭐ Markdown report
└──────────┬──────────┘
           │
           │ has many
           ↓
┌─────────────────────┐
│  import_anomalies   │
│─────────────────────│
│ id (PK)             │
│ session_id (FK) ────→ import_sessions
│ row_number          │
│ raw_row (JSON)      │ ⭐ Full original row
│ anomaly_type        │ ⭐ 15+ types
│ description         │
│ suggestion          │
│ resolution          │ ⭐ pending/approved/rejected
│ resolution_note     │
│ resolved_by (FK) ───→ auth_user
│ resolved_at         │
└─────────────────────┘
```

---

## 📐 **Schema Design Decisions**

### **1. Currency Handling**

**Design:**
- Store both `amount_original` and `amount_inr`
- Record `conversion_rate` used

**Rationale:**
- Audit trail for all conversions
- Historical accuracy (rates change)
- Can recalculate if needed
- Transparency for users

### **2. Time-Bounded Membership**

**Design:**
- `date_joined` (required)
- `date_left` (NULL = still active)

**Rationale:**
- Handles members joining/leaving mid-period
- Only splits expenses during active membership
- Accurate balance calculations
- Supports re-joining

### **3. Expense Splits Always in INR**

**Design:**
- `share_amount` always in INR
- Separate from original currency

**Rationale:**
- Consistent balance calculations
- No currency mixing in calculations
- Simplified aggregation queries
- Clear financial reporting

### **4. Anomaly Storage**

**Design:**
- Store full `raw_row` as JSON
- Separate resolution tracking
- Link to user who resolved

**Rationale:**
- Complete audit trail
- Can review decisions later
- Accountability
- Data forensics

### **5. Soft Deletes via date_left**

**Design:**
- Don't delete memberships
- Set `date_left` instead

**Rationale:**
- Historical data preserved
- Can see past members
- Audit trail intact
- Can re-add members

---

## 📊 **Key Metrics**

### **Tables:** 7 core tables
### **Anomaly Types:** 15+ detected
### **Currency Support:** 2 (INR, USD)
### **Split Types:** 4 (equal, percentage, exact, shares)
### **Resolution States:** 5 (pending, approved, modified, rejected, auto_fixed)

---

## 🔒 **Data Integrity**

### **Constraints:**

1. **Unique Together:**
   - `(group, user, date_joined)` in group_members

2. **Foreign Keys:**
   - All with CASCADE or SET_NULL
   - Referential integrity enforced

3. **Check Constraints:**
   - Amounts > 0 (enforced in application layer)
   - Valid dates (no future dates beyond threshold)

4. **Indexes:**
   - Primary keys (auto-indexed)
   - Foreign keys (auto-indexed)
   - Date fields for range queries

---

## 📝 **Import Report Generation**

### **Report includes:**

1. Total rows processed
2. Clean rows imported
3. Flagged rows (with reasons)
4. Rejected rows
5. Resolution summary
6. Timestamp and user

**Stored in:** `ImportSession.report_summary` (Markdown format)

---

**Last Updated:** June 15, 2026  
**Schema Version:** 1.0  
**Anomaly Types:** 15+
