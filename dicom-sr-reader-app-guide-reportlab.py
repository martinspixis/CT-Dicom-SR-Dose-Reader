from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_pdf_report(save_path):
    styles = getSampleStyleSheet()
    
    doc = SimpleDocTemplate(save_path, pagesize=letter)
    elements = []
    
    # Add title
    elements.append(Paragraph("DICOM SR Dose Data Reader - Application Guide", styles["Heading1"]))
    elements.append(Spacer(1, 12))
    
    # Add application overview
    elements.append(Paragraph("Application Overview", styles["Heading2"]))
    elements.append(Paragraph("The DICOM SR Dose Data Reader is a Python-based application designed to extract and analyze radiation dose data from DICOM Structured Reports (DICOM SR) files. This tool is particularly useful for healthcare professionals, medical physicists, and radiation safety officers who need to monitor and evaluate patient radiation exposure during medical imaging procedures.", styles["BodyText"]))
    elements.append(Spacer(1, 12))
    
    # Add key features and functionality
    elements.append(Paragraph("Key Features and Functionality", styles["Heading2"]))
    elements.append(Paragraph("- DICOM SR File Processing: The application can scan a specified directory (including subdirectories) for DICOM SR files, extract relevant patient and dose data, and process the information.", styles["BodyText"]))
    elements.append(Paragraph("- Dose Data Extraction: The tool extracts various dose-related parameters from the DICOM SR files, such as Acquisition Protocol, Total DLP (Dose Length Product), and CTDIvol (CT Dose Index).", styles["BodyText"]))
    elements.append(Paragraph("- Data Analysis and Reporting: The application performs in-depth analysis of the extracted data, including calculating the average DLP and CTDIvol values, comparing the patient dose data with Diagnostic Reference Levels (DRLs), and generating detailed reports.", styles["BodyText"]))
    elements.append(Paragraph("- User-friendly Interface: The application features a clean and intuitive graphical user interface (GUI) built using the Tkinter library.", styles["BodyText"]))
    elements.append(Paragraph("- Configurable DRL Settings: The application allows users to configure the Diagnostic Reference Levels (DRLs) for various examination protocols through a separate DRL Configuration window.", styles["BodyText"]))
    elements.append(Spacer(1, 12))
    
    # Add installation and setup
    elements.append(Paragraph("Installation and Setup", styles["Heading2"]))
    elements.append(Paragraph("1. Python Installation: Ensure you have Python 3.x installed on your system.", styles["BodyText"]))
    elements.append(Paragraph("2. Install Required Libraries: The application requires the following Python libraries to be installed: pydicom, pandas, tkinter, tkcalendar, xhtml2pdf, jinja2. You can install these libraries using pip, the Python package installer. Open a terminal or command prompt and run the following command:\n\npip install pydicom pandas tkinter tkcalendar xhtml2pdf jinja2", styles["BodyText"]))
    elements.append(Paragraph("3. Download the DICOM SR Dose Data Reader Code: Obtain the Python script (e.g., main.py) containing the DICOMSRReaderApp class and any supporting files (e.g., drl_config.py, drl_config_window.py) from the provided source.", styles["BodyText"]))
    elements.append(Paragraph("4. Run the Application: Navigate to the directory containing the DICOM SR Dose Data Reader code and run the main script:\n\npython main.py", styles["BodyText"]))
    elements.append(Spacer(1, 12))
    
    # Add usage and reporting
    elements.append(Paragraph("Usage and Reporting", styles["Heading2"]))
    elements.append(Paragraph("1. Select the Directory: In the application's GUI, click the \"Browse\" button to select the directory containing the DICOM SR files you want to analyze.", styles["BodyText"]))
    elements.append(Paragraph("2. Set Date Range (optional): If desired, use the calendar widgets to specify a date range for the analysis.", styles["BodyText"]))
    elements.append(Paragraph("3. Process Files: Click the \"Process Files\" button to initiate the data extraction and analysis workflow.", styles["BodyText"]))
    elements.append(Paragraph("4. Save Reports: Once the processing is complete, the application will prompt you to save the generated Excel (XLSX) and PDF reports. The reports will include the detailed dose data analysis and DRL comparisons.", styles["BodyText"]))
    elements.append(Paragraph("5. Configure DRL Settings: If needed, you can access the DRL Configuration window by clicking the \"DRL Configuration\" button. This allows you to customize the Diagnostic Reference Levels for the various examination protocols.", styles["BodyText"]))
    elements.append(Spacer(1, 12))
    
    # Add disclaimer
    elements.append(Paragraph("Disclaimer", styles["Heading2"]))
    elements.append(Paragraph("The use of the DICOM SR Dose Data Reader application is at the user's own risk and responsibility. If the user wishes to use the program for commercial purposes or to suggest improvements, please contact the program author, medical physicist Martin Piksis, at martins.piksis@gmail.com.", styles["BodyText"]))
    
    # Generate PDF
    doc.build(elements)
    print(f"PDF guide generated: {save_path}")

# Example usage
generate_pdf_report("dicom_sr_reader_guide.pdf")
