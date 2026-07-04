# Portfolio Manager & Risk Analyzer

A Python-based portfolio management and risk analysis application designed to help investors manage their portfolios, track live market prices, analyze performance, and evaluate portfolio risk.

> **Project Status:** 🚧 In Development

---

# Overview

This project is being developed as a complete portfolio management application using Python and Object-Oriented Programming (OOP).

The long-term goal is to build a desktop application capable of:

* Managing investment portfolios
* Fetching live market data
* Tracking portfolio performance
* Performing risk analysis
* Visualizing financial data
* Providing an intuitive graphical user interface (GUI)

The project is built incrementally, with each feature designed to follow clean architecture and software engineering best practices.

---

# Current Features

* ✅ Asset management
* ✅ Portfolio management
* ✅ Duplicate asset validation
* ✅ Input validation with exceptions
* ✅ Live stock price retrieval using Yahoo Finance
* ✅ Automatic portfolio price updates
* ✅ Portfolio market value calculation
* ✅ Cost basis calculation
* ✅ Profit/Loss calculation
* ✅ Portfolio return calculation
* ✅ Portfolio allocation (asset weights)
* ✅ Basic portfolio risk analysis

---

# Technologies

* Python 3.14
* Object-Oriented Programming (OOP)
* yfinance

Planned technologies:

* pandas
* NumPy
* Matplotlib
* PyQt6
* pytest

---

# Project Structure

```text
portfolio-manager-and-risk-analyzer/
│
├── models/
│   ├── asset.py
│   └── portfolio.py
│
├── services/
│   └── market_data.py
│
├── data/
├── tests/
│
├── main.py
├── README.md
└── .gitignore
```

---

# Installation

Clone the repository:

```bash
git clone https://github.com/emataka/portfolio-manager-and-risk-analyzer.git
```

Move into the project directory:

```bash
cd portfolio-manager-and-risk-analyzer
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the project:

```bash
python main.py
```

---

# Roadmap

## Phase 1 – Core Portfolio Management

* [x] Asset class
* [x] Portfolio class
* [x] Market data service
* [x] Portfolio valuation
* [x] Performance calculations
* [x] Basic risk analysis

## Phase 2 – Data Management

* [ ] Save portfolios to JSON
* [ ] Load portfolios from JSON
* [ ] CSV import/export

## Phase 3 – Portfolio Analytics

* [ ] Historical price analysis
* [ ] Performance over time
* [ ] Portfolio diversification metrics
* [ ] Advanced risk analysis

## Phase 4 – Visualization

* [ ] Portfolio allocation charts
* [ ] Performance charts
* [ ] Historical trend visualization

## Phase 5 – Desktop Application

* [ ] PyQt6 graphical user interface
* [ ] Interactive portfolio management
* [ ] Settings and preferences

## Phase 6 – Software Quality

* [ ] Unit tests (pytest)
* [ ] Logging
* [ ] Documentation improvements
* [ ] Continuous improvements

---

# Learning Objectives

This project is also intended as a practical learning experience for:

* Python
* Object-Oriented Programming
* Software Architecture
* Clean Code principles
* Git & GitHub workflow
* Financial software development

---

# Author

**Emataka**

GitHub: https://github.com/emataka
