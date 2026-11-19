from pathlib import Path
import math
import json

# Input file from Matt.
file_path = Path(
    r"C:\Users\alfon\Downloads\labels_txt_reviewed"
    r"\labels_txt_reviewed\000002.txt"
)

# Temporary test point—not a confirmed reference object.
reference = (0.0, 0.0, 0.0)

# Prepare the results.
output = {
    "frame_id": file_path.stem,
    "validation_status": "unverified coordinate meanings and units",
    "distance_method": "3D Euclidean using assumed xyz",
    "distance_units": "input units",
    "reference_object_id": None,
    "reference_point_type": "temporary test point",
    "reference_object_location": {
        "x": reference[0],
        "y": reference[1],
        "z": reference[2]
    },
    "reference_object_size": None,
    "vehicle_count": 0,
    "vehicles": []
}

print("Frame:", file_path.stem)
print("Reference point:", reference)
print("UNVERIFIED: assuming the first three values are x, y, z.")
print("Distances are in input units, not confirmed meters.\n")

# Read the file and calculate each distance.
with file_path.open("r", encoding="utf-8") as file:
    for line_number, line in enumerate(file, start=1):
        parts = line.split()

        if not parts:
            continue

        if len(parts) != 8:
            print(f"Skipping line {line_number}: expected 8 fields.")
            continue

        try:
            x, y, z = map(float, parts[1:4])

            if not all(math.isfinite(v) for v in (x, y, z)):
                raise ValueError("Coordinates must be finite.")
        except ValueError:
            print(f"Skipping line {line_number}: invalid coordinates.")
            continue

        distance = math.sqrt(
            (x - reference[0]) ** 2
            + (y - reference[1]) ** 2
            + (z - reference[2]) ** 2
        )

        print("Vehicle type:", parts[0])
        print("Assumed position:", (x, y, z))
        print(f"Distance from test point: {distance:.2f} input units")
        print()

        output["vehicles"].append({
            "vehicle_id": f"{file_path.stem}_line_{line_number}",
            "vehicle_id_scope": "this frame only; not a tracking ID",
            "vehicle_type": parts[0],
            "vehicle_location_on_frame": {"x": x, "y": y, "z": z},
            "vehicle_bounding_box_size": None,
            "vehicle_distance_from_reference_point": round(distance, 2),
            "vehicle_confidence": None,
            "vehicle_lane": None
        })

# Count the vehicle entries successfully processed.
output["vehicle_count"] = len(output["vehicles"])

# Save beside this Python script.
output_path = (
    Path(__file__).resolve().parent
    / f"frame_{file_path.stem}_unverified.json"
)

with output_path.open("w", encoding="utf-8") as file:
    json.dump(output, file, indent=4, allow_nan=False)

print(f"Results saved to: {output_path}")