"""Realistic metadata presets for spoofing."""

# ─────────────────────────────────────────────────────
#  Camera presets with full realistic specs
# ─────────────────────────────────────────────────────

CAMERA_PRESETS = {
    "iphone_15_pro": {
        "make": "Apple",
        "model": "iPhone 15 Pro",
        "software": "17.5.1",
        "lens_make": "Apple",
        "lens_model": "iPhone 15 Pro back triple camera 6.765mm f/1.78",
        "focal_length": 6.765,
        "focal_length_35mm": 24,
        "f_number": 1.78,
        "iso": (50, 3200),
        "iso_common": [50, 64, 100, 200, 400, 800, 1000, 1600],
        "exposure_time": (1/8000, 1/4),
        "image_sizes": [(4032, 3024), (4032, 2268), (3024, 4032), (2268, 4032)],
        "color_space": 65535,  # Uncalibrated (Apple DCI-P3)
        "exposure_program": 2,  # Normal program
        "metering_mode": 5,  # Multi-segment
        "white_balance": 0,  # Auto
        "scene_type": 1,  # Directly photographed
        "flash": 16,  # No flash, no flash function
        "unique_model": "iPhone 15 Pro back triple camera 6.765mm f/1.78",
    },
    "iphone_14": {
        "make": "Apple",
        "model": "iPhone 14",
        "software": "16.7.8",
        "lens_make": "Apple",
        "lens_model": "iPhone 14 back dual wide camera 5.7mm f/1.5",
        "focal_length": 5.7,
        "focal_length_35mm": 26,
        "f_number": 1.5,
        "iso": (32, 3200),
        "iso_common": [32, 50, 64, 100, 200, 400, 800, 1250, 2000],
        "exposure_time": (1/8000, 1/3),
        "image_sizes": [(4032, 3024), (4032, 2268), (3024, 4032)],
        "color_space": 65535,
        "exposure_program": 2,
        "metering_mode": 5,
        "white_balance": 0,
        "scene_type": 1,
        "flash": 16,
        "unique_model": "iPhone 14 back dual wide camera 5.7mm f/1.5",
    },
    "iphone_13": {
        "make": "Apple",
        "model": "iPhone 13",
        "software": "17.4.1",
        "lens_make": "Apple",
        "lens_model": "iPhone 13 back dual wide camera 5.1mm f/1.6",
        "focal_length": 5.1,
        "focal_length_35mm": 26,
        "f_number": 1.6,
        "iso": (25, 2500),
        "iso_common": [25, 32, 50, 64, 100, 200, 400, 800, 1250],
        "exposure_time": (1/9000, 1/3),
        "image_sizes": [(4032, 3024), (3024, 4032)],
        "color_space": 65535,
        "exposure_program": 2,
        "metering_mode": 5,
        "white_balance": 0,
        "scene_type": 1,
        "flash": 16,
        "unique_model": "iPhone 13 back dual wide camera 5.1mm f/1.6",
    },
    "samsung_s24_ultra": {
        "make": "samsung",
        "model": "SM-S928B",
        "software": "S928BXXU3AXK3",
        "lens_make": "Samsung",
        "lens_model": "Samsung S24 Ultra Rear Wide Camera",
        "focal_length": 6.3,
        "focal_length_35mm": 23,
        "f_number": 1.7,
        "iso": (50, 3200),
        "iso_common": [50, 100, 125, 200, 250, 400, 500, 800, 1250],
        "exposure_time": (1/12000, 1/4),
        "image_sizes": [(4000, 3000), (4000, 2252), (3000, 4000), (12000, 9000)],
        "color_space": 1,
        "exposure_program": 2,
        "metering_mode": 2,  # Center-weighted
        "white_balance": 0,
        "scene_type": 1,
        "flash": 0,
        "unique_model": "SM-S928B",
    },
    "samsung_s23": {
        "make": "samsung",
        "model": "SM-S911B",
        "software": "S911BXXS7CXJ1",
        "lens_make": "Samsung",
        "lens_model": "Samsung S23 Rear Wide Camera",
        "focal_length": 5.4,
        "focal_length_35mm": 24,
        "f_number": 1.8,
        "iso": (50, 3200),
        "iso_common": [50, 100, 125, 200, 320, 500, 800, 1000],
        "exposure_time": (1/12000, 1/4),
        "image_sizes": [(4000, 3000), (4000, 2252), (3000, 4000)],
        "color_space": 1,
        "exposure_program": 2,
        "metering_mode": 2,
        "white_balance": 0,
        "scene_type": 1,
        "flash": 0,
        "unique_model": "SM-S911B",
    },
    "pixel_8_pro": {
        "make": "Google",
        "model": "Pixel 8 Pro",
        "software": "HDR+ 1.0.665933433zd",
        "lens_make": "Google",
        "lens_model": "Pixel 8 Pro back camera 6.9mm f/1.68",
        "focal_length": 6.9,
        "focal_length_35mm": 24,
        "f_number": 1.68,
        "iso": (44, 2600),
        "iso_common": [44, 55, 67, 100, 141, 200, 283, 400, 566, 800],
        "exposure_time": (1/16000, 1/4),
        "image_sizes": [(4080, 3072), (4080, 2296), (3072, 4080)],
        "color_space": 1,
        "exposure_program": 2,
        "metering_mode": 5,
        "white_balance": 0,
        "scene_type": 1,
        "flash": 16,
        "unique_model": "Pixel 8 Pro",
    },
    "pixel_9": {
        "make": "Google",
        "model": "Pixel 9",
        "software": "HDR+ 1.0.714205199zd",
        "lens_make": "Google",
        "lens_model": "Pixel 9 back camera 6.9mm f/1.68",
        "focal_length": 6.9,
        "focal_length_35mm": 24,
        "f_number": 1.68,
        "iso": (33, 2800),
        "iso_common": [33, 50, 67, 100, 150, 200, 400, 600, 800],
        "exposure_time": (1/16000, 1/4),
        "image_sizes": [(4080, 3072), (4080, 2296), (3072, 4080)],
        "color_space": 1,
        "exposure_program": 2,
        "metering_mode": 5,
        "white_balance": 0,
        "scene_type": 1,
        "flash": 16,
        "unique_model": "Pixel 9",
    },
    "canon_eos_r5": {
        "make": "Canon",
        "model": "Canon EOS R5",
        "software": "Firmware Version 2.0.0",
        "lens_model": "RF24-105mm F4 L IS USM",
        "focal_length": 50.0,
        "focal_length_35mm": 50,
        "f_number": 4.0,
        "iso": (100, 51200),
        "iso_common": [100, 200, 400, 800, 1600, 3200, 6400],
        "exposure_time": (1/8000, 30),
        "image_sizes": [(8192, 5464), (6720, 4480), (4800, 3200), (3360, 2240)],
        "color_space": 1,
        "exposure_program": 3,  # Aperture priority
        "metering_mode": 5,
        "white_balance": 0,
        "scene_type": 1,
        "flash": 16,
        "focal_lengths_available": [24, 28, 35, 50, 70, 85, 105],
        "f_numbers_available": [4.0, 5.6, 8.0, 11.0, 16.0],
        "unique_model": "Canon EOS R5",
    },
    "canon_eos_r6ii": {
        "make": "Canon",
        "model": "Canon EOS R6m2",
        "software": "Firmware Version 1.4.0",
        "lens_model": "RF50mm F1.8 STM",
        "focal_length": 50.0,
        "focal_length_35mm": 50,
        "f_number": 1.8,
        "iso": (100, 102400),
        "iso_common": [100, 200, 400, 800, 1600, 3200, 6400, 12800],
        "exposure_time": (1/8000, 30),
        "image_sizes": [(6000, 4000), (4800, 3200), (3984, 2656)],
        "color_space": 1,
        "exposure_program": 3,
        "metering_mode": 5,
        "white_balance": 0,
        "scene_type": 1,
        "flash": 16,
        "f_numbers_available": [1.8, 2.0, 2.8, 4.0, 5.6, 8.0, 11.0],
        "unique_model": "Canon EOS R6m2",
    },
    "sony_a7iv": {
        "make": "SONY",
        "model": "ILCE-7M4",
        "software": "ILCE-7M4 v2.01",
        "lens_model": "FE 24-70mm F2.8 GM II",
        "focal_length": 35.0,
        "focal_length_35mm": 35,
        "f_number": 2.8,
        "iso": (100, 51200),
        "iso_common": [100, 200, 400, 800, 1600, 3200, 6400],
        "exposure_time": (1/8000, 30),
        "image_sizes": [(7008, 4672), (4672, 7008), (7008, 3936)],
        "color_space": 1,
        "exposure_program": 3,
        "metering_mode": 5,
        "white_balance": 0,
        "scene_type": 1,
        "flash": 16,
        "focal_lengths_available": [24, 28, 35, 50, 70],
        "f_numbers_available": [2.8, 4.0, 5.6, 8.0, 11.0],
        "unique_model": "ILCE-7M4",
    },
    "sony_a7cr": {
        "make": "SONY",
        "model": "ILCE-7CR",
        "software": "ILCE-7CR v1.01",
        "lens_model": "FE 35mm F1.4 GM",
        "focal_length": 35.0,
        "focal_length_35mm": 35,
        "f_number": 1.4,
        "iso": (100, 32000),
        "iso_common": [100, 200, 400, 800, 1600, 3200],
        "exposure_time": (1/8000, 30),
        "image_sizes": [(7008, 4672), (4672, 7008)],
        "color_space": 1,
        "exposure_program": 3,
        "metering_mode": 5,
        "white_balance": 0,
        "scene_type": 1,
        "flash": 16,
        "f_numbers_available": [1.4, 2.0, 2.8, 4.0, 5.6, 8.0],
        "unique_model": "ILCE-7CR",
    },
    "nikon_z8": {
        "make": "NIKON CORPORATION",
        "model": "NIKON Z 8",
        "software": "Ver.02.01",
        "lens_model": "NIKKOR Z 24-70mm f/2.8 S",
        "focal_length": 35.0,
        "focal_length_35mm": 35,
        "f_number": 2.8,
        "iso": (64, 25600),
        "iso_common": [64, 100, 200, 400, 800, 1600, 3200, 6400],
        "exposure_time": (1/32000, 30),
        "image_sizes": [(8256, 5504), (6192, 4128), (4128, 2752)],
        "color_space": 1,
        "exposure_program": 3,
        "metering_mode": 5,
        "white_balance": 0,
        "scene_type": 1,
        "flash": 0,
        "focal_lengths_available": [24, 28, 35, 50, 70],
        "f_numbers_available": [2.8, 4.0, 5.6, 8.0, 11.0, 16.0],
        "unique_model": "NIKON Z 8",
    },
    "nikon_z6iii": {
        "make": "NIKON CORPORATION",
        "model": "NIKON Z 6III",
        "software": "Ver.01.00",
        "lens_model": "NIKKOR Z 50mm f/1.8 S",
        "focal_length": 50.0,
        "focal_length_35mm": 50,
        "f_number": 1.8,
        "iso": (100, 64000),
        "iso_common": [100, 200, 400, 800, 1600, 3200, 6400],
        "exposure_time": (1/16000, 30),
        "image_sizes": [(6048, 4032), (4032, 6048), (6048, 3400)],
        "color_space": 1,
        "exposure_program": 3,
        "metering_mode": 5,
        "white_balance": 0,
        "scene_type": 1,
        "flash": 0,
        "f_numbers_available": [1.8, 2.0, 2.8, 4.0, 5.6, 8.0],
        "unique_model": "NIKON Z 6III",
    },
    "fuji_xt5": {
        "make": "FUJIFILM",
        "model": "X-T5",
        "software": "Digital Camera X-T5 Ver2.11",
        "lens_model": "XF18-55mmF2.8-4 R LM OIS",
        "focal_length": 23.0,
        "focal_length_35mm": 35,
        "f_number": 4.0,
        "iso": (125, 12800),
        "iso_common": [125, 200, 400, 800, 1600, 3200, 6400],
        "exposure_time": (1/180000, 15),
        "image_sizes": [(6240, 4160), (4160, 6240), (6240, 3512)],
        "color_space": 1,
        "exposure_program": 3,
        "metering_mode": 5,
        "white_balance": 0,
        "scene_type": 1,
        "flash": 16,
        "focal_lengths_available": [18, 23, 27, 35, 55],
        "f_numbers_available": [2.8, 4.0, 5.6, 8.0, 11.0],
        "unique_model": "X-T5",
    },
    "gopro_hero12": {
        "make": "GoPro",
        "model": "HERO12 Black",
        "software": "H24.01.02.10.00",
        "lens_model": "GoPro Wide",
        "focal_length": 3.0,
        "focal_length_35mm": 16,
        "f_number": 2.5,
        "iso": (100, 3200),
        "iso_common": [100, 200, 400, 800, 1600],
        "exposure_time": (1/2000, 1/30),
        "image_sizes": [(5568, 4176), (4000, 3000), (5568, 3132)],
        "color_space": 1,
        "exposure_program": 2,
        "metering_mode": 5,
        "white_balance": 0,
        "scene_type": 1,
        "flash": 32,
        "unique_model": "HERO12 Black",
    },
    "dji_mini_4_pro": {
        "make": "DJI",
        "model": "FC8482",
        "software": "v01.00.0800",
        "lens_model": "DJI Mini 4 Pro 6.72mm f/1.7",
        "focal_length": 6.72,
        "focal_length_35mm": 24,
        "f_number": 1.7,
        "iso": (100, 6400),
        "iso_common": [100, 200, 400, 800, 1600],
        "exposure_time": (1/8000, 2),
        "image_sizes": [(4032, 3024), (4032, 2264)],
        "color_space": 1,
        "exposure_program": 2,
        "metering_mode": 2,
        "white_balance": 0,
        "scene_type": 1,
        "flash": 32,
        "unique_model": "FC8482",
    },
    "dji_air_3": {
        "make": "DJI",
        "model": "FC4170",
        "software": "v01.02.0200",
        "lens_model": "DJI Air 3 6.72mm f/1.7",
        "focal_length": 6.72,
        "focal_length_35mm": 24,
        "f_number": 1.7,
        "iso": (100, 6400),
        "iso_common": [100, 200, 400, 800],
        "exposure_time": (1/8000, 8),
        "image_sizes": [(4032, 3024), (8064, 6048)],
        "color_space": 1,
        "exposure_program": 2,
        "metering_mode": 2,
        "white_balance": 0,
        "scene_type": 1,
        "flash": 32,
        "unique_model": "FC4170",
    },
}

