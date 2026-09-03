import tempfile
import unittest
from pathlib import Path

import server
import affinity_engine
import tarot_engine
import ziwei_engine


class XuanhengBackendTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        server.STATE_DIR = Path(self.temp_dir.name)
        server.STATE_DB = server.STATE_DIR / "state.sqlite3"
        server.initialize_state()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_bazi_complete_fields(self):
        stdout = server.run_engine([
            "python3", str(server.PAI_PAN), "--solar", "1990-05-15", "--hour", "12:00", "--sex", "男"
        ])
        chart = server.parse_output(stdout)
        self.assertEqual([p["stem"] + p["branch"] for p in chart["pillars"]], ["庚午", "辛巳", "庚辰", "壬午"])
        self.assertEqual([p["nayin"] for p in chart["pillars"]], ["路旁土", "白蜡金", "白蜡金", "杨柳木"])
        self.assertEqual(chart["pillars"][0]["hiddenStems"][0]["tenGod"], "正官")
        self.assertTrue(any(item["name"] == "天乙贵人" for item in chart["shenshaDetails"]))

    def test_question_history_is_reused_and_exportable(self):
        result = {"title": "测试研判", "summary": "结果", "action": "行动", "evidence": [], "disclaimer": "参考"}
        payload = {"question": "测试问题", "intent": "question", "historyId": "abc"}
        record_id, existed = server.save_question_history(payload, "f" * 64, result)
        self.assertFalse(existed)
        same_id, existed = server.save_question_history(payload, "f" * 64, result)
        self.assertTrue(existed)
        self.assertEqual(record_id, same_id)
        item = server.get_question_history(record_id)
        self.assertEqual(item["result"]["title"], "测试研判")
        self.assertIn("测试问题", server.question_markdown(item))

    def test_tarot_draw_is_reproducible_and_unique(self):
        first = tarot_engine.draw_reading("celtic", "方向", 42, "night")
        second = tarot_engine.draw_reading("celtic", "方向", 42, "night")
        self.assertEqual(first, second)
        names = [card["name"] for card in first["cards"]]
        self.assertEqual(len(names), 10)
        self.assertEqual(len(names), len(set(names)))
        self.assertTrue(all(card["meaning"] for card in first["cards"]))

    def test_tarot_history_reopens_same_draw(self):
        record = server.save_tarot_draw({"spread": "three", "question": "事业", "seed": 123, "timeFactor": "morning"})
        opened = server.get_tarot_reading(record["id"])
        self.assertEqual(opened["draw"], record["draw"])
        interpretation = tarot_engine.local_interpretation(opened["draw"])
        server.update_tarot_interpretation(record["id"], interpretation)
        reopened = server.get_tarot_reading(record["id"])
        self.assertEqual(reopened["interpretation"], interpretation)
        self.assertIn("Seed", server.tarot_markdown(reopened))

    def test_tarot_interpretation_falls_back_without_api_and_is_cached(self):
        record = server.save_tarot_draw({"spread": "single", "question": "下一步", "seed": 7, "timeFactor": "afternoon"})
        with server.API_CONFIG_LOCK:
            original = dict(server.API_CONFIG)
            server.API_CONFIG.clear()
        try:
            interpretation, cached = server.analyze_tarot_record(record["id"])
            self.assertFalse(cached)
            self.assertEqual(interpretation["source"], "local")
            reopened, cached = server.analyze_tarot_record(record["id"])
            self.assertTrue(cached)
            self.assertEqual(reopened, interpretation)
        finally:
            with server.API_CONFIG_LOCK:
                server.API_CONFIG.clear()
                server.API_CONFIG.update(original)

    def test_tarot_draw_requires_a_question(self):
        with self.assertRaisesRegex(ValueError, "请先写下"):
            server.save_tarot_draw({"spread": "three", "question": "   "})
        self.assertEqual(server.list_tarot_readings(), [])

    def test_ziwei_fixed_chart_has_complete_structure(self):
        chart = ziwei_engine.calculate_chart(
            lunar_year=2002, lunar_month=5, lunar_day=5,
            hour=11, minute=30, sex="女",
        )
        self.assertEqual(chart["input"]["yearPillar"], "壬午")
        self.assertEqual(chart["core"]["mingPalace"], "子")
        self.assertEqual(chart["core"]["shenPalace"], "子")
        self.assertEqual(chart["core"]["bureau"], "木三局")
        self.assertEqual(chart["core"]["ziweiPalace"], "寅")
        self.assertEqual(chart["core"]["tianfuPalace"], "寅")
        self.assertEqual(len(chart["palaces"]), 12)
        self.assertEqual(set(chart["starLocations"]), set(ziwei_engine.MAIN_STARS + ziwei_engine.ASSISTANT_STARS))
        self.assertEqual(
            [(item["type"], item["star"]) for item in chart["transformations"]],
            [("化禄", "天梁"), ("化权", "紫微"), ("化科", "左辅"), ("化忌", "武曲")],
        )
        self.assertTrue(chart["selfCheck"]["passed"])
        self.assertEqual(len(chart["focusPalaces"]), 6)
        self.assertIsInstance(chart["structures"], list)

        timing = ziwei_engine.timing_layers(chart, 2026)
        self.assertEqual(timing["annualPillar"], "丙午")
        self.assertEqual(timing["nominalAge"], 25)
        self.assertEqual(len(timing["decadeYears"]), 10)
        self.assertEqual([layer["name"] for layer in timing["layers"]], ["本命", "大限", "流年"])
        self.assertTrue(all(len(layer["transformations"]) == 4 for layer in timing["layers"]))

    def test_ziwei_position_matches_upstream_rule(self):
        for bureau in range(2, 7):
            for multiplier in range(1, 13):
                lunar_day = bureau * multiplier
                if lunar_day > 30:
                    break
                self.assertEqual(
                    ziwei_engine.ziwei_position(bureau, lunar_day),
                    ziwei_engine.BRANCHES[multiplier - 1],
                )

    def test_ziwei_profile_payload_is_cached(self):
        payload = {"calendar": "solar", "date": "2002-06-15", "time": "11:30", "sex": "女", "timeMode": "standard"}
        first, cached = server.calculate_ziwei_cached(payload)
        self.assertFalse(cached)
        second, cached = server.calculate_ziwei_cached(payload)
        self.assertTrue(cached)
        self.assertEqual(first, second)
        self.assertEqual(first["input"]["lunarMonth"], 5)
        self.assertEqual(first["input"]["lunarDay"], 5)

    def test_ziwei_rejects_unknown_birth_time(self):
        with self.assertRaisesRegex(ValueError, "需要明确出生时辰"):
            server.calculate_ziwei_cached({"calendar": "solar", "date": "2002-06-15", "time": "", "accuracy": "时间不确定", "sex": "女"})

    def test_ziwei_late_zi_and_lunar_date_normalization(self):
        late_zi = server.normalize_ziwei_input({"calendar": "solar", "date": "2002-06-15", "time": "23:30", "sex": "女", "timeMode": "standard"})
        self.assertTrue(late_zi["source"]["lateZiAdvanced"])
        self.assertEqual((late_zi["lunarMonth"], late_zi["lunarDay"]), (5, 6))
        self.assertEqual(ziwei_engine.hour_branch(late_zi["hour"], late_zi["minute"]), "子")

        lunar = server.normalize_ziwei_input({"calendar": "lunar", "date": "2004-02-30", "time": "12:00", "sex": "男", "timeMode": "standard"})
        self.assertEqual((lunar["lunarYear"], lunar["lunarMonth"], lunar["lunarDay"]), (2004, 2, 30))

    def test_ziwei_frontend_entry_is_enabled(self):
        html = (Path(__file__).resolve().parents[1] / "index.html").read_text()
        theme = (Path(__file__).resolve().parents[1] / "night-theme.css").read_text()
        self.assertIn('id="ziwei-page"', html)
        self.assertIn('data-system-route="ziwei"', html)
        self.assertIn('/api/ziwei/chart', html)
        self.assertIn('/api/ziwei/timing', html)
        self.assertNotIn('data-coming="紫微斗数"', html)
        self.assertNotIn('确定性引擎待接入', html)
        self.assertIn('.ziwei-loading[hidden]', theme)
        self.assertIn('#app-page .intro', theme)
        self.assertIn('grid-template-columns:320px 168px minmax(300px,1fr) auto auto', theme)
        self.assertIn('.site-header>.system-switch{grid-column:2', theme)
        self.assertIn('#app-page.shell{width:100%;min-height:100vh;margin:0;grid-template-rows:auto minmax(0,1fr);overflow:visible;border:0;border-radius:0;box-shadow:none;backdrop-filter:none}', theme)
        self.assertIn('.home-coordinate b{color:rgba(210,173,104,.42);font-size:44px}', theme)
        self.assertIn('.home-launch{margin-top:72px;padding:42px', theme)

    def test_affinity_engine_is_deterministic_and_evidence_based(self):
        first = {"id": "first", "name": "甲", "pillars": "壬午/丙午/甲寅/己巳"}
        second = {"id": "second", "name": "乙", "pillars": "甲申/己巳/丁未/丙午"}
        result = affinity_engine.calculate_affinity(first, second, "亲密关系")
        repeated = affinity_engine.calculate_affinity(first, second, "亲密关系")
        self.assertEqual(result, repeated)
        self.assertEqual(len(result["comparisons"]), 4)
        self.assertEqual(len(result["dimensions"]), 4)
        self.assertGreaterEqual(result["score"], 35)
        self.assertLessEqual(result["score"], 92)
        self.assertIn("不代表现实关系", result["summary"])
        self.assertNotIn("注定", result["summary"])
        cooperation = affinity_engine.calculate_affinity(first, second, "合作关系")
        self.assertEqual(cooperation["score"], result["score"])
        self.assertNotEqual(
            server.local_affinity_interpretation(cooperation)["action"],
            server.local_affinity_interpretation(result)["action"],
        )

    def test_affinity_history_is_cached_reopenable_and_exportable(self):
        now = "2026-09-03T12:00:00"
        profiles = (
            ("1" * 20, "a" * 64, "甲", "女", "壬午/丙午/甲寅/己巳"),
            ("2" * 20, "b" * 64, "乙", "男", "甲申/己巳/丁未/丙午"),
        )
        with server.state_connection() as connection:
            for record_id, fingerprint, name, sex, pillars in profiles:
                connection.execute(
                    """INSERT INTO chart_history(
                        id, fingerprint, name, sex, calendar, birth_date, birth_time,
                        accuracy, place, leap, time_mode, timezone_offset, timezone_label,
                        longitude, latitude, pillars, dayun_direction, dayun_start, created_at, updated_at
                    ) VALUES(?, ?, ?, ?, 'solar', '2000-01-01', '12:00', '时间准确', '', 0,
                             'standard', 8, '北京（UTC+8）', '', '', ?, '顺排', '3岁', ?, ?)""",
                    (record_id, fingerprint, name, sex, pillars, now, now),
                )
        payload = {"profileAId": "1" * 20, "profileBId": "2" * 20, "relationship": "亲密关系"}
        item, cached = server.save_affinity_reading(payload)
        self.assertFalse(cached)
        reopened, cached = server.save_affinity_reading(payload)
        self.assertTrue(cached)
        self.assertEqual(reopened["id"], item["id"])
        with server.API_CONFIG_LOCK:
            original = dict(server.API_CONFIG)
            server.API_CONFIG.clear()
        try:
            interpretation, interpretation_cached = server.analyze_affinity_record(item["id"])
            self.assertFalse(interpretation_cached)
            self.assertEqual(interpretation["source"], "local")
            same, interpretation_cached = server.analyze_affinity_record(item["id"])
            self.assertTrue(interpretation_cached)
            self.assertEqual(same, interpretation)
        finally:
            with server.API_CONFIG_LOCK:
                server.API_CONFIG.clear()
                server.API_CONFIG.update(original)
        self.assertIn("玄衡合缘记录", server.affinity_markdown(server.get_affinity_reading(item["id"])))
        self.assertEqual(len(server.list_affinity_readings()), 1)
        with self.assertRaisesRegex(ValueError, "两份不同"):
            server.save_affinity_reading({"profileAId": "1" * 20, "profileBId": "1" * 20})

    def test_affinity_frontend_entry_is_enabled(self):
        html = (Path(__file__).resolve().parents[1] / "index.html").read_text()
        theme = (Path(__file__).resolve().parents[1] / "night-theme.css").read_text()
        self.assertIn('id="affinity-page"', html)
        self.assertIn('/api/affinity/calculate', html)
        self.assertIn('/api/affinity/history', html)
        self.assertIn('data-route="affinity">合缘</a>', html)
        self.assertNotIn('合缘 <em>待开放</em>', html)
        self.assertIn('.affinity-loading[hidden]', theme)
        self.assertIn('.affinity-main{width:min(1160px', theme)


if __name__ == "__main__":
    unittest.main()
