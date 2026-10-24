# 💧 Water Harvesting Tracker

A web-based application for tracking rainwater harvesting, monitoring water usage, and estimating rainwater collection potential. The project helps users understand how rainwater can be collected, stored, and used efficiently.

## 🌐 Live Demo

**Live Website:** https://water-harvesting-tracker.onrender.com

**GitHub Repository:** https://github.com/pavanimandati13-jpg/water-harvesting-tracker

## 📌 Project Overview

Water Harvesting Tracker is a Flask-based web application designed to support rainwater management. Users can record rainfall, track water consumption, manage harvesting sites, and estimate the amount of rainwater that can be collected from rooftops.

The dashboard presents important water statistics to help users monitor harvesting activity and make better water conservation decisions.

## 🎯 Objectives

- Track rainfall and harvested rainwater.
- Monitor water consumption and usage purposes.
- Manage multiple rainwater harvesting sites.
- Estimate rainwater collection potential.
- Monitor storage capacity, overflow, and unmet water demand.
- Encourage sustainable water conservation practices.

## ✨ Features

- **Dashboard:** View key water harvesting and usage statistics.
- **Rainfall Logging:** Record rainfall measurements and dates.
- **Water Usage Tracking:** Record water consumption for different purposes.
- **Site Management:** Add and manage harvesting sites.
- **Rainwater Estimator:** Estimate potential annual rainwater collection.
- **Tank Monitoring:** Track storage capacity and related water statistics.
- **Data Visualization:** View monthly harvested water and usage comparisons.
- **Responsive Interface:** Access the application through a web browser.

## 🛠️ Technologies Used

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, Flask
- **Testing:** Pytest
- **Deployment:** Render
- **Version Control:** Git and GitHub

## ⚙️ Installation and Setup

### Prerequisites

Install the following software:

- Python 3
- Git
- A web browser

### Step 1: Clone the Repository

```bash
git clone https://github.com/pavanimandati13-jpg/water-harvesting-tracker.git
```

### Step 2: Open the Project Folder

```bash
cd water-harvesting-tracker
```

### Step 3: Create a Virtual Environment

```bash
python -m venv venv
```

### Step 4: Activate the Virtual Environment

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 6: Run the Application

```bash
python app.py
```

Open the following address in your browser:

http://127.0.0.1:5000

## 🧪 Testing

Run the test suite with:

```bash
pytest
```

## 🌧️ Rainwater Harvesting Calculation

A basic estimate of rainwater collection potential can be calculated using:

**Potential Rainwater (Litres) = Rainfall (mm) × Roof Area (m²) × Runoff Coefficient**

For example, if annual rainfall is 1,000 mm, the roof area is 50 m², and the runoff coefficient is 0.8:

`1,000 × 50 × 0.8 = 40,000 litres`

This is a theoretical estimate. Actual collection depends on rainfall distribution, roof conditions, collection efficiency, storage capacity, and overflow.

## 📂 Project Structure

```text
water-harvesting-tracker/
├── app.py
├── requirements.txt
├── README.md
├── Dockerfile
├── Procfile
├── templates/
│   └── index.html
└── tests/
    └── test_app.py
```

## 🌱 Applications

- College and educational projects
- Rainwater harvesting awareness
- Rooftop water collection planning
- Water consumption monitoring
- Sustainable water resource management

## 🔮 Future Enhancements

- Weather API integration for rainfall forecasts
- Database integration for persistent data storage
- User authentication and personalized dashboards
- Downloadable reports and historical analytics
- Alerts for low tank levels and high overflow
- Support for multiple buildings and locations

## 🤝 Contribution

Contributions and suggestions are welcome. Fork the repository, create a feature branch, and submit a pull request with your improvements.

## 📄 License

This project is intended for educational and demonstration purposes. Add a suitable open-source license to the repository if you wish to formally permit reuse and redistribution.

---

**Developed as a water conservation and rainwater management project.** 💧
