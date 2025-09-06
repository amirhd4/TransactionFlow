# FinanceFlow: A Dynamic Financial Transaction System

FinanceFlow is a web application built with Django that simulates a financial transaction system. It supports multi-currency accounts, calculates transaction fees, performs currency conversions via an external API, and dynamically distributes funds based on configurable rules. The entire application is containerized using Docker for a streamlined setup and development process.

---

## Features

* **User & Account Management:** Users can have multiple financial accounts in different currencies.
* **Multi-Currency Transactions:** Transfer funds between accounts, with automatic currency conversion.
* **Fee Calculation:** A configurable percentage-based fee is applied to each transaction.
* **Live Currency Conversion:** Utilizes an external API (ExchangeRate-API) to fetch real-time exchange rates.
* **Dynamic Fund Distribution:** A "gateway" account can be configured to automatically split and distribute incoming funds to multiple other accounts based on predefined percentage rules.
* **Web Interface:** A user-friendly interface for viewing account balances and initiating transactions.
* **Containerized Environment:** Fully containerized with Docker and Docker Compose for consistency across different environments.

---

## Technology Stack

* **Backend:** Python, Django
* **Database:** PostgreSQL
* **Web Server:** Gunicorn
* **Containerization:** Docker, Docker Compose
* **Static Files:** WhiteNoise
* **Core Libraries:** Django REST Framework, python-decouple

---

## Setup and Installation

Follow these steps to get the project up and running on your local machine.

### Prerequisites

* [Docker](https://www.docker.com/get-started)
* [Docker Compose](https://docs.docker.com/compose/install/)

### Configuration Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/amirhd4/TransactionFlow.git
    cd TransactionFlow
    ```

2.  **Create the environment file:**
    This project uses a `.env` file to manage secrets and configuration. A sample file is provided. Rename `env.example` to `.env` or create it manually.

    ```bash
    # Create the file
    cp env.example .env
    ```

    Then, open the `.env` file and fill in the required values, especially your API key.
    ```env
    # .env
    SECRET_KEY='your-django-secret-key'
    DEBUG=True

    POSTGRES_DB=financial_db
    POSTGRES_USER=user
    POSTGRES_PASSWORD=password

    DB_NAME=financial_db
    DB_USER=user
    DB_PASS=password
    DB_HOST=db
    DB_PORT=5432

    EXCHANGERATE_API_KEY='your-free-api-key-from-exchangerate-api.com'
    ```
    **Note:** You must obtain a free API key from [ExchangeRate-API.com](https://www.exchangerate-api.com) for the currency conversion feature to work.

3.  **Build and run the Docker containers:**
    ```bash
    docker-compose up --build -d
    ```

4.  **Apply database migrations:**
    ```bash
    docker-compose exec web python manage.py migrate
    ```

5.  **Collect static files:**
    ```bash
    docker-compose exec web python manage.py collectstatic --no-input
    ```

6.  **Create a superuser:**
    This will allow you to access the Django admin panel.
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```
    Follow the prompts to create your admin account.

---

## Usage

Once the setup is complete, you can start using the application.

1.  **Access the application:**
    * Web Application: `http://localhost:8000`
    * Django Admin Panel: `http://localhost:8000/admin/`

2.  **Initial Data Setup (via Admin Panel):**
    * Log into the admin panel with your superuser credentials.
    * Create a few `User` objects.
    * Create `Account` objects for these users. Ensure you create at least one "gateway" account by checking the `is_gateway` box.
    * For the gateway account, create several `DistributionRule` objects, linking them to other non-gateway accounts. **Ensure the percentages of all rules for a single gateway sum up to 100%.**

3.  **Perform a Transaction:**
    * Navigate to `http://localhost:8000` and log in as a regular user.
    * You will be redirected to your dashboard, where you can see your account balances.
    * Click on "New Transaction", fill out the form, and submit it.
    * You will be redirected back to the dashboard with a success or failure message.

---

## Architectural Notes & Production Disclaimer

### Development Environment

This project is configured for a development and testing environment.

* **Static Files:** The project uses **WhiteNoise** to serve static files directly from the Gunicorn server. This is a simple and effective solution for development. For a large-scale production environment, the standard practice would be to configure a dedicated web server like **Nginx** to handle static files and act as a reverse proxy for improved performance and security.
* **Debugging:** `DEBUG` is set to `True` to provide detailed error pages. This must be set to `False` in a production environment.

### Security Notice

⚠️ The `.env` file containing secrets is included in this repository's instructions **for demonstration and ease of testing only**. In a real-world production environment, you must **NEVER** commit your `.env` file or any other secrets to version control. They should be managed securely using environment variables injected by your hosting platform, or tools like Docker Secrets, Kubernetes Secrets, or a cloud provider's secret management service.

---

## License

This project is licensed under the MIT License.