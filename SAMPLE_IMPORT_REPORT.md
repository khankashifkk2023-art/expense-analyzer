# CSV Import Report — Sample

## Import Session #42

**Date:** June 15, 2026, 14:35 IST  
**Uploaded By:** afaque  
**Group:** Apartment 301 Flatmates  
**File:** `june_2026_expenses.csv`  
**Status:** ✅ Completed

---

## Summary

| Metric | Count |
|--------|-------|
| **Total Rows Processed** | 47 |
| **Clean Rows** | 38 |
| **Flagged Rows** | 9 |
| **Successfully Imported** | 41 |
| **Skipped Rows** | 6 |
| **Import Duration** | 12 seconds |

---

## Import Statistics

### ✅ Successfully Imported: 41 Expenses

- **Total Amount:** ₹87,450.00
- **Date Range:** June 1-14, 2026
- **Currency Breakdown:**
  - INR: 35 expenses (₹64,200)
  - USD: 6 expenses ($278 = ₹23,250 @ 83.5)
- **Split Types:**
  - Equal: 28 expenses
  - Percentage: 7 expenses
  - Exact: 4 expenses
  - Shares: 2 expenses

### ⚠️ Flagged Rows: 9 Issues Detected

Anomalies were detected and reviewed by user. See details below.

---

## Anomaly Details

### 🔴 Row 12: Duplicate Row
**Status:** ❌ Rejected  
**Resolved By:** afaque  
**Resolution Date:** June 15, 2026, 14:37 IST

**Original Data:**
```csv
2026-06-05,Groceries - Walmart,1500,INR,john,equal,,
```

**Issue:**
Duplicate of row 5. Same date, description, and amount.

**Suggestion:**
Skip this row or verify if it's a legitimate duplicate expense.

**User Decision:**
"This was a copy-paste error. Skipping."

**Action Taken:** Row skipped ✓

---

### 🟡 Row 18: Negative Amount
**Status:** ✅ Approved (Modified)  
**Resolved By:** afaque  
**Resolution Date:** June 15, 2026, 14:38 IST

**Original Data:**
```csv
2026-06-07,Electricity Bill Refund,-250,INR,jane,equal,,
```

**Issue:**
Amount is negative (₹-250). Possible refund or data entry error.

**Suggestion:**
Verify if this is a refund. If yes, consider recording as a settlement or positive adjustment.

**User Decision:**
"This was a refund from electricity department. Changed to +250 as settlement to Jane."

**Action Taken:** Recorded as settlement (Jane → Group, ₹250) ✓

---

### 🔴 Row 23: Currency Mismatch
**Status:** ❌ Rejected  
**Resolved By:** afaque  
**Resolution Date:** June 15, 2026, 14:39 IST

**Original Data:**
```csv
2026-06-09,Hotel Booking,500,EUR,bob,equal,,
```

**Issue:**
Unsupported currency: EUR. Only INR and USD are supported.

**Suggestion:**
Convert to INR or USD before importing.

**User Decision:**
"Will convert manually and re-add."

**Action Taken:** Row skipped, to be fixed in CSV ✓

---

### 🟠 Row 27: Post-Moveout Expense
**Status:** ✅ Approved  
**Resolved By:** afaque  
**Resolution Date:** June 15, 2026, 14:40 IST

**Original Data:**
```csv
2026-06-10,Water Bill,800,INR,john,equal,,
```

**Issue:**
Sam left the group on June 8, 2026, but this expense is dated June 10.

**Suggestion:**
Sam will be automatically excluded from this expense split.

**User Decision:**
"Correct, Sam shouldn't pay for this."

**Action Taken:** Imported with Sam excluded from split ✓

---

### 🟡 Row 31: Zero Amount
**Status:** ❌ Rejected  
**Resolved By:** afaque  
**Resolution Date:** June 15, 2026, 14:41 IST

**Original Data:**
```csv
2026-06-11,Test Entry,0,INR,alice,equal,,
```

