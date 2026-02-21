# Deep Work Guardian

**Artificial Intelligence Module — Week 1 Project**

The Deep Work Guardian is a goal-based AI agent designed to maintain an optimal, distraction-free, and ergonomic work environment. By monitoring both physical and digital sensors, the agent automates the management of productivity, privacy, and health.

---

## Overview

During long study sessions, productivity is often hampered by five key factors: poor posture, privacy risks, environmental noise, power management, and digital distractions. This agent addresses all five through a unified, multi-threaded system.

---

## Agent Classification

| Property        | Details                                               |
| --------------- | ----------------------------------------------------- |
| **Type**        | Goal-Based Agent                                      |
| **Goal**        | Maintain an optimal work environment                  |
| **Environment** | Laptop desktop + immediate physical space             |
| **Sensors**     | Webcam, Microphone, Battery API, Window Title Monitor |

---

## System Architecture

The system utilizes a **Shared State Pattern**. A central `SharedState` object holds all sensor data and flags, protected by thread locks to ensure data integrity while five specialized agents run in parallel threads.

### Subsystems & Team Roles

| Member   | Subsystem             | Responsibility                                               |
| -------- | --------------------- | ------------------------------------------------------------ |
| Muhammad | Ergonomics Monitor    | Monitors face distance via webcam to prevent eye strain.     |
| Abdulla  | Privacy Shield        | Detects background faces and blurs the screen for privacy.   |
| Shabaz   | Atmosphere Controller | Measures dB levels and plays white noise when it's too loud. |
| Peshawa  | Power Optimizer       | Toggles Dark Mode and lowers brightness when unplugged.      |
| Rasyar   | Distraction Blocker   | Blocks social media/games after 5 minutes of continuous use. |

---

## Installation & Setup

1. Clone the repository (if not already done).
2. Navigate to the project folder:

```bash
cd week-1-project/deep-work-guardian
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

> **Note:** Ensure you have `OpenCV`, `PyAudio`, `psutil`, and `pygetwindow` installed.

---

## 🚦 How to Run

Launch the main agent by running:

```bash
python main.py
```

The agent will initialize the webcam and start all five monitoring threads. You can see the real-time status of your environment in the terminal output.

---

## Privacy Note

The Deep Work Guardian processes webcam and microphone data **locally in real-time**. No data is stored, recorded, or transmitted to external servers.
