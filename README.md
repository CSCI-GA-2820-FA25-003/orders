# Orders Service

[![Build Status](https://github.com/CSCI-GA-2820-FA25-003/orders/actions/workflows/workflow.yml/badge.svg)](https://github.com/CSCI-GA-2820-FA25-003/orders/actions)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-FA25-003/orders/graph/badge.svg?token=CTUI5TLDLE)](https://codecov.io/gh/CSCI-GA-2820-FA25-003/orders)
[![Tekton Pipeline](https://img.shields.io/badge/Tekton-Pipeline-blue?logo=tekton&logoColor=white)](https://console-openshift-console.apps.os-cluster.example.com)

## Overview

This is a RESTful microservice for managing orders and their associated items. The service is built using Flask and SQLAlchemy with PostgreSQL as the database. It provides a complete CRUD (Create, Read, Update, Delete) API for orders and items, following RESTful design principles and DevOps best practices.

## Features

- **Order Management**: Create, read, update, and delete orders
- **Item Management**: Manage items within orders with full CRUD operations
- **Order Status Tracking**: Support for order statuses (PENDING, SHIPPED, DELIVERED, CANCELED)
- **Automatic Price Calculation**: Total price automatically calculated based on items
- **RESTful API**: Clean, intuitive API design
- **PostgreSQL Database**: Robust data persistence with relational integrity
- **Comprehensive Testing**: Full test coverage with pytest
- **CI/CD Pipeline**: Automated testing and deployment with GitHub Actions

## Technology Stack

- **Framework**: Flask 3.1.1
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Testing**: pytest, pytest-cov
- **Code Quality**: pylint, flake8, black
- **Web Server**: Gunicorn
- **Python Version**: 3.11

## API Endpoints

### Health & Info

| Endpoint  | Method | Description                     |
| --------- | ------ | ------------------------------- |
| `/health` | GET    | Health check endpoint           |
| `/`       | GET    | Service information and version |

### Order Operations

| Endpoint             | Method | Description                                         |
| -------------------- | ------ | --------------------------------------------------- |
| `/orders`            | POST   | Create a new order                                  |
| `/orders`            | GET    | List all orders (supports `?name=` query parameter) |
| `/orders/<order_id>` | GET    | Retrieve a specific order by ID                     |
| `/orders/<order_id>` | PUT    | Update an existing order                            |
| `/orders/<order_id>` | DELETE | Delete an order                                     |

### Item Operations

| Endpoint                             | Method | Description                |
| ------------------------------------ | ------ | -------------------------- |
| `/orders/<order_id>/items`           | POST   | Add an item to an order    |
| `/orders/<order_id>/items`           | GET    | List all items in an order |
| `/orders/<order_id>/items/<item_id>` | GET    | Get a specific item        |
| `/orders/<order_id>/items/<item_id>` | PUT    | Update an item             |
| `/orders/<order_id>/items/<item_id>` | DELETE | Delete an item             |

## Data Models

### Order Model

- `id`: Integer (Primary Key)
- `customer_id`: Integer (Required)
- `status`: Enum (PENDING, SHIPPED, DELIVERED, CANCELED)
- `total_price`: Float (Auto-calculated)
- `items`: Relationship to Item model

### Item Model

- `id`: Integer (Primary Key)
- `name`: String (63 chars)
- `category`: String (63 chars)
- `description`: String (1023 chars)
- `price`: Numeric (14, 2)
- `quantity`: Integer (Default: 1)
- `order_id`: Foreign Key to Order

## Project Structure

```text
.
├── service/                   # Service application package
│   ├── __init__.py           # Application factory
│   ├── config.py             # Configuration settings
│   ├── routes.py             # API route definitions
│   ├── models/               # Data models
│   │   ├── order.py          # Order model
│   │   ├── item.py           # Item model
│   │   └── persistent_base.py # Base model class
│   └── common/               # Shared utilities
│       ├── cli_commands.py   # CLI commands
│       ├── error_handlers.py # Error handling
│       ├── log_handlers.py   # Logging configuration
│       └── status.py         # HTTP status codes
├── tests/                    # Test suite
│   ├── test_routes.py        # API endpoint tests
│   ├── test_models.py        # Model tests
│   └── factories.py          # Test data factories
├── .github/workflows/        # CI/CD configuration
├── Pipfile                   # Python dependencies
└── wsgi.py                   # WSGI entry point
```

## Getting Started

### Prerequisites

- Python 3.11
- PostgreSQL
- pipenv

### Installation

1. Clone the repository:

```bash
git clone https://github.com/CSCI-GA-2820-FA25-003/orders.git
cd orders
```

2. Install dependencies:

```bash
pipenv install --dev
```

3. Set up environment variables:

```bash
cp dot-env-example .env
# Edit .env with your configuration
```

4. Initialize the database:

```bash
flask db-create
```

### Running the Service

Development mode:

```bash
honcho start
```

Production mode:

```bash
gunicorn --bind 0.0.0.0:8080 --log-level=info wsgi:app
```

### Running Tests

Run all tests:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=service --cov-report=term-missing
```

Run linting:

```bash
make lint
```

## OpenShift & Tekton Pipeline

We use **Tekton** on Red Hat OpenShift to automate our Continuous Delivery (CD) workflow. The pipeline definition files are stored in the `.tekton/` directory.

### Pipeline Workflow

The pipeline consists of 6 automated tasks that run whenever code is pushed to the `master` branch:

1.  **Clone**: Clones the repository from GitHub.
2.  **Lint & Test (Parallel)**:
      * Runs `flake8` to check for code quality issues.
      * Runs unit tests using `pytest` / `nosetests` to ensure code correctness.
3.  **Build**: Uses Buildah to create a Docker image from the source code and pushes it to the OpenShift Image Registry.
4.  **Deploy**: Updates the Kubernetes deployment to use the newly built image.
5.  **BDD Test**: Runs Behavior-Driven Development tests (using `behave`) against the live deployment to verify functionality.

### Setup & Installation (Cluster)

To deploy this pipeline to a new OpenShift cluster:

#### 1\. Prerequisites

  * OpenShift CLI (`oc`) installed.
  * Tekton CLI (`tkn`) installed (optional but recommended).
  * Access to an OpenShift project.

#### 2\. Prepare the Database

The service requires a PostgreSQL instance running in the cluster.

```bash
oc new-app postgresql-ephemeral --name=postgresql -p POSTGRESQL_USER=postgres -p POSTGRESQL_PASSWORD=postgres -p POSTGRESQL_DATABASE=testdb
```

#### 3\. Apply Tekton Manifests

Apply the configuration files in the following order to set up the pipeline infrastructure:

```bash
# 1. Apply Tasks (Standard and Custom)
oc apply -f .tekton/tasks.yaml

# 2. Apply Storage (Workspace)
oc apply -f .tekton/workspace.yaml

# 3. Apply the Pipeline Definition
oc apply -f .tekton/pipeline.yaml

# 4. Apply Triggers (Event Listener, Bindings, Template)
oc apply -f .tekton/triggers.yaml
```

### Triggering the Pipeline

#### Automatic (Webhook)

The pipeline is configured to run automatically via a GitHub Webhook whenever:

  * A push is made to the `master` branch.
  * A Pull Request is merged into `master`.

*The Webhook URL is generated by the EventListener route in OpenShift.*

#### Manual Trigger (CLI)

For testing or debugging purposes, you can manually trigger a pipeline run using the Tekton CLI:

```bash
tkn pipeline start cd-pipeline \
    -w name=pipeline-workspace,claimName=pipeline-pvc \
    -p repo-url="[https://github.com/CSCI-GA-2820-FA25-003/orders.git](https://github.com/CSCI-GA-2820-FA25-003/orders.git)" \
    -p branch="master" \
    --showlog
```

*(Note: Ensure parameter names like `pipeline-workspace` match those defined in your `pipeline.yaml`)*

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