# ─────────────────────────────────────────────────────
#  Scene profiles for realistic correlated parameters
# ─────────────────────────────────────────────────────

SCENE_PROFILES = {
    "daylight_outdoor": {
        "weight": 30,  # probability weight
        "iso_range": (100, 400),
        "exposure_range": (1/4000, 1/125),
        "f_preference": "mid",  # f/5.6 - f/11
        "time_range": (8, 18),  # hours
        "orientation_weights": {1: 60, 6: 15, 8: 15, 3: 10},
        "scene_capture_type": 0,  # Standard
    },
    "golden_hour": {
        "weight": 15,
        "iso_range": (100, 800),
        "exposure_range": (1/2000, 1/30),
        "f_preference": "wide",  # f/1.4 - f/4
        "time_range": (6, 8),  # or 17-19, handled in code
        "orientation_weights": {1: 70, 6: 10, 8: 10, 3: 10},
        "scene_capture_type": 0,
    },
    "indoor": {
        "weight": 20,
        "iso_range": (400, 3200),
        "exposure_range": (1/250, 1/15),
        "f_preference": "wide",
        "time_range": (9, 23),
        "orientation_weights": {1: 50, 6: 20, 8: 20, 3: 10},
        "scene_capture_type": 0,
    },
    "night_street": {
        "weight": 10,
        "iso_range": (800, 6400),
        "exposure_range": (1/125, 1/4),
        "f_preference": "wide",
        "time_range": (20, 3),  # wraps around midnight
        "orientation_weights": {1: 70, 6: 15, 8: 15, 3: 0},
        "scene_capture_type": 3,  # Night
    },
    "portrait": {
        "weight": 15,
        "iso_range": (100, 800),
        "exposure_range": (1/1000, 1/60),
        "f_preference": "bokeh",  # widest available
        "time_range": (10, 17),
        "orientation_weights": {1: 40, 6: 30, 8: 30, 3: 0},
        "scene_capture_type": 2,  # Portrait
    },
    "landscape": {
        "weight": 10,
        "iso_range": (100, 400),
        "exposure_range": (1/500, 1/30),
        "f_preference": "sharp",  # f/8 - f/16
        "time_range": (6, 19),
        "orientation_weights": {1: 80, 6: 5, 8: 5, 3: 10},
        "scene_capture_type": 1,  # Landscape
    },
}

