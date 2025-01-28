Application Overview
The DICOM SR Dose Data Reader is a Python-based application designed to extract and analyze
radiation dose data from DICOM Structured Reports (DICOM SR) files. This tool is particularly useful
for healthcare professionals, medical physicists, and radiation safety officers who need to monitor and
evaluate patient radiation exposure during medical imaging procedures.
Key Features and Functionality
- DICOM SR File Processing: The application can scan a specified directory (including subdirectories)
for DICOM SR files, extract relevant patient and dose data, and process the information.
- Dose Data Extraction: The tool extracts various dose-related parameters from the DICOM SR files,
such as Acquisition Protocol, Total DLP (Dose Length Product), and CTDIvol (CT Dose Index).
- Data Analysis and Reporting: The application performs in-depth analysis of the extracted data,
including calculating the average DLP and CTDIvol values, comparing the patient dose data with
Diagnostic Reference Levels (DRLs), and generating detailed reports.
- User-friendly Interface: The application features a clean and intuitive graphical user interface (GUI)
built using the Tkinter library.
- Configurable DRL Settings: The application allows users to configure the Diagnostic Reference Levels
(DRLs) for various examination protocols through a separate DRL Configuration window.
