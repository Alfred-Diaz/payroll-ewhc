# Local Setup Guide

This repository is intended to run as a Laravel + MySQL HRIS payroll system on a local server.

## Requirements

Install these on the local machine or server:

- PHP 8.2 or higher
- Composer
- MySQL or MariaDB
- Node.js and npm
- Git

## Initial Laravel installation

Because this repository currently contains the payroll foundation files, create the Laravel app locally first, then copy or merge this repository's files into it.

```bash
composer create-project laravel/laravel payroll-ewhc
cd payroll-ewhc
```

## Database setup

Create a MySQL database:

```sql
CREATE DATABASE payroll_ewhc CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Update `.env`:

```env
APP_NAME="Payroll EWHC"
APP_ENV=local
APP_DEBUG=true
APP_URL=http://127.0.0.1:8000

DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=payroll_ewhc
DB_USERNAME=root
DB_PASSWORD=
```

## Install frontend assets

```bash
npm install
npm run build
```

## Run migrations

After the migration files are added to the Laravel project, run:

```bash
php artisan migrate
```

## Run locally

```bash
php artisan serve
```

Open:

```text
http://127.0.0.1:8000
```

## Local server deployment note

For LAN access, host the app through Apache or Nginx and point the web root to Laravel's `public` directory.

Example local URL:

```text
http://192.168.1.10/payroll-ewhc
```

## First working module

The first working module should be the DTR importer:

1. Upload Excel DTR.
2. Save raw biometric logs.
3. Normalize by employee code and date.
4. Use earliest time in and latest time out.
5. Save attendance summary.
