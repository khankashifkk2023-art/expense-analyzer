# DECISIONS.md — Design Decisions Log

## Project: SplitLedger
**Developer:** Afaque HK  
**Repository:** https://github.com/afaquehk/expense-analyzer  
**Date:** June 14-15, 2026

---

## Decision Log

This document records every significant design decision, the alternatives considered, and the rationale behind the final choice.

---

## 1. Framework Choice: Django 6.0

### Options Considered:
1. **Django 6.0** (MVT framework)
2. **Flask** (Microframework)
3. **FastAPI** (Modern async framework)
4. **Express.js + Node.js** (JavaScript backend)

### Decision: Django 6.0

### Rationale:
- **Built-in admin interface** — Essential for quick data management during development and debugging
- **Mature ORM** — Complex balance calculations require reliable database abstraction
- **Authentication system** — User management out-of-the-box saves significant development time
- **Form handling** — 8+ forms needed (expense, split, group, member, settlement, CSV import)
- **Template engine** — Server-side rendering fits project scope better than SPA
- **Migration system** — Safe database schema evolution
- **Security by default** — CSRF, XSS, SQL injection protection built-in
- **Proven stability** — Battle-tested framework for production use

### Why NOT Flask:
- Would require adding libraries for authentication, forms, admin, migrations
- More boilerplate code for features Django provides

### Why NOT FastAPI:
- Async capabilities not needed for this use case
- Smaller ecosystem compared to Django
- Less mature admin tools

### Why NOT Express.js:
- Python ecosystem better for data processing (Decimal handling, CSV parsing)
- Django's ORM more mature than Node.js ORMs (Sequelize, TypeORM)

---

## 2. Database: MySQL

### Options Considered:
1. **MySQL** (Relational database)
2. **PostgreSQL** (Advanced relational database)
3. **SQLite** (File-based database)
4. **MongoDB** (NoSQL document database)

### Decision: MySQL

### Rationale:
- **Free hosting on PythonAnywhere** — MySQL included in free tier
- **ACID compliance** — Financial data requires transaction safety
- **Wide availability** — Supported by almost all hosting providers
- **Adequate for project scale** — Handles thousands of expenses efficiently
- **Developer familiarity** — Widely used, extensive documentation
- **mysqlclient support** — Mature Django adapter

### Why NOT PostgreSQL:
- Not available on PythonAnywhere free tier
- Advanced features (JSONB, full-text search, arrays) not needed for this project
- Would increase deployment complexity

### Why NOT SQLite:
- Not suitable for production (file locking issues with concurrent writes)
- Limited for multi-user applications
- Good for development only

### Why NOT MongoDB:
- Financial data fits relational model perfectly
- No need for schema flexibility
- Django ORM optimized for SQL databases
- Complex join queries needed for balance calculations

---

## 3. Split Type Implementation: 4 Distinct Types

### Options Considered:
1. **Equal split only** (Simplest)
2. **Equal + percentage** (Most common patterns)
3. **Equal + percentage + exact + shares** (Full flexibility) ✓
4. **Custom formula engine** (Maximum flexibility but complex)

### Decision: 4 Split Types (Equal, Percentage, Exact, Shares)

### Rationale:
- **User requirements** — CSV data contained all 4 types
- **Real-world scenarios:**
  - **Equal**: Groceries, utilities split evenly
  - **Percentage**: Income-based splitting (60%-40%)
  - **Exact**: Custom amounts per person (John ₹500, Jane ₹300)
  - **Shares**: Ratio-based (2:1:1 for couples + singles)
- **CSV compatibility** — Support existing user data without transformation
- **No over-engineering** — 4 types cover 99% of use cases without formula complexity

### Why NOT equal split only:
- Insufficient for real-world expense sharing scenarios
- Users specifically requested flexible splitting

