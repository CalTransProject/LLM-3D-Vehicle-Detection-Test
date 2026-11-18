from __future__ import annotations
import argparse, json, math
from pathlib import Path

def xy(p):
    if len(p) < 2:
        raise ValueError("Point needs x and y")
    return float(p[0]), float(p[1])

def point_to_segment_distance_xy(point, a, b):
    px, py = xy(point); ax, ay = xy(a); bx, by = xy(b)
    abx, aby = bx-ax, by-ay
    d2 = abx*abx + aby*aby
    if d2 == 0:
        return math.hypot(px-ax, py-ay), (ax, ay)
    t = ((px-ax)*abx + (py-ay)*aby) / d2
    t = max(0.0, min(1.0, t))
    nx, ny = ax + t*abx, ay + t*aby
    return math.hypot(px-nx, py-ny), (nx, ny)

def distance_to_polyline_xy(point, polyline):
    if not polyline:
        raise ValueError("Lane polyline cannot be empty")
    if len(polyline) == 1:
        x, y = xy(polyline[0]); px, py = xy(point)
        return math.hypot(px-x, py-y), (x, y), 0
    best = (float("inf"), None, -1)
    for i in range(len(polyline)-1):
        d, q = point_to_segment_distance_xy(point, polyline[i], polyline[i+1])
        if d < best[0]:
            best = (d, q, i)
    return best

def lane_centerline(lane):
    if "points" in lane:
        if not lane["points"]:
            raise ValueError("Lane points cannot be empty")
        return lane["points"]
    left, right = lane.get("left_boundary"), lane.get("right_boundary")
    if left is None or right is None or len(left) != len(right) or not left:
        raise ValueError("Lane needs points or matching left/right boundaries")
    out = []
    for l, r in zip(left, right):
        p = [(float(l[0])+float(r[0]))/2, (float(l[1])+float(r[1]))/2]
        if len(l) >= 3 and len(r) >= 3:
            p.append((float(l[2])+float(r[2]))/2)
        out.append(p)
    return out

def assign_vehicle_lane(vehicle_location, lanes, max_lane_distance=None):
    if not lanes:
        return {"lane_id":"Unassigned","distance":None,"nearest_lane_point":None}
    best = None
    for lane in lanes:
        lane_id = str(lane.get("lane_id", lane.get("id", "UnknownLane")))
        d, q, seg = distance_to_polyline_xy(vehicle_location, lane_centerline(lane))
        item = {"lane_id":lane_id,"distance":d,
                "nearest_lane_point":[round(q[0],4),round(q[1],4)],
                "nearest_segment_index":seg}
        if best is None or d < best["distance"]:
            best = item
    if max_lane_distance is not None and best["distance"] > max_lane_distance:
        best["lane_id"] = "Unassigned"
    best["distance"] = round(best["distance"], 4)
    return best

def vehicle_list(frame):
    v = frame.get("vehicles", frame.get("Vehicle", []))
    if isinstance(v, dict): return [v]
    if isinstance(v, list): return v
    raise ValueError("vehicles/Vehicle must be a list or object")

def vehicle_location(v):
    for k in ("vehicle_location_on_frame","Vehicle_location_on_frame","location","center","xyz"):
        if k in v: return v[k]
    raise ValueError("Vehicle has no recognized location field")

def process_frame(frame, max_lane_distance=None):
    lanes = frame.get("lanes", frame.get("lane_references", []))
    vehicles = vehicle_list(frame)
    counts = {str(l.get("lane_id", l.get("id","UnknownLane"))):0 for l in lanes}
    counts["Unassigned"] = 0
    enriched = []
    for v in vehicles:
        r = assign_vehicle_lane(vehicle_location(v), lanes, max_lane_distance)
        e = dict(v)
        e["Vehicle_lane"] = r["lane_id"]
        e["Vehicle_distance_from_lane"] = r["distance"]
        e["Vehicle_nearest_lane_point"] = r["nearest_lane_point"]
        enriched.append(e)
        counts[r["lane_id"]] = counts.get(r["lane_id"], 0) + 1
    out = dict(frame)
    out.pop("Vehicle", None)
    out["vehicle_count"] = len(vehicles)
    out["vehicles"] = enriched
    out["lane_vehicle_counts"] = counts
    return out

def main():
    p = argparse.ArgumentParser()
    p.add_argument("input_json", type=Path)
    p.add_argument("output_json", type=Path)
    p.add_argument("--max-lane-distance", type=float, default=None)
    a = p.parse_args()
    frame = json.loads(a.input_json.read_text(encoding="utf-8"))
    out = process_frame(frame, a.max_lane_distance)
    a.output_json.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Processed frame:", out.get("frame_id","unknown"))
    print("Vehicles:", out["vehicle_count"])
    print("Lane counts:", out["lane_vehicle_counts"])
    print("Saved:", a.output_json)

if __name__ == "__main__":
    main()