**Issue:**
Amount is zero.

**Suggestion:**
Verify or skip this row.

**User Decision:**
"Test entry, can skip."

**Action Taken:** Row skipped ✓

---

### 🔴 Row 34: Unknown Member
**Status:** ❌ Rejected  
**Resolved By:** afaque  
**Resolution Date:** June 15, 2026, 14:42 IST

**Original Data:**
```csv
2026-06-12,Uber Ride,450,INR,mike,equal,,
```

**Issue:**
User "mike" not found in the system.

**Suggestion:**
Use an existing username or create this user first.

**User Decision:**
"This should be 'michael' (existing user). Will fix in CSV."

**Action Taken:** Row skipped, to be corrected ✓

---

### 🟢 Row 38: Percentage Sum ≠ 100%
**Status:** ✅ Approved  
**Resolved By:** afaque  
**Resolution Date:** June 15, 2026, 14:43 IST

**Original Data:**
```csv
2026-06-13,Dinner at Restaurant,3000,INR,john,percentage,"john_percentage=50,jane_percentage=30,bob_percentage=25",
```

**Issue:**
Percentage split sums to 105% (50 + 30 + 25 = 105).

**Suggestion:**
App will calculate splits proportionally based on provided percentages.

**User Decision:**
"That's fine, proportional split is okay."

**Action Taken:** 
- John: 50/105 × ₹3,000 = ₹1,428.57
- Jane: 30/105 × ₹3,000 = ₹857.14
- Bob: 25/105 × ₹3,000 = ₹714.29
✓ Imported

---

### 🟡 Row 42: Settlement Recorded as Expense
**Status:** ✅ Approved (Modified)  
**Resolved By:** afaque  
**Resolution Date:** June 15, 2026, 14:44 IST

**Original Data:**
```csv
2026-06-13,Bob paid back John,1500,INR,bob,exact,"john_amount=1500",
```

**Issue:**
Description suggests this is a settlement (direct payment) not an expense.

**Suggestion:**
Record this as a settlement instead of an expense.

**User Decision:**
"Yes, this is Bob settling his debt to John."

**Action Taken:** Recorded as settlement (Bob → John, ₹1,500) ✓

---

### 🟠 Row 45: Future-Dated Expense
**Status:** ✅ Approved  
**Resolved By:** afaque  
**Resolution Date:** June 15, 2026, 14:45 IST

**Original Data:**
```csv
2026-06-20,Rent (Advance),15000,INR,alice,equal,,
```

**Issue:**
Expense date (June 20) is in the future. Today is June 15, 2026.

**Suggestion:**
Verify date is correct. If this is a planned expense, import anyway.

**User Decision:**
"This is rent due on June 20, recording in advance."

**Action Taken:** Imported with future date ✓

---

## Resolution Summary

| Resolution | Count | Action |
|------------|-------|--------|
| ✅ **Approved** | 4 | Imported as-is or with modifications |
| ❌ **Rejected** | 5 | Skipped (duplicates, invalid data) |
| 🔧 **Auto-Fixed** | 0 | System auto-corrected with notification |

---

## Imported Expenses Breakdown

### By Date

| Date | Expenses | Total Amount (INR) |
|------|----------|-------------------|
| June 1 | 3 | ₹4,200 |
| June 2 | 5 | ₹8,150 |
| June 3 | 2 | ₹3,500 |
| June 4 | 4 | ₹6,800 |
| June 5 | 6 | ₹11,250 |
| June 6 | 3 | ₹5,400 |
| June 7 | 4 | ₹7,200 |
| June 8 | 2 | ₹9,500 |
| June 9 | 3 | ₹6,300 |
| June 10 | 4 | ₹8,900 |
| June 11 | 2 | ₹4,750 |
| June 12 | 1 | ₹2,500 |
| June 13 | 1 | ₹3,000 |
| June 14 | 1 | ₹6,000 |
| **Total** | **41** | **₹87,450** |

### By Member (Paid By)

