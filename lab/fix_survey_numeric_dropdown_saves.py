from pathlib import Path
import ast
p=Path(__file__).parent/'meeting-native/patched/register-staff-portal-api/openg2p_registry_core/services/intake_form_data_service.py';s=p.read_text();anchor='        column = mapper.columns[key]\n        if isinstance(column.type, SQLDate):';insert='''        column = mapper.columns[key]
        # Browser select controls return strings even when a dropdown stores a count.
        from decimal import Decimal, InvalidOperation
        import math
        try: numeric_type = column.type.python_type
        except (AttributeError, NotImplementedError): numeric_type = None
        if isinstance(value, str) and numeric_type in (int, float, Decimal):
            if not value.strip(): return None
            try:
                parsed = Decimal(value)
                if not parsed.is_finite() or (numeric_type is int and parsed != parsed.to_integral_value()):
                    self._invalid_request("Enter a valid number for " + key.replace("_", " ") + ".")
                return int(parsed) if numeric_type is int else float(parsed) if numeric_type is float else parsed
            except (InvalidOperation, ValueError):
                self._invalid_request("Enter a valid number for " + key.replace("_", " ") + ".")
        if isinstance(column.type, SQLDate):'''
if '# Browser select controls' not in s:s=s.replace(anchor,insert,1);s=s.replace('        converted = data_dict.copy()','        converted = {key: self._normalize_model_value(value, key, mapper) for key,value in data_dict.items()}');ast.parse(s);p.write_text(s)
print('Normalized numeric dropdown values on native draft saves')
