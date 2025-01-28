# main.py
import os
import pydicom
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, date
import warnings
from tkcalendar import DateEntry
from xhtml2pdf import pisa
from jinja2 import Template
from drl_config import DRLConfiguration
from drl_config_window import DRLConfigWindow

warnings.filterwarnings('ignore', category=UserWarning)

class DICOMSRReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CT DICOM SR Dose Data Reader")
        self.root.geometry("800x400")
        self.drl_config = DRLConfiguration()
        self.create_variables()
        self.setup_gui()
        
    def setup_gui(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(padx=20, pady=20)
        
        title_label = tk.Label(main_frame, 
                             text="All credits goes to Liepaja Regional Hospital \nMedical Physicists :)\nCT DICOM SR Dose Reader",
                             font=("Helvetica", 16, "bold"),
                             fg="green")
        title_label.pack(pady=10)
        
        content_frame = tk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(content_frame, 
                text="Select Directory with DICOM SR Files",
                font=("Helvetica", 10)).pack(pady=10)
        
        browse_btn = tk.Button(content_frame, 
                             text="Browse", 
                             command=self.select_directory,
                             width=20,
                             relief=tk.GROOVE)
        browse_btn.pack()
        
        tk.Label(content_frame, 
                textvariable=self.path_var, 
                wraplength=600).pack(pady=5)

        # Date range frame with calendar widgets
        date_frame = tk.Frame(content_frame)
        date_frame.pack(pady=5)
        
        tk.Label(date_frame, text="Date Range:", font=("Helvetica", 10)).pack(side=tk.LEFT, padx=5)
        
        self.date_from = DateEntry(date_frame, width=12,
                                 background='darkblue', foreground='white',
                                 date_pattern='dd.mm.yyyy',
                                 locale='lv_LV')
        self.date_from.pack(side=tk.LEFT, padx=2)
        
        tk.Label(date_frame, text="to", font=("Helvetica", 10)).pack(side=tk.LEFT, padx=2)
        
        self.date_to = DateEntry(date_frame, width=12,
                               background='darkblue', foreground='white',
                               date_pattern='dd.mm.yyyy',
                               locale='lv_LV')
        self.date_to.pack(side=tk.LEFT, padx=2)
        
        clear_btn = tk.Button(date_frame, text="Clear Dates", 
                            command=self.clear_dates,
                            relief=tk.GROOVE)
        clear_btn.pack(side=tk.LEFT, padx=10)

        # DRL Configuration button
        drl_config_btn = tk.Button(content_frame, 
                                 text="DRL Configuration", 
                                 command=self.open_drl_config,
                                 width=20,
                                 relief=tk.GROOVE)
        drl_config_btn.pack(pady=5)
        
        tk.Checkbutton(content_frame, 
                      text="Scan Subdirectories", 
                      variable=self.scan_subdirs,
                      font=("Helvetica", 10)).pack(pady=5)
        
        self.process_btn = tk.Button(content_frame, 
                                   text="Process Files", 
                                   command=self.process_files,
                                   state=tk.DISABLED,
                                   width=20,
                                   relief=tk.GROOVE)
        self.process_btn.pack(pady=10)
        
        tk.Label(content_frame, 
                textvariable=self.status_var,
                font=("Helvetica", 10)).pack(pady=5)

    def create_variables(self):
        self.path_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.scan_subdirs = tk.BooleanVar(value=True)

    def find_dicom_files(self, directory):
        dicom_files = []
        try:
            if self.date_from.get():
                date_from = datetime.strptime(self.date_from.get(), '%d.%m.%Y').date()
            else:
                date_from = None
                
            if self.date_to.get():
                date_to = datetime.strptime(self.date_to.get(), '%d.%m.%Y').date()
            else:
                date_to = None
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Invalid date selection")
            return []
            
        if self.scan_subdirs.get():
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith(('.dcm', '.DCM')):
                        file_path = os.path.join(root, file)
                        try:
                            dcm = pydicom.dcmread(file_path)
                            study_date = dcm.get('StudyDate', '')
                            if study_date:
                                file_date = datetime.strptime(study_date, '%Y%m%d').date()
                                if ((not date_from or file_date >= date_from) and 
                                    (not date_to or file_date <= date_to)):
                                    dicom_files.append(file_path)
                        except:
                            continue
        else:
            for file in os.listdir(directory):
                if file.endswith(('.dcm', '.DCM')):
                    file_path = os.path.join(directory, file)
                    try:
                        dcm = pydicom.dcmread(file_path)
                        study_date = dcm.get('StudyDate', '')
                        if study_date:
                            file_date = datetime.strptime(study_date, '%Y%m%d').date()
                            if ((not date_from or file_date >= date_from) and 
                                (not date_to or file_date <= date_to)):
                                dicom_files.append(file_path)
                    except:
                        continue
        return dicom_files

    def process_files(self):
        directory = self.path_var.get()
        dicom_files = self.find_dicom_files(directory)
        
        if not dicom_files:
            messagebox.showerror("Error", "No DICOM files found")
            return
        
        results = []
        for file_path in dicom_files:
            data = self.extract_patient_dose_data(file_path)
            if data:
                results.append(data)
        
        if not results:
            messagebox.showerror("Error", "No valid DICOM SR files found")
            return

        # Generate filename based on date range
        filename_base = "DICOM_SR_Report"
        if self.date_from.get() and self.date_to.get():
            filename_base = f"DICOM_SR_{self.date_from.get()}-{self.date_to.get()}"
        elif self.date_from.get():
            filename_base = f"DICOM_SR_{self.date_from.get()}"
        elif self.date_to.get():
            filename_base = f"DICOM_SR_{self.date_to.get()}"

        excel_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=filename_base + ".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        
        if excel_path:
            try:
                df = pd.DataFrame(results)
                df['Modality'] = df['Modality'].replace('SR', 'CT')
                df.to_excel(excel_path, index=False)
                
                # Generate PDF with same name but .pdf extension
                pdf_path = os.path.splitext(excel_path)[0] + ".pdf"
                self.generate_pdf_report(df, pdf_path)
                
                self.status_var.set(f"Processed {len(results)} files")
                messagebox.showinfo("Success", 
                    f"Processed {len(results)} files\nSaved to:\n{excel_path}\n{pdf_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save files: {e}")

    def open_drl_config(self):
        DRLConfigWindow(self.root)

    def clear_dates(self):
        self.date_from.set_date(None)
        self.date_to.set_date(None)

    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.path_var.set(directory)
            self.process_btn['state'] = tk.NORMAL
            self.status_var.set("Ready to process")

    def process_content_sequence(self, sequence, patient_data):
        if not sequence:
            return
            
        for content_item in sequence:
            if hasattr(content_item, 'ConceptNameCodeSequence'):
                concept_name = content_item.ConceptNameCodeSequence[0].CodeMeaning
                
                if 'Acquisition Protocol' in concept_name and hasattr(content_item, 'TextValue'):
                    patient_data['AcquisitionProtocol'] = str(content_item.TextValue)
                elif 'Mean CTDIvol' in concept_name and hasattr(content_item, 'MeasuredValueSequence'):
                    try:
                        patient_data['CTDIvol'] = float(content_item.MeasuredValueSequence[0].NumericValue)
                    except:
                        pass
                elif 'DLP' in concept_name and hasattr(content_item, 'MeasuredValueSequence'):
                    try:
                        patient_data['TotalDLP'] = float(content_item.MeasuredValueSequence[0].NumericValue)
                    except:
                        pass
                        
            if hasattr(content_item, 'ContentSequence'):
                self.process_content_sequence(content_item.ContentSequence, patient_data)

    def extract_patient_dose_data(self, file_path):
        try:
            dcm = pydicom.dcmread(file_path)
            
            if dcm.get('Modality', '') != 'SR':
                return None
                
            patient_data = {
                'File': os.path.basename(file_path),
                'Modality': dcm.get('Modality', ''),
                'Manufacturer': dcm.get('Manufacturer', ''),
                'DeviceObserverModelName': dcm.get('DeviceObserverModelName', ''),
                'PatientName': str(dcm.get('PatientName', '')),
                'PatientID': dcm.get('PatientID', ''),
                'PatientSex': dcm.get('PatientSex', ''),
                'PatientBirthDate': dcm.get('PatientBirthDate', ''),
                'PatientAge': dcm.get('PatientAge', ''),
                'PatientWeight': dcm.get('PatientWeight', None),
                'StudyDate': dcm.get('StudyDate', ''),
                'StudyDescription': dcm.get('StudyDescription', ''),
                'AcquisitionProtocol': '',
                'TotalDLP': None,
                'CTDIvol': None
            }
            
            if patient_data['PatientBirthDate']:
                birth_date = datetime.strptime(patient_data['PatientBirthDate'], '%Y%m%d').date()
                study_date = datetime.strptime(dcm.get('StudyDate', date.today().strftime('%Y%m%d')), '%Y%m%d').date()
                patient_data['CalculatedAge'] = (study_date - birth_date).days // 365

            if hasattr(dcm, 'ContentSequence'):
                self.process_content_sequence(dcm.ContentSequence, patient_data)

            return patient_data
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return None

    def calculate_drl_comparison(self, df):
        """Calculate DRL comparison data for the report"""
        comparison_data = []
        
        # Group data by protocol and calculate mean values
        grouped_stats = df.groupby('AcquisitionProtocol').agg({
            'TotalDLP': 'mean',
            'CTDIvol': 'mean',
            'DeviceObserverModelName': 'first'
        }).round(2)
        
        for protocol, stats in grouped_stats.iterrows():
            # Find matching DRL protocol
            drl_protocol, drl_data = self.drl_config.get_matching_protocol(protocol)
            
            # Only include protocols that have matching DRL values
            if drl_data and any(pattern.lower() in protocol.lower() 
                               for pattern in drl_data['protocol_match']):
                # Get appropriate DRL value
                child_records = df[df['CalculatedAge'] <= 18]
                if len(child_records) > 0:
                    # For children, find appropriate age range
                    for age_range, values in drl_data['child'].items():
                        min_age, max_age = map(int, age_range.split('-'))
                        age_records = child_records[
                            (child_records['CalculatedAge'] >= min_age) & 
                            (child_records['CalculatedAge'] <= max_age)
                        ]
                        if len(age_records) > 0:
                            drl_level = values['DLP']
                            break
                    else:
                        drl_level = drl_data['adult']['DLP']
                else:
                    drl_level = drl_data['adult']['DLP']
                
                # Calculate percentage and determine status
                percentage = (stats['TotalDLP'] / drl_level) * 100
                relative_percentage = percentage - 100  # Novirze no 100%
                
                if percentage <= 85:
                    status = "Optimals"
                    color = "#90EE90"  # Light green
                elif percentage <= 100:
                    status = "Pienemams"
                    color = "#FFD700"  # Gold
                else:
                    status = "Parsniegts"
                    color = "#FFB6C6"  # Light red
                
                comparison_data.append({
                    'protocol': protocol,
                    'device_model': stats['DeviceObserverModelName'],
                    'avg_dlp': stats['TotalDLP'],
                    'avg_ctdi': stats['CTDIvol'],
                    'drl_level': drl_level,
                    'percentage': relative_percentage,
                    'status': status,
                    'color': color
                })
        
        return comparison_data

    def generate_pdf_report(self, df, save_path):
        # HTML template
        html_template = """
        <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <style>
                @page {
                    size: a4 portrait;
                    @frame header_frame {
                        -pdf-frame-content: header_content;
                        left: 50pt; width: 512pt; top: 30pt; height: 40pt;
                    }
                    @frame content_frame {
                        left: 50pt; width: 512pt; top: 90pt; height: 632pt;
                    }
                }
                body { 
                    font-family: sans-serif;
                    font-size: 10pt;
                }
                h1 { 
                    text-align: center; 
                    font-size: 16pt; 
                    color: #000;
                }
                h2 { 
                    font-size: 14pt; 
                    color: #333; 
                    margin-top: 20pt;
                }
                table { 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 10pt 0; 
                }
                th, td { 
                    border: 1px solid #999; 
                    padding: 6pt; 
                    text-align: left;
                    font-size: 10pt;
                }
                th { 
                    background-color: #f0f0f0; 
                }
            </style>
        </head>
        <body>
            <div id="header_content">
                <h1>SIA Liepajas regionala slimnica</h1>
                <h2 style="text-align: center;">DICOM SR Dose Data Report</h2>
            </div>
            
            {% if date_range %}
            <p>Periods: {{ date_range }}</p>
            {% endif %}
            
            {% if drl_comparison %}
            <h2>DRL Salidzinajums</h2>
            <table>
                <tr>
                    <th>Protokols</th>
                    <th>Videjais DLP</th>
                    <th>Videjais CTDIvol</th>
                    <th>DRL Limits</th>
                    <th>Novirze no DRL</th>
                    <th>Statuss</th>
                </tr>
                {% for row in drl_comparison %}
                <tr style="background-color: {{ row.color }}">
                    <td>{{ row.protocol }}</td>
                    <td>{{ "%.2f"|format(row.avg_dlp) }}</td>
                    <td>{{ "%.2f"|format(row.avg_ctdi) }}</td>
                    <td>{{ "%.1f"|format(row.drl_level) }}</td>
                    <td>{% if row.percentage >= 0 %}+{% endif %}{{ "%.1f"|format(row.percentage) }}%</td>
                    <td>{{ row.status }}</td>
                </tr>
                {% endfor %}
            </table>
            {% endif %}
            
            {% if children_data %}
            <h2>Kategorija: Berni (0-18 gadi)</h2>
            <table>
                <tr>
                    <th>Protokols</th>
                    <th>Vecums</th>
                    <th>Videjais DLP</th>
                    <th>Videjais CTDIvol</th>
                    <th>Skaits</th>
                </tr>
                {% for row in children_data %}
                <tr>
                    <td>{{ row.protocol }}</td>
                    <td>{{ row.age }} gadi</td>
                    <td>{{ "%.2f"|format(row.dlp) }}</td>
                    <td>{{ "%.2f"|format(row.ctdi) }}</td>
                    <td>{{ row.count }}</td>
                </tr>
                {% endfor %}
            </table>
            {% endif %}
            
            {% for category in adult_categories %}
            {% if category.data %}
            <h2>Kategorija: Pieaugusie - {{ category.label }}</h2>
            <table>
                <tr>
                    <th>Protokols</th>
                    <th>Videjais DLP</th>
                    <th>Videjais CTDIvol</th>
                    <th>Skaits</th>
                </tr>
                {% for row in category.data %}
                <tr>
                    <td>{{ row.protocol }}</td>
                    <td>{{ "%.2f"|format(row.dlp) }}</td>
                    <td>{{ "%.2f"|format(row.ctdi) }}</td>
                    <td>{{ row.count }}</td>
                </tr>
                {% endfor %}
            </table>
            {% endif %}
            {% endfor %}
        </body>
        </html>
        """
        
        # Prepare data for template
        template_data = {
            'date_range': '',
            'children_data': [],
            'adult_categories': [],
            'drl_comparison': self.calculate_drl_comparison(df)
        }
        
        # Date range
        if self.date_from.get():
            template_data['date_range'] = f"No: {self.date_from.get()}"
        if self.date_to.get():
            template_data['date_range'] += f" Lidz: {self.date_to.get()}"
        
        # Process children data
        children_df = df[df['CalculatedAge'] <= 18]
        if len(children_df) > 0:
            # Labotā grupēšanas metode
            children_stats = children_df.groupby(['AcquisitionProtocol', 'CalculatedAge']).agg({
                'TotalDLP': 'mean',
                'CTDIvol': 'mean'
            }).reset_index()
            
            # Pievienojam skaitu atsevišķi
            count_df = children_df.groupby(['AcquisitionProtocol', 'CalculatedAge']).size()
            children_stats['count'] = count_df.values
            
            for _, row in children_stats.iterrows():
                template_data['children_data'].append({
                    'protocol': row['AcquisitionProtocol'],
                    'age': row['CalculatedAge'],
                    'dlp': row['TotalDLP'],
                    'ctdi': row['CTDIvol'],
                    'count': row['count']
                })
    
        # Process adults by weight categories
        adults_df = df[df['CalculatedAge'] > 18]
        weight_ranges = [
            (40, 50, "40kg - 50kg"),
            (50, 60, "50kg - 60kg"),
            (60, 70, "60kg - 70kg"),
            (70, 80, "70kg - 80kg"),
            (80, 90, "80kg - 90kg"),
            (90, 100, "90kg - 100kg"),
            (100, float('inf'), "Virs 100kg")
        ]
        
        for weight_min, weight_max, weight_label in weight_ranges:
            category_data = {
                'label': weight_label,
                'data': []
            }
            
            if weight_max == float('inf'):
                weight_df = adults_df[adults_df['PatientWeight'] >= weight_min]
            else:
                weight_df = adults_df[(adults_df['PatientWeight'] >= weight_min) & 
                                    (adults_df['PatientWeight'] < weight_max)]
            
            if len(weight_df) > 0:
                # Labotā grupēšanas metode
                protocol_stats = weight_df.groupby(['AcquisitionProtocol', 'DeviceObserverModelName']).agg({
                    'TotalDLP': 'mean',
                    'CTDIvol': 'mean'
                }).reset_index()
                
                # Pievienojam skaitu atsevišķi
                count_df = weight_df.groupby(['AcquisitionProtocol', 'DeviceObserverModelName']).size()
                protocol_stats['count'] = count_df.values
                
                for _, row in protocol_stats.iterrows():
                    category_data['data'].append({
                        'protocol': row['AcquisitionProtocol'],
                        'device_model': row['DeviceObserverModelName'],
                        'dlp': row['TotalDLP'],
                        'ctdi': row['CTDIvol'],
                        'count': row['count']
                    })
                    
                template_data['adult_categories'].append(category_data)
        
        # Generate HTML
        template = Template(html_template)
        html_out = template.render(**template_data)
        
        # Convert to PDF
        with open(save_path, "wb") as output_file:
            pdf = pisa.pisaDocument(
                src=html_out,
                dest=output_file,
                encoding='UTF-8'
            )


def main():
    root = tk.Tk()
    app = DICOMSRReaderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
