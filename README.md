# 🏢 Finance and Account Dashboard

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28.1-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)

A comprehensive, enterprise-grade financial management application built with Streamlit for tracking sales, purchases, bank transactions, and vendor payable management. Perfect for small to medium businesses looking for an efficient accounting solution.

## 🌟 Live Demo

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://financial-analyst.streamlit.app)

## 📋 Table of Contents

- [Features](#-features)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage Guide](#-usage-guide)
- [Data Structure](#-data-structure)
- [Screenshots](#-screenshots)
- [Technology Stack](#-technology-stack)
- [Future Roadmap](#-future-roadmap)
- [Contributing](#-contributing)
- [License](#-license)
- [Support](#-support)

## ✨ Features

### Core Modules

| Module | Description | Key Features |
|--------|-------------|--------------|
| 🏠 **Home Dashboard** | Central command center | Real-time KPIs, recent activity, quick metrics |
| 📝 **Bank Data Entry** | Financial transaction management | Debit/Credit tracking, multiple payment methods, CSV export |
| 💰 **Sales Entry** | Sales invoice management | Customer tracking, payment status, due date monitoring |
| 📦 **Purchase Entry** | Accounts payable management | Supplier tracking, PO management, payment scheduling |
| 🏢 **Vendor Payable** | Vendor payment tracking | Aging analysis, payment recommendations, statement download |
| 📊 **Reports Dashboard** | Analytics & insights | Interactive charts, date filtering, export capabilities |

### Advanced Capabilities

- **Real-time Data Entry**: Instant transaction recording with validation
- **Multi-currency Support**: Configurable currency settings (INR/BDT/USD)
- **Data Export**: Export any view to CSV/Excel format
- **Interactive Visualizations**: Dynamic charts using Plotly
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Dark/Light Mode**: Automatic theme detection

## 📁 Project Structure

FINANCIALANALYSIS/
├── 📂 data/ # Data storage directory
│ ├── financial_transactions.csv # Bank/financial transactions
│ ├── cosmetics_sales.csv # Sales invoices
│ └── purchase_transactions.csv # Purchase orders
│
├── 📂 pages/ # Multi-page application
│ ├── Reports.py # Reports dashboard
│ ├── Sales.py # Sales analytics
│ ├── Vendor.py # Vendor management
│ └── Payable.py # Payable management
│
├── 📂 assets/ # Static assets
│ ├── logo.png
│ └── style.css
│
├── 📂 utils/ # Utility functions
│ ├── data_loader.py
│ ├── validators.py
│ └── helpers.py
│
├── HOME.py # Main application entry point
├── requirements.txt # Python dependencies
├── README.md # Project documentation
├── .gitignore # Git ignore file
├── config.yaml # Configuration settings
└── tests/ # Unit tests
├── test.ipynb
└── test_validators.py



## 🚀 Installation

### Prerequisites

- **Python**: 3.8 or higher
- **pip**: Latest version
- **Git**: For cloning the repository
- **Virtual Environment** (recommended)

### Quick Start


#### 1. Clone the repository
- git clone https://github.com/mujakkirdv/account-module.git
- cd account-module

#### 2. Create virtual environment
- python -m venv venv

#### Activate virtual environment
#### On Windows:
- venv\Scripts\activate

#### On macOS/Linux:
- source venv/bin/activate

#### 3. Install dependencies
- pip install -r requirements.txt

##### 4. Run the application

- streamlit run HOME.py