# Payroll EWHC HRIS

Local-server HRIS project with payroll as the foundation module.

## Target timeline

Initial payroll foundation: August

## Phase 1 scope

- Employee masterfile
- Biometric DTR import
- First-in / last-out attendance normalization
- Shifting schedule setup
- Payroll period setup
- Payroll run computation foundation
- Payroll register structure
- Payslip data foundation

## Payroll wishlist coverage

- Biometrics sync with only IN and OUT records
- Repeated biometric punches normalized to first IN and last OUT
- Overtime, tardiness, undertime, night differential
- Regular and special holiday rules
- Leave without pay, VL, SL, and sick leave conversion
- Loans with monthly amortization and running balance
- Salary adjustments with effective dates
- Government contribution tables: withholding tax, SSS, PhilHealth, Pag-IBIG
- Pag-IBIG adjustment override per employee
- 13th month pay and annualized final tax computation
- Final pay and tax finalization
- Payroll register and payslip generation

## Uploaded DTR format

The initial DTR file reviewed is `DTR_20260520-20260619 (1).xlsx` with these columns:

| Column | Description |
|---|---|
| EMPLOYEE CODE | Biometric / employee code |
| EMPLOYEE NAME | Employee name from DTR source |
| DATE | Attendance date |
| WEEK DAY | Day name |
| TIME IN | Biometric time in |
| TIME OUT | Biometric time out |

Normalization rule:

- Group by employee code and date.
- Use earliest non-empty `TIME IN` as final time in.
- Use latest non-empty `TIME OUT` as final time out.
- Keep the raw imported rows for audit trail.

## Proposed local-server stack

- Backend: Laravel or PHP API layer
- Database: MySQL / MariaDB
- Frontend: Blade, Vue, or simple admin UI
- Deployment: local server, LAN-accessible

## Repository structure

```text
docs/
  payroll-requirements.md
  dtr-import-spec.md
  payroll-formulas.md
database/
  schema.sql
  seed_reference_tables.sql
src/
  README.md
```

## Next build step

Implement the database schema and DTR import parser, then create the payroll computation service.
