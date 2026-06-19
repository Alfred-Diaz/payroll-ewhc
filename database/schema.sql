CREATE TABLE employees (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    employee_code VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    department VARCHAR(100),
    position_title VARCHAR(100),
    employment_status VARCHAR(50),
    monthly_salary DECIMAL(12,2) DEFAULT 0,
    tax_status VARCHAR(50),
    sss_no VARCHAR(50),
    philhealth_no VARCHAR(50),
    pagibig_no VARCHAR(50),
    pagibig_override_amount DECIMAL(10,2) NULL,
    created_at TIMESTAMP NULL,
    updated_at TIMESTAMP NULL
);

CREATE TABLE schedules (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    schedule_name VARCHAR(100),
    time_in TIME,
    time_out TIME,
    break_minutes INT DEFAULT 60,
    is_shifting TINYINT DEFAULT 0,
    created_at TIMESTAMP NULL,
    updated_at TIMESTAMP NULL
);

CREATE TABLE employee_schedules (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    employee_id BIGINT,
    schedule_id BIGINT,
    effective_date DATE,
    end_date DATE NULL
);

CREATE TABLE biometric_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    employee_code VARCHAR(50),
    attendance_date DATE,
    time_in DATETIME NULL,
    time_out DATETIME NULL,
    source_file VARCHAR(255),
    created_at TIMESTAMP NULL
);

CREATE TABLE attendance_summaries (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    employee_id BIGINT,
    attendance_date DATE,
    first_in DATETIME,
    last_out DATETIME,
    tardiness_minutes INT DEFAULT 0,
    undertime_minutes INT DEFAULT 0,
    overtime_minutes INT DEFAULT 0,
    night_diff_minutes INT DEFAULT 0
);

CREATE TABLE payroll_periods (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    period_name VARCHAR(100),
    date_from DATE,
    date_to DATE,
    status VARCHAR(20)
);

CREATE TABLE payroll_runs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    payroll_period_id BIGINT,
    employee_id BIGINT,
    basic_pay DECIMAL(12,2) DEFAULT 0,
    overtime_pay DECIMAL(12,2) DEFAULT 0,
    holiday_pay DECIMAL(12,2) DEFAULT 0,
    night_diff_pay DECIMAL(12,2) DEFAULT 0,
    gross_pay DECIMAL(12,2) DEFAULT 0,
    total_deductions DECIMAL(12,2) DEFAULT 0,
    net_pay DECIMAL(12,2) DEFAULT 0
);

CREATE TABLE loans (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    employee_id BIGINT,
    loan_type VARCHAR(100),
    principal_amount DECIMAL(12,2),
    monthly_amortization DECIMAL(12,2),
    balance DECIMAL(12,2),
    status VARCHAR(20)
);