### Why NOT custom formula engine:
- Over-engineered for current needs
- Difficult to validate and debug
- Poor UX (non-technical users can't write formulas)
- Can add later if needed

---

## 4. Balance Calculation Algorithm: Greedy Settlement Matching

### Options Considered:
1. **Everyone pays everyone** (Highest transaction count)
2. **Greedy matching: highest creditor ↔ highest debtor** ✓
3. **Min-cost max-flow algorithm** (Optimal but complex)
4. **Round-robin settlement** (Fair but inefficient)

### Decision: Greedy Matching Algorithm

### Algorithm:
```python
while creditors and debtors:
    match highest creditor with highest debtor
    settle min(credit, debt)
    remove/update balances
```

### Rationale:
- **Aisha's requirement:** "I just want one number per person. Who pays whom, how much, done."
- **Near-optimal** — Usually produces minimum or near-minimum transaction count
- **Simple to understand** — Users can verify the logic easily
- **Fast computation** — O(n log n) with sorting
- **Good enough** — For groups of 3-10 people, difference from optimal is negligible

### Example:
```
Alice: +₹1,000 (owed)
Bob: -₹600 (owes)
Charlie: -₹400 (owes)

Result: Bob → Alice ₹600, Charlie → Alice ₹400 (2 transactions)
```

### Why NOT min-cost max-flow:
- Requires graph algorithms library
- Overkill for small groups (3-10 members)
- Greedy solution is 95% optimal in practice
- Harder to explain to users

### Why NOT everyone pays everyone:
- Creates too many small transactions
- Example: 5 people = up to 20 transactions
- Violates Aisha's "one number per person" requirement

---

## 5. Currency Conversion: Dual Storage with Audit Trail

### Options Considered:
1. **Store only INR** (Single currency, convert on input)
2. **Store original + INR with conversion rate** ✓
3. **Store original only** (Convert on read)
4. **Multi-currency balances** (Complex)

### Decision: Store Original + INR + Conversion Rate

### Schema:
```python
amount_original = Decimal  # E.g., $100
currency = 'USD'           # Original currency
amount_inr = Decimal       # ₹8,350
conversion_rate = Decimal  # 83.50
```

### Rationale:
- **Priya's requirement:** "Half the trip was in dollars. The sheet pretends a dollar is a rupee. That can't be right."
- **Audit trail** — Can see exactly what rate was used historically
- **No recalculation surprises** — Historical expenses don't change when rates fluctuate
- **Transparency** — Users can verify conversions
- **Consistent balance calculations** — All balances always in INR (no currency mixing)
- **Forensic capability** — Can trace data errors back to source

### Why NOT store only INR:
- Loses original transaction data
- Cannot verify if conversion was correct
- Cannot recalculate if rate was wrong

### Why NOT convert on read:
- Balance calculations would be inconsistent over time
- Performance hit (recalculating every query)
- Race conditions with rate changes mid-calculation

### Why NOT multi-currency balances:
- Too complex for project scope
- Users want final balances in one currency (INR)
- Would require complex settlement logic

---

## 6. Time-Bounded Membership: date_joined + date_left

### Options Considered:
1. **Simple membership flag** (active/inactive)
2. **date_joined + date_left with NULL for active** ✓
3. **Separate history table** (Over-normalized)
4. **Event log approach** (Complex)

### Decision: date_joined + date_left (NULL = still active)

### Schema:
```python
class GroupMembership:
    date_joined = DateField()
    date_left = DateField(null=True)  # NULL = active
```

### Rationale:
- **Sam's requirement:** "I moved in mid-April. Why would March electricity affect my balance?"
- **Expense filtering:**
  ```python
  if expense.date >= membership.date_joined:
      if not membership.date_left or expense.date <= membership.date_left:
          include_in_split()
  ```
- **Re-joining supported** — Can have multiple membership rows for same user
- **Historical accuracy** — Past expenses always calculate correctly
- **Query simplicity** — Single table with clear semantics

### Example:
```
Sam joins: April 10, 2026
March 15 expense → Sam NOT included
April 20 expense → Sam included
Sam leaves: June 1
June 10 expense → Sam NOT included
```

### Why NOT simple flag:
- No history of when member was active
- Cannot correctly calculate past balances
- Cannot handle re-joining

### Why NOT separate history table:
- Over-engineering for this use case
- More complex queries
- Two tables to maintain

---

## 7. CSV Import Workflow: Review Before Commit

### Options Considered:
1. **Auto-import everything** (Fast but risky)
2. **Reject any row with issues** (Safe but strict)
3. **Preview → Review → Approve** ✓
4. **Smart auto-fix with notification** (Complex)

### Decision: Preview → Review Anomalies → User Decides

### Workflow:
```
Upload CSV
    ↓
Parse & detect 15+ anomaly types
    ↓
Show review screen with all flagged rows
    ↓
User decides per row: approve/modify/reject
    ↓
Import clean + approved rows
    ↓
Generate import report
```

### Rationale:
- **Meera's requirement:** "Clean up the duplicates — but I want to approve anything the app deletes or changes."
- **No surprises** — User sees exactly what will be imported
- **Data safety** — Nothing deleted/modified without explicit approval
- **Educational** — Users learn about data quality issues
- **Audit trail** — Every decision recorded in ImportAnomaly table
- **Transparency** — Shows reason + suggestion for each anomaly

### Why NOT auto-import:
- Risk of importing duplicate/incorrect data
- No way to catch errors before they affect balances
- Violates Meera's requirement

### Why NOT auto-reject:
- Too strict (legitimate duplicates exist, e.g., monthly rent)
- Forces users to fix CSV manually and re-upload
- Poor UX for large files with minor issues

---

## 8. UI Framework: Pure CSS (No Framework)

### Options Considered:
1. **Pure CSS3 with custom design** ✓
2. **Bootstrap** (Most popular framework)
3. **Tailwind CSS** (Utility-first framework)
4. **Material-UI** (React component library)

### Decision: Pure CSS3 with Glassmorphism Design

### Rationale:
- **No external dependencies** — Faster page loads, no build step
- **Full design control** — Unique visual identity
- **Learning opportunity** — Master CSS fundamentals
- **Lightweight** — Single CSS file (~8KB)
- **Modern techniques:**
  - CSS custom properties for theming
  - Flexbox and Grid for layout
  - Backdrop filters for glassmorphism
  - CSS animations for micro-interactions
- **Mobile-first responsive** — Works on all devices

### Why NOT Bootstrap:
- Generic look (thousands of sites look identical)
- Bloated (includes components we don't need)
- Hard to customize without overriding
- ~150KB CSS file

### Why NOT Tailwind:
- Requires build step (PostCSS, purging)
- Utility classes clutter HTML
- Harder to maintain consistent design system
- Learning curve for team members

### Why NOT Material-UI:
- Requires React (too heavy for this project)
- Opinionated design (Google's Material Design)
- Large bundle size

---

## 9. Deployment Platform: PythonAnywhere

### Options Considered:
1. **PythonAnywhere** ✓
2. **Heroku**
3. **Vercel**
4. **DigitalOcean / AWS**
5. **Railway**

### Decision: PythonAnywhere

### Rationale:
- **Free tier includes:**
  - Python web app hosting
  - MySQL database (1GB)
  - 512MB storage
  - HTTPS included
- **Django-optimized** — Pre-configured WSGI setup
- **No credit card required** — True free tier
- **Simple deployment** — No Docker or complex configs
- **Beginner-friendly** — Web-based console and file manager
- **Good for learning** — Clear documentation

### Why NOT Heroku:
- Free tier discontinued (paid plans only now)
- Requires credit card even for trial
- Ephemeral filesystem (media files need S3)

### Why NOT Vercel:
- Optimized for Next.js / serverless functions
- **Incompatible with Django** — Django needs persistent process
- Would require splitting into API + frontend

### Why NOT DigitalOcean/AWS:
- Requires server management (VPS setup, nginx, security patches)
- Paid only (no free tier for compute)
- Overkill for a learning project

### Why NOT Railway:
- Requires GitHub OAuth
- Free tier limited (500 hours/month)
- Newer platform (less stable)

---

## 10. JavaScript Approach: Vanilla JS (No Framework)

### Options Considered:
1. **Vanilla JavaScript ES6+** ✓
2. **jQuery**
3. **React**
4. **Vue.js**
5. **Alpine.js**

### Decision: Vanilla JavaScript

### Rationale:
- **Minimal needs** — Only need:
  - Mobile nav toggle
  - Flash message auto-dismiss
  - Delete confirmations
  - Form helpers
- **No build step** — Write JS, refresh browser
- **Fast page loads** — No framework overhead
- **Modern browser APIs** — querySelector, fetch, classList
- **Progressive enhancement** — Site works without JS

### Use Cases:
```javascript
// Mobile nav toggle
document.querySelector('.mobile-toggle').addEventListener('click', ...)

// Auto-dismiss messages
setTimeout(() => message.classList.add('fade-out'), 5000)

// Delete confirmation
button.addEventListener('click', (e) => {
    if (!confirm('Are you sure?')) e.preventDefault()
})
```

### Why NOT jQuery:
- No longer needed (modern browsers have native APIs)
- Adds 30KB for features we don't need
- Outdated approach

### Why NOT React:
- Massive overkill for simple interactions
- Requires build tooling (Webpack, Babel)
- Would force SPA architecture
- ~40KB+ bundle size

### Why NOT Vue:
- Still too heavy for this project's needs
- Would require rearchitecting frontend
- No need for reactive components

### Why NOT Alpine.js:
- Only needed if we had complex state management
- Current needs are too simple to justify

---

## 11. Authentication: Django's Built-in System

### Options Considered:
1. **Django's built-in authentication** ✓
2. **django-allauth** (Social auth)
3. **Auth0** (Third-party service)
4. **Custom JWT system**

### Decision: Django's Built-in Authentication

### Rationale:
- **Sufficient for needs:**
  - User registration
  - Login/logout
  - Password hashing (PBKDF2)
  - Session management
- **No external dependencies** — Works out of box
- **Battle-tested** — Used by thousands of production sites
- **Secure by default** — CSRF protection, secure cookies
- **Easy to customize** — Can add social auth later if needed

### Why NOT django-allauth:
- Don't need social login (Google, Facebook) for v1
- Adds complexity
- Can add later if users request it

### Why NOT Auth0:
- External dependency (internet required)
- Overkill for simple project
- Free tier has limits

### Why NOT custom JWT:
- Unnecessary complexity
- Would need to implement refresh tokens
- Session-based auth sufficient for web app

---

## 12. Balance Display: Detailed Breakdown Option

### Options Considered:
1. **Only summary balance** (Simple but opaque)
2. **Summary + detailed breakdown on click** ✓
3. **Always show full breakdown** (Overwhelming)

### Decision: Summary + Drill-down Detail View

### Implementation:
- **Balance view**: Shows net balance per person with settlement suggestions
- **Detail view**: Click user → see:
  - All expenses paid
  - All expenses owed (with splits)
  - All settlements
  - Running balance calculation

### Rationale:
- **Rohan's requirement:** "No magic numbers. If the app says I owe ₹2,300, I want to see exactly which expenses make that up."
- **Progressive disclosure** — Simple view by default, details on demand
- **Transparency** — Users can audit every calculation
- **Trust building** — Shows app logic is correct
- **Debugging** — Helps identify data errors

### Why NOT summary only:
- Users don't trust "black box" calculations
- Can't verify if balance is correct
- Violates Rohan's requirement

### Why NOT always show everything:
- Information overload
- Most users just want "who owes whom"
- Slows down quick checks

---

## 13. Anomaly Storage: Separate Table with JSON

### Options Considered:
1. **Store anomalies in separate table with raw_row as JSON** ✓
2. **Log file approach**
3. **Don't store anomalies** (Only show on screen)
4. **Normalized tables for each anomaly type**

### Decision: ImportAnomaly table with JSONField

### Schema:
```python
class ImportAnomaly:
    session = ForeignKey(ImportSession)
    row_number = int
    raw_row = JSONField  # Full original CSV row
    anomaly_type = str   # 15+ types
    description = text
    suggestion = text
    resolution = str     # pending/approved/rejected
    resolved_by = ForeignKey(User)
    resolved_at = datetime
```

### Rationale:
- **Complete audit trail** — Can review decisions months later
- **JSON flexibility** — CSV columns vary, JSON handles any structure
- **Accountability** — Tracks who approved/rejected what
- **Data forensics** — Can investigate balance discrepancies
- **Learning** — Review past import issues to improve data quality

### Why NOT log files:
- Not queryable (can't filter, sort, analyze)
- No structured data
- Can't tie to specific import session

### Why NOT in-memory only:
- Lost after import completes
- Can't review decisions later
- No audit trail

### Why NOT normalized tables:
- 15+ anomaly types → 15 tables? Too many
- CSV columns dynamic (can't predict schema)
- JSON is perfect for semi-structured data

---

## Summary of Key Decisions

| Decision | Choice | Main Reason |
|----------|--------|-------------|
| Framework | Django 6.0 | Built-in admin, ORM, auth, forms |
| Database | MySQL | Free on PythonAnywhere, adequate for scale |
| Split Types | 4 types | Covers real-world scenarios |
| Balance Algorithm | Greedy matching | Near-optimal, simple to understand |
| Currency | Dual storage | Audit trail, no recalculation surprises |
| Membership | Time-bounded | Sam's requirement, historical accuracy |
| Import Workflow | Review before commit | Meera's requirement, data safety |
| UI | Pure CSS | No dependencies, full control |
| Deployment | PythonAnywhere | Free tier, Django-optimized |
| JavaScript | Vanilla JS | Minimal needs, no framework overhead |
| Authentication | Django built-in | Sufficient, secure by default |
| Balance Display | Summary + detail | Rohan's requirement, transparency |
| Anomaly Storage | Separate table + JSON | Audit trail, forensics |

---

## Trade-offs Accepted

### Performance vs. Audit Trail
- **Trade-off:** Storing original currency + INR requires more database space
- **Accepted because:** Audit trail more important than saving a few MB
- **Mitigation:** Archive old imports after 1 year if needed

### UX vs. Data Safety
- **Trade-off:** CSV review step adds friction
- **Accepted because:** Meera's requirement, prevents costly mistakes
- **Mitigation:** Make review interface fast and clear

### Simplicity vs. Optimality
- **Trade-off:** Greedy settlement algorithm not always optimal
- **Accepted because:** Difference negligible for small groups (< 10 people)
- **Mitigation:** Can upgrade to min-cost max-flow if needed

### Flexibility vs. Complexity
- **Trade-off:** 4 split types instead of formula engine
- **Accepted because:** Covers 99% of use cases without complexity
- **Mitigation:** Can add custom formulas in v2 if requested

---

**Last Updated:** June 15, 2026  
**Total Decisions Logged:** 13  
**Status:** All major architectural decisions documented
