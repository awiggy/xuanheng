#!/usr/bin/env python3
"""玄衡合缘确定性规则引擎。

这里只计算可复核的干支关系、五行构成和生肖关系；文本结论不得把
传统配对规则包装成现实关系的确定性判决。
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


RULESET_VERSION = "xuanheng-affinity-2026.09.03-v1"
STEM_ELEMENTS = dict(zip("甲乙丙丁戊己庚辛壬癸", "木木火火土土金金水水"))
BRANCH_ELEMENTS = dict(zip("子丑寅卯辰巳午未申酉戌亥", "水土木木土火火土金金土水"))
ZODIAC = dict(zip("子丑寅卯辰巳午未申酉戌亥", "鼠牛虎兔龙蛇马羊猴鸡狗猪"))
HIDDEN_STEMS = {
    "子": "癸", "丑": "己癸辛", "寅": "甲丙戊", "卯": "乙",
    "辰": "戊乙癸", "巳": "丙庚戊", "午": "丁己", "未": "己丁乙",
    "申": "庚壬戊", "酉": "辛", "戌": "戊辛丁", "亥": "壬甲",
}

STEM_COMBINES = {
    frozenset(pair): element
    for pair, element in (("甲己", "土"), ("乙庚", "金"), ("丙辛", "水"), ("丁壬", "木"), ("戊癸", "火"))
}
STEM_CLASHES = {frozenset(pair) for pair in ("甲庚", "乙辛", "丙壬", "丁癸")}
BRANCH_COMBINES = {
    frozenset(pair): element
    for pair, element in (("子丑", "土"), ("寅亥", "木"), ("卯戌", "火"), ("辰酉", "金"), ("巳申", "水"), ("午未", "土"))
}
BRANCH_CLASHES = {frozenset(pair) for pair in ("子午", "丑未", "寅申", "卯酉", "辰戌", "巳亥")}
BRANCH_HARMS = {frozenset(pair) for pair in ("子未", "丑午", "寅巳", "卯辰", "申亥", "酉戌")}
BRANCH_PUNISHMENTS = {frozenset(pair) for pair in ("子卯", "寅巳", "巳申", "寅申", "丑未", "未戌", "丑戌")}
HARMONY_GROUPS = (("申", "子", "辰", "水"), ("寅", "午", "戌", "火"), ("巳", "酉", "丑", "金"), ("亥", "卯", "未", "木"))
GENERATES = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
CONTROLS = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
PILLAR_NAMES = ("年柱", "月柱", "日柱", "时柱")


def _parse_pillars(value: str | list[str]) -> list[str]:
    pillars = value.split("/") if isinstance(value, str) else list(value)
    if len(pillars) != 4:
        raise ValueError("双方档案都需要完整四柱")
    normalized: list[str] = []
    for pillar in pillars:
        text = str(pillar).strip()
        if len(text) != 2 or text[0] not in STEM_ELEMENTS or text[1] not in BRANCH_ELEMENTS:
            raise ValueError("档案四柱格式不完整，请先重新排盘")
        normalized.append(text)
    return normalized


def _stem_relation(first: str, second: str) -> dict[str, Any]:
    pair = frozenset((first, second))
    if pair in STEM_COMBINES:
        return {"type": "combine", "label": f"{first}{second}五合", "detail": f"天干相合，合化取{STEM_COMBINES[pair]}为传统观察线索。", "impact": 8}
    if pair in STEM_CLASHES:
        return {"type": "clash", "label": f"{first}{second}相冲", "detail": "天干取向相对，容易在表达方式或主导节奏上拉扯。", "impact": -7}
    first_element, second_element = STEM_ELEMENTS[first], STEM_ELEMENTS[second]
    if first_element == second_element:
        return {"type": "same", "label": f"同属{first_element}", "detail": "基础气质接近，理解快，也可能在同一议题上较劲。", "impact": 3}
    if GENERATES[first_element] == second_element:
        return {"type": "generate", "label": f"{first_element}生{second_element}", "detail": "前者更容易承担支持与推动的一侧。", "impact": 4}
    if GENERATES[second_element] == first_element:
        return {"type": "generated", "label": f"{second_element}生{first_element}", "detail": "后者更容易承担支持与推动的一侧。", "impact": 4}
    if CONTROLS[first_element] == second_element:
        return {"type": "control", "label": f"{first_element}克{second_element}", "detail": "互动中可能出现较强的推动、要求或边界议题。", "impact": -2}
    return {"type": "controlled", "label": f"{second_element}克{first_element}", "detail": "互动中可能出现较强的推动、要求或边界议题。", "impact": -2}


def _branch_relation(first: str, second: str) -> dict[str, Any]:
    pair = frozenset((first, second))
    if pair in BRANCH_COMBINES:
        return {"type": "combine", "label": f"{first}{second}六合", "detail": f"地支六合，合化取{BRANCH_COMBINES[pair]}为传统观察线索。", "impact": 10}
    if pair in BRANCH_CLASHES:
        return {"type": "clash", "label": f"{first}{second}六冲", "detail": "节奏与反应方式容易对冲；这代表磨合议题，不等于关系结论。", "impact": -9}
    if pair in BRANCH_HARMS:
        return {"type": "harm", "label": f"{first}{second}六害", "detail": "容易出现好意没有被准确接收的隐性摩擦。", "impact": -6}
    if pair in BRANCH_PUNISHMENTS or (first == second and first in "辰午酉亥"):
        return {"type": "punishment", "label": f"{first}{second}相刑", "detail": "相似压力反应可能彼此放大，需要更明确的沟通边界。", "impact": -5}
    for *members, element in HARMONY_GROUPS:
        if first != second and first in members and second in members:
            return {"type": "harmony", "label": f"同属三合{element}局", "detail": "两支处在同一三合结构，传统上视为目标或行动节奏较易呼应。", "impact": 7}
    if first == second:
        return {"type": "same", "label": f"同为{first}", "detail": "反应模式相近，默契与固着可能同时出现。", "impact": 2}
    return {"type": "neutral", "label": "无直接合冲", "detail": "此位置没有强合冲，实际互动更依赖其他柱位与现实经验。", "impact": 0}


def _element_profile(pillars: list[str]) -> dict[str, float]:
    counts = {element: 0.0 for element in "木火土金水"}
    for pillar in pillars:
        stem, branch = pillar
        counts[STEM_ELEMENTS[stem]] += 2.0
        counts[BRANCH_ELEMENTS[branch]] += 2.0
        for hidden in HIDDEN_STEMS[branch]:
            counts[STEM_ELEMENTS[hidden]] += 0.5
    total = sum(counts.values()) or 1.0
    return {element: round(value / total * 100, 1) for element, value in counts.items()}


def _complementarity(first: dict[str, float], second: dict[str, float]) -> dict[str, Any]:
    differences = sum(abs(first[element] - second[element]) for element in first)
    similarity = max(0.0, 100.0 - differences / 2)
    support_a = [element for element in first if first[element] < 12 and second[element] >= 20]
    support_b = [element for element in first if second[element] < 12 and first[element] >= 20]
    score = round(min(92.0, max(42.0, similarity * 0.65 + 24 + 4 * (len(support_a) + len(support_b)))))
    notes = []
    if support_a:
        notes.append(f"乙方的{'、'.join(support_a)}可补充甲方较少的部分")
    if support_b:
        notes.append(f"甲方的{'、'.join(support_b)}可补充乙方较少的部分")
    if not notes:
        notes.append("双方五行构成接近，互补不强，理解相似经验会更容易")
    return {"score": score, "supportA": support_a, "supportB": support_b, "notes": notes}


def _score_label(score: int) -> str:
    if score >= 82:
        return "呼应较多"
    if score >= 68:
        return "可相互补充"
    if score >= 54:
        return "合冲并见"
    return "需要更多磨合"


def calculate_affinity(first: dict[str, Any], second: dict[str, Any], relationship: str = "亲密关系") -> dict[str, Any]:
    """计算两份已经排盘的档案之间的结构关系。"""
    first_pillars = _parse_pillars(first.get("pillars", ""))
    second_pillars = _parse_pillars(second.get("pillars", ""))
    relationship = relationship if relationship in {"亲密关系", "相处磨合", "合作关系"} else "亲密关系"

    comparisons = []
    for index, (left, right) in enumerate(zip(first_pillars, second_pillars)):
        stem_relation = _stem_relation(left[0], right[0])
        branch_relation = _branch_relation(left[1], right[1])
        comparisons.append({
            "pillar": PILLAR_NAMES[index], "first": left, "second": right,
            "stem": stem_relation, "branch": branch_relation,
            "score": max(30, min(94, 62 + stem_relation["impact"] + branch_relation["impact"])),
        })

    first_elements = _element_profile(first_pillars)
    second_elements = _element_profile(second_pillars)
    complement = _complementarity(first_elements, second_elements)
    year_score = comparisons[0]["score"]
    day_score = comparisons[2]["score"]
    interaction_score = round(sum(item["score"] for item in comparisons) / len(comparisons))
    score = round(year_score * 0.2 + day_score * 0.35 + complement["score"] * 0.25 + interaction_score * 0.2)
    score = max(35, min(92, score))

    strengths: list[str] = []
    frictions: list[str] = []
    for item in comparisons:
        for relation in (item["stem"], item["branch"]):
            text = f"{item['pillar']}：{relation['label']}。{relation['detail']}"
            if relation["impact"] >= 4:
                strengths.append(text)
            elif relation["impact"] < 0:
                frictions.append(text)
    strengths.extend(complement["notes"])
    if not frictions:
        frictions.append("四柱同位未见强冲害；仍需以真实沟通、边界与共同经历验证关系质量。")

    year_branch_a, year_branch_b = first_pillars[0][1], second_pillars[0][1]
    zodiac_relation = _branch_relation(year_branch_a, year_branch_b)
    identity_source = {
        "firstId": first.get("id", ""), "secondId": second.get("id", ""),
        "firstPillars": first_pillars, "secondPillars": second_pillars,
        "relationship": relationship, "rulesetVersion": RULESET_VERSION,
    }
    result_id = hashlib.sha256(json.dumps(identity_source, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20]
    return {
        "id": f"a_{result_id}", "rulesetVersion": RULESET_VERSION, "relationship": relationship,
        "score": score, "label": _score_label(score),
        "profiles": [
            {"id": first.get("id", ""), "name": first.get("name") or "未命名资料", "pillars": first_pillars, "elements": first_elements, "zodiac": ZODIAC[year_branch_a]},
            {"id": second.get("id", ""), "name": second.get("name") or "未命名资料", "pillars": second_pillars, "elements": second_elements, "zodiac": ZODIAC[year_branch_b]},
        ],
        "dimensions": [
            {"key": "year", "label": "年柱与生肖", "score": year_score},
            {"key": "day", "label": "日柱互动", "score": day_score},
            {"key": "elements", "label": "五行互补", "score": complement["score"]},
            {"key": "overall", "label": "四柱同位关系", "score": interaction_score},
        ],
        "comparisons": comparisons,
        "zodiac": {"first": ZODIAC[year_branch_a], "second": ZODIAC[year_branch_b], **zodiac_relation},
        "complement": complement,
        "strengths": strengths[:5], "frictions": frictions[:5],
        "summary": f"两份命盘在当前规则下呈现“{_score_label(score)}”的结构。分数用于整理合、冲与互补线索，不代表现实关系的好坏或结局。",
        "action": "把最明显的一项呼应和一项摩擦写成具体生活场景，分别确认彼此的需要、边界与可调整动作。",
        "disclaimer": "合缘仅为传统文化关系观察与娱乐参考，不替代真实相处、沟通或专业关系咨询。",
    }

