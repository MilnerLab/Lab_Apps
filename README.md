# Project Setup & Useful Commands

This repository contains several Python tools and apps used in the lab.  
Below is a quick reference for setting up the environment and running the programs.

---

## 1. Virtual Environment

### 1.1 Create / check / activate environment

Use the provided PowerShell script:

```powershell
. .\setup_env.ps1
````

This script will:

* Create the `.venv` virtual environment if it does not exist
* Activate the virtual environment
* Install / update the required packages
* Install / update the recommended extensions

### 1.2 Manually activate existing venv (if needed)

If you need to activate the environment manually:

```powershell
.\.venv\Scripts\Activate.ps1
```
---

## 4. Running the Applications

All applications are started via Python’s module syntax from the repository root.

```powershell
python -m apps.plot_bot.script
```
```powershell
python -m apps.scan_averaging.script
```
```powershell
python -m apps.single_scan.script
```
```powershell
python -m apps.stft_analysis.script
```
---
