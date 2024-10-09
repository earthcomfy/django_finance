# Personal Finance Management App with Django, HTMX, Alpine, Tailwind, and Plaid

This project is a personal finance management app that integrates [Plaid](https://plaid.com/) to link bank accounts and provide financial insights. I used [Plaid’s official examples](https://github.com/plaid/pattern) from their repository as a reference.

![Plaid](https://github.com/user-attachments/assets/331395bf-74e7-4298-aab6-fe559716038f)


## Features

- [Plaid](https://plaid.com/docs/) Integration to link bank accounts, fetch real-time account data, and track transactions.
- Automated webhooks to:
  - Automatically sync and update bank data whenever new transactions are available.
  - Easily update and re-authenticate accounts when they enter a bad state (e.g., login required).
  - Automatically detect new bank accounts and prompt users to add newly detected accounts.
- Provides financial insights such as net worth, account-specific details, and category-based spending breakdowns.
- Two-factor authentication (2FA) with an authenticator app for an added layer of security.

## Technologies Used

- Django
- HTMX
- Alpine
- Tailwind + Flowbite

## Learn More
Check out my article on [DEV](https://dev.to/earthcomfy/personal-finance-management-app-with-django-htmx-alpine-tailwind-and-plaid-2bl0)
