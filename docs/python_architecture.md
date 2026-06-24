# Python-First Payroll Architecture

## Project Direction

Build the payroll system entirely in Python first.

Stack:
- Python 3.12+
- FastAPI
- SQLAlchemy
- MySQL
- Pandas
- OpenPyXL
- Uvicorn

## Modules

1. Employee Masterfile
2. DTR Import Engine
3. Attendance Normalization
4. Payroll Computation Engine
5. Government Contributions
6. Loans
7. Leave Management
8. Payroll Register
9. Payslip Generation
10. Final Pay and Annualization

## DTR Rules

- Store raw biometric logs.
- Group by employee and date.
- Earliest punch = First In.
- Latest punch = Last Out.

## API Structure

/api/employees
/api/dtr/import
/api/attendance/process
/api/payroll/compute
/api/payroll/register
/api/payslips

## Initial Folder Structure

src/
  api/
  services/
  models/
  payroll/
  attendance/
  reports/

data/
exports/
imports/

## Goal

Produce a working payroll engine in Python before building a web portal UI.
