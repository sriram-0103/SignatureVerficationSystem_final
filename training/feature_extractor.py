import json
from pathlib import Path
from typing import Dict, List, Union

import numpy as np
from scipy.spatial import ConvexHull
from scipy.stats import entropy

FEATURE_ORDER = [

    # ---------- Geometry ----------
    "width",
    "height",
    "aspect_ratio",
    "bounding_box_area",
    "path_length",
    "mean_x",
    "mean_y",
    "std_x",
    "std_y",
    "centroid_x",
    "centroid_y",
    "convex_hull_area",
    "stroke_density",
    "compactness",
    "straightness",

    # ---------- Temporal ----------
    "duration",
    "mean_velocity",
    "max_velocity",
    "min_velocity",
    "std_velocity",
    "median_velocity",
    "mean_acceleration",
    "max_acceleration",
    "min_acceleration",
    "std_acceleration",
    "mean_jerk",
    "max_jerk",
    "pause_count",
    "active_points",

    # ---------- Direction ----------
    "mean_angle",
    "std_angle",
    "max_angle",
    "min_angle",
    "mean_angular_velocity",
    "std_angular_velocity",
    "direction_change_count",
    "mean_direction_change",
    "max_direction_change",
    "mean_curvature",
    "max_curvature",
    "std_curvature",

    # ---------- Stroke ----------
    "stroke_count",
    "pen_lifts",
    "mean_stroke_length",
    "max_stroke_length",
    "min_stroke_length",
    "std_stroke_length",
    "mean_stroke_duration",
    "max_stroke_duration",
    "min_stroke_duration",

    # ---------- Shape ----------
    "solidity",
    "circularity",
    "eccentricity",
    "direction_entropy",
    "x_entropy",
    "y_entropy",
    "trajectory_complexity",

    # ---------- Pressure ----------
    "mean_pressure",
    "max_pressure",
    "min_pressure",
    "std_pressure",
    "pressure_range",
    "pressure_change"

]


