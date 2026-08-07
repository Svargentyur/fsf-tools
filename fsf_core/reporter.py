from pathlib import Path
from typing import Dict, List, Tuple, Any

class PrivacyReporter:
    """Analyze file metadata for privacy risks."""
    
    # Risk rules for different metadata fields
    RISK_RULES = {
        # EXIF risks
        'gps': {
            'risk_level': 'high',
            'weight': 30,
            'description': 'GPS coordinates reveal exact location where photo was taken',
        },
        'serial_number': {
            'risk_level': 'high',
            'weight': 25,
            'description': 'Camera serial number can uniquely identify your device',
        },
        'make_model': {
            'risk_level': 'medium',
            'weight': 10,
            'description': 'Camera make/model reveals device used',
        },
        'software': {
            'risk_level': 'low',
            'weight': 5,
            'description': 'Software info reveals editing tools used',
        },
        'datetime': {
            'risk_level': 'medium',
            'weight': 15,
            'description': 'Date/time reveals when photo was taken',
        },
        'thumbnail': {
            'risk_level': 'high',
            'weight': 20,
            'description': 'Embedded thumbnail may contain original uncropped image',
        },
        # Audio risks
        'artist': {
            'risk_level': 'medium',
            'weight': 10,
            'description': 'Artist name may reveal identity',
        },
        'comment': {
            'risk_level': 'medium',
            'weight': 10,
            'description': 'Comments may contain personal information',
        },
        'encoder': {
            'risk_level': 'low',
            'weight': 5,
            'description': 'Encoder info reveals software used',
        },
        # PDF risks
        'author': {
            'risk_level': 'high',
            'weight': 25,
            'description': 'Author name directly identifies the creator',
        },
        'creator_tool': {
            'risk_level': 'medium',
            'weight': 10,
            'description': 'Creator tool reveals software environment',
        },
        'creation_date': {
            'risk_level': 'medium',
            'weight': 10,
            'description': 'Creation date reveals when document was made',
        },
    }
    
    def analyze(self, metadata: Dict[str, Dict[str, Any]], file_type: str) -> Tuple[List[Dict[str, Any]], int]:
        """Analyze metadata for privacy risks.
        
        Args:
            metadata: dict of categories -> {field: value}
            file_type: 'image', 'audio', or 'pdf'
        
        Returns:
            (risks_list, overall_score)
            risks_list: list of {field, value, risk_level, description}
            overall_score: 0-100 privacy risk score
        """
        risks = []
        total_weight = 0
        matched_rules = set()

        for category, data in metadata.items():
            if not data:
                continue
            for field, value in data.items():
                field_lower = field.lower()
                matched_rule = None
                
                # Fuzzy matching logic
                if 'gps' in field_lower or 'latitude' in field_lower or 'longitude' in field_lower or 'altitude' in field_lower:
                    matched_rule = 'gps'
                elif 'serial' in field_lower or 'cameraid' in field_lower:
                    matched_rule = 'serial_number'
                elif 'make' in field_lower or 'model' in field_lower:
                    matched_rule = 'make_model'
                elif 'software' in field_lower or 'processing' in field_lower:
                    matched_rule = 'software'
                elif 'date' in field_lower or 'time' in field_lower:
                    if file_type == 'pdf':
                        matched_rule = 'creation_date'
                    else:
                        matched_rule = 'datetime'
                elif 'thumb' in field_lower:
                    matched_rule = 'thumbnail'
                elif 'artist' in field_lower or 'contributor' in field_lower:
                    matched_rule = 'artist'
                elif 'comment' in field_lower or 'description' in field_lower:
                    matched_rule = 'comment'
                elif 'encoder' in field_lower or 'encodedby' in field_lower:
                    matched_rule = 'encoder'
                elif 'author' in field_lower or 'creator' in field_lower and 'tool' not in field_lower:
                    matched_rule = 'author'
                elif 'tool' in field_lower or 'producer' in field_lower:
                    matched_rule = 'creator_tool'

                if matched_rule and matched_rule in self.RISK_RULES:
                    rule = self.RISK_RULES[matched_rule]
                    
                    risks.append({
                        'field': field,
                        'value': value,
                        'risk_level': rule['risk_level'],
                        'description': rule['description']
                    })
                    
                    # Only add weight once per rule type to avoid score blowing up for e.g. multiple GPS tags
                    if matched_rule not in matched_rules:
                        total_weight += rule['weight']
                        matched_rules.add(matched_rule)

        # Sort risks: high -> medium -> low
        risk_order = {'high': 0, 'medium': 1, 'low': 2}
        risks.sort(key=lambda x: risk_order.get(x['risk_level'], 3))
        
        overall_score = min(100, total_weight)
        
        return risks, overall_score
