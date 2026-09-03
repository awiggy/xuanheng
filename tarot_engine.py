#!/usr/bin/env python3
"""玄衡塔罗确定性抽牌与本地降级解读。

抽牌规则复用 vendor/tarot-skill 的 draw.py；本模块只把结果整理成稳定的
产品数据结构，并在未配置模型时提供不宣判命运的基础解读。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DRAW_SCRIPT = ROOT / "vendor" / "tarot-skill" / "scripts" / "draw.py"


def _load_draw_module() -> Any:
    spec = importlib.util.spec_from_file_location("xuanheng_tarot_draw", DRAW_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("无法载入塔罗抽牌引擎")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


DRAW = _load_draw_module()

MAJOR_INFO = {
    "愚者": ("The Fool", "启程、自由、尝试", "鲁莽、迟疑、准备不足"),
    "魔术师": ("The Magician", "意志、资源、开始行动", "分散、操控、能力未整合"),
    "女祭司": ("The High Priestess", "直觉、静观、隐而未显", "封闭、忽略直觉、信息不明"),
    "女皇": ("The Empress", "滋养、丰盛、创造", "过度照料、停滞、消耗"),
    "皇帝": ("The Emperor", "秩序、边界、承担", "僵化、控制、权责失衡"),
    "教皇": ("The Hierophant", "传统、学习、共同规则", "教条、反叛、价值冲突"),
    "恋人": ("The Lovers", "连接、选择、价值一致", "摇摆、失衡、关系错位"),
    "战车": ("The Chariot", "推进、自律、掌舵", "失控、方向冲突、强行推进"),
    "力量": ("Strength", "温柔的勇气、耐心、驯服冲动", "自我怀疑、耗竭、压抑"),
    "隐士": ("The Hermit", "独处、求索、内在指引", "隔绝、过度退缩、拒绝帮助"),
    "命运之轮": ("Wheel of Fortune", "周期、变化、时机", "抗拒变化、反复、失去节奏"),
    "正义": ("Justice", "衡量、责任、因果", "偏见、逃避责任、失衡"),
    "倒吊人": ("The Hanged Man", "暂停、换位、让渡", "拖延、徒劳牺牲、拒绝转念"),
    "死神": ("Death", "结束、转化、腾出空间", "执着旧局、延迟告别、停滞"),
    "节制": ("Temperance", "调和、节奏、整合", "过量、失序、难以协调"),
    "恶魔": ("The Devil", "欲望、束缚、阴影觉察", "松绑、看见代价、脱离控制"),
    "高塔": ("The Tower", "突变、真相、结构重建", "延迟崩解、害怕改变、暗中松动"),
    "星星": ("The Star", "希望、疗愈、重新相信", "失望、耗散、理想脱离现实"),
    "月亮": ("The Moon", "潜意识、迷雾、感受", "迷雾渐散、压抑恐惧、误判"),
    "太阳": ("The Sun", "清晰、活力、坦诚", "延迟喜悦、过度乐观、能量不足"),
    "审判": ("Judgement", "觉醒、回应、重新评估", "自我否定、回避召唤、迟迟不决"),
    "世界": ("The World", "完成、整合、进入新周期", "未完成、缺少收尾、循环未闭合"),
}

SUIT_INFO = {
    "权杖": {"english": "Wands", "element": "火", "domain": "行动与创造", "glyph": "✦"},
    "圣杯": {"english": "Cups", "element": "水", "domain": "情感与关系", "glyph": "◡"},
    "宝剑": {"english": "Swords", "element": "风", "domain": "思维与冲突", "glyph": "†"},
    "星币": {"english": "Pentacles", "element": "土", "domain": "身体、金钱与技能", "glyph": "✺"},
}

RANK_INFO = {
    "Ace": ("Ace", "种子与起点", "尚未落地或机会被忽略"),
    "二": ("Two", "选择与配对", "犹疑、失衡或两难"),
    "三": ("Three", "初步成果与协作", "合作受阻或成果分散"),
    "四": ("Four", "稳定、休整与边界", "停滞、封闭或基础松动"),
    "五": ("Five", "冲突、缺口与考验", "冲突内化或开始修复"),
    "六": ("Six", "恢复、流动与支持", "进展延迟或旧账未清"),
    "七": ("Seven", "考验、评估与坚持", "策略失焦或信心动摇"),
    "八": ("Eight", "加速、精进与约束", "卡顿、过载或需要松绑"),
    "九": ("Nine", "接近完成与独立", "焦虑、孤立或临门退缩"),
    "十": ("Ten", "完成、责任与过载", "负担松动或收尾困难"),
    "侍从": ("Page", "学习、消息与好奇", "不成熟、消息延迟或浅尝辄止"),
    "骑士": ("Knight", "行动、追求与推进", "冒进、反复或方向偏离"),
    "皇后": ("Queen", "滋养、成熟与内在掌握", "过度付出、情绪失衡或自我忽略"),
    "国王": ("King", "掌控、责任与外在领导", "控制过度、固执或权责错位"),
}


def spread_catalog() -> list[dict[str, Any]]:
    items = []
    for key, (name, raw) in DRAW.SPREADS.items():
        positions = [part.split(",", 1)[0] for part in raw.split("|")]
        items.append({"id": key, "name": name, "count": len(positions), "positions": positions})
    return items


def card_detail(name: str, orientation: str = "正位") -> dict[str, Any]:
    if name in MAJOR_INFO:
        english, upright, reversed_meaning = MAJOR_INFO[name]
        index = DRAW.MAJORS.index(name)
        return {
            "id": f"major-{index:02d}", "name": name, "english": english,
            "arcana": "major", "number": index, "element": DRAW.ELEMENTS[name],
            "glyph": "✧", "upright": upright, "reversed": reversed_meaning,
            "meaning": upright if orientation == "正位" else reversed_meaning,
        }
    suit = next((value for value in SUIT_INFO if name.startswith(value)), "")
    rank = name[len(suit):]
    rank_english, upright, reversed_meaning = RANK_INFO[rank]
    suit_info = SUIT_INFO[suit]
    index = DRAW.MINORS.index(name)
    return {
        "id": f"minor-{index:02d}", "name": name,
        "english": f"{rank_english} of {suit_info['english']}", "arcana": "minor",
        "number": list(RANK_INFO).index(rank) + 1, "suit": suit,
        "element": suit_info["element"], "domain": suit_info["domain"],
        "glyph": suit_info["glyph"],
        "upright": f"{suit_info['domain']}中的{upright}",
        "reversed": f"{suit_info['domain']}中的{reversed_meaning}",
        "meaning": f"{suit_info['domain']}中的{upright if orientation == '正位' else reversed_meaning}",
    }


def full_deck() -> list[dict[str, Any]]:
    return [card_detail(name) for name in DRAW.CARDS]


def draw_reading(spread: str, question: str = "", seed: int | None = None, time_factor: str | None = None) -> dict[str, Any]:
    if spread not in DRAW.SPREADS:
        raise ValueError("未知牌阵")
    if time_factor is not None and time_factor not in DRAW.TIME:
        raise ValueError("时段因子必须是 morning、afternoon 或 night")
    result = DRAW.draw_cards(spread, question, seed, time_factor)
    for item in result["cards"]:
        item.update(card_detail(item["card"], item["orientation"]))
    return result


def local_interpretation(reading: dict[str, Any]) -> dict[str, Any]:
    cards = reading["cards"]
    major_count = sum(bool(card.get("is_major")) for card in cards)
    elements: dict[str, int] = {}
    for card in cards:
        element = str(card.get("element", ""))
        elements[element] = elements.get(element, 0) + 1
    dominant = max(elements, key=elements.get) if elements else ""
    element_copy = {"火": "行动与意志", "水": "情绪与关系", "风": "判断与沟通", "土": "现实资源与落地"}
    card_readings = [
        {
            "position": card["position"], "card": card["name"],
            "orientation": card["orientation"], "keywords": card["meaning"],
            "interpretation": f"在“{card['position']}”位置，{card['name']}{card['orientation']}提醒你留意{card['meaning']}。把它视为观察问题的一面镜子，而不是固定结论。",
        }
        for card in cards
    ]
    names = "、".join(f"{card['name']}{card['orientation']}" for card in cards)
    relation = (
        f"本次 {len(cards)} 张牌中有 {major_count} 张大阿卡纳；"
        + (f"{element_copy.get(dominant, dominant)}的主题相对集中。" if dominant else "需要逐张结合位置理解。")
    )
    return {
        "source": "local",
        "title": "把牌面转成一个可以验证的下一步",
        "summary": f"本次牌面为{names}。先从最贴近现实处境的一张开始核对，再观察其他牌如何补充或制衡它。",
        "cards": card_readings,
        "relationship": relation,
        "action": "今天选一个成本较低、能在一周内获得反馈的动作去验证牌面提示，并记录真实结果；若现实反馈不一致，以现实为准。",
        "energy": "观照而行",
        "reflection": "哪一张牌最像你已经知道、但尚未采取行动的部分？",
        "disclaimer": "塔罗用于自我观察与娱乐参考，不替代医疗、法律、投资或重大人生决定。牌显示的是当下视角，你的选择随时可以改变走向。",
    }