| Member | Expenses Paid | Total Amount Paid (INR) |
|--------|---------------|------------------------|
| john | 12 | ₹28,400 |
| jane | 10 | ₹19,800 |
| alice | 9 | ₹21,250 |
| bob | 8 | ₹14,500 |
| sam | 2 | ₹3,500 (left June 8) |
| **Total** | **41** | **₹87,450** |

### By Split Type

| Split Type | Count | Total Amount (INR) | Avg Amount |
|------------|-------|-------------------|-----------|
| Equal | 28 | ₹64,200 | ₹2,293 |
| Percentage | 7 | ₹12,800 | ₹1,829 |
| Exact | 4 | ₹8,200 | ₹2,050 |
| Shares | 2 | ₹2,250 | ₹1,125 |
| **Total** | **41** | **₹87,450** | **₹2,133** |

### By Category (based on description)

| Category | Count | Amount (INR) |
|----------|-------|-------------|
| Groceries | 8 | ₹12,400 |
| Utilities (Electricity, Water, Internet) | 5 | ₹6,800 |
| Rent | 1 | ₹15,000 |
| Food & Dining | 12 | ₹18,300 |
| Transportation (Uber, Fuel) | 6 | ₹7,200 |
| Entertainment | 4 | ₹9,450 |
| Household Items | 3 | ₹5,600 |
| Healthcare | 2 | ₹12,700 |
| **Total** | **41** | **₹87,450** |

---

## Currency Conversions Applied

| Original Currency | Count | Total Original | Conversion Rate | Total INR |
|-------------------|-------|---------------|-----------------|-----------|
| USD | 6 | $278.00 | 83.50 | ₹23,213.00 |

**Conversion Audit Trail:**

1. **Row 8:** $45 → ₹3,757.50 @ 83.50 (Hotel booking)
2. **Row 14:** $82 → ₹6,847.00 @ 83.50 (Amazon purchase)
3. **Row 21:** $35 → ₹2,922.50 @ 83.50 (Uber ride from airport)
4. **Row 29:** $58 → ₹4,843.00 @ 83.50 (Online subscription)
5. **Row 36:** $38 → ₹3,173.00 @ 83.50 (App purchase)
6. **Row 41:** $20 → ₹1,670.00 @ 83.50 (Food delivery)

**Note:** Conversion rate sourced from settings.py (default rate). All conversions are permanently recorded for audit purposes.

---

## Settlements Created

During import, 2 rows were identified as settlements and recorded separately:

1. **Bob → John:** ₹1,500 (June 13, 2026)
   - Description: "Bob paid back John"
   - Reason: Detected as settlement based on description

2. **Electricity Refund → Jane:** ₹250 (June 7, 2026)
   - Description: "Electricity Bill Refund"
   - Reason: Negative amount converted to settlement

**Total Settlements:** ₹1,750

---

## Data Quality Notes

### ✅ Strengths:
- Consistent date format (YYYY-MM-DD)
- Clear expense descriptions
- Correct member usernames (except 1 typo)
- Proper currency codes (except 1 EUR entry)

### ⚠️ Issues Found:
- 1 duplicate row (manual error)
- 1 currency not supported (EUR)
- 1 unknown member (typo: "mike" instead of "michael")
- 2 entries should have been settlements
- 1 zero amount test entry
- 1 percentage split didn't sum to 100% (acceptable)
- 1 future-dated expense (intentional)

### 📋 Recommendations:
1. **Remove test entries** before final export
2. **Convert EUR expenses** to INR or USD before import
3. **Double-check usernames** against registered members
4. **Record settlements separately** in a different CSV or use settlement form
5. **Verify duplicate expenses** aren't copy-paste errors

---

## Impact on Group Balances

### Before Import:
| Member | Balance |
|--------|---------|
| john | +₹2,400 |
| jane | -₹800 |
| alice | +₹1,200 |
| bob | -₹2,100 |
| sam | -₹700 |

