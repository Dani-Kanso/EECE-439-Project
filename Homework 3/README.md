# Doctor Contact Directory

This project extends Assignment 3 into a medical contact directory that can be deployed on Azure App Service. It now ships with a dataset, management commands to synchronize records, and a lightweight recommendation engine inspired by the lab reference project.

## Local setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py sync_contacts --replace
python manage.py runserver
```

## Features

- **Richer Contact Model:** Tracks specialty, hospital affiliation, geography, consultation fees, patient ratings, and whether new patients are accepted.
- **Dataset Synchronization:** `python manage.py sync_contacts --replace` loads the sample doctor contacts from `contacts/data/doctor_contacts.json`. Modify that file or load another public dataset to keep the app in sync.
- **Searchable Directory:** `/` renders a searchable table that supports keyword search, city/state filters, budget/rating constraints, and sorting options.
- **Recommendation Engine:** `/recommendations/` scores contacts using specialty, budget, ratings, experience, and optional GPS coordinates.
- **Environment-driven settings:** `DEBUG` toggles via the `DJANGO_DEBUG` environment variable (defaults to `True` for local work so the Django admin serves CSS). On Azure, set `DJANGO_DEBUG=False`. `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS` automatically include the `AZURE_WEBAPP_NAME` you configure.

## Azure deployment checklist

1. Push this repository (including `requirements.txt`) to GitHub.
2. Create an Azure App Service (Linux, Python 3.12+ recommended) named `cloudcontactsapp439` or update the name in `contactproject/settings.py`.
3. Configure App Service to pull your GitHub repo (continuous deployment) or use `az webapp up`.
4. Set `DJANGO_SETTINGS_MODULE=contactproject.settings` and `PYTHONPATH` to the project root if needed.
5. Run `python manage.py migrate` and `python manage.py sync_contacts --replace` from the App Service console or via GitHub Actions so the dataset is populated in production.
6. Set `DJANGO_DEBUG=False` and provide a production `SECRET_KEY` through App Service configuration before exposing the site publicly.

With those steps complete, your app will be reachable at `https://cloudcontactsapp439.azurewebsites.net`.