# ─────────────────────────────────────────────────────
#  Standard shutter speeds (real cameras use these)
# ─────────────────────────────────────────────────────

STANDARD_SHUTTER_SPEEDS = [
    1/8000, 1/6400, 1/5000, 1/4000, 1/3200, 1/2500, 1/2000,
    1/1600, 1/1250, 1/1000, 1/800, 1/640, 1/500, 1/400,
    1/320, 1/250, 1/200, 1/160, 1/125, 1/100, 1/80, 1/60,
    1/50, 1/40, 1/30, 1/25, 1/20, 1/15, 1/13, 1/10, 1/8,
    1/6, 1/5, 1/4, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0,
    1.3, 1.6, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0,
    10.0, 13.0, 15.0, 20.0, 25.0, 30.0,
]

# ─────────────────────────────────────────────────────
#  Cities with neighborhoods for realistic GPS offsets
# ─────────────────────────────────────────────────────

CITY_PRESETS = {
    "tokyo": {
        "lat": 35.6762, "lon": 139.6503, "lat_ref": "N", "lon_ref": "E",
        "hotspots": [
            (35.6595, 139.7004),  # Shibuya
            (35.7101, 139.8107),  # Asakusa
            (35.6938, 139.7034),  # Shinjuku
            (35.6585, 139.7454),  # Tokyo Tower
            (35.6329, 139.8804),  # Disneyland
        ],
    },
    "new_york": {
        "lat": 40.7128, "lon": -74.0060, "lat_ref": "N", "lon_ref": "W",
        "hotspots": [
            (40.7580, -73.9855),  # Times Square
            (40.7484, -73.9857),  # Empire State
            (40.6892, -74.0445),  # Statue of Liberty
            (40.7812, -73.9665),  # Central Park
            (40.7061, -73.9969),  # Brooklyn Bridge
        ],
    },
    "london": {
        "lat": 51.5074, "lon": -0.1278, "lat_ref": "N", "lon_ref": "W",
        "hotspots": [
            (51.5014, -0.1419),  # Buckingham Palace
            (51.5081, -0.0759),  # Tower of London
            (51.5007, -0.1246),  # Westminster
            (51.5033, -0.1195),  # London Eye
            (51.5194, -0.1270),  # British Museum
        ],
    },
    "paris": {
        "lat": 48.8566, "lon": 2.3522, "lat_ref": "N", "lon_ref": "E",
        "hotspots": [
            (48.8584, 2.2945),   # Eiffel Tower
            (48.8606, 2.3376),   # Louvre
            (48.8530, 2.3499),   # Notre-Dame
            (48.8738, 2.2950),   # Arc de Triomphe
            (48.8867, 2.3431),   # Sacré-Cœur
        ],
    },
    "berlin": {
        "lat": 52.5200, "lon": 13.4050, "lat_ref": "N", "lon_ref": "E",
        "hotspots": [
            (52.5163, 13.3777),  # Brandenburg Gate
            (52.5186, 13.3762),  # Reichstag
            (52.5076, 13.3904),  # Checkpoint Charlie
            (52.5219, 13.4132),  # Alexanderplatz
            (52.5075, 13.3903),  # Berlin Wall Memorial
        ],
    },
    "moscow": {
        "lat": 55.7558, "lon": 37.6173, "lat_ref": "N", "lon_ref": "E",
        "hotspots": [
            (55.7539, 37.6208),  # Red Square
            (55.7601, 37.6186),  # Kremlin
            (55.7520, 37.6175),  # St. Basil's
            (55.7417, 37.6295),  # Tretyakov
            (55.7616, 37.6070),  # Arbat
        ],
    },
    "dubai": {
        "lat": 25.2048, "lon": 55.2708, "lat_ref": "N", "lon_ref": "E",
        "hotspots": [
            (25.1972, 55.2744),  # Burj Khalifa
            (25.1412, 55.1851),  # Burj Al Arab
            (25.2285, 55.2866),  # Dubai Creek
            (25.0762, 55.1398),  # Dubai Marina
            (25.2048, 55.2708),  # Downtown
        ],
    },
    "sydney": {
        "lat": -33.8688, "lon": 151.2093, "lat_ref": "S", "lon_ref": "E",
        "hotspots": [
            (-33.8568, 151.2153),  # Opera House
            (-33.8523, 151.2108),  # Harbour Bridge
            (-33.8916, 151.2767),  # Bondi Beach
            (-33.8688, 151.2093),  # Circular Quay
        ],
    },
    "sao_paulo": {
        "lat": -23.5505, "lon": -46.6333, "lat_ref": "S", "lon_ref": "W",
        "hotspots": [
            (-23.5613, -46.6560),  # Paulista Avenue
            (-23.5475, -46.6361),  # Sé Cathedral
            (-23.5874, -46.6576),  # Ibirapuera Park
        ],
    },
    "istanbul": {
        "lat": 41.0082, "lon": 28.9784, "lat_ref": "N", "lon_ref": "E",
        "hotspots": [
            (41.0086, 28.9802),  # Hagia Sophia
            (41.0054, 28.9768),  # Blue Mosque
            (41.0115, 28.9833),  # Grand Bazaar
            (41.0256, 29.0132),  # Galata Tower
        ],
    },
    "bangkok": {
        "lat": 13.7563, "lon": 100.5018, "lat_ref": "N", "lon_ref": "E",
        "hotspots": [
            (13.7510, 100.4927),  # Grand Palace
            (13.7465, 100.5089),  # Wat Pho
            (13.7437, 100.4882),  # Wat Arun
        ],
    },
    "cairo": {
        "lat": 30.0444, "lon": 31.2357, "lat_ref": "N", "lon_ref": "E",
        "hotspots": [
            (29.9792, 31.1342),  # Pyramids
            (30.0478, 31.2336),  # Egyptian Museum
        ],
    },
    "mumbai": {
        "lat": 19.0760, "lon": 72.8777, "lat_ref": "N", "lon_ref": "E",
        "hotspots": [
            (18.9220, 72.8347),  # Gateway of India
            (19.0760, 72.8777),  # Downtown
        ],
    },
    "seoul": {
        "lat": 37.5665, "lon": 126.9780, "lat_ref": "N", "lon_ref": "E",
        "hotspots": [
            (37.5796, 126.9770),  # Gyeongbokgung
            (37.5512, 126.9882),  # Namsan Tower
            (37.5665, 126.9780),  # City Hall
        ],
    },
    "singapore": {
        "lat": 1.3521, "lon": 103.8198, "lat_ref": "N", "lon_ref": "E",
        "hotspots": [
            (1.2814, 103.8586),  # Marina Bay Sands
            (1.2494, 103.8303),  # Sentosa
            (1.3521, 103.8198),  # Orchard Road
        ],
    },
    "rome": {
        "lat": 41.9028, "lon": 12.4964, "lat_ref": "N", "lon_ref": "E",
        "hotspots": [
            (41.8902, 12.4922),  # Colosseum
            (41.9022, 12.4539),  # Vatican
            (41.8986, 12.4769),  # Pantheon
            (41.9009, 12.4833),  # Trevi Fountain
        ],
    },
    "barcelona": {
        "lat": 41.3874, "lon": 2.1686, "lat_ref": "N", "lon_ref": "E",
        "hotspots": [
            (41.4036, 2.1744),   # Sagrada Familia
            (41.3905, 2.1649),   # La Rambla
            (41.4145, 2.1527),   # Park Güell
        ],
    },
    "kyoto": {
        "lat": 35.0116, "lon": 135.7681, "lat_ref": "N", "lon_ref": "E",
        "hotspots": [
            (35.0394, 135.7292),  # Kinkaku-ji
            (34.9948, 135.7850),  # Fushimi Inari
            (35.0170, 135.7842),  # Kiyomizu-dera
        ],
    },
    "amsterdam": {
        "lat": 52.3676, "lon": 4.9041, "lat_ref": "N", "lon_ref": "E",
        "hotspots": [
            (52.3600, 4.8852),   # Rijksmuseum
            (52.3702, 4.8952),   # Dam Square
            (52.3738, 4.8842),   # Anne Frank House
        ],
    },
    "prague": {
        "lat": 50.0755, "lon": 14.4378, "lat_ref": "N", "lon_ref": "E",
        "hotspots": [
            (50.0865, 14.4110),  # Prague Castle
            (50.0866, 14.4114),  # Charles Bridge
            (50.0870, 14.4213),  # Old Town Square
        ],
    },
}

