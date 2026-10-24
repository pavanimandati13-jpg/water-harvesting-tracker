import os, sys, tempfile, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "test.db")
import app as appmod


class HarvestTests(unittest.TestCase):
    def setUp(self):
        self.c = appmod.app.test_client()
        r = self.c.post("/api/sites", json={"name": "T", "roof_area": 100, "runoff_coeff": 0.8, "tank_capacity": 5000})
        self.sid = r.get_json()["id"]

    def test_health_and_seed(self):
        self.assertEqual(self.c.get("/health").get_json()["status"], "ok")
        self.assertGreaterEqual(len(self.c.get("/api/sites").get_json()), 2)

    def test_harvest_formula(self):
        self.assertEqual(appmod.harvest_litres(100, 10, 0.8), 800)

    def test_tank_fill_overflow_and_shortfall(self):
        self.c.post(f"/api/sites/{self.sid}/rainfall", json={"date": "2026-01-01", "mm": 100})  # 8000 L into 5000 L tank
        s = self.c.get(f"/api/sites/{self.sid}/summary").get_json()
        self.assertEqual(s["current_level"], 5000)
        self.assertEqual(s["overflow_wasted"], 3000)
        self.c.post(f"/api/sites/{self.sid}/usage", json={"date": "2026-01-02", "litres": 6000})
        s = self.c.get(f"/api/sites/{self.sid}/summary").get_json()
        self.assertEqual(s["current_level"], 0)
        self.assertEqual(s["shortfall"], 1000)
        self.assertEqual(s["percent_full"], 0)

    def test_validation(self):
        self.assertEqual(self.c.post("/api/sites", json={"name": "", "roof_area": -1}).status_code, 400)
        self.assertEqual(self.c.post(f"/api/sites/{self.sid}/rainfall", json={"date": "bad", "mm": 5}).status_code, 400)
        self.assertEqual(self.c.post(f"/api/sites/{self.sid}/usage", json={"date": "2026-01-01", "litres": 0}).status_code, 400)
        self.assertEqual(self.c.get("/api/sites/9999/summary").status_code, 404)

    def test_estimate(self):
        r = self.c.get("/api/estimate?area=100&rainfall=1000&coeff=0.8").get_json()
        self.assertEqual(r["litres_per_year"], 80000)
        self.assertEqual(self.c.get("/api/estimate?area=x").status_code, 400)

    def test_delete_entries(self):
        rid = self.c.post(f"/api/sites/{self.sid}/rainfall", json={"date": "2026-02-01", "mm": 10}).get_json()["id"]
        self.assertEqual(self.c.delete(f"/api/rainfall/{rid}").status_code, 200)
        self.assertEqual(self.c.delete(f"/api/rainfall/{rid}").status_code, 404)


if __name__ == "__main__":
    unittest.main()
