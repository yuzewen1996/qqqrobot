#!/usr/bin/env python
# coding: utf-8
import os
from pathlib import Path
import json
import gate_api

# Load .env if exists
env_paths = [Path(__file__).parent / '.env', Path('C:/Users/admin/Desktop/gatekey.env')]
for p in env_paths:
    if p.exists():
        with open(p, 'r', encoding='utf-8') as f:
            for line in f:
                line=line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k,v=line.split('=',1)
                    os.environ.setdefault(k.strip(), v.strip())
        break

api_key = os.getenv('GATE_API_KEY')
api_secret = os.getenv('GATE_API_SECRET')
if not api_key or not api_secret:
    raise SystemExit('Missing GATE_API_KEY/GATE_API_SECRET')

conf = gate_api.Configuration(host='https://api.gateio.ws/api/v4', key=api_key, secret=api_secret)
client = gate_api.ApiClient(conf)
futures = gate_api.FuturesApi(client)

positions = futures.list_positions(settle='usdt')
if not positions:
    print('No positions returned')
else:
    for idx, pos in enumerate(positions):
        print('\n--- POSITION', idx, '---')
        # try to get to_dict
        try:
            d = pos.to_dict()
        except Exception:
            try:
                d = pos.__dict__
            except Exception:
                d = str(pos)
        print(json.dumps(d, default=str, ensure_ascii=False, indent=2))
        # print some key attrs raw
        try:
            print('contract:', getattr(pos,'contract',None))
            print('size:', getattr(pos,'size',None))
            print('entry_price raw:', getattr(pos,'entry_price',None))
            print('mark_price raw:', getattr(pos,'mark_price',None))
            if hasattr(pos,'to_dict'):
                td = pos.to_dict()
                if 'entry_price' in td:
                    print('entry_price in to_dict:', td.get('entry_price'))
        except Exception as e:
            print('attr error', e)

print('\nDump complete')
