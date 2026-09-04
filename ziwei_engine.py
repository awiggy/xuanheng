#!/usr/bin/env python3
"""玄衡紫微斗数确定性排盘引擎。

当前口径来自 FANzR-arch/Numerologist_skills 的三合派规则集。模块只负责
固定排盘，不生成吉凶结论；解释层必须消费这里返回的结构化结果。
"""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any


RULESET_VERSION = "numerologist-skills-ea28c3f-xuanheng-v2"
BRANCHES = ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"]
HOUR_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
STEMS = list("甲乙丙丁戊己庚辛壬癸")
PALACE_NAMES = ["命宫", "兄弟宫", "夫妻宫", "子女宫", "财帛宫", "疾厄宫", "迁移宫", "交友宫", "官禄宫", "田宅宫", "福德宫", "父母宫"]
MAIN_STARS = ["紫微", "天机", "太阳", "武曲", "天同", "廉贞", "天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军"]
ASSISTANT_STARS = ["文昌", "文曲", "左辅", "右弼", "天魁", "天钺", "禄存", "擎羊", "陀罗", "火星", "铃星", "地空", "地劫", "天马"]
SECONDARY_STARS = ["天刑", "天姚", "红鸾", "天喜", "孤辰", "寡宿", "天哭", "天虚"]

PALACE_RELATIONS = {
    "命宫": ("迁移宫", "财帛宫", "官禄宫"),
    "兄弟宫": ("交友宫", "疾厄宫", "田宅宫"),
    "夫妻宫": ("官禄宫", "迁移宫", "福德宫"),
    "子女宫": ("田宅宫", "交友宫", "父母宫"),
    "财帛宫": ("福德宫", "命宫", "官禄宫"),
    "疾厄宫": ("父母宫", "兄弟宫", "田宅宫"),
    "迁移宫": ("命宫", "夫妻宫", "福德宫"),
    "交友宫": ("兄弟宫", "子女宫", "父母宫"),
    "官禄宫": ("夫妻宫", "命宫", "财帛宫"),
    "田宅宫": ("子女宫", "兄弟宫", "疾厄宫"),
    "福德宫": ("财帛宫", "夫妻宫", "迁移宫"),
    "父母宫": ("疾厄宫", "子女宫", "交友宫"),
}

SIHUA = {
    "甲": ("廉贞", "破军", "武曲", "太阳"), "乙": ("天机", "天梁", "紫微", "太阴"),
    "丙": ("天同", "天机", "文昌", "廉贞"), "丁": ("太阴", "天同", "天机", "巨门"),
    "戊": ("贪狼", "太阴", "右弼", "天机"), "己": ("武曲", "贪狼", "天梁", "文曲"),
    "庚": ("太阳", "武曲", "太阴", "天同"), "辛": ("巨门", "太阳", "文曲", "文昌"),
    "壬": ("天梁", "紫微", "左辅", "武曲"), "癸": ("破军", "巨门", "太阴", "贪狼"),
}

BRIGHTNESS = {
    "紫微": "旺 落陷 庙 平 得地 得地 庙 落陷 庙 平 得地 得地".split(),
    "天机": "庙 得地 庙 旺 平 落陷 庙 得地 庙 旺 平 落陷".split(),
    "太阳": "落陷 不得地 旺 庙 旺 庙 庙 得地 得地 落陷 落陷 落陷".split(),
    "武曲": "旺 庙 得地 利 庙 平 旺 庙 得地 利 庙 平".split(),
    "天同": "旺 不得地 落陷 平 庙 落陷 落陷 不得地 落陷 平 庙 落陷".split(),
    "廉贞": "庙 平 落陷 落陷 得地 旺 庙 平 落陷 落陷 得地 旺".split(),
    "天府": "旺 得地 庙 得地 庙 旺 庙 得地 庙 得地 庙 旺".split(),
    "太阴": "庙 庙 得地 落陷 落陷 落陷 落陷 不得地 得地 旺 庙 庙".split(),
    "贪狼": "旺 庙 平 庙 落陷 旺 旺 庙 平 庙 落陷 旺".split(),
    "巨门": "旺 不得地 庙 庙 落陷 庙 旺 不得地 庙 庙 落陷 庙".split(),
    "天相": "庙 落陷 得地 庙 旺 利 庙 落陷 得地 庙 旺 利".split(),
    "天梁": "庙 旺 落陷 庙 庙 旺 庙 旺 落陷 庙 庙 旺".split(),
    "七杀": "旺 庙 庙 旺 平 庙 旺 庙 庙 旺 平 庙".split(),
    "破军": "旺 庙 落陷 平 平 旺 旺 庙 落陷 平 平 旺".split(),
}


