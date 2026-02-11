# VTOP Authentication System (Python)

Python implementation of VTOP authentication with custom captcha recognition.

## Features

- Automated VTOP login with captcha solving
- Custom neural network for captcha recognition (98%+ accuracy)
- Automatic profile data extraction after login
- Session management and error handling
- Debug mode with HTML/image logging
- JSON data storage with timestamps and update tracking

## Project Structure

```
vtop_auth/
├── authentication/          # Authentication module
│   ├── auth_service.py     # Main authentication service
│   ├── constants.py        # Configuration constants
│   ├── models.py           # Data models
│   └── captcha/            # Captcha recognition
│       ├── captcha_solver.py
│       ├── neural_model.py
│       ├── preprocessor.py
│       └── vellore_weights.json
├── data_service/           # Data extraction services
│   ├── profile_info.py     # Profile information extraction
│   └── __init__.py
├── data/                   # Extracted data (JSON files)
│   └── profile-info-data.json
├── debug/                  # Debug logs (HTML/images)
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
└── credentials.json        # Login credentials
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `credentials.json`:
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

## Usage

### Interactive Mode
```bash
python main.py
```

### Command Line
```bash
python main.py <username> <password>
```

### Run Tests
```bash
python main.py --test
```

## Authentication Flow

1. GET `/vtop` - Establish session
2. POST `/vtop/prelogin/setup` - Setup session with form data
3. GET `/vtop/login` - Load login page with captcha
4. Extract captcha image (base64 from img src)
5. Solve captcha using neural network
6. POST `/vtop/login` with all form fields (including CSRF token)
7. Verify login success
8. Automatically extract profile information

## Data Extraction

After successful authentication, the system automatically extracts:

### Profile Information
- Student name, register number, email
- Program, branch, school name
- Date of birth
- Hostel details (block, room, bed type)
- Mess information

Data is saved to `data/profile-info-data.json` with:
- ISO format timestamp: `2026-02-12T00:20:32.658294`
- Human readable: `2026-02-12 00:20:32`
- Unix timestamp (ms): `1770835832658`
- Previous update tracking for change history

## Captcha Recognition

- Custom neural network trained on Vellore captcha format
- 6-character alphanumeric captchas
- Character set: `ABCDEFGHJKLMNPQRSTUVWXYZ23456789` (32 chars)
- Confidence threshold: 70% (auto-submit), 90% (high confidence)
- Preprocessing: Saturation channel extraction + block segmentation

## Debug Mode

All HTTP responses and captcha images are saved to `debug/` folder:
- `01_home_*.html` - Homepage response
- `02_setup_*.html` - Setup response
- `03_login_*.html` - Login page
- `05_captcha_*_N.png` - Captcha images (N = attempt number)
- `06_response_*_N.html` - Login submission responses

## Error Codes

- `0` - Success
- `1` - Invalid captcha
- `2` - Invalid credentials
- `3` - Account locked
- `4` - Maximum attempts reached
- `51` - Server connection error
- `63` - Captcha extraction error

## Notes

- SSL verification is disabled for VTOP's certificate issues
- Session cookies are maintained throughout the flow
- All form fields (including CSRF token) are captured and submitted
- Maximum 3 captcha attempts per login session
- Profile data is automatically extracted after successful login
- Data files are stored in `data/` directory (excluded from git)
- Each update preserves previous update timestamp for tracking changes

## Data File Format

Example `data/profile-info-data.json`:

```json
{
  "profile": {
    "name": "STUDENT NAME",
    "registerNumber": "23XXX1234",
    "vitEmail": "student.name2023@vitstudent.ac.in",
    "program": "BTECH - Computer Science and Engineering",
    "branch": "Computer Science and Engineering",
    "schoolName": "School of Computer Science and Engineering",
    "dateOfBirth": "01-Jan-2004",
    "hostelBlock": "A Block Mens Hostel",
    "roomNumber": "123",
    "bedType": "4-BED-NAC",
    "messName": "Food Park - RASSENSE"
  },
  "metadata": {
    "lastUpdated": "2026-02-12T00:20:32.658294",
    "lastUpdatedHuman": "2026-02-12 00:20:32",
    "extractionTimestamp": 1770835832658
  },
  "previousUpdate": {
    "lastUpdated": "2026-02-11T23:15:10.123456",
    "lastUpdatedHuman": "2026-02-11 23:15:10",
    "extractionTimestamp": 1770832510123
  }
}
```