SOFTWARE_PRESETS = [
    "Adobe Photoshop 25.12",
    "Adobe Photoshop 26.1",
    "Adobe Lightroom Classic 14.1",
    "Adobe Lightroom 8.1",
    "GIMP 2.10.38",
    "Snapseed 2.21.0",
    "VSCO 401",
    "Google Photos",
    "Samsung Gallery",
    "Apple Photos",
    "Capture One 16.4",
    "DxO PhotoLab 8",
    "Affinity Photo 2.5",
    "Luminar Neo 1.20",
    "darktable 4.8.1",
    "RawTherapee 5.11",
]

AUDIO_PRESETS = {
    "genres": [
        "Rock", "Pop", "Electronic", "Hip-Hop", "Jazz", "Classical",
        "R&B", "Metal", "Indie", "Folk", "Ambient", "Lo-fi",
        "Synthwave", "Alternative", "Punk", "Blues", "Soul",
        "House", "Techno", "Drum and Bass", "Trip-Hop", "Shoegaze",
    ],
    "encoders": [
        "LAME 3.100", "LAME 3.101", "iTunes 12.13.3.3",
        "foobar2000 2.1.3", "Audacity 3.6.4", "FFmpeg",
        "VLC media player", "dBpoweramp 2024.09",
        "XLD 20240912", "MediaMonkey 5.0",
    ],
    "labels": [
        "Independent", "Self-Released", "Bandcamp",
        "SoundCloud", "DistroKid", "TuneCore",
    ],
}