def _branch(index: int) -> str:
    return BRANCHES[index % 12]


def hour_branch(hour: int, minute: int = 0) -> str:
    if not 0 <= hour <= 23 or not 0 <= minute <= 59:
        raise ValueError("出生时间不存在")
    return HOUR_BRANCHES[((hour + 1) // 2) % 12]


def lunar_year_pillar(year: int) -> tuple[str, str]:
    index = (year - 1984) % 60
    return STEMS[index % 10], list("子丑寅卯辰巳午未申酉戌亥")[index % 12]


def ziwei_position(bureau_number: int, lunar_day: int) -> str:
    if bureau_number not in {2, 3, 4, 5, 6}:
        raise ValueError("五行局数必须为 2 至 6")
    if not 1 <= lunar_day <= 30:
        raise ValueError("农历日必须为 1 至 30")
    quotient = math.ceil(lunar_day / bureau_number)
    remainder = quotient * bureau_number - lunar_day
    base = quotient - 1
    if remainder == 0:
        return _branch(base)
    return _branch(base - remainder if remainder % 2 else base + remainder)


def _palace_stems(year_stem: str) -> dict[str, str]:
    yin_starts = {"甲": "丙", "己": "丙", "乙": "戊", "庚": "戊", "丙": "庚", "辛": "庚", "丁": "壬", "壬": "壬", "戊": "甲", "癸": "甲"}
    start = STEMS.index(yin_starts[year_stem])
    return {branch: STEMS[(start + index) % 10] for index, branch in enumerate(BRANCHES)}


def _bureau(stem: str, branch: str) -> tuple[str, int]:
    stem_number = {"甲": 1, "乙": 1, "丙": 2, "丁": 2, "戊": 3, "己": 3, "庚": 4, "辛": 4, "壬": 5, "癸": 5}[stem]
    branch_number = {"子": 1, "午": 1, "丑": 1, "未": 1, "寅": 2, "申": 2, "卯": 2, "酉": 2, "辰": 3, "戌": 3, "巳": 3, "亥": 3}[branch]
    residue = (stem_number + branch_number - 1) % 5 + 1
    return {1: ("木三局", 3), 2: ("金四局", 4), 3: ("水二局", 2), 4: ("火六局", 6), 5: ("土五局", 5)}[residue]


def _main_star_positions(ziwei_branch: str) -> dict[str, str]:
    ziwei_index = BRANCHES.index(ziwei_branch)
    positions = {
        "紫微": _branch(ziwei_index), "天机": _branch(ziwei_index - 1),
        "太阳": _branch(ziwei_index - 3), "武曲": _branch(ziwei_index - 4),
        "天同": _branch(ziwei_index - 5), "廉贞": _branch(ziwei_index - 8),
    }
    tianfu_by_ziwei = {"寅": "寅", "卯": "丑", "辰": "子", "巳": "亥", "午": "戌", "未": "酉", "申": "申", "酉": "未", "戌": "午", "亥": "巳", "子": "辰", "丑": "卯"}
    tianfu_index = BRANCHES.index(tianfu_by_ziwei[ziwei_branch])
    for star, offset in (("天府", 0), ("太阴", 1), ("贪狼", 2), ("巨门", 3), ("天相", 4), ("天梁", 5), ("七杀", 6), ("破军", 10)):
        positions[star] = _branch(tianfu_index + offset)
    return positions


def _assistant_star_positions(lunar_month: int, time_branch: str, year_stem: str, year_branch: str) -> dict[str, str]:
    hour_index = HOUR_BRANCHES.index(time_branch)
    positions = {
        "文昌": ["戌", "酉", "申", "未", "午", "巳", "辰", "卯", "寅", "丑", "子", "亥"][hour_index],
        "文曲": ["辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑", "寅", "卯"][hour_index],
        "左辅": _branch(BRANCHES.index("辰") + lunar_month - 1),
        "右弼": _branch(BRANCHES.index("戌") - (lunar_month - 1)),
    }
    kui = {"甲": "丑", "乙": "子", "丙": "亥", "丁": "酉", "戊": "丑", "己": "子", "庚": "丑", "辛": "午", "壬": "卯", "癸": "卯"}
    yue = {"甲": "未", "乙": "申", "丙": "酉", "丁": "未", "戊": "未", "己": "申", "庚": "未", "辛": "寅", "壬": "巳", "癸": "巳"}
    lucun = {"甲": "寅", "乙": "卯", "丙": "巳", "戊": "巳", "丁": "午", "己": "午", "庚": "申", "辛": "酉", "壬": "亥", "癸": "子"}
    positions.update({"天魁": kui[year_stem], "天钺": yue[year_stem], "禄存": lucun[year_stem]})
    lu_index = BRANCHES.index(positions["禄存"])
    positions.update({"擎羊": _branch(lu_index + 1), "陀罗": _branch(lu_index - 1)})

    group = next(group for group in (("寅午戌"), ("申子辰"), ("巳酉丑"), ("亥卯未")) if year_branch in group)
    fire_start = {"寅午戌": "丑", "申子辰": "寅", "巳酉丑": "卯", "亥卯未": "酉"}[group]
    bell_start = {"寅午戌": "卯", "申子辰": "戌", "巳酉丑": "戌", "亥卯未": "戌"}[group]
    positions["火星"] = _branch(BRANCHES.index(fire_start) + hour_index)
    positions["铃星"] = _branch(BRANCHES.index(bell_start) + hour_index)
    positions["地空"] = ["亥", "戌", "酉", "申", "未", "午", "巳", "辰", "卯", "寅", "丑", "子"][hour_index]
    positions["地劫"] = ["亥", "子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌"][hour_index]
    positions["天马"] = {"寅午戌": "申", "申子辰": "寅", "巳酉丑": "亥", "亥卯未": "巳"}[group]
    return positions


def _secondary_star_positions(lunar_month: int, year_branch: str) -> dict[str, str]:
    """安常用杂曜。

    这里只收录上游解读规范明确会使用的八颗星，并把定位结果作为
    可核验数据返回；其余杂曜后续可按流派作为独立规则集扩充。
    """
    month_offset = lunar_month - 1
    year_index = list("子丑寅卯辰巳午未申酉戌亥").index(year_branch)
    solitude_group = next(
        group for group in ("亥子丑", "寅卯辰", "巳午未", "申酉戌") if year_branch in group
    )
    lonely = {"亥子丑": "寅", "寅卯辰": "巳", "巳午未": "申", "申酉戌": "亥"}[solitude_group]
    widow = {"亥子丑": "戌", "寅卯辰": "丑", "巳午未": "辰", "申酉戌": "未"}[solitude_group]
    return {
        "天刑": _branch(BRANCHES.index("酉") + month_offset),
        "天姚": _branch(BRANCHES.index("丑") + month_offset),
        "红鸾": _branch(BRANCHES.index("卯") - year_index),
        "天喜": _branch(BRANCHES.index("酉") - year_index),
        "孤辰": lonely,
        "寡宿": widow,
        "天哭": _branch(BRANCHES.index("午") - year_index),
        "天虚": _branch(BRANCHES.index("午") + year_index),
    }


def calculate_chart(*, lunar_year: int, lunar_month: int, lunar_day: int, hour: int, minute: int, sex: str, is_leap: bool = False, source: dict[str, Any] | None = None) -> dict[str, Any]:
    if not 1 <= lunar_month <= 12 or not 1 <= lunar_day <= 30:
        raise ValueError("农历月日超出紫微排盘范围")
    if sex not in {"男", "女"}:
        raise ValueError("性别必须为男或女")
    time_branch = hour_branch(hour, minute)
    year_stem, year_branch = lunar_year_pillar(lunar_year)
    month_base = lunar_month - 1
    time_index = HOUR_BRANCHES.index(time_branch)
    ming_index = (month_base - time_index) % 12
    shen_index = (month_base + time_index) % 12
    ming_branch, shen_branch = _branch(ming_index), _branch(shen_index)
    palace_stems = _palace_stems(year_stem)
    bureau_name, bureau_number = _bureau(palace_stems[ming_branch], ming_branch)
    main_positions = _main_star_positions(ziwei_position(bureau_number, lunar_day))
    assistant_positions = _assistant_star_positions(lunar_month, time_branch, year_stem, year_branch)
    secondary_positions = _secondary_star_positions(lunar_month, year_branch)
    star_positions = {**main_positions, **assistant_positions, **secondary_positions}

    palace_name_by_branch = {_branch(ming_index - offset): name for offset, name in enumerate(PALACE_NAMES)}
    palaces: list[dict[str, Any]] = []
    for branch_index, branch in enumerate(BRANCHES):
        name = palace_name_by_branch[branch]
        main = [{"name": star, "brightness": BRIGHTNESS[star][branch_index]} for star in MAIN_STARS if main_positions[star] == branch]
        assistants = [star for star in ASSISTANT_STARS if assistant_positions[star] == branch]
        secondary = [star for star in SECONDARY_STARS if secondary_positions[star] == branch]
        opposite, triad_one, triad_two = PALACE_RELATIONS[name]
        palaces.append({
            "name": name, "stem": palace_stems[branch], "branch": branch,
            "isMing": branch == ming_branch, "isShen": branch == shen_branch,
            "mainStars": main, "assistantStars": assistants, "secondaryStars": secondary,
            "transformations": [], "flyingTransformations": [],
            "relations": {"opposite": opposite, "triads": [triad_one, triad_two]},
        })
    palace_by_branch = {palace["branch"]: palace for palace in palaces}

    transformations = []
    for kind, star in zip(("化禄", "化权", "化科", "化忌"), SIHUA[year_stem]):
        branch = star_positions[star]
        item = {"type": kind, "star": star, "branch": branch, "palace": palace_by_branch[branch]["name"]}
        transformations.append(item)
        palace_by_branch[branch]["transformations"].append({"type": kind, "star": star})

    palace_flying_transformations = []
    for origin in palaces:
        flying = _transformation_layer_from_positions(star_positions, palace_by_branch, origin["stem"], origin["name"])
        origin["flyingTransformations"] = flying
        palace_flying_transformations.append({
            "originPalace": origin["name"], "originStem": origin["stem"],
            "originBranch": origin["branch"], "transformations": flying,
        })

    is_yang_year = year_stem in "甲丙戊庚壬"
    forward = (sex == "男" and is_yang_year) or (sex == "女" and not is_yang_year)
    decades = []
    for index in range(12):
        branch = _branch(ming_index + index if forward else ming_index - index)
        start_age = bureau_number + index * 10
        decades.append({"index": index + 1, "palace": palace_by_branch[branch]["name"], "stem": palace_stems[branch], "branch": branch, "startAge": start_age, "endAge": start_age + 9})

    destiny_master = {"子": "贪狼", "丑": "巨门", "寅": "禄存", "卯": "文曲", "辰": "廉贞", "巳": "武曲", "午": "破军", "未": "武曲", "申": "廉贞", "酉": "文曲", "戌": "禄存", "亥": "巨门"}[ming_branch]
    body_master = {"子": "火星", "丑": "天相", "寅": "天梁", "卯": "天同", "辰": "文昌", "巳": "天机", "午": "火星", "未": "天相", "申": "天梁", "酉": "天同", "戌": "文昌", "亥": "天机"}[year_branch]
    checks = {
        "twelvePalaces": len(palaces) == 12 and len({p["name"] for p in palaces}) == 12,
        "fourteenMainStars": len(main_positions) == 14 and set(main_positions) == set(MAIN_STARS),
        "assistantStars": len(assistant_positions) == len(ASSISTANT_STARS),
        "secondaryStars": len(secondary_positions) == len(SECONDARY_STARS),
        "fourTransformations": len(transformations) == 4 and all(item["star"] in star_positions for item in transformations),
        "palaceFlyingTransformations": len(palace_flying_transformations) == 12 and all(len(item["transformations"]) == 4 for item in palace_flying_transformations),
        "decadesContinuous": all(item["endAge"] + 1 == decades[index + 1]["startAge"] for index, item in enumerate(decades[:-1])),
    }
    if not all(checks.values()):
        raise RuntimeError("紫微排盘自检失败")

    input_data = {"lunarYear": lunar_year, "lunarMonth": lunar_month, "lunarDay": lunar_day, "leap": bool(is_leap), "hour": hour, "minute": minute, "timeBranch": time_branch, "sex": sex, "yearPillar": year_stem + year_branch}
    chart_key = hashlib.sha256(json.dumps({"ruleset": RULESET_VERSION, **input_data}, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    warnings = []
    if is_leap:
        warnings.append("当前闰月按原月序安命身宫；如需沿用其他软件的闰月口径，应先切换规则后再校盘。")
    result = {
        "id": chart_key[:20], "rulesetVersion": RULESET_VERSION, "school": "三合派常用安星诀",
        "input": input_data, "source": source or {},
        "rules": {"lateZiDayChange": True, "leapMonthPolicy": "same_month_number", "ageSystem": "虚岁", "decadeDirection": "顺行" if forward else "逆行"},
        "core": {"mingPalace": ming_branch, "shenPalace": shen_branch, "bureau": bureau_name, "bureauNumber": bureau_number, "destinyMaster": destiny_master, "bodyMaster": body_master, "ziweiPalace": main_positions["紫微"], "tianfuPalace": main_positions["天府"]},
        "palaces": palaces, "starLocations": star_positions, "transformations": transformations,
        "palaceFlyingTransformations": palace_flying_transformations,
        "decades": decades, "selfCheck": {"passed": True, "checks": checks}, "warnings": warnings,
        "disclaimer": "紫微斗数属于传统文化参考；排盘结果受子时换日、闰月归属与流派口径影响，不替代现实专业意见。",
    }
    result["structures"] = detect_structures(result)
    result["focusPalaces"] = focus_palaces(result)
    return result


def _palace_for_star(chart: dict[str, Any], star: str) -> dict[str, Any]:
    branch = chart["starLocations"][star]
    return next(palace for palace in chart["palaces"] if palace["branch"] == branch)


def _transformation_layer_from_positions(
    star_positions: dict[str, str], palace_by_branch: dict[str, dict[str, Any]], stem: str, layer: str
) -> list[dict[str, Any]]:
    items = []
    for kind, star in zip(("化禄", "化权", "化科", "化忌"), SIHUA[stem]):
        branch = star_positions[star]
        palace = palace_by_branch[branch]
        items.append({"layer": layer, "type": kind, "star": star, "palace": palace["name"], "branch": branch})
    return items


def _transformation_layer(chart: dict[str, Any], stem: str, layer: str) -> list[dict[str, Any]]:
    by_branch = {palace["branch"]: palace for palace in chart["palaces"]}
    return _transformation_layer_from_positions(chart["starLocations"], by_branch, stem, layer)


def focus_palaces(chart: dict[str, Any]) -> list[dict[str, Any]]:
    """为解读层提供六个核心宫及其三方四正证据，不生成结论。"""
    by_name = {palace["name"]: palace for palace in chart["palaces"]}
    result = []
    for name in ("命宫", "官禄宫", "财帛宫", "夫妻宫", "迁移宫", "福德宫"):
        palace = by_name[name]
        related_names = [name, palace["relations"]["opposite"], *palace["relations"]["triads"]]
        result.append({
            "name": name, "stem": palace["stem"], "branch": palace["branch"],
            "mainStars": palace["mainStars"], "assistantStars": palace["assistantStars"],
            "secondaryStars": palace.get("secondaryStars", []),
            "transformations": palace["transformations"], "relatedPalaces": related_names,
            "relatedMainStars": [
                {"palace": related, "stars": [item["name"] for item in by_name[related]["mainStars"]]}
                for related in related_names
            ],
        })
    return result


def detect_structures(chart: dict[str, Any]) -> list[dict[str, Any]]:
    """依据 patterns.md 检测可核验结构；仅给名称和证据，不评价成败。"""
    by_name = {palace["name"]: palace for palace in chart["palaces"]}
    ming = by_name["命宫"]
    ming_stars = {item["name"] for item in ming["mainStars"]}
    related_names = ["命宫", ming["relations"]["opposite"], *ming["relations"]["triads"]]
    related_main = {
        item["name"] for name in related_names for item in by_name[name]["mainStars"]
    }
    related_all = related_main | {
        star for name in related_names for star in by_name[name]["assistantStars"]
    }
    related_transformations = {
        item["type"] for name in related_names for item in by_name[name]["transformations"]
    }
    structures: list[dict[str, Any]] = []

    def add(name: str, evidence: list[str]) -> None:
        structures.append({"name": name, "evidence": evidence, "scope": "命宫三方四正"})

    pair_patterns = {
        "紫府同宫": {"紫微", "天府"}, "紫杀同宫": {"紫微", "七杀"},
        "武府同宫": {"武曲", "天府"}, "廉贞七杀": {"廉贞", "七杀"},
    }
    for name, stars in pair_patterns.items():
        if stars <= ming_stars:
            add(name, [f"命宫同见{'、'.join(sorted(stars))}"])
    if not ming_stars:
        add("命无正曜", [f"命宫在{ming['branch']}，无十四主星", f"对宫为{ming['relations']['opposite']}"])
    if {"七杀", "破军", "贪狼"} <= related_main:
        add("杀破狼", ["七杀、破军、贪狼分布于命宫三方四正"])
    if {"天机", "太阴", "天同", "天梁"} <= related_main:
        add("机月同梁", ["天机、太阴、天同、天梁分布于命宫三方四正"])
    if {"化禄", "化权", "化科"} <= related_transformations:
        add("三奇加会", ["生年化禄、化权、化科同入命宫三方四正"])
    natal_lu_star = SIHUA[chart["input"]["yearPillar"][0]][0]
    if "禄存" in related_all and natal_lu_star in related_main:
        add("双禄朝垣", [f"禄存与{natal_lu_star}化禄同入命宫三方四正"])
    for catalyst in ("火星", "铃星"):
        if chart["starLocations"]["贪狼"] == chart["starLocations"][catalyst]:
            add("火贪格" if catalyst == "火星" else "铃贪格", [f"贪狼与{catalyst}同宫"])
    return structures


def timing_layers(chart: dict[str, Any], target_year: int) -> dict[str, Any]:
    """叠加某年的大限与流年四化，供时间轴和 LLM 解读使用。"""
    if not 1800 <= int(target_year) <= 2200:
        raise ValueError("流年年份超出支持范围")
    target_year = int(target_year)
    birth_year = int(chart["input"]["lunarYear"])
    nominal_age = target_year - birth_year + 1
    current_decade = next(
        (item for item in chart["decades"] if item["startAge"] <= nominal_age <= item["endAge"]),
        None,
    )
    annual_stem, annual_branch = lunar_year_pillar(target_year)
    annual_palace = next(palace for palace in chart["palaces"] if palace["branch"] == annual_branch)
    layers = [{"name": "本命", "stem": chart["input"]["yearPillar"][0], "transformations": chart["transformations"]}]
    if current_decade:
        layers.append({
            "name": "大限", "stem": current_decade["stem"],
            "transformations": _transformation_layer(chart, current_decade["stem"], "大限"),
        })
    layers.append({"name": "流年", "stem": annual_stem, "transformations": _transformation_layer(chart, annual_stem, "流年")})
    decade_years = []
    if current_decade:
        first_year = birth_year + current_decade["startAge"] - 1
        for year in range(first_year, first_year + 10):
            stem, branch = lunar_year_pillar(year)
            decade_years.append({"year": year, "age": year - birth_year + 1, "stem": stem, "branch": branch, "pillar": stem + branch})
    interactions = _timing_interactions(layers, annual_palace["name"])
    return {
        "targetYear": target_year, "nominalAge": nominal_age,
        "annualPillar": annual_stem + annual_branch,
        "annualMingPalace": {"name": annual_palace["name"], "branch": annual_branch},
        "currentDecade": current_decade, "decadeYears": decade_years, "layers": layers,
        "interactions": interactions,
        "rule": "流年地支所在本命宫位作为流年命宫；大限以所在宫干、流年以流年天干飞四化。",
    }


def _timing_interactions(layers: list[dict[str, Any]], annual_palace: str) -> list[dict[str, Any]]:
    """从三层四化中抽取可复核的叠加关系，不直接下吉凶结论。"""
    by_palace: dict[str, list[dict[str, Any]]] = {}
    for layer in layers:
        for item in layer.get("transformations", []):
            enriched = {**item, "layer": layer["name"]}
            by_palace.setdefault(item["palace"], []).append(enriched)
    result: list[dict[str, Any]] = []
    for palace, items in by_palace.items():
        types = [item["type"] for item in items]
        layers_here = sorted({item["layer"] for item in items})
        evidence = [f"{item['layer']}·{item['star']}{item['type']}" for item in items]
        if len(layers_here) >= 2:
            result.append({"type": "层级汇聚", "palace": palace, "layers": layers_here, "evidence": evidence})
        if types.count("化禄") >= 2:
            result.append({"type": "双禄叠见", "palace": palace, "layers": layers_here, "evidence": evidence})
        if types.count("化忌") >= 2:
            result.append({"type": "双忌叠见", "palace": palace, "layers": layers_here, "evidence": evidence})
        if "化禄" in types and "化忌" in types:
            result.append({"type": "禄忌同宫", "palace": palace, "layers": layers_here, "evidence": evidence})
        if palace == annual_palace:
            result.append({"type": "流年命宫触发", "palace": palace, "layers": layers_here, "evidence": evidence})
    return result
