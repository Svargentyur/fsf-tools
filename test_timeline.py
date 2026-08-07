from fsf_core.timeline import TripTimeline
tl = TripTimeline(city='tokyo', preset='sony_a7iv', days=3, style='casual')
photos = tl.generate(num_photos=10)
assert len(photos) == 10
assert 'datetime_original' in photos[0]
assert 'gps_lat' in photos[0]
# Verify chronological order
for i in range(1, len(photos)):
    assert photos[i]['datetime_original'] >= photos[i-1]['datetime_original']
print(f'Timeline works! {len(photos)} photos over {tl.days} days')
for p in photos[:3]:
    print(f"  {p['datetime_original']} | GPS: {p['gps_lat']:.4f} {p['gps_lat_ref']}, {p['gps_lon']:.4f} {p['gps_lon_ref']} | ISO:{p['iso']} f/{p['f_number']}")
