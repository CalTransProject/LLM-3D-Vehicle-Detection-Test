# Simulated data for testing—not real vehicle detections.
# All positions are in meters in the same coordinate system.
# Positions represent object centers.

frame_id = "sample_frame_001"

reference_object = {
    "id": "reference_01",
    "location": {"x": 0.0, "y": 0.0, "z": 0.0},
    "size": None
}

vehicles = [
    {
        "id": "vehicle_01",
        "type": "car",
        "location": {"x": 3.0, "y": 4.0, "z": 0.0}
    },
    {
        "id": "vehicle_02",
        "type": "truck",
        "location": {"x": 0.0, "y": 0.0, "z": 12.0}
    },
    {
        "id": "vehicle_03",
        "type": "car",
        "location": {"x": 2.0, "y": 3.0, "z": 6.0}
    }
]

import math


def calculate_distance(vehicle_location, reference_location):
    dx = vehicle_location["x"] - reference_location["x"]
    dy = vehicle_location["y"] - reference_location["y"]
    dz = vehicle_location["z"] - reference_location["z"]

    return math.sqrt(dx**2 + dy**2 + dz**2)


import json
import time

start_time = time.perf_counter()

output = {
    "frame_id": frame_id,
    "data_source": "simulated",
    "distance_method": "3D center-to-center Euclidean",
    "reference_object_id": reference_object["id"],
    "reference_object_location": reference_object["location"],
    "reference_object_size": reference_object["size"],
    "vehicle_count": len(vehicles),
    "vehicles": []
}

for vehicle in vehicles:
    distance = calculate_distance(
        vehicle["location"],
        reference_object["location"]
    )

    output["vehicles"].append({
        "vehicle_id": vehicle["id"],
        "vehicle_type": vehicle["type"],
        "vehicle_location_on_frame": vehicle["location"],
        "vehicle_bounding_box_size": None,
        "vehicle_distance_from_reference_object_meters": round(distance, 2),
        "vehicle_confidence": None,
        "vehicle_lane": None
    })

elapsed_time = time.perf_counter() - start_time

print(json.dumps(output, indent=4))
print(f"\nCalculation and output-building time: {elapsed_time:.6f} seconds")

## Saves results and prints to JSON

from pathlib import Path

output_path = Path(__file__).resolve().parent / "frame_output.json"

with output_path.open("w", encoding="utf-8") as file:
    json.dump(output, file, indent=4)

print(f"Results saved to: {output_path}")

## Automatically verifies the calculations

expected_distances = [5.0, 12.0, 7.0]

for vehicle, expected in zip(vehicles, expected_distances):
    actual = calculate_distance(
        vehicle["location"],
        reference_object["location"]
    )

    assert math.isclose(actual, expected, abs_tol=1e-9), (
        f'{vehicle["id"]}: expected {expected}, got {actual}'
    )

print("PASS: All 3 sample distances are correct.")