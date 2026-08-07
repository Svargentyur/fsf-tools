"""Realistic metadata randomizer with physically correlated parameters."""

import random
import math
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from .presets import (
    CAMERA_PRESETS, CITY_PRESETS, SOFTWARE_PRESETS, AUDIO_PRESETS, PDF_PRESETS,
    SCENE_PROFILES, STANDARD_SHUTTER_SPEEDS,
    IDENTITY_FIRST_NAMES, IDENTITY_LAST_NAMES,
    ALBUM_WORDS, TRACK_TITLE_WORDS,
)


class MetadataRandomizer:
    """Generates random but physically plausible metadata.

    Unlike naive randomizers, this correlates ISO, shutter speed, aperture,
    and scene type to produce metadata that looks like real camera output.
    """

    # ─────────────────────────────────────────────────
    #  Image EXIF
    # ─────────────────────────────────────────────────

    def random_image_exif(self, preset_name: Optional[str] = None,
                          city: Optional[str] = None,
                          scene: Optional[str] = None,
                          actual_size: Optional[tuple] = None) -> Dict[str, Any]:
        """Generate realistic EXIF data with physically correlated parameters.

        The generated ISO, shutter speed, and aperture follow the exposure
        triangle — they're correlated to produce a correct exposure for
        the chosen scene profile.
        """
        # Pick camera
        if preset_name and preset_name in CAMERA_PRESETS:
            cam = CAMERA_PRESETS[preset_name]
        else:
            preset_name = random.choice(list(CAMERA_PRESETS.keys()))
            cam = CAMERA_PRESETS[preset_name]

        # Pick scene profile (weighted random)
        if scene and scene in SCENE_PROFILES:
            profile = SCENE_PROFILES[scene]
        else:
            profiles = list(SCENE_PROFILES.items())
            weights = [p[1]["weight"] for p in profiles]
            scene_name, profile = random.choices(profiles, weights=weights, k=1)[0]

        # ── Generate correlated exposure parameters ──

        # 1. Pick ISO from scene-appropriate range, biased towards lower values
        iso_min, iso_max = profile["iso_range"]
        # Clamp to camera's actual range
        iso_min = max(iso_min, cam["iso"][0])
        iso_max = min(iso_max, cam["iso"][1])

        # Use camera's common ISO values within the scene range
        common_isos = [iso for iso in cam.get("iso_common", []) if iso_min <= iso <= iso_max]
        if common_isos:
            # Weight towards lower ISOs (more common in real photography)
            weights = [1.0 / (1 + i * 0.7) for i in range(len(common_isos))]
            iso = random.choices(common_isos, weights=weights, k=1)[0]
        else:
            iso = self._biased_low_random(iso_min, iso_max)

        # 2. Pick shutter speed from scene range using standard stops
        exp_min, exp_max = profile["exposure_range"]
        available_speeds = [s for s in STANDARD_SHUTTER_SPEEDS if exp_min <= s <= exp_max]
        if not available_speeds:
            # Fallback: find closest standard speeds
            available_speeds = sorted(STANDARD_SHUTTER_SPEEDS,
                                      key=lambda s: abs(math.log(s) - math.log((exp_min + exp_max) / 2)))[:5]
        exposure_time = random.choice(available_speeds)

        # 3. Pick f-number based on scene preference
        f_pref = profile.get("f_preference", "mid")
        available_f = cam.get("f_numbers_available")
        base_f = cam["f_number"]

        if available_f:
            if f_pref == "bokeh":
                f_number = available_f[0]  # widest
            elif f_pref == "wide":
                f_number = random.choice(available_f[:max(2, len(available_f) // 2)])
            elif f_pref == "sharp":
                sharp_range = [f for f in available_f if 8.0 <= f <= 16.0]
                f_number = random.choice(sharp_range) if sharp_range else available_f[-1]
            else:  # mid
                mid_range = [f for f in available_f if 4.0 <= f <= 8.0]
                f_number = random.choice(mid_range) if mid_range else random.choice(available_f)
        else:
            f_number = base_f

        # 4. Pick focal length (if zoom lens)
        focal_lengths = cam.get("focal_lengths_available")
        if focal_lengths:
            focal_length = random.choice(focal_lengths)
            focal_length_35mm = focal_length  # Assume full-frame for simplicity
        else:
            focal_length = cam["focal_length"]
            focal_length_35mm = cam.get("focal_length_35mm", int(focal_length))

        # 5. Generate realistic date/time based on scene
        time_range = profile.get("time_range", (8, 22))
        dt = self.random_date_with_time(time_range)

        # 6. GPS from city hotspot
        gps = self.random_gps(city)

        # 7. Orientation (weighted by scene)
        orient_weights = profile.get("orientation_weights", {1: 60, 6: 15, 8: 15, 3: 10})
        orientations = list(orient_weights.keys())
        weights = list(orient_weights.values())
        orientation = random.choices(orientations, weights=weights, k=1)[0]

        # 8. Image dimensions from camera presets
        image_size = random.choice(cam.get("image_sizes", [(4032, 3024)]))
        if orientation in (6, 8):  # Portrait orientation → swap if landscape dims
            if image_size[0] > image_size[1]:
                image_size = (image_size[1], image_size[0])

        # 9. Scene capture type
        scene_capture_type = profile.get("scene_capture_type", 0)

        datetime_str = dt.strftime("%Y:%m:%d %H:%M:%S")
        # Add subsecond for realism (many cameras record this)
        subsec = f"{random.randint(0, 999):03d}"

        return {
            # IFD0 tags
            "make": cam["make"],
            "model": cam["model"],
            "software": cam.get("software", ""),
            "orientation": orientation,
            "datetime": datetime_str,
            # ExifIFD tags
            "datetime_original": datetime_str,
            "datetime_digitized": datetime_str,
            "subsec_time_original": subsec,
            "iso": iso,
            "exposure_time": exposure_time,
            "f_number": f_number,
            "focal_length": float(focal_length),
            "focal_length_35mm": focal_length_35mm,
            "exposure_program": cam.get("exposure_program", 2),
            "metering_mode": cam.get("metering_mode", 5),
            "white_balance": cam.get("white_balance", 0),
            "flash": cam.get("flash", 16),
            "color_space": cam.get("color_space", 1),
            "scene_capture_type": scene_capture_type,
            "image_width": actual_size[0] if actual_size else image_size[0],
            "image_height": actual_size[1] if actual_size else image_size[1],
            "lens_model": cam.get("lens_model", ""),
            # GPS
            "gps_lat": gps["latitude"],
            "gps_lat_ref": gps["lat_ref"],
            "gps_lon": gps["longitude"],
            "gps_lon_ref": gps["lon_ref"],
            "gps_altitude": round(random.uniform(0, 150), 1),
            "gps_timestamp": dt,
        }

    # ─────────────────────────────────────────────────
    #  Date/time generation
    # ─────────────────────────────────────────────────

    def random_date(self, start_year: int = 2022, end_year: int = 2025) -> datetime:
        """Generate random plausible date."""
        start = datetime(start_year, 1, 1)
        end = datetime(end_year, 12, 31)
        delta = end - start
        random_seconds = random.randint(0, int(delta.total_seconds()))
        return start + timedelta(seconds=random_seconds)

    def random_date_with_time(self, time_range: tuple,
                               start_year: int = 2022, end_year: int = 2025) -> datetime:
        """Generate date with time of day matching the scene profile.

        Photos are rarely taken at 3am (unless nightlife). This method
        generates times that match when people actually take photos.
        """
        # Base date
        start = datetime(start_year, 1, 1)
        end = datetime(end_year, 12, 31)
        days = (end - start).days
        random_day = start + timedelta(days=random.randint(0, days))

        # Time of day from scene range
        hour_start, hour_end = time_range
        if hour_start <= hour_end:
            hour = random.randint(hour_start, hour_end)
        else:
            # Wraps around midnight (e.g., 20-3)
            if random.random() < 0.6:
                hour = random.randint(hour_start, 23)
            else:
                hour = random.randint(0, hour_end)

        minute = random.randint(0, 59)
        second = random.randint(0, 59)

        return random_day.replace(hour=hour, minute=minute, second=second)

    # ─────────────────────────────────────────────────
    #  GPS generation
    # ─────────────────────────────────────────────────

    def random_gps(self, city: Optional[str] = None) -> Dict[str, Any]:
        """Generate GPS coords near a real tourist hotspot in the city.

        Instead of random offset, picks a real landmark/hotspot and adds
        small natural walking-distance variation (~100-300m).
        """
        if city and city in CITY_PRESETS:
            city_data = CITY_PRESETS[city]
        else:
            city = random.choice(list(CITY_PRESETS.keys()))
            city_data = CITY_PRESETS[city]

        # Pick a hotspot (or city center)
        hotspots = city_data.get("hotspots", [(city_data["lat"], city_data["lon"])])
        base_lat, base_lon = random.choice(hotspots)

        # Add realistic walking-distance offset (~100-500m ≈ 0.001-0.005 degrees)
        lat_offset = random.gauss(0, 0.002)  # Gaussian for natural clustering
        lon_offset = random.gauss(0, 0.002)

        return {
            "latitude": round(abs(base_lat + lat_offset), 6),
            "longitude": round(abs(base_lon + lon_offset), 6),
            "lat_ref": city_data["lat_ref"],
            "lon_ref": city_data["lon_ref"],
        }

    # ─────────────────────────────────────────────────
    #  Audio tags
    # ─────────────────────────────────────────────────

    def random_audio_tags(self) -> Dict[str, Any]:
        """Generate realistic audio metadata tags."""
        locale = random.choice(list(IDENTITY_FIRST_NAMES.keys()))
        artist = self._random_person_name(locale)
        album = self._random_album_name()
        year = random.randint(2015, 2025)
        genre = random.choice(AUDIO_PRESETS["genres"])
        total_tracks = random.choice([4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])
        track_num = random.randint(1, total_tracks)

        return {
            "title": self._random_track_title(),
            "artist": artist,
            "album": album,
            "album_artist": artist,
            "year": str(year),
            "genre": genre,
            "track": f"{track_num}/{total_tracks}",
            "comment": "",
            "encoder": random.choice(AUDIO_PRESETS["encoders"]),
        }

    # ─────────────────────────────────────────────────
    #  PDF metadata
    # ─────────────────────────────────────────────────

    def random_pdf_meta(self) -> Dict[str, Any]:
        """Generate realistic PDF metadata."""
        locale = random.choice(["en", "de", "es"])
        author = self._random_person_name(locale)
        creator = random.choice(PDF_PRESETS["creators"])
        producer = random.choice(PDF_PRESETS["producers"])

        # Creation and mod dates should be close
        creation_date = self.random_date(2021, 2025)
        # Most edits happen within days, not months
        mod_offset = random.choices(
            [timedelta(minutes=random.randint(5, 120)),
             timedelta(hours=random.randint(1, 48)),
             timedelta(days=random.randint(1, 14))],
            weights=[40, 35, 25], k=1
        )[0]
        mod_date = creation_date + mod_offset

        # Matching creator/producer pairs (Word produces Word, etc.)
        if "Word" in creator:
            producer = random.choice([p for p in PDF_PRESETS["producers"] if "Word" in p])
        elif "LibreOffice" in creator:
            producer = random.choice([p for p in PDF_PRESETS["producers"] if "LibreOffice" in p])
        elif "LaTeX" in creator:
            producer = random.choice([p for p in PDF_PRESETS["producers"] if "pdfTeX" in p or "LaTeX" in p])

        # Realistic document titles
        doc_titles = [
            f"Report - {creation_date.strftime('%B %Y')}",
            f"Meeting Notes {creation_date.strftime('%d.%m.%Y')}",
            "Project Proposal",
            f"Invoice #{random.randint(1000, 9999)}",
            "Untitled Document",
            f"{author} - Resume",
            f"Presentation Q{(creation_date.month - 1) // 3 + 1} {creation_date.year}",
            "Technical Specification",
            "User Guide",
            f"Agreement - {creation_date.strftime('%Y%m%d')}",
        ]

        return {
            "author": author,
            "title": random.choice(doc_titles),
            "creator": creator,
            "producer": producer,
            "creation_date": creation_date.strftime("D:%Y%m%d%H%M%S+00'00'"),
            "mod_date": mod_date.strftime("D:%Y%m%d%H%M%S+00'00'"),
        }

    # ─────────────────────────────────────────────────
    #  Identity forge (consistent persona)
    # ─────────────────────────────────────────────────

    def forge_identity(self, locale: Optional[str] = None) -> Dict[str, Any]:
        """Generate a complete fake identity for consistent metadata spoofing.

        Returns a persona dict that can be reused across multiple files
        to create a consistent metadata trail.
        """
        if not locale:
            locale = random.choice(list(IDENTITY_FIRST_NAMES.keys()))

        name = self._random_person_name(locale)
        camera_name = random.choice(list(CAMERA_PRESETS.keys()))
        camera = CAMERA_PRESETS[camera_name]
        city = random.choice(list(CITY_PRESETS.keys()))
        base_date = self.random_date(2023, 2025)

        # Consistent software (a person typically uses one editor)
        software = random.choice(SOFTWARE_PRESETS)

        return {
            "name": name,
            "locale": locale,
            "camera_preset": camera_name,
            "camera": camera,
            "home_city": city,
            "software": software,
            "base_date": base_date,
            "style": random.choice(["daylight_outdoor", "portrait", "indoor", "golden_hour"]),
        }

    def random_image_from_identity(self, identity: Dict[str, Any],
                                    day_offset: int = 0) -> Dict[str, Any]:
        """Generate EXIF data consistent with a forged identity.

        Multiple calls with the same identity produce metadata that looks
        like it came from the same person's camera over time.
        """
        cam = identity["camera"]
        preset_name = identity["camera_preset"]

        # Date progresses naturally from base_date
        dt = identity["base_date"] + timedelta(
            days=day_offset + random.randint(0, 3),
            hours=random.randint(-2, 2),
            minutes=random.randint(0, 59),
        )

        # Same city with slight variation
        city = identity["home_city"]

        exif = self.random_image_exif(
            preset_name=preset_name,
            city=city,
            scene=identity.get("style"),
        )

        # Override with consistent identity data
        exif["software"] = identity["software"]
        exif["datetime"] = dt.strftime("%Y:%m:%d %H:%M:%S")
        exif["datetime_original"] = dt.strftime("%Y:%m:%d %H:%M:%S")
        exif["datetime_digitized"] = dt.strftime("%Y:%m:%d %H:%M:%S")

        return exif

    # ─────────────────────────────────────────────────
    #  Private helpers
    # ─────────────────────────────────────────────────

    def _biased_low_random(self, low: int, high: int) -> int:
        """Generate random int biased towards lower values (log distribution)."""
        if low <= 0:
            low = 1
        log_low = math.log(low)
        log_high = math.log(high)
        return int(round(math.exp(random.uniform(log_low, log_high * 0.6))))

    def _random_person_name(self, locale: str = "en") -> str:
        """Generate a random plausible person name from a specific locale."""
        first = random.choice(IDENTITY_FIRST_NAMES.get(locale, IDENTITY_FIRST_NAMES["en"]))
        last = random.choice(IDENTITY_LAST_NAMES.get(locale, IDENTITY_LAST_NAMES["en"]))
        return f"{first} {last}"

    def _random_album_name(self) -> str:
        """Generate a random plausible album name."""
        adj = random.choice(ALBUM_WORDS["adjectives"])
        noun = random.choice(ALBUM_WORDS["nouns"])
        noun2 = random.choice(ALBUM_WORDS["nouns"])
        num = random.randint(1, 4)

        pattern = random.choice(ALBUM_WORDS["patterns"])
        return pattern.format(adj=adj, noun=noun, noun2=noun2, num=num)

    def _random_track_title(self) -> str:
        """Generate a random plausible track title."""
        verb = random.choice(TRACK_TITLE_WORDS["verbs"])
        thing = random.choice(TRACK_TITLE_WORDS["things"])

        pattern = random.choice(TRACK_TITLE_WORDS["patterns"])
        return pattern.format(verb=verb, thing=thing)
