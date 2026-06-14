/**
 * SplitLedger — Main JavaScript
 *
 * Shared utilities: mobile nav toggle, flash message auto-dismiss,
 * confirmation modals, and form helpers.
 *
 * No frameworks — plain vanilla JS.
 */

document.addEventListener('DOMContentLoaded', function () {

    // ── Mobile Nav Toggle ────────────────────────────────────────────
    const navToggle = document.getElementById('nav-toggle');
    const navbar = document.getElementById('main-nav');

    if (navToggle && navbar) {
        navToggle.addEventListener('click', function () {
            navbar.classList.toggle('nav-open');
        });

        // Close mobile nav when clicking outside
        document.addEventListener('click', function (e) {
            if (!navbar.contains(e.target)) {
                navbar.classList.remove('nav-open');
            }
        });
    }


    // ── Flash Message Auto-Dismiss ───────────────────────────────────
    // Messages auto-fade via CSS animation after 4s.
    // This removes them from the DOM after the animation completes
    // so they don't block clicks.
    const messages = document.querySelectorAll('.message');
    messages.forEach(function (msg) {
        setTimeout(function () {
            if (msg.parentElement) {
                msg.remove();
            }
        }, 5000); // 4s visible + 0.4s fade + buffer
    });


    // ── Confirm Delete ───────────────────────────────────────────────
    // Add data-confirm="Are you sure?" to any form/link for a
    // confirmation dialog before submission.
    document.querySelectorAll('[data-confirm]').forEach(function (el) {
        el.addEventListener('click', function (e) {
            if (!confirm(el.dataset.confirm)) {
                e.preventDefault();
                e.stopPropagation();
            }
        });
    });


    // ── Form: Auto-format Currency Inputs ─────────────────────────────
    // Strips non-numeric chars (except . and -) from amount fields
    // on blur, so pasted values like "1,200" or "₹500" get cleaned.
    document.querySelectorAll('input[data-type="currency"]').forEach(function (input) {
        input.addEventListener('blur', function () {
            // Remove everything except digits, dots, and minus
            let cleaned = this.value.replace(/[^0-9.\-]/g, '');
            if (cleaned && !isNaN(parseFloat(cleaned))) {
                this.value = parseFloat(cleaned).toFixed(2);
            }
        });
    });

});
