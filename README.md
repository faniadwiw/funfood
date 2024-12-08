# FUNFOOD - Recipe Sharing Platform

A Django web application for sharing and discovering recipes.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone the repository

  ```bash
  git clone https://github.com/yourusername/funfood.git
  cd funfood
  ```

2. Create a virtual environment

  ```bash
  python -m venv env
  ```

3. Activate the virtual environment

  On Windows:
  ```bash
  .\env\Scripts\activate
  ```

  On macOS/Linux:
  ```bash
  source env/bin/activate
  ```

4. Install dependencies

  ```bash
  pip install -r requirements.txt
  ```

5. Run database migrations

  ```bash
  python manage.py migrate
  ```

6. Create a superuser (admin)

  ```bash
  python manage.py createsuperuser
  ```

7. Run the development server

  ```bash
  python manage.py runserver
  ```

8. Open your browser and go to [http://127.0.0.1:8000](http://127.0.0.1:8000)
