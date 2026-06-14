# CSV Import Guide — All Split Types

Complete guide for importing expenses with different split types.

---

## 📋 Basic Format (All Split Types)

**Required columns:**
- `date` — YYYY-MM-DD format (e.g., 2026-06-01)
- `description` — Expense description
- `amount` — Decimal number (e.g., 1500.00)
- `currency` — INR or USD
- `paid_by` — Username of who paid
- `split_type` — equal, percentage, exact, or shares

**Optional columns:**
- `notes` — Additional notes about the expense

---

## 1️⃣ **Equal Split** (Default)

### Format:
```csv
date,description,amount,currency,paid_by,split_type,notes
2026-06-01,Groceries,1500.00,INR,john,equal,Weekly shopping
2026-06-02,Electricity,850.00,INR,jane,equal,May bill
```

### What happens:
- Splits equally among **all active members** in the group
- No additional columns needed
- Example: ₹1,500 ÷ 3 members = ₹500 each

### When to use:
- Shared expenses (utilities, groceries, rent)
- Fair split among all members
- Simplest format

---

## 2️⃣ **Percentage Split**

### Format:
```csv
date,description,amount,currency,paid_by,split_type,john_percentage,jane_percentage,mike_percentage,notes
2026-06-01,Rent,30000.00,INR,john,percentage,40,30,30,John has bigger room
2026-06-05,Dinner,2400.00,INR,jane,percentage,50,30,20,John ate more
```

### Required additional columns:
- `{username}_percentage` for each member
- Values should be numbers (e.g., 40 for 40%)
- **Should sum to 100%** (app will calculate regardless)

### What happens:
- Each person pays their specified percentage
- Example: ₹30,000 → John 40% = ₹12,000, Jane 30% = ₹9,000, Mike 30% = ₹9,000

### When to use:
- Rent (based on room size)
- Utilities (based on usage)
- Any expense with known percentage splits

---

## 3️⃣ **Exact Amount Split**

### Format:
```csv
date,description,amount,currency,paid_by,split_type,john_amount,jane_amount,mike_amount,notes
2026-06-01,Restaurant,2500.00,INR,john,exact,1200.00,800.00,500.00,Based on orders
2026-06-05,Shopping,3000.00,INR,jane,exact,1000.00,1500.00,500.00,Personal items
```

### Required additional columns:
- `{username}_amount` for each member
- Values should be decimal numbers
- **Should sum to total amount** (app will accept any amounts)

### What happens:
- Each person pays exactly the specified amount
- Example: Restaurant ₹2,500 → John ₹1,200, Jane ₹800, Mike ₹500

### When to use:
- Restaurant bills (everyone ordered different items)
- Shopping with personal items mixed in
- Any expense where exact amounts are known

---

## 4️⃣ **Shares/Ratio Split**

### Format:
```csv
date,description,amount,currency,paid_by,split_type,john_shares,jane_shares,mike_shares,notes
2026-06-01,Hotel,6000.00,INR,john,shares,2,1,1,John + partner vs singles
2026-06-05,Storage,3000.00,INR,jane,shares,2,1,2,Based on space used
```

### Required additional columns:
- `{username}_shares` for each member
- Values should be numbers (can be whole or decimal)
- Total shares calculated automatically

### What happens:
- Amount divided by total shares, then multiplied by each person's shares
- Example: Hotel ₹6,000 with shares 2:1:1 (4 total)
  - John: 2/4 = ₹3,000
  - Jane: 1/4 = ₹1,500
  - Mike: 1/4 = ₹1,500

### When to use:
- Hotel rooms (couples vs singles)
- Storage space (based on volume used)
- Any ratio-based split

---

## 🎯 Complete Examples

### Example 1: Mixed Split Types
```csv
date,description,amount,currency,paid_by,split_type,john_percentage,jane_percentage,notes
2026-06-01,Groceries,1500.00,INR,john,equal,,,"Split equally"
2026-06-02,Rent,30000.00,INR,jane,percentage,40,60,"Jane has larger room"
```

### Example 2: With USD Currency
```csv
date,description,amount,currency,paid_by,split_type,john_amount,jane_amount,notes
2026-06-10,Online Shopping,100.00,USD,john,exact,60.00,40.00,"Amazon order"
```
*Automatically converts to INR using the rate in .env*

### Example 3: Only Two Members in Split
```csv
date,description,amount,currency,paid_by,split_type,john_shares,jane_shares,notes
2026-06-15,Couple Dinner,2000.00,INR,john,shares,1,1,"Just us two"
```
*Mike not included in this expense*

---

## 🔍 Important Rules

### For All Split Types:
1. **Usernames must match exactly** (case-sensitive)
2. **Users must be active members** of the group
3. **Date format:** YYYY-MM-DD only
4. **Amount format:** Use decimal (e.g., 1500.00 not 1,500)
5. **Currency:** INR or USD only

### Split Type Specific:

**Percentage:**
- Values are interpreted as percentages (40 = 40%)
- Doesn't need to sum to 100% (app calculates proportionally)
- Can have decimals (33.33)

**Exact:**
- Values are interpreted as INR amounts
- Should ideally sum to total amount
- Can be different from total (app accepts any)

**Shares:**
- Values are ratios (2:1:1 means 2, 1, 1)
- Total calculated automatically
- Can use any numbers (1, 2, 3 or 0.5, 1.5, 2.5)

---

## 📁 Sample Files Included

1. **`sample_import.csv`** — Equal split examples
2. **`sample_import_percentage.csv`** — Percentage split examples
3. **`sample_import_exact.csv`** — Exact amount split examples
4. **`sample_import_shares.csv`** — Share/ratio split examples

Try importing these to see how each split type works!

---

## 🚨 Fallback Behavior

If split columns are missing or invalid:
- **Percentage split** → Falls back to equal split
- **Exact split** → Falls back to equal split
- **Shares split** → Falls back to equal split

This ensures imports don't fail due to missing split data.

---

## ✅ Import Workflow

1. **Prepare CSV** with one of the formats above
2. **Go to group** → Click "Import CSV"
3. **Upload file** — System validates and detects anomalies
4. **Review flagged issues** — Fix data errors if any
5. **Import clean rows** — Expenses created with proper splits
6. **Check balances** — Verify splits calculated correctly

---

## 💡 Pro Tips

### Tip 1: Start Simple
Begin with equal splits to test the import, then try advanced types.

### Tip 2: Match Column Names
Column names for splits MUST match usernames exactly:
- ✅ `john_percentage` (if user is "john")
- ❌ `John_percentage` (wrong case)

### Tip 3: Test with Small Files
Import 2-3 expenses first to verify format before bulk import.

### Tip 4: Check Active Members
Only active members (not left the group) will appear in splits.

### Tip 5: Mix Split Types
You can have different split types in the same CSV file!

---

## 🐛 Troubleshooting

### "Unknown member" error:
- User doesn't exist or username misspelled
- Solution: Register user first or fix username

### Splits not showing correctly:
- Check column names match usernames exactly
- Verify split_type is spelled correctly
- Try with equal split first to test

### Amount doesn't match:
- For exact splits, sum of amounts should match total
- App will accept any amounts but may show discrepancies

### Missing split columns:
- Falls back to equal split automatically
- No error, but splits may not be as expected

---

## 📞 Need Help?

- Check `README.md` for general CSV import info
- Check `QUICK_REFERENCE.md` for quick commands
- Verify your CSV format matches examples above

---

**Last Updated:** June 14, 2026  
**Supported Split Types:** equal, percentage, exact, shares  
**CSV Encoding:** UTF-8
