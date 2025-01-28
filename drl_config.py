# drl_config.py
import json
import pandas as pd

class DRLConfiguration:
    def __init__(self):
        self.protocols = {}
        self.config_file = "drl_config.json"
        self.load_config()
    
    def load_config(self):
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.protocols = json.load(f)
        except FileNotFoundError:
            # Default empty configuration structure
            self.protocols = {}
    
    def save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.protocols, f, indent=4, ensure_ascii=False)
    
    def add_protocol(self, name, data):
        self.protocols[name] = data
        self.save_config()
    
    def delete_protocol(self, name):
        if name in self.protocols:
            del self.protocols[name]
            self.save_config()
    
    def get_protocol(self, name):
        return self.protocols.get(name, None)
    
    def get_all_protocols(self):
        return self.protocols

    def get_matching_protocol(self, protocol_name):
        for protocol, data in self.protocols.items():
            if any(pattern.lower() in protocol_name.lower() 
                  for pattern in data['protocol_match']):
                return protocol, data
        return None, None

    def import_from_excel(self, file_path):
        try:
            df = pd.read_excel(file_path)
            new_protocols = {}
            
            for _, row in df.iterrows():
                protocol_data = {
                    'protocol_match': [x.strip() for x in row['Match Patterns'].split(',')],
                    'adult': {
                        'DLP': float(row['Adult DLP']),
                        'CTDIvol': float(row['Adult CTDIvol'])
                    },
                    'child': {}
                }
                
                # Process children data
                age_ranges = ['0-1', '1-5', '5-10', '10-15']
                for age_range in age_ranges:
                    if f'Child {age_range} DLP' in row and f'Child {age_range} CTDIvol' in row:
                        protocol_data['child'][age_range] = {
                            'DLP': float(row[f'Child {age_range} DLP']),
                            'CTDIvol': float(row[f'Child {age_range} CTDIvol'])
                        }
                
                new_protocols[row['Protocol']] = protocol_data
            
            self.protocols = new_protocols
            self.save_config()
            return True, "Import successful"
        except Exception as e:
            return False, str(e)
    
    def export_to_excel(self, file_path):
        try:
            data = []
            for protocol_name, protocol_data in self.protocols.items():
                row = {
                    'Protocol': protocol_name,
                    'Match Patterns': ','.join(protocol_data['protocol_match']),
                    'Adult DLP': protocol_data['adult']['DLP'],
                    'Adult CTDIvol': protocol_data['adult']['CTDIvol']
                }
                
                for age_range, values in protocol_data['child'].items():
                    row[f'Child {age_range} DLP'] = values['DLP']
                    row[f'Child {age_range} CTDIvol'] = values['CTDIvol']
                
                data.append(row)
            
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)
            return True, "Export successful"
        except Exception as e:
            return False, str(e)