# Payroll Requirements

## Project direction

The HRIS will be hosted on a local server and will use payroll as the foundation module.

Recommended stack:

- Laravel
- MySQL or MariaDB
- Local network deployment
- Role-based HR access

## Payroll core requirements

### Attendance and biometrics

- Import biometric DTR files.
- Preserve raw biometric rows for audit.
- Normalize attendance per employee per day.
- Use earliest valid `TIME IN` as official time in.
- Use latest valid `TIME OUT` as official time out.
- Ignore duplicate/intermediate punches for payroll computation.
- Payroll should read the employee's assigned schedule.

### Schedule management

- Fixed schedules.
- Shifting schedules.
- MLCU schedule support.
- Schedule assignment by employee and date range.
- Grace period and break rules should be configurable.

### Payroll computation

Required computation items:

- Basic pay
- Daily rate
- Hourly rate
- Tardiness deduction
- Undertime deduction
- Overtime pay
- Night differential
- Regular holiday pay
- Special holiday pay
- Holiday overtime
- Leave without pay
- VL and SL usage
- Sick leave conversion
- Allowance provisional field for future use
- Salary adjustment by effective date

Default rate basis requested:

```text
Daily rate = monthly salary x 12 / 22
Hourly rate = daily rate / 8
```

### Government deductions

The system must support configurable yearly tables for:

- Withholding tax
- SSS
- PhilHealth
- Pag-IBIG

Pag-IBIG must allow manual employee contribution adjustment when HR needs to override the standard amount.

### Loans

- HR inputs loan type, principal amount, and monthly amortization.
- Payroll automatically deducts active loan amortization.
- System records every loan deduction transaction.
- System computes accumulated payment and running balance.
- Loan becomes paid once balance is zero.

### Bonuses and 13th month

- Compute 13th month pay.
- Include year-to-date basic salary basis.
- Consider absences and leave without pay for the whole year.
- Support monthly average computation.
- Support bonus entries by payroll period.

### Final pay and annualization

- Compute final pay.
- Include remaining salary, deductions, loans, leave conversion, and other adjustments.
- Perform annualized withholding tax finalization.

### Payroll register and payslip

- Payroll register should show employee-level earnings, deductions, adjustments, and net pay.
- HR must be able to view general payroll register.
- Employees may view individual payslips in a later phase.
- Payslip should be printable/exportable.

## Phase order

1. Employee, schedule, attendance, and payroll period foundation.
2. DTR import and first-in/last-out normalization.
3. Payroll computation engine.
4. Government contribution tables and deductions.
5. Loans, bonuses, and 13th month.
6. Payroll register and payslip generation.
7. Final pay and annualization.
