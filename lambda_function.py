import base64
import json
import gzip

def lambda_handler(event, context):
    output = []
    for record in event['records']:
        try:
            payload = base64.b64decode(record['data'])
            
            try:
                payload = gzip.decompress(payload)
            except Exception:
                pass
            
            payload_str = payload.decode('utf-8')
            
            try:
                log_data = json.loads(payload_str)
                if 'logEvents' in log_data:
                    extracted_logs = []
                    for log_event in log_data['logEvents']:
                        extracted_logs.append(log_event['message'].strip())
                    payload_str = '\n'.join(extracted_logs) + '\n'
            except Exception:
                pass
            
            output_record = {
                'recordId': record['recordId'],
                'result': 'Ok',
                'data': base64.b64encode(payload_str.encode('utf-8')).decode('utf-8')
            }
        except Exception as e:
            output_record = {
                'recordId': record['recordId'],
                'result': 'ProcessingFailed',
                'data': record['data']
            }
        output.append(output_record)
        
    return {'records': output}