PDF_PRESETS = {
    "creators": [
        "Microsoft® Word for Microsoft 365",
        "Microsoft® Word 2024",
        "LibreOffice 24.8",
        "LibreOffice 7.6",
        "Google Docs",
        "Adobe InDesign 2024 (Windows)",
        "Adobe InDesign 19.5 (Macintosh)",
        "LaTeX with hyperref package",
        "Pages 14.2",
        "Notion",
        "Canva",
        "WPS Office 12.8",
    ],
    "producers": [
        "Microsoft® Word for Microsoft 365",
        "Microsoft® Word 2024",
        "LibreOffice 24.8",
        "Skia/PDF m131",
        "Adobe PDF Library 24.4.91",
        "pdfTeX-1.40.26",
        "macOS 15.2 Quartz PDFContext",
        "wkhtmltopdf 0.12.6.1",
        "Qt 6.7.2",
        "Prince 15.3",
        "iText® 8.0.3",
        "ReportLab PDF Library",
    ],
}

# ─────────────────────────────────────────────────────
#  Identity presets for forge feature
# ─────────────────────────────────────────────────────

IDENTITY_FIRST_NAMES = {
    "en": ["James", "Emma", "William", "Olivia", "Benjamin", "Sophia", "Lucas", "Isabella",
           "Henry", "Mia", "Alexander", "Charlotte", "Daniel", "Amelia", "Matthew", "Harper",
           "Samuel", "Evelyn", "Joseph", "Abigail", "David", "Emily", "Andrew", "Elizabeth"],
    "de": ["Maximilian", "Marie", "Alexander", "Sophie", "Paul", "Anna", "Leon", "Emilia",
           "Felix", "Mia", "Lukas", "Lena", "Jonas", "Hannah", "Tim", "Laura"],
    "jp": ["Haruto", "Yui", "Sota", "Hina", "Yuto", "Aoi", "Riku", "Sakura",
           "Minato", "Koharu", "Kaito", "Rin", "Asahi", "Mio", "Hiroto", "Akari"],
    "es": ["Santiago", "Valentina", "Mateo", "Camila", "Sebastián", "Isabella",
           "Diego", "Luciana", "Alejandro", "Sofía", "Daniel", "María"],
    "ru": ["Alexander", "Maria", "Dmitry", "Anna", "Maxim", "Ekaterina", "Artem", "Daria",
           "Ivan", "Sofia", "Nikita", "Anastasia", "Mikhail", "Victoria"],
    "kr": ["Minjun", "Seo-yeon", "Seo-jun", "Ji-woo", "Do-yoon", "Seo-hyun",
           "Ye-jun", "Ha-yoon", "Si-woo", "Jia"],
}

