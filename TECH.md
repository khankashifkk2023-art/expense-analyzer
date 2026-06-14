# SplitLedger — Technology Stack

## Backend

### Framework & Language
- **Python 3.x** — Primary programming language
- **Django 6.0** — High-level web framework
  - MVT (Model-View-Template) architecture
  - Built-in ORM for database abstraction
  - Admin interface for data management
  - Form handling and validation
  - User authentication system

### Database
- **MySQL** — Relational database management system
- **mysqlclient 2.2+** — Python MySQL database connector
- Connection pooling enabled (CONN_MAX_AGE: 600s)
- Strict transaction mode for data integrity

### Configuration & Environment
- **python-dotenv 1.0+** — Environment variable management
- Secrets stored in `.env` file (not committed to version control)
- Configuration for database, debug mode, secret key, and API rates

## Frontend

### Styling & Design
- **Pure CSS3** — No CSS frameworks or preprocessors
- **CSS Custom Properties (Variables)** — Consistent theming
- **Glassmorphism design pattern** — Modern UI with backdrop filters
- **Mobile-first responsive design** — Flexbox and CSS Grid
- **Dark theme** — Deep space color palette with vibrant accents

### Typography
- **Inter font family** — Google Fonts
- Variable weights (300, 400, 500, 600, 700)
- Optimized for screen readability

### JavaScript
- **Vanilla JavaScript (ES6+)** — No frameworks
- DOM manipulation for:
  - Mobile navigation toggle
  - Flash message auto-dismiss
  - Form validation and formatting
  - Delete confirmations

### UI Components
- Custom-built components:
  - Glassmorphic cards
  - Form inputs with focus states
  - Tables with hover effects
  - Badges and status indicators
  - Flash messages with animations
  - Empty states

## Design System

### Color Palette
| Purpose | Color | Hex Code |
|---------|-------|----------|
| Background | Deep Space | `#0a0a1a` → `#12122a` |
| Primary | Indigo | `#6c63ff` |
| Success | Mint | `#00d4aa` |
| Danger | Coral | `#ff6b6b` |
| Warning | Amber | `#ffd93d` |
| Info | Sky Blue | `#4da6ff` |
| Text Primary | Light Gray | `#e8e8f0` |
| Text Secondary | Medium Gray | `#8888a0` |

### Animation & Transitions
- CSS animations (slideIn, fadeOut, fadeIn, pulse)
- Staggered card entrance animations
- Micro-interactions on hover/focus
- 150ms (fast), 250ms (base), 400ms (slow) transition speeds

## Development & Deployment

### Package Management
- **pip** — Python package installer
- `requirements.txt` for dependency tracking

### Development Tools
- Django development server (`python manage.py runserver`)
- Django management commands for:
  - Database migrations
  - Static file collection
  - Admin user creation
  - Custom commands

### File Structure
```
splitledger/
├── splitledger/          # Main project configuration
│   ├── settings.py       # Project settings
│   ├── urls.py           # Root URL configuration
│   ├── wsgi.py           # WSGI application entry
│   └── asgi.py           # ASGI application entry (async)
├── core/                 # Main application
│   ├── models.py         # Database models
│   ├── views/            # View functions/classes
│   ├── forms.py          # Django forms
│   ├── urls.py           # App URL routing
│   ├── admin.py          # Admin configurations
│   ├── services/         # Business logic
│   ├── templatetags/     # Custom template filters
│   └── migrations/       # Database migrations
├── templates/            # HTML templates
├── static/               # Static assets (CSS, JS)
├── media/                # User uploads (CSV files)
├── manage.py             # Django CLI entry point
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables (not committed)
```

## Features & Capabilities

### Core Functionality
1. **Multi-currency support** — INR (primary), USD with conversion
2. **Flexible expense splitting** — Equal, exact amounts, percentage, shares/ratio
3. **Time-bounded memberships** — Track when members join/leave
4. **Balance calculations** — Real-time debt tracking between members
5. **Settlement tracking** — Record direct payments separately from expenses
6. **CSV import** — Bulk expense import with anomaly detection
7. **Audit trail** — Full history of conversions, splits, and imports

### Split Types
- **Equal**: Divide evenly among active members
- **Exact**: Specify exact amount per person
- **Percentage**: Split by percentage (must sum to 100%)
- **Shares/Ratio**: Weight-based distribution

### CSV Import Anomaly Detection
Detects 15+ types of issues:
- Duplicate rows
- Settlements recorded as expenses
- Negative/zero amounts
- Currency mismatches
- Post-moveout expenses
- Missing fields
- Name inconsistencies
- Split sum validation errors
- Unknown members
- Future-dated expenses
- Ambiguous date formats
- Format errors
- And more...

## Security

### Best Practices
- **CSRF protection** — Built-in Django middleware
- **SQL injection prevention** — ORM parameterized queries
- **Password hashing** — Django's built-in password validators
- **Environment variables** — Secrets not hardcoded
- **Secure cookies** — Session management
- **XSS protection** — Django template auto-escaping

### Authentication
- Django's built-in authentication system
- User registration with validation
- Login/logout with session management
- Password reset capability (configurable)

## Browser Support

### Modern Browsers
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

### Progressive Enhancement
- Core functionality works without JavaScript
- JavaScript enhances UX with:
  - Mobile navigation
  - Auto-dismiss messages
  - Form helpers

## API Integrations

### Currency Conversion (Planned)
- **Frankfurter API** — Free currency exchange rates
- Fallback to configured rate in `.env`
- Historical rate tracking for audit purposes

## Performance Optimizations

- **Database connection pooling** — Reuse connections for 10 minutes
- **Static file serving** — Separate URL namespace
- **CSS custom properties** — Reduced CSS file size
- **No external dependencies** — Faster page loads (except Google Fonts)
- **Efficient queries** — ORM optimizations with select_related/prefetch_related

## Accessibility

- **Semantic HTML5** — Proper heading hierarchy
- **ARIA labels** — For interactive elements
- **Keyboard navigation** — All features accessible via keyboard
- **Color contrast** — WCAG AA compliant (dark theme)
- **Screen reader friendly** — Descriptive labels and hints
- **Focus indicators** — Clear visual feedback

## Future Enhancements

### Potential Stack Additions
- **Redis** — Caching and session storage
- **Celery** — Background task processing (email, imports)
- **PostgreSQL** — Alternative database option
- **Docker** — Containerization for deployment
- **nginx** — Production web server
- **gunicorn** — WSGI HTTP server
- **React/Vue** — Optional SPA frontend
- **REST API** — Django REST Framework for mobile apps
- **WebSockets** — Real-time balance updates

---

**Last Updated**: June 14, 2026  
**Framework Version**: Django 6.0  
**Python Version**: 3.10+
