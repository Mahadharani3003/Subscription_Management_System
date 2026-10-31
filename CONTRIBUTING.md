# Contributing to Brightloop

Thank you for your interest in contributing to **Brightloop – Subscription Management System**!

## Code of Conduct
We are committed to providing a friendly, safe, and welcoming environment for everyone, regardless of experience level, background, or identity.

## Development Standards & Guidelines

### 1. Odoo Conventions
- Follow standard [Odoo Guidelines](https://www.odoo.com/documentation/17.0/developer/reference/standard_modules.html).
- Keep model names prefixed with `brightloop.` (e.g. `brightloop.subscription`).
- Always define explicit field labels (`string`), help tooltips (`help`), and sensible defaults.
- Any field used in search, filter, or cron domains **must** be indexed with `index=True`.

### 2. Python Standards
- Python 3.10+ compatibility.
- Format with PEP 8 standards.
- Never write raw string SQL queries. Always use the Odoo ORM (`self.env['model'].search(...)`).
- Do not add heavy external dependencies (e.g., PyTorch, TensorFlow) without architectural approval.

### 3. XML & UI Views
- Use semantic IDs prefixed with model and view type (e.g., `view_brightloop_subscription_kanban`).
- Ensure all views validate against Odoo 17.0 RNG schemas.
- Provide descriptive empty states (`<p class="o_view_nocontent_smiling_face">`) for all actions.

### 4. Automated Testing
Every PR must pass all test suites before merge:
```bash
# 1. Run static AST, XML, and ACL verification
python verify_backend.py

# 2. Run all unit, integration, and stress tests
python -m unittest discover -s tests -p "test_*.py"
```

## Pull Request Process
1. Fork the repository and create your branch from `main`.
2. Ensure no hardcoded secrets or unindexed foreign keys exist.
3. Update relevant documentation in `docs/` if modifying workflows or schemas.
4. Submit your pull request with a descriptive title and commit message following Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`).