### After Import:
| Member | Balance |
|--------|---------|
| john | +₹8,350 (+₹5,950) |
| jane | +₹1,150 (+₹1,950) |
| alice | +₹5,200 (+₹4,000) |
| bob | -₹9,850 (-₹7,750) |
| sam | -₹700 (no change, left June 8) |

**Note:** Sam's balance unchanged because all imported expenses are dated after his move-out date (June 8).

---

## Settlement Suggestions (After Import)

To balance all accounts:

1. **Bob → Alice:** ₹5,200
2. **Bob → John:** ₹4,650

**Total Transactions:** 2  
**After settlements, all balances will be ₹0**

---

## Audit Trail

**Session Created:** June 15, 2026, 14:35:22 IST  
**Parsing Started:** June 15, 2026, 14:35:23 IST  
**Parsing Completed:** June 15, 2026, 14:35:28 IST (5 seconds)  
**Review Started:** June 15, 2026, 14:37:00 IST  
**Review Completed:** June 15, 2026, 14:45:15 IST (8 minutes 15 seconds)  
**Import Executed:** June 15, 2026, 14:45:16 IST  
**Import Completed:** June 15, 2026, 14:45:21 IST (5 seconds)  
**Report Generated:** June 15, 2026, 14:45:22 IST  
**Total Duration:** 12 seconds (excluding user review time)

---

## Actions Taken Log

| Time | Action | Details |
|------|--------|---------|
| 14:35:22 | Session Created | File uploaded: june_2026_expenses.csv (3.2 KB) |
| 14:35:28 | Parsing Complete | 47 rows processed, 9 anomalies detected |
| 14:37:14 | Row 12 Rejected | Duplicate row skipped by afaque |
| 14:38:05 | Row 18 Modified | Converted to settlement by afaque |
| 14:39:12 | Row 23 Rejected | Currency not supported (EUR) |
| 14:40:03 | Row 27 Approved | Sam excluded from split (post-moveout) |
| 14:41:11 | Row 31 Rejected | Zero amount test entry |
| 14:42:08 | Row 34 Rejected | Unknown member "mike" |
| 14:43:19 | Row 38 Approved | Proportional percentage split applied |
| 14:44:27 | Row 42 Modified | Converted to settlement by afaque |
| 14:45:09 | Row 45 Approved | Future-dated expense allowed |
| 14:45:16 | Import Started | 41 expenses + 2 settlements to import |
| 14:45:21 | Import Complete | 43 records successfully created |
| 14:45:22 | Report Generated | This report created and saved |

---

## Files Created

### Database Records:
- **41 Expense records** in `expenses` table
- **82 ExpenseSplit records** in `expense_splits` table (avg 2 splits per expense)
- **2 Settlement records** in `settlements` table
- **1 ImportSession record** in `import_sessions` table
- **9 ImportAnomaly records** in `import_anomalies` table

### Total Records Created: 135

---

## Technical Details

**Import Method:** CSV Bulk Import  
**Encoding:** UTF-8  
**Delimiter:** Comma (`,`)  
**Line Endings:** CRLF (Windows)  
**File Size:** 3.2 KB  
**Parser:** Python csv.DictReader  
**Validator:** Custom CSVImportService  
**Database Transactions:** Atomic (all-or-nothing per row)

---

## Next Steps

1. ✅ Import completed successfully
2. 🔄 Review updated balances in balance view
3. 📊 Check suggested settlements
4. 🔍 Verify specific expenses if needed (use detail view)
5. 📝 Fix rejected rows in CSV and re-import if needed
6. 💰 Process settlements between members

---

## Support

If you have questions about this import:
- View full expense list: `/groups/7/expenses/`
- View balances: `/groups/7/balances/`
- View anomaly details: `/imports/42/review/`
- Contact admin: afaque@example.com

---

**Report Generated:** June 15, 2026, 14:45:22 IST  
**Import Session ID:** 42  
**Report Version:** 1.0  
**Format:** Markdown

---

✅ **Import Completed Successfully**

