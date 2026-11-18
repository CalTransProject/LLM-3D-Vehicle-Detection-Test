import unittest
from lane_distance import point_to_segment_distance_xy, assign_vehicle_lane, lane_centerline, process_frame

class Tests(unittest.TestCase):
    def test_segment_distance(self):
        d, q = point_to_segment_distance_xy([5,2,0],[0,0,0],[10,0,0])
        self.assertAlmostEqual(d,2.0); self.assertEqual(q,(5.0,0.0))

    def test_nearest_lane(self):
        lanes=[
            {"lane_id":"Lane_1","points":[[0,-3.5,0],[50,-3.5,0]]},
            {"lane_id":"Lane_2","points":[[0,0,0],[50,0,0]]},
            {"lane_id":"Lane_3","points":[[0,3.5,0],[50,3.5,0]]}]
        r=assign_vehicle_lane([20,0.4,0.2],lanes)
        self.assertEqual(r["lane_id"],"Lane_2"); self.assertAlmostEqual(r["distance"],0.4)

    def test_unassigned_threshold(self):
        lanes=[{"lane_id":"Lane_1","points":[[0,0,0],[50,0,0]]}]
        r=assign_vehicle_lane([10,10,0],lanes,max_lane_distance=4)
        self.assertEqual(r["lane_id"],"Unassigned")

    def test_boundaries_to_centerline(self):
        lane={"lane_id":"L","left_boundary":[[0,-2,0],[10,-2,0]],"right_boundary":[[0,2,0],[10,2,0]]}
        self.assertEqual(lane_centerline(lane),[[0.0,0.0,0.0],[10.0,0.0,0.0]])

    def test_process_counts(self):
        frame={"frame_id":"f1","lanes":[
            {"lane_id":"Lane_1","points":[[0,-3.5,0],[50,-3.5,0]]},
            {"lane_id":"Lane_2","points":[[0,0,0],[50,0,0]]},
            {"lane_id":"Lane_3","points":[[0,3.5,0],[50,3.5,0]]}],
            "vehicles":[
                {"vehicle_id":"v1","vehicle_location_on_frame":[10,-3.2,0]},
                {"vehicle_id":"v2","vehicle_location_on_frame":[18,0.2,0]},
                {"vehicle_id":"v3","vehicle_location_on_frame":[30,3.8,0]}]}
        o=process_frame(frame,max_lane_distance=2)
        self.assertEqual([v["Vehicle_lane"] for v in o["vehicles"]],["Lane_1","Lane_2","Lane_3"])
        self.assertEqual(o["lane_vehicle_counts"]["Lane_1"],1)
        self.assertEqual(o["lane_vehicle_counts"]["Lane_2"],1)
        self.assertEqual(o["lane_vehicle_counts"]["Lane_3"],1)

if __name__=="__main__":
    unittest.main()
