# Impulse Analyzer

![GitHub top language](https://img.shields.io/github/languages/top/almarazj/impulse-analyzer) 
![GitHub repo size](https://img.shields.io/github/repo-size/almarazj/impulse-analyzer)
![License](https://img.shields.io/github/license/almarazj/impulse-analyzer)
![GitHub Repo stars](https://img.shields.io/github/stars/almarazj/impulse-analyzer)

Impulse Analyzer is a Python-based application for analyzing impulse responses and sine sweeps. It provides a graphical user interface (GUI) built with PyQt5 and integrates audio processing and visualization features.

## Features

- Import and analyze impulse response (IR) files in `.wav` format.
- Import sine sweep and inverse filter.
- Visualize impulse responses with dynamic plots.
- Switch between left and right audio channels for stereo files.
- Apply filters and smoothing options to the data.
- Calculate acoustical parameters (EDT, T20, T30, C50, C80, IACC)
- Export results to CSV or copy them to the clipboard.

## Installation

This project uses [Poetry](https://python-poetry.org/) for dependency management. Follow the steps below to set up the project:

### Prerequisites

- Python 3.8 or higher
- Poetry installed on your system

### Steps to Install

1. Clone the repository:

    ```bash
   git clone https://github.com/almarazj/impulse-analyzer.git
   cd impulse-analyzer
    ```

2. Install dependencies using Poetry:

    ```bash
    poetry install
    poetry env activate
    # Copy and paste the output of the previous command
    ```

3. Run the application:

    ```bash
    python main.py
    ```
