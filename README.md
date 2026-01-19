# secure-django-app
# Secure Task Management Web Application (IKB21503)

## 1. Project Description
[cite_start]The **Secure Task App** is a Django-based web application developed for the course **IKB21503 Secure Software Development** at UniKL MIIT[cite: 78, 93]. [cite_start]This system is designed to allow users to manage personal tasks securely while enforcing proper security controls and **Role-Based Access Control (RBAC)** between normal users and administrators[cite: 79, 81].



## 3. Security Features Summary (OWASP Aligned)
[cite_start]In compliance with **OWASP Top 10** and **ASVS** requirements, the following security features have been implemented[cite: 82, 83]:
* [cite_start]**Authentication**: Secure login/logout using Django's built-in framework with **Argon2** password hashing[cite: 80, 83, 174].
* [cite_start]**Access Control**: Role-Based Access Control (RBAC) to restrict administrative functions (e.g., Audit Logs) to authorized users only[cite: 81, 158, 182].
* [cite_start]**Input Validation**: Server-side validation using **Django Forms** to mitigate XSS and Injection attacks[cite: 83, 162, 166].
* [cite_start]**Database Security**: Prevention of SQL Injection through the use of **Django ORM** for all database interactions[cite: 80, 132, 168].
* [cite_start]**Session Management**: Protection against session hijacking via **HttpOnly** and **Secure** cookie flags[cite: 175, 700].
* [cite_start]**CSRF Protection**: Middleware and tokens enforced for all state-changing requests[cite: 80, 176, 222].
* [cite_start]**Error Handling**: Custom 400, 403, 404, and 500 pages to prevent information leakage[cite: 133, 186].
* [cite_start]**Secret Management**: Sensitive configuration (e.g., SECRET_KEY) stored in environment variables (`.env`)[cite: 192, 200].
* [cite_start]**Audit Logging**: Comprehensive logging of security-relevant events such as logins and task operations[cite: 100, 207, 212].

## 4. Installation Steps
1. **Clone the project**:
   ```bash
   git clone [https://github.com/azimsyafawi04/secure-task-app-ssd-project.git](https://github.com/azimsyafawi04/secure-task-app-ssd-project.git)

2
   python -m venv venv
    venv\Scripts\activate  # For Windows

3 Install Dependencies:
pip install -r requirements.txt

4 Environment Configuration: Create a .env file based on .env.example and set your SECRET_KEY and DEBUG=False

5 Run Migrations
python manage.py migrate

6 Start Application
python manage.py runserver




