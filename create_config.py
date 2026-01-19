#!/usr/bin/env python3
import os

# Read environment variables
service_count = int(os.environ.get('SERVICE_COUNT', 0))

# Read template
with open('nginx.conf.template', 'r') as f:
    template = f.read()

if '{{MULTI_SERVICE_BLOCK}}' not in template:
    print('ERROR: {{MULTI_SERVICE_BLOCK}} missing in template')
    exit(1)

# Generate service blocks
block = ''
for i in range(1, service_count + 1):
    path = os.environ[f'SERVICE_{i}_PATH']
    name = os.environ[f'SERVICE_{i}_NAME']
    port = os.environ[f'SERVICE_{i}_PORT']
    print(f' - adding {path} -> {name}:{port}')
    
    path_clean = path.strip('/')
    
    # Clean and effective sub_filter configuration
    block += f'''    location {path}/ {{
        proxy_pass http://{name}:{port}/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        
        # Disable compression for sub_filter to work properly
        proxy_set_header Accept-Encoding "";
        
        # Comprehensive URL rewriting
        sub_filter_once off;
        
        # Fix static assets and common URLs
        sub_filter 'href="/' 'href="/{path_clean}/';
        sub_filter 'src="/' 'src="/{path_clean}/';
        sub_filter 'action="/' 'action="/{path_clean}/';
        sub_filter "setUIRoot('')" "setUIRoot('/{path_clean}')";
    }}

'''

# Replace and write result
result = template.replace('{{MULTI_SERVICE_BLOCK}}', block)
with open('nginx.conf', 'w') as f:
    f.write(result)

print('>>> Generated nginx.conf successfully')
