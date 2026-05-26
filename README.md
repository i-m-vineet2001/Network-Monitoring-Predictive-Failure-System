# 🌐 Network Monitoring & Predictive Failure System

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-Active-success.svg)]()

**A comprehensive real-time network monitoring solution with predictive failure detection and intuitive GUI visualization**

[Features](#features) • [Installation](#installation) • [Quick Start](#quick-start) • [Configuration](#configuration) • [Architecture](#architecture)

</div>

<div align="center">

![Project Screenshot](https://via.placeholder.com/960x320.png?text=Network+Monitoring+Dashboard+Placeholder)

## </div>

## 📋 Overview

The **Network Monitoring & Predictive Failure System** is a sophisticated tool designed to monitor network health, track node availability, and predict potential network failures before they occur. Built with Python and featuring a modern PySide6 GUI, it provides real-time insights into your network infrastructure.

Whether you're managing a small office network or a large enterprise infrastructure, this system helps you maintain uptime and proactively address network issues.

---

## ✨ Features

### 🔍 Core Monitoring

- **Real-time Network Monitoring** - Continuous monitoring of network nodes and hosts
- **Ping-based Health Checks** - Lightweight ICMP ping monitoring for quick responsiveness
- **Multi-node Support** - Monitor multiple network nodes simultaneously
- **Availability Tracking** - Historical data on node uptime and downtime

### 📊 Analytics & Visualization

- **Interactive Dashboards** - Real-time charts and metrics visualization
- **Network Health Summary** - Quick overview of network status
- **Node Availability Charts** - Visual representation of uptime trends
- **Performance Metrics** - Detailed statistics and analytics

### 🚨 Alerts & Notifications

- **Intelligent Alerting** - Smart notifications for network anomalies
- **Alert Filters** - Type and time-range dropdown filters in the alert panel
- **Notification Control** - Bell toggle to enable or disable alert popups
- **History View** - Review recent alert events with severity and latency
- **AI Alerts** - Predictive failure alerts from ML models

### 🤖 Predictive Capabilities

- **Failure Prediction** - ML-based prediction of potential network failures
- **Trend Analysis** - Identify patterns in network behavior
- **Proactive Maintenance** - Get ahead of issues before they impact users

### 💾 Data Management

- **Persistent Storage** - Store monitoring data for historical analysis
- **Logging** - Comprehensive system logging for debugging
- **Export Capabilities** - Export data for further analysis

### 🛠️ Recent Fixes

- Fixed alert panel bell toggle so notifications can be enabled/disabled reliably
- Restored alert badge rendering and prevented `main.py` startup crashes
- Smooth dropdown filter styling added for alert type and time range selection
- Added production-ready simulated node support with Controller heartbeat ingestion
- Fixed node list auto-scroll on alert refresh and expanded sidebar node panel height

### 🎛️ New Production Behavior

- `src/main.py` now starts:
  - the real node monitor for `real_nodes`
  - the Controller server on port `9000`
  - simulated node clients for all `sim_nodes`
- Simulated nodes now send real heartbeat JSON to the Controller and generate actual log entries
- GUI reads `logs/log.txt` from both real and simulated nodes, instead of relying on fallback config-only display

### 🎨 User Interface

- **Intuitive GUI** - Built with PySide6 for a modern, responsive interface
- **Real-time Updates** - Live data refresh without page reloads
- **Cross-platform** - Works on Windows, macOS, and Linux

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11** or higher
- **pip** (Python package manager)
- Network connectivity
- Sufficient permissions for ICMP ping operations

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/i-m-vineet2001/Network-Monitoring-Predictive-Failure-System.git
   cd Network-Monitoring-Predictive-Failure-System
   ```

2. **Create a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the system**

   ```bash
   nano src/config.py
   ```

   - Update `src/config.py` to define monitored nodes, thresholds, and alert settings.
   - Optionally use `.env` for environment-specific values loaded by `src/main.py`.

5. **Run the application**

   ```bash
   python src/main.py
   ```

   > Note: The current update automatically starts the Controller and all configured `sim_nodes` when you run `src/main.py`.

---

## 📖 Usage

### Starting the Monitor

```bash
python src/main.py
```

> This starts the monitoring engine, the Controller, and all simulated nodes automatically.

### Launch GUI Only

```bash
python src/run_gui.py
```

The GUI will launch with the main dashboard showing:

- Network health status
- Active node monitoring
- Real-time performance metrics
- Alert notifications

### Configuration

The application reads settings from `src/config.py`.

Edit `src/config.py` to customize monitored nodes, latency thresholds, and alert behavior.

Example configuration:

```python
LATENCY_THRESHOLD = 30  # ms threshold for degraded latency

nodes = {
    "node_1_phone1": {
        "ip": "192.168.1.33",
        "state": "UP",
        "network_type": "wifi",
        "fail_count": 0,
        "last_latency": None,
        "ping_blocked": True,
        "last_ml_alert": None,
    },
    "node_2_laptop": {
        "ip": "192.168.1.35",
        "state": "UP",
        "network_type": "wifi",
        "fail_count": 0,
        "last_latency": None,
        "ping_blocked": False,
        "last_ml_alert": None,
    },
}
```

### Monitoring Nodes

1. **Add Nodes** - Configure nodes in the settings panel
2. **Monitor** - Watch real-time status in the dashboard
3. **Analyze** - Review charts and historical data
4. **Act** - Respond to alerts and notifications

## 🔧 Configuration Guide

The system is configured through `src/config.py`.

Edit `src/config.py` to define `LATENCY_THRESHOLD`, monitored `nodes`, and alert-related flags such as `ping_blocked`.

Example configuration:

```python
LATENCY_THRESHOLD = 30  # ms threshold for degraded latency

nodes = {
    "node_1_phone1": {
        "ip": "192.168.1.33",
        "state": "UP",
        "network_type": "wifi",
        "fail_count": 0,
        "last_latency": None,
        "ping_blocked": True,
        "last_ml_alert": None,
    },
    "node_2_laptop": {
        "ip": "192.168.1.35",
        "state": "UP",
        "network_type": "wifi",
        "fail_count": 0,
        "last_latency": None,
        "ping_blocked": False,
        "last_ml_alert": None,
    },
}
```

### GUI Settings

Configure via the application settings panel:

- Refresh rate
- Chart update interval
- Alert notification style
- Data retention period

---

## 📊 Performance Metrics

The system tracks and displays:

- **Response Time** - Average ping response time
- **Packet Loss** - Percentage of failed packets
- **Availability** - Uptime percentage over time
- **Status** - Current node status (Online/Offline)
- **Last Seen** - Timestamp of last successful check

---

## 🚨 Alert System

### Alert Types

- **Node Failure** - Node became unreachable
- **High Latency** - Response time exceeds threshold
- **Intermittent Failures** - Inconsistent connectivity
- **Recovery** - Node came back online

### Alert Actions

- Visual notifications in GUI
- Log entries
- Customizable thresholds
- Alert history and archival

---

## 🏗️ Project Structure

This repository is organized to support monitoring, simulation, GUI, prediction, and persistence.

```
Network Monitoring & Predictive Failure System/
├── README.md
├── PROJECT_UNDERSTANDING.md
├── requirements.txt
├── .env                   # optional runtime configuration
├── logs/
│   └── log.txt            # monitoring and heartbeat logs
├── model/
│   ├── predictor.py       # ML prediction logic
│   ├── n_w_model.py
│   ├── n_w_modelV3f_withMetric.py
│   ├── failurePred_modelv1.py
│   ├── export_logs.py
│   ├── logs.csv
│   ├── updated_logs.csv
│   └── network_failure_predictor.ipynb
├── gui/
│   ├── gui.py
│   ├── chart.py
│   ├── global_chart.py
│   ├── node_availability_chart.py
│   ├── node_pie_chart.py
│   ├── alerts.py
│   ├── summary.py
│   ├── widgets.py
│   ├── login_window.py
│   ├── signup_window.py
│   ├── theme.py
│   ├── data.py
│   └── tempCodeRunnerFile.py
├── src/
│   ├── main.py
│   ├── monitor.py
│   ├── ping.py
│   ├── sim_node.py
│   ├── controller.py
│   ├── network_profiles.py
│   ├── config.py
│   ├── sim_node.py
│   └── db/
│       ├── __init__.py
│       ├── file_log_service.py
│       ├── log_service.py
│       ├── mongo.py
│       └── user_service.py
└── project pic/           # project graphics and presentation assets
```

### Key responsibilities

- `src/main.py` — starts the GUI, monitor loop, Controller, and simulated nodes
- `src/monitor.py` — performs real node ping checks and state evaluation
- `src/controller.py` — receives simulated node heartbeats and writes logs
- `src/sim_node.py` — simulates node behavior and generates heartbeat data
- `src/config.py` — defines monitored nodes, thresholds, and simulation metadata
- `gui/` — contains PySide6 UI components and dashboard logic
- `model/` — contains ML models, data exports, and analysis notebooks
- `db/` — contains local file and MongoDB logging services

---

## 📦 Dependencies

See `requirements.txt` for complete list:

- **PySide6** - Modern GUI framework with Qt Charts for visualizations
- **pymongo** - Optional MongoDB logging support
- **python-dotenv** - Environment variable loading for optional runtime settings
- **scikit-learn** - Machine learning models for predictive alerts
- **pandas** - Data analysis and time series handling
- **matplotlib** - Plotting and chart generation
- **seaborn** - Statistical data visualization

Install all dependencies:

```bash
pip install -r requirements.txt
```

---

## 🐛 Troubleshooting

### Issue: Permission Denied (Ping)

**Solution:** Run with elevated privileges or configure ICMP permissions

```bash
sudo python src/main.py
```

### Issue: GUI Not Launching

**Solution:** Ensure PySide6 is installed correctly

```bash
pip install --upgrade PySide6
```

### Issue: Configuration Not Loading

**Solution:** Verify `src/config.py` is valid Python and contains the expected `LATENCY_THRESHOLD` and `nodes` definitions.

### Issue: High CPU Usage

**Solution:** Reduce the number of active monitored nodes or adjust the polling frequency in application logic to lower resource usage.

---

## 📈 Use Cases

### 🏢 Enterprise Networks

- Monitor critical infrastructure
- Proactive failure detection
- SLA compliance tracking

### 🖥️ Data Centers

- Real-time server health monitoring
- Automated failure alerts
- Performance analytics

### 🏠 Home Networks

- Track internet connectivity
- Monitor IoT devices
- Network troubleshooting

### 🔬 Network Research

- Collect network statistics
- Analyze failure patterns
- Predictive modeling

---

## 🔐 Security Considerations

- **ICMP Firewall Rules** - Ensure ICMP is allowed for monitored nodes
- **Access Control** - Restrict GUI access to authorized users
- **Data Privacy** - Logs contain network information; store securely
- **Configuration Security** - Protect config files with appropriate permissions

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup

```bash
git clone https://github.com/i-m-vineet2001/Network-Monitoring-Predictive-Failure-System.git
cd Network-Monitoring-Predictive-Failure-System
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2026 Network Monitoring Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files...
```

---

## 👨‍💼 About the Author

**Vineet Patel**

- Email: [your-email@example.com]
- GitHub: [@i-m-vineet2001](https://github.com/i-m-vineet2001)
- LinkedIn: [Your LinkedIn Profile]

---

## 📞 Support & Contact

For issues, questions, or suggestions:

- **Issues** - [GitHub Issues](https://github.com/i-m-vineet2001/Network-Monitoring-Predictive-Failure-System/issues)
- **Email** - your-email@example.com
- **Documentation** - See [WIKI](https://github.com/i-m-vineet2001/Network-Monitoring-Predictive-Failure-System/wiki)

---

## 🙏 Acknowledgments

- PySide6 team for the excellent GUI framework
- Python community for amazing libraries
- Contributors and users for feedback and suggestions

---

## 📚 Additional Resources

- [Python Documentation](https://docs.python.org/3/)
- [PySide6 Documentation](https://doc.qt.io/qtforpython/)
- [Python Documentation](https://docs.python.org/3/)
- [Network Monitoring Best Practices](https://en.wikipedia.org/wiki/Network_monitoring)

---

<div align="center">

### ⭐ If you found this project helpful, please consider giving it a star!

Made with ❤️ by [Vineet Patel](https://github.com/i-m-vineet2001)

</div>
