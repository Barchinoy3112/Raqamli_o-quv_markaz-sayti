Raqamli O'quv Markaz

Quick start

1. Create and activate a virtualenv (example):

```bash
python -m venv venv
source ./venv/Scripts/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables (see `.env.example`) and run migrations from project folder `raqamli_markaz`:

```bash
cd raqamli_markaz
python manage.py migrate
python manage.py runserver
```

Run tests

```bash
cd raqamli_markaz
python manage.py test
```

CI

A GitHub Actions workflow is added at `.github/workflows/ci.yml` which runs migrations and tests on push/PR to `main`.
