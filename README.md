# Batch Slug Test Analysis

A comprehensive Dash application for analyzing slug test data in groundwater studies.

## Features

- **Interactive Dashboard**: Clean, modern web interface for data analysis
- **File Upload**: Support for CSV and Excel files
- **Real-time Analysis**: Immediate visualization of slug test results
- **Professional UI**: Bootstrap-based design with custom branding

## Quick Start

### Prerequisites

- Python 3.8+
- Conda environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pyAqTest
   ```

2. **Create conda environment**
   ```bash
   conda create -n pump_test python=3.9
   conda activate pump_test
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. **Activate environment**
   ```bash
   conda activate pump_test
   ```

2. **Run the main app**
   ```bash
   python src/pyAqTest/app.py
   ```
   Or use the launcher:
   ```bash
   python run_app.py
   ```

3. **Access the dashboard**
   - Open your browser to `http://localhost:8050`

## Project Structure

```
pyAqTest/
├── run_app.py               # Simple launcher script
├── requirements.txt         # Python dependencies
├── assets/                  # Static assets
│   └── logo.png             # Application logo
├── src/pyAqTest/           # Core analysis modules
│   ├── app.py              # Main Dash application
│   ├── dashboard/           # Dashboard components
│   │   ├── __init__.py     # Package initialization
│   │   ├── layout.py       # Layout components
│   │   ├── callbacks.py    # Callback functions
│   │   ├── components.py   # Reusable UI components
│   │   └── README.md       # Dashboard documentation
│   ├── slug_tests.py       # Slug test analysis
│   ├── batch_processing.py # Batch processing
│   └── ...
└── tests/                   # Test files
```

## Usage

1. **Upload Data**: Drag and drop your slug test data files
2. **View Results**: Interactive plots show analysis results
3. **Export**: Download results in various formats

## Development

### Code Quality
- **Formatting**: `black src/pyAqTest/app.py`
- **Linting**: `flake8 src/pyAqTest/app.py`
- **Testing**: `pytest tests/`

### Adding Features
- New analysis methods: Add to `src/pyAqTest/`
- UI components: Add to `src/pyAqTest/dashboard/components.py`
- Layout changes: Modify `src/pyAqTest/dashboard/layout.py`
- Callbacks: Add to `src/pyAqTest/dashboard/callbacks.py`
- Main app: Only `src/pyAqTest/app.py` should be modified for app configuration

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For questions or issues, please open an issue on GitHub.
