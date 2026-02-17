# The Deep Work Guardian

### AI Agent — Project Documentation

**Course:** Artificial Intelligence Practical Week 1 Project

---

# Table of Contents

- [1. Project Overview](#1-project-overview)
- [2. The Problem](#2-the-problem)
- [3. The Solution](#3-the-solution)
- [4. Agent Classification](#4-agent-classification)
- [5. PEAS Analysis](#5-peas-analysis)
- [6. System Architecture](#6-system-architecture)
- [7. Functional Requirements](#7-functional-requirements)
- [8. Task Distribution](#8-task-distribution)
- [9. Shared Responsibilities](#9-shared-responsibilities)
- [10. Suggested Tech Stack](#10-suggested-tech-stack)

---

## 1. Project Overview

The **Deep Work Guardian** is a context-aware (it knows its environment and can adapt to it), goal-based (it has a specific goal and acts to achieve it) AI agent that runs on a laptop. It monitors both the **Physical Environment** (e.g. the student's posture, the background noise, and nearby people) and the **Digital Environment** (e.g. active windows, battery status) to automatically keep the user focused, comfortable, and productive during long study or work sessions.

Instead of the user manually managing distracitons, ergonomics (comfortable and healthy work setup), privacy, and power. The agent handles all of it automatically in the background.

---

## 2. The Problem

Students during long study sessions face **5 recurring problems** that negatively affect their productivity:

| #   | Problem                                                 | Impact                |
| --- | ------------------------------------------------------- | --------------------- |
| 1   | Sitting too close to the screen / bad posture           | Eye strain, back pain |
| 2   | Someone looking over your shoulder at sensitive work    | Privacy breach        |
| 3   | Noisy environment breaking concentration                | Loss of focus         |
| 4   | Laptop unplugged, battery draining fast                 | Disturbs Focus        |
| 5   | Accidentally spending too long on social media or games | Wasted study time     |

> **The Deep Work Guardian** is a solution to these recurring problems.

---

## 3. The Solution

A **single backgound agent** divided into **5 subsystems**, each handled by one team member. Each subsystem monitors a specific sensor and triggers a specific action when a problem is detected.

All 5 subsystems share one common goal:

> **"Maintain an optimal work environment for the user at all times."**

---

## 4. Agent Classification

| Property             | Detail                                    |
| -------------------- | ----------------------------------------- |
| **Agent Type**       | Goal-Based Agent                          |
| **Goal**             | Optimal Work Environment                  |
| **Environment**      | Laptop desktop + immediate physical space |
| **Environment Type** | Partially Observable, Dynamic, Continuous |

---

## 5. PEAS Analysis

**P - Performance Measures:** How do we know the agent is doing well?

- User maintains safe screen distance throughout the session.
- No unauthorized person views the screen.
- Distracting background noise stays below distraction threshold.
- Battery does not drop to critical levels unexpectedly.
- Time spent under distracting apps stays under 5 minutes.

**E - Environment:**

The laptop hardware and software system, and the user's physical workspace (desk area, noise, surrounding people, etc.).

**A - Actuators:** What does the agent do?

- System notificaiton popups
- Screen blur or window minimizer
- OS audio controller
- OS window manager
- Display and theme settings controller
- Process / app manager

**S - Sensors:** What does the agent see?

- Webcam (face detection + background face detection)
- Microphone (background noise decibel level)
- Battery or Charger Status API
- Active window title monitor

---

## 6. System Architecture

```
┌─────────────────────────────────────────────────────┐
│                  DEEP WORK GUARDIAN                  │
│                  [ Goal-Based Agent ]                │
└──────────────────────────┬──────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   SENSORS            PROCESSING          ACTUATORS
  (Inputs)         (Decision Logic)       (Outputs)
        │                  │                  │
  ┌─────┴─────┐      ┌─────┴──────┐     ┌────┴─────┐
  │ Webcam    │      │ Condition  │     │ Notify   │
  │ Microphone│ ───► │ Check per  │───► │ Blur     │
  │ Battery   │      │ subsystem  │     │ Audio    │
  │ Window    │      └────────────┘     │ Settings │
  │ Title     │                         │ Kill App │
  └───────────┘                         └──────────┘
```

---

## 7. Functional Requirements

These are the specific behaviors the agent **MUST** perform:

### Member 1 - Ergonomics (Posture and a healthy work environment) Monitor

- **Must** access the webcam in real time
- **Must** detect and measure the distance of the user's face from the screen using face detection
- **Must** trigger a popup notification if the user's face is too close (threshold: ~50 cm)
- **Must** repeat the warning every 2 minutes if the problem persists
- **Must not** store or record any webcam footage

### Member 2 - Privacy Sheild

- **Must** use the webcam to scan the background for additional faces
- **Must** detect if a second person appears behind or beside the user
- **Must** instantly minimize all open windows OR apply a screen blur overlay when triggered
- **Must** restore the screen automatically once the second person leaves
- **Must not** conflict with Member 1's webcam usage (both can share the same camera feed)

### Member 3 - Atmosphere Controller

- **Must** continuously read the microphone input and measure decibel (dB) level
- **Must** define a noise threshold (e.g., above 60 dB = too loud)
- **Must** automatically play white noise or lo-fi audio through the OS when the threshold is exceeded
- **Must** stop the audio automatically when the environment becomes quiet again
- Allow the user to configure the threshold and audio type (optional)

### Member 4 - Power Optimizer

- **Must** monitor the laptop's battery percentage and charging status
- **Must** detect when the charger is unplugged
- **Must** automatically switch the OS to Dark Mode when unplugged
- **Must** lower screen brightness and/or refresh rate when unplugged
- **Must** restore original settings when the charger is plugged back in

### Member 5 - Distraction Blocker

- **Must** read the title of the currently active/foreground window every few seconds
- **Must** maintain a blocklist of distracting apps (e.g., YouTube, Instagram, games)
- **Must** start a timer when a blocklisted app becomes active
- **Must** minimize or close the app if it remains active for more than 5 continuous minutes

## 8. Task Distribution

| Member       | Subsystem             | Sensor Used                        | Actuator (Action)                   |
| ------------ | --------------------- | ---------------------------------- | ----------------------------------- |
| **Muhammad** | Ergonomics Monitor    | Webcam — face distance             | System notification popup           |
| **Abdulla**  | Privacy Shield        | Webcam — background face detection | Window minimizer / screen blur      |
| **Shabaz**   | Atmosphere Controller | Microphone — ambient dB level      | OS audio player                     |
| **Peshawa**  | Power Optimizer       | Battery / charger status           | Display settings + Dark Mode toggle |
| **Rasyar**   | Distraction Blocker   | Active window title                | Process / app manager               |

---

## 9. Shared Responsibilities

- **Integration:** All 5 subsystems must run simultaneously and coordinate with each other without crashing.
- **Main Runner Script:** One `main.py` or any other file that launches all 5 subsystems as parallel threads or processes.

---

## 10. Suggested Tech Stack

| Tool                      | Purpose                                          |
| ------------------------- | ------------------------------------------------ |
| `Python 3.x`              | Main programming language                        |
| `OpenCV`                  | Webcam access and face detection (Members 1 & 2) |
| `PyAudio` / `sounddevice` | Microphone input (Member 3)                      |
| `pygame` / `playsound`    | Audio playback (Member 3)                        |
| `psutil`                  | Battery status monitoring (Member 4)             |
| `pygetwindow` / `psutil`  | Active window detection (Member 5)               |
| `plyer` / `tkinter`       | Desktop notifications                            |
| `threading`               | Running all subsystems in parallel               |

---

_Documentation prepared for internal team use. Last updated: February 2026._