IDENTITY_LAST_NAMES = {
    "en": ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
           "Wilson", "Anderson", "Taylor", "Thomas", "Moore", "Martin", "Jackson", "Thompson",
           "White", "Harris", "Clark", "Lewis", "Robinson", "Walker", "Hall", "Young"],
    "de": ["Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner",
           "Becker", "Hoffmann", "Richter", "Klein", "Wolf", "Schröder"],
    "jp": ["Sato", "Suzuki", "Takahashi", "Tanaka", "Watanabe", "Ito", "Yamamoto",
           "Nakamura", "Kobayashi", "Kato", "Yoshida", "Yamada", "Sasaki"],
    "es": ["García", "Rodríguez", "Martínez", "López", "González", "Hernández",
           "Pérez", "Sánchez", "Ramírez", "Torres", "Flores"],
    "ru": ["Ivanov", "Petrov", "Smirnov", "Kuznetsov", "Popov", "Vasiliev",
           "Sokolov", "Mikhailov", "Novikov", "Fedorov", "Morozov"],
    "kr": ["Kim", "Lee", "Park", "Choi", "Jung", "Kang", "Yoon", "Jang",
           "Lim", "Han", "Oh", "Seo", "Shin"],
}

ALBUM_WORDS = {
    "adjectives": [
        "Midnight", "Golden", "Silent", "Fading", "Electric", "Crystal",
        "Neon", "Crimson", "Hollow", "Velvet", "Distant", "Floating",
        "Broken", "Lucid", "Phantom", "Burning", "Frozen", "Eternal",
        "Radiant", "Sunken", "Waking", "Paper", "Iron", "Glass",
        "Violet", "Sapphire", "Amber", "Ivory", "Obsidian", "Silver",
    ],
    "nouns": [
        "Echoes", "Dreams", "Shadows", "Horizons", "Memories", "Visions",
        "Waves", "Lights", "City", "Rain", "Autumn", "Signals",
        "Ruins", "Atlas", "Orbit", "Tides", "Embers", "Gardens",
        "Prayers", "Letters", "Mirrors", "Bridges", "Corners", "Oceans",
        "Stations", "Frequencies", "Constellations", "Portraits", "Distances",
    ],
    "patterns": [
        "{adj} {noun}",
        "The {adj} {noun}",
        "{noun} of {adj}",
        "{adj}",
        "{noun}",
        "Vol. {num}",
        "{adj} {noun} EP",
        "After {noun}",
        "Before the {noun}",
        "Into {adj} {noun}",
        "{noun} & {noun2}",
    ],
}

TRACK_TITLE_WORDS = {
    "verbs": ["Breathe", "Dissolve", "Wander", "Fall", "Drift", "Collapse", "Rise",
              "Bloom", "Shatter", "Ignite", "Surrender", "Vanish", "Awaken"],
    "things": ["Skyline", "Highway", "Rooftop", "Coastline", "Basement", "Balcony",
               "Midnight", "Sunrise", "Twilight", "Airport", "Subway", "Corridor"],
    "patterns": [
        "{verb}", "{thing}", "{verb} {thing}",
        "The {thing}", "Still {verb}ing",
        "{thing} (Revisited)", "{verb} Again",
    ],
}