class Signature:

    """
    Universal Signature Object

    Supports:
        - SVC2004 Task1
        - SVC2004 Task2
        - Live Canvas JSON
    """

    def __init__(self, source):

        self.source = source

        self.x = np.array([])
        self.y = np.array([])
        self.t = np.array([])
        self.pen = np.array([])
        self.pressure = np.array([])
        self.stroke = np.array([])

        self.load()

        self.clean()

        self.normalize()

        self.compute_arrays()

    # ---------------------------------------------------------

    def load(self):

        if isinstance(self.source, str):

            self._load_txt(self.source)

        elif isinstance(self.source, list):

            self._load_json(self.source)

        else:

            raise ValueError("Unsupported signature source.")

    # ---------------------------------------------------------

    def _load_txt(self, file_path):

        points = []

        with open(file_path, "r") as f:
            lines = f.readlines()

        if not lines:
            raise ValueError("Empty signature.")

        start = 1 if len(lines[0].split()) == 1 else 0

        stroke_id = 0
        previous_pen = 1

        for line in lines[start:]:

            p = line.split()

            if len(p) < 4:
                continue

            x = float(p[0])
            y = float(p[1])
            t = float(p[2])
            pen = int(p[3])

            pressure = 0.0

            if len(p) >= 7:
                pressure = float(p[6])

            if pen == 0 and previous_pen == 1:
                stroke_id += 1

            previous_pen = pen

            points.append(
                (
                    x,
                    y,  
                    t,
                    pen,
                    pressure,
                    stroke_id
                )
            )

        if len(points) < 2:
            raise ValueError("Insufficient signature points.")

        arr = np.asarray(points, dtype=np.float64)

        self.x = arr[:, 0]
        self.y = arr[:, 1]
        self.t = arr[:, 2]
        self.pen = arr[:, 3].astype(np.int32)
        self.pressure = arr[:, 4]
        self.stroke = arr[:, 5].astype(np.int32)

    # ---------------------------------------------------------

    def _load_json(self, signatures):

        points = []
        stroke_id = 0

        for stroke in signatures:

            for p in stroke:

                points.append(
                    (
                        float(p["x"]),
                        float(p["y"]),
                        float(p["time"]),
                        1,
                        float(p.get("pressure", 0.5)),
                        stroke_id
                    )
                )

            stroke_id += 1

        if len(points) < 2:
            raise ValueError("Insufficient signature points.")

        arr = np.asarray(points, dtype=np.float64)

        self.x = arr[:, 0]
        self.y = arr[:, 1]
        self.t = arr[:, 2]
        self.pen = arr[:, 3].astype(np.int32)
        self.pressure = arr[:, 4]
        self.stroke = arr[:, 5].astype(np.int32)

    # ---------------------------------------------------------

    def clean(self):

        if len(self.x) < 2:

            return

        keep = [0]

        for i in range(1, len(self.x)):

            if self.x[i] != self.x[i-1] or self.y[i] != self.y[i-1]:

                keep.append(i)

        self.x = self.x[keep]

        self.y = self.y[keep]

        self.t = self.t[keep]

        self.pen = self.pen[keep]

        self.pressure = self.pressure[keep]

        self.stroke = self.stroke[keep]

        valid = np.diff(self.t, prepend=self.t[0]) >= 0

        self.x = self.x[valid]

        self.y = self.y[valid]

        self.t = self.t[valid]

        self.pen = self.pen[valid]

        self.pressure = self.pressure[valid]

        self.stroke = self.stroke[valid]

    # ---------------------------------------------------------

    def normalize(self):

        if len(self.x)==0:
            return
        self.x=self.x-np.min(self.x)
        self.y=self.y-np.min(self.y)
        w=np.max(self.x); h=np.max(self.y)
        scale=max(w,h)
        if scale>0:
            self.x=self.x/scale
            self.y=self.y/scale
        if len(self.t):
            self.t=self.t-self.t[0]

    def compute_arrays(self):

        if len(self.x) < 2:

            self.dx = np.array([], dtype=np.float64)
            self.dy = np.array([], dtype=np.float64)
            self.dt = np.array([], dtype=np.float64)

            self.distance = np.array([], dtype=np.float64)
            self.velocity = np.array([], dtype=np.float64)
            self.acceleration = np.array([], dtype=np.float64)
            self.angle = np.array([], dtype=np.float64)
            self.angular_velocity = np.array([], dtype=np.float64)

            return

        self.dx = np.diff(self.x)
        self.dy = np.diff(self.y)
        self.dt = np.diff(self.t)

        self.dt[self.dt <= 0] = 1e-6

        self.distance = np.sqrt(
            self.dx ** 2 +
            self.dy ** 2
        )

        self.velocity = self.distance / self.dt

        if len(self.velocity):

            self.acceleration = np.diff(
                self.velocity,
                prepend=self.velocity[0]
            ) / self.dt

        else:

            self.acceleration = np.array([], dtype=np.float64)

        self.angle = np.arctan2(
            self.dy,
            self.dx
        )

        if len(self.angle):

            self.angular_velocity = np.diff(
                self.angle,
                prepend=self.angle[0]
            ) / self.dt

        else:

            self.angular_velocity = np.array([], dtype=np.float64)

            # ---------------------------------------------------------
    # GEOMETRIC FEATURES
    # ---------------------------------------------------------

    def geometry_features(self):

        features = {}

        if len(self.x) < 2:

            for name in FEATURE_ORDER[:15]:
                features[name] = 0.0

            return features

        width = float(np.max(self.x) - np.min(self.x))
        height = float(np.max(self.y) - np.min(self.y))

        path_length = float(np.sum(self.distance))

        features["width"] = width
        features["height"] = height

        features["aspect_ratio"] = (
            width / height
            if height > 1e-8
            else 0.0
        )

        features["bounding_box_area"] = width * height

        features["path_length"] = path_length

        features["mean_x"] = float(np.mean(self.x))
        features["mean_y"] = float(np.mean(self.y))

        features["std_x"] = float(np.std(self.x))
        features["std_y"] = float(np.std(self.y))

        features["centroid_x"] = features["mean_x"]
        features["centroid_y"] = features["mean_y"]

        hull_area = 0.0

        if len(self.x) >= 3:

            try:

                hull = ConvexHull(
                    np.column_stack((self.x, self.y))
                )

                hull_area = float(hull.volume)

            except Exception:

                hull_area = 0.0

        features["convex_hull_area"] = hull_area

        features["stroke_density"] = (
            path_length /
            (hull_area + 1e-8)
        )

        features["compactness"] = (
            (path_length ** 2) /
            (4 * np.pi * (hull_area + 1e-8))
        )

        direct = np.hypot(

            self.x[-1] - self.x[0],

            self.y[-1] - self.y[0]

        )

        features["straightness"] = (
            direct /
            (path_length + 1e-8)
        )

        return features
    

        # ---------------------------------------------------------
    # TEMPORAL FEATURES
    # ---------------------------------------------------------

    def temporal_features(self):

        features = {}

        if len(self.t) < 2 or len(self.velocity) == 0:

            features["duration"] = 0.0
            features["mean_velocity"] = 0.0
            features["max_velocity"] = 0.0
            features["min_velocity"] = 0.0
            features["std_velocity"] = 0.0
            features["median_velocity"] = 0.0

            features["mean_acceleration"] = 0.0
            features["max_acceleration"] = 0.0
            features["min_acceleration"] = 0.0
            features["std_acceleration"] = 0.0

            features["mean_jerk"] = 0.0
            features["max_jerk"] = 0.0

            features["pause_count"] = 0
            features["active_points"] = len(self.x)

            return features

        duration = float(self.t[-1] - self.t[0])

        features["duration"] = duration

        features["mean_velocity"] = float(np.mean(self.velocity))
        features["max_velocity"] = float(np.max(self.velocity))
        features["min_velocity"] = float(np.min(self.velocity))
        features["std_velocity"] = float(np.std(self.velocity))
        features["median_velocity"] = float(np.median(self.velocity))

        features["mean_acceleration"] = float(np.mean(self.acceleration))
        features["max_acceleration"] = float(np.max(self.acceleration))
        features["min_acceleration"] = float(np.min(self.acceleration))
        features["std_acceleration"] = float(np.std(self.acceleration))

        jerk = np.diff(
            self.acceleration,
            prepend=self.acceleration[0]
        )

        features["mean_jerk"] = float(np.mean(jerk))
        features["max_jerk"] = float(np.max(np.abs(jerk)))

        features["pause_count"] = int(
            np.sum(self.velocity < 0.001)
        )

        features["active_points"] = int(len(self.x))

        return features
    

        # ---------------------------------------------------------
    # DIRECTION FEATURES
    # ---------------------------------------------------------

    def direction_features(self):

        features = {}

        if len(self.angle) == 0:

            features["mean_angle"] = 0.0
            features["std_angle"] = 0.0
            features["max_angle"] = 0.0
            features["min_angle"] = 0.0

            features["mean_angular_velocity"] = 0.0
            features["std_angular_velocity"] = 0.0

            features["direction_change_count"] = 0
            features["mean_direction_change"] = 0.0
            features["max_direction_change"] = 0.0

            features["mean_curvature"] = 0.0
            features["max_curvature"] = 0.0
            features["std_curvature"] = 0.0

            return features

        features["mean_angle"] = float(np.mean(self.angle))
        features["std_angle"] = float(np.std(self.angle))
        features["max_angle"] = float(np.max(self.angle))
        features["min_angle"] = float(np.min(self.angle))

        if len(self.angular_velocity):

            features["mean_angular_velocity"] = float(
                np.mean(self.angular_velocity)
            )

            features["std_angular_velocity"] = float(
                np.std(self.angular_velocity)
            )


        else:

            features["mean_angular_velocity"] = 0.0
            features["std_angular_velocity"] = 0.0

        direction_changes = np.abs(np.diff(self.angle))

        if len(direction_changes):

            features["direction_change_count"] = int(
                np.sum(direction_changes > (np.pi / 4))
            )

            features["mean_direction_change"] = float(
                np.mean(direction_changes)
            )

            features["max_direction_change"] = float(
                np.max(direction_changes)
            )

        else:

            features["direction_change_count"] = 0
            features["mean_direction_change"] = 0.0
            features["max_direction_change"] = 0.0

        if len(self.distance) > 1 and len(direction_changes):

            n = min(
                len(direction_changes),
                len(self.distance) - 1
            )

            curvature = direction_changes[:n] / (
                self.distance[1:n+1] + 1e-8
            )

            features["mean_curvature"] = float(
                np.mean(curvature)
            )

            features["max_curvature"] = float(
                np.max(curvature)
            )

            features["std_curvature"] = float(
                np.std(curvature)
            )

        else:

            features["mean_curvature"] = 0.0
            features["max_curvature"] = 0.0
            features["std_curvature"] = 0.0

        return features
    

        # ---------------------------------------------------------
    # STROKE FEATURES
    # ---------------------------------------------------------

    def stroke_features(self):

        features = {}

        stroke_ids = np.unique(self.stroke)

        stroke_lengths = []

        stroke_durations = []

        for sid in stroke_ids:

            idx = self.stroke == sid

            if np.sum(idx) < 2:

                continue

            xs = self.x[idx]

            ys = self.y[idx]

            ts = self.t[idx]

            length = np.sum(

                np.sqrt(

                    np.diff(xs) ** 2 +

                    np.diff(ys) ** 2

                )

            )

            stroke_lengths.append(length)

            stroke_durations.append(

                ts[-1] - ts[0]

            )

        features["stroke_count"] = len(stroke_lengths)

        features["pen_lifts"] = max(

            len(stroke_lengths) - 1,

            0

        )

        if len(stroke_lengths):

            features["mean_stroke_length"] = np.mean(stroke_lengths)

            features["max_stroke_length"] = np.max(stroke_lengths)

            features["min_stroke_length"] = np.min(stroke_lengths)

            features["std_stroke_length"] = np.std(stroke_lengths)

        else:

            features["mean_stroke_length"] = 0

            features["max_stroke_length"] = 0

            features["min_stroke_length"] = 0

            features["std_stroke_length"] = 0

        if len(stroke_durations):

            features["mean_stroke_duration"] = np.mean(stroke_durations)

            features["max_stroke_duration"] = np.max(stroke_durations)

            features["min_stroke_duration"] = np.min(stroke_durations)

        else:

            features["mean_stroke_duration"] = 0

            features["max_stroke_duration"] = 0

            features["min_stroke_duration"] = 0

        return features
    

        # ---------------------------------------------------------
    # SHAPE FEATURES
    # ---------------------------------------------------------

    def shape_features(self):

        features = {}

        if len(self.x) < 3:

            features["solidity"] = 0.0
            features["circularity"] = 0.0
            features["eccentricity"] = 0.0
            features["direction_entropy"] = 0.0
            features["x_entropy"] = 0.0
            features["y_entropy"] = 0.0
            features["trajectory_complexity"] = 0.0

            return features

        pts = np.column_stack((self.x, self.y))

        hull_area = 0.0
        perimeter = 0.0

        try:

            hull = ConvexHull(pts)

            hull_area = float(hull.volume)

            hull_vertices = pts[hull.vertices]

            closed = np.vstack(
                [hull_vertices, hull_vertices[0]]
            )

            perimeter = float(
                np.sum(
                    np.linalg.norm(
                        np.diff(closed, axis=0),
                        axis=1
                    )
                )
            )

        except Exception:

            pass

        path_length = float(np.sum(self.distance))

        features["solidity"] = (
            path_length /
            (hull_area + 1e-8)
        )

        features["circularity"] = (
            (4 * np.pi * hull_area) /
            (perimeter ** 2 + 1e-8)
        )

    # ---------- Stable Eccentricity ----------

        if len(self.x) >= 2:

            covariance = np.cov(self.x, self.y)

            eigvals = np.linalg.eigvalsh(covariance)

            eigvals = np.sort(
                np.abs(eigvals)
            )[::-1]

            if len(eigvals) >= 2 and eigvals[0] > 1e-12:

                features["eccentricity"] = float(

                    np.sqrt(

                        max(

                            0.0,

                            1.0 - eigvals[1] / eigvals[0]

                        )

                    )

                )

            else:

                features["eccentricity"] = 0.0

        else:

            features["eccentricity"] = 0.0

    # ---------- Entropy ----------

        hist, _ = np.histogram(
            self.angle,
            bins=36,
            density=True
        )

        features["direction_entropy"] = float(
            entropy(hist + 1e-12)
        )

        hx, _ = np.histogram(
            self.x,
            bins=30,
            density=True
        )

        hy, _ = np.histogram(
            self.y,
            bins=30,
            density=True
        )

        features["x_entropy"] = float(
            entropy(hx + 1e-12)
        )

        features["y_entropy"] = float(
            entropy(hy + 1e-12)
        )

        if len(self.angle):

            features["trajectory_complexity"] = float(

                np.sum(

                    np.abs(

                        np.diff(self.angle)

                    )

                )

            )

        else:

            features["trajectory_complexity"] = 0.0

        return features
    
        # ---------------------------------------------------------
    # PRESSURE FEATURES
    # ---------------------------------------------------------

    def pressure_features(self):

        features = {}

        if len(self.pressure) == 0 or np.max(self.pressure) <= 0:

            features["mean_pressure"] = 0.0
            features["max_pressure"] = 0.0
            features["min_pressure"] = 0.0
            features["std_pressure"] = 0.0
            features["pressure_range"] = 0.0
            features["pressure_change"] = 0.0

            return features

        features["mean_pressure"] = float(np.mean(self.pressure))
        features["max_pressure"] = float(np.max(self.pressure))
        features["min_pressure"] = float(np.min(self.pressure))
        features["std_pressure"] = float(np.std(self.pressure))

        features["pressure_range"] = float(
            np.max(self.pressure) -
            np.min(self.pressure)
        )

        if len(self.pressure) > 1:

            dp = np.diff(self.pressure)

            features["pressure_change"] = float(
                np.mean(np.abs(dp))
            )

        else:

            features["pressure_change"] = 0.0

        return features



    # ---------------------------------------------------------
    # FINAL FEATURE VECTOR
    # ---------------------------------------------------------

    def extract_features(self):

        features = {}

        features.update(self.geometry_features())
        features.update(self.temporal_features())
        features.update(self.direction_features())
        features.update(self.stroke_features())
        features.update(self.shape_features())
        features.update(self.pressure_features())

        return features


    # ---------------------------------------------------------

    def feature_vector(self):

        features = self.extract_features()

        missing = [

            name

            for name in FEATURE_ORDER

            if name not in features

        ]

        if missing:

            raise ValueError(

                f"Missing features: {missing}"

            )

        return np.asarray(

            [

                float(features[name])

                for name in FEATURE_ORDER

            ],

            dtype=np.float32

        )


    # ---------------------------------------------------------

    def feature_names(self):

        return FEATURE_ORDER.copy()