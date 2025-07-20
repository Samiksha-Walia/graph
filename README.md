
# 🌦️ MeteoGraph – Weather Data Visualization Platform

**MeteoGraph** is a Django-based web application developed as part of an internship project at the India Meteorological Department (IMD). The platform empowers users to upload weather data in CSV format and dynamically generate insightful meteorological visualizations including temperature trends, wind rose diagrams, and more.


## 📌 Features

* 📁 **CSV File Upload**
  Upload structured weather data files in `.csv` format through a user-friendly web interface.

* 📊 **Dynamic Graph Generation**
  Generate various meteorological plots such as:

  * Yearly Mean Temperature
  * Mean of Maximum Daily Temperatures
  * Daily Maximum Temperatures for Each Month
  * Wind Rose Diagrams (monthly)
  * Hourly Mean Plots with Error Bars (by month and column)

* 🌬️ **Wind Rose Visualization**
  Interactive and visual representation of wind speed and direction distribution.

* 📥 **Download Options**
  Users can download:

  * Generated plots (PNG)
  * Aggregated analysis data (CSV)

* 🌐 **Responsive Web UI**
  Clean, minimal, and responsive interface with a weather-themed background and fixed navigation bar.



## 🛠️ Technologies Used

* **Backend**: Django (Python)
* **Frontend**: HTML, CSS (custom styling)
* **Data Analysis**: Pandas, NumPy
* **Plotting**: Matplotlib, Seaborn, WindroseAxes
* **Visualization Rendering**: Non-interactive Matplotlib backend (`Agg`)






## 🔧 How to Run Locally

### 1. Clone the Repository

```bash
git clone https://github.com/Samiksha-Walia/graph.git
cd meteograph
```

### 2. Install Dependencies

It’s recommended to use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # For Linux/macOS
venv\Scripts\activate     # For Windows

pip install -r requirements.txt
```

If `requirements.txt` is missing, install core libraries manually:

```bash
pip install django pandas matplotlib seaborn windrose
```

### 3. Run the Server

```bash
python manage.py runserver
```

Then, go to `http://127.0.0.1:8000/` in your browser.



## 📑 Usage Guide

1. **Upload CSV** from homepage.
2. **Select Graph Type** (e.g., yearly mean, wind rose, etc.).
3. **Choose Column** (for hourly means).
4. **View Results** and download plots or processed CSV files.

> ✅ Only CSV files up to 5MB are supported. Ensure the format includes `DATE`, `TIME(UTC)`, and relevant weather columns like `TEMP(C)`, `WIND_SPEED(kt)`, and `WIND_DIR(deg)`.

## 👨‍💻 Contributors

* **Samiksha Walia** – Intern @ IMD
[GitHub](https://github.com/Samiksha-Walia) • [LinkedIn](https://linkedin.com/in/samiksha-walia) 


* **Samdisha Walia** – Intern @ IMD
[GitHub](https://github.com/Samdisha-Walia) • [LinkedIn](https://linkedin.com/in/samdisha-walia) 


* **Sahil Thakur** – Intern @ IMD
[GitHub](https://github.com/sahilrajput280) • [LinkedIn](https://www.linkedin.com/in/sahil-thakur-ab8602239/) 


