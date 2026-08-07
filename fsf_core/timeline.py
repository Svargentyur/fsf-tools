"""Trip timeline generator — creates realistic photo sequences."""
import random
import math
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

from .presets import CITY_PRESETS
from .randomizer import MetadataRandomizer

log = logging.getLogger('fsf')


class TripTimeline:
    """Generate a realistic sequence of photo metadata simulating a trip.
    
    Features:
    - Photos are spread across a multi-day trip (1-14 days)
    - Each day has a realistic shooting pattern (morning/afternoon/evening)
    - GPS coordinates drift naturally between hotspots
    - Scene types change based on time of day
    - Camera settings adapt to lighting conditions
    """
    
    # Typical photo counts per day for different photographer types
    SHOOTING_PATTERNS = {
        'casual': (5, 15),      # Tourist with phone
        'enthusiast': (15, 40), # Hobbyist with mirrorless
        'professional': (50, 200),  # Working photographer
    }
    
    # Time-of-day to scene mapping
    TIME_SCENES = {
        (5, 7): 'golden_hour',     # Sunrise
        (7, 10): 'daylight_outdoor',
        (10, 12): 'daylight_outdoor',
        (12, 14): 'indoor',         # Lunch break, cafes
        (14, 17): 'daylight_outdoor',
        (17, 19): 'golden_hour',    # Sunset
        (19, 21): 'night_street',
        (21, 23): 'night_street',
    }
    
    def __init__(self, city: str = None, preset: str = None,
                 days: int = None, style: str = 'casual'):
        self.city = city or random.choice(list(CITY_PRESETS.keys()))
        self.preset = preset
        self.days = days or random.randint(2, 7)
        self.style = style
        self.randomizer = MetadataRandomizer()
        
        city_data = CITY_PRESETS.get(self.city, {})
        self.hotspots = city_data.get('hotspots', [])
        self.base_lat = city_data.get('lat', 35.6762)
        self.base_lon = city_data.get('lon', 139.6503)
    
    def _get_scene_for_hour(self, hour: int) -> str:
        for (start, end), scene in self.TIME_SCENES.items():
            if start <= hour < end:
                return scene
        return 'night_street'
    
    def _interpolate_gps(self, hotspot_idx: int, progress: float) -> tuple:
        """Smoothly interpolate GPS between hotspots."""
        if not self.hotspots or len(self.hotspots) < 2:
            # Random drift around base coordinates  
            lat = self.base_lat + random.gauss(0, 0.005)
            lon = self.base_lon + random.gauss(0, 0.005)
            return lat, lon
        
        idx = hotspot_idx % len(self.hotspots)
        next_idx = (idx + 1) % len(self.hotspots)
        
        spot = self.hotspots[idx]
        next_spot = self.hotspots[next_idx]
        
        # Lerp + small random noise
        lat = spot[0] + (next_spot[0] - spot[0]) * progress + random.gauss(0, 0.001)
        lon = spot[1] + (next_spot[1] - spot[1]) * progress + random.gauss(0, 0.001)
        
        return lat, lon
    
    def generate(self, num_photos: int = None) -> List[Dict[str, Any]]:
        """Generate a complete timeline of photo metadata.
        
        Returns a list of metadata dicts, one per photo, ordered by timestamp.
        Each dict is ready to be passed to handler.spoof_metadata().
        """
        min_per_day, max_per_day = self.SHOOTING_PATTERNS.get(self.style, (5, 15))
        
        if num_photos:
            photos_per_day = max(1, num_photos // self.days)
        else:
            photos_per_day = random.randint(min_per_day, max_per_day)
            num_photos = photos_per_day * self.days
        
        # Pick a random start date (1-3 years ago)
        start_date = datetime.now() - timedelta(
            days=random.randint(30, 1095),
            hours=random.randint(0, 23)
        )
        
        timeline = []
        hotspot_counter = 0
        
        for day in range(self.days):
            day_date = start_date + timedelta(days=day)
            
            # Generate shooting windows for this day
            # Most tourists shoot between 8am and 10pm
            day_photos = min(photos_per_day + random.randint(-3, 3), 
                           num_photos - len(timeline))
            if day == self.days - 1:
                day_photos = num_photos - len(timeline)
            
            if day_photos <= 0:
                continue
            
            # Spread photos across the day with natural gaps
            shoot_start = random.randint(7, 10)  # Start shooting hour
            shoot_end = random.randint(19, 22)    # End shooting hour
            
            for i in range(day_photos):
                if len(timeline) >= num_photos:
                    break
                
                # Calculate time for this photo
                progress = i / max(day_photos - 1, 1)
                hour = shoot_start + (shoot_end - shoot_start) * progress
                hour_int = int(hour)
                minute = int((hour % 1) * 60) + random.randint(-5, 5)
                minute = max(0, min(59, minute))
                second = random.randint(0, 59)
                
                photo_time = day_date.replace(
                    hour=max(0, min(23, hour_int)),
                    minute=minute,
                    second=second
                )
                
                # Determine scene based on time of day
                scene = self._get_scene_for_hour(hour_int)
                
                # GPS position — drift through hotspots
                gps_progress = (i / max(day_photos, 1))
                lat, lon = self._interpolate_gps(hotspot_counter, gps_progress)
                
                # Generate full EXIF with correlated physics
                exif = self.randomizer.random_image_exif(
                    preset_name=self.preset,
                    city=self.city,
                    scene=scene
                )
                
                # Override with our timeline-specific values
                dt_str = photo_time.strftime('%Y:%m:%d %H:%M:%S')
                exif['datetime_original'] = dt_str
                exif['datetime_digitized'] = dt_str
                exif['gps_lat'] = abs(lat)
                exif['gps_lat_ref'] = 'N' if lat >= 0 else 'S'
                exif['gps_lon'] = abs(lon)
                exif['gps_lon_ref'] = 'E' if lon >= 0 else 'W'
                
                timeline.append(exif)
            
            hotspot_counter += 1
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x.get('datetime_original', ''))
        
        log.info(f'Generated timeline: {len(timeline)} photos over {self.days} days in {self.city}')
        return timeline
