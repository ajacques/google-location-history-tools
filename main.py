import datetime
import json
import matplotlib.pyplot as plt
import os
import pandas as pd
import time

tracker_id = 'aj'

def load_new_style(file_name) -> pd.DataFrame:
  output = []
  for r in json.load(open(file_name))['semanticSegments']:
      if 'timelinePath' in r:
          for point in r['timelinePath']:
              latlng = point['point'].replace('°', '').split(',')
              output.append({
                  'latitudeE7': float(latlng[0]),
                  'longitudeE7': float(latlng[1].strip()),
                  'timestamp': datetime.datetime.fromisoformat(point['time'])
              })
              # TODO: Emit DeviceTag

  return pd.DataFrame(output)

def load_old_style() -> pd.DataFrame:
  df_gps = pd.read_json('/data/Records.json', typ='frame', orient='records')
  gps = df_gps.apply(lambda x: x['locations'], axis=1, result_type='expand')
  gps['latitudeE7'] = gps['latitudeE7'] / 10.**7
  gps['longitudeE7'] = gps['longitudeE7'] / 10.**7
  gps.loc[gps['timestamp'].str.len() == len('2013-12-16T05:42:25.711Z'), 'timestamp'] = pd.to_datetime(gps['timestamp'])
  gps.loc[gps['timestamp'].str.len() == len('2013-12-16T05:42:25Z'), 'timestamp'] = pd.to_datetime(gps['timestamp'], format='%Y-%m-%dT%H:%M:%S%Z', utc=True)
  gps['timestamp'] = pd.to_datetime(gps['timestamp'])
  
  return gps

def render_device_chart(df: pd.DataFrame):
  df = df.sort_values(by='timestamp')
  devices = df['deviceTag'].unique()

  plt.figure(figsize=(10, 6))
  colors = plt.cm.viridis_r([i / len(devices) for i in range(len(devices))])

  for i, device in enumerate(devices):
    device_data = df[df['deviceTag'] == device]
    first_year = device_data['timestamp'].dt.year.min()
    last_year = device_data['timestamp'].dt.year.max()
    middle_year = (first_year + last_year) / 2
    
    plt.hlines(y=i, xmin=first_year, xmax=last_year, color=colors[i], linewidth=4)
    plt.text(middle_year, i + 0.25, device, verticalalignment='center', fontsize=8)

    plt.xlabel('Year')
    plt.ylabel('Device')
    plt.title('Device Reporting Years')
    plt.tick_params(axis='x', which='both', bottom=True, top=True)
    plt.grid(True)
    
    # Show the plot
    plt.show()


def save_output(gps: pd.DataFrame):
  output_folder = "output"
  if not os.path.exists(output_folder):
      os.makedirs(output_folder)
  owntracks = gps.rename(columns={'latitudeE7': 'lat', 'longitudeE7': 'lon', 'accuracy': 'acc', 'altitude': 'alt', 'verticalAccuracy': 'vac'})
  owntracks['tst'] = (owntracks['timestamp'].astype(int) / 10**9)

  files = {}

  years = gps['timestamp'].dt.year.agg(['min', 'max'])
  for year in range(years['min'], years['max'] + 1):
      for month in range(1, 13):
          files[f"{year}-{month}"] = open(f"{output_folder}/{year}-{str(month).rjust(2, '0')}.rec", 'w')
          pass

  try:
      for index, row in owntracks.iterrows():
          d = row.to_dict()
          record = {
              '_type': 'location',
              'tid': tracker_id
          }
          record['tst'] = int(time.mktime(d['timestamp'].timetuple()))

          for key in ['lat', 'lon']:
              if key in row and not pd.isnull(row[key]):
                  record[key] = row[key]
          for key in ['acc', 'alt', 'vac']:
              if key in row and not pd.isnull(row[key]):
                  record[key] = int(row[key])
          
          timestamp = row['timestamp'].strftime("%Y-%m-%dT%H:%M:%SZ")
          line = f"{timestamp}\t*                 \t{json.dumps(record, separators=(',', ':'))}\n"
          files[f"{d['timestamp'].year}-{d['timestamp'].month}"].write(line)
  finally:
      for key, file in files.items():
          print(file)
          file.flush()
          file.close()

df = load_new_style('./Timeline.json')

render_device_chart(df)

save_output(df)
