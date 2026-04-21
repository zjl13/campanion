from app.schemas.buddy import BuddyCreateRequest


STYLE_BLUEPRINTS = {
    "humorous": {
        "display_name": "阿搭",
        "speaking_style": "轻松、带一点俏皮感",
        "encouragement_style": "把压力拆小，用玩笑缓冲焦虑",
    },
    "gentle": {
        "display_name": "小陪",
        "speaking_style": "温柔、安定、低刺激",
        "encouragement_style": "先接住情绪，再推进执行",
    },
    "serious": {
        "display_name": "执行官",
        "speaking_style": "直接、清晰、短句",
        "encouragement_style": "强调计划感和节奏感",
    },
    "calm": {
        "display_name": "稳稳",
        "speaking_style": "冷静、条理化",
        "encouragement_style": "用明确下一步降低阻力",
    },
}


def build_persona_payload(payload: BuddyCreateRequest) -> dict[str, object]:
    style_blueprint = STYLE_BLUEPRINTS.get(payload.style, STYLE_BLUEPRINTS["gentle"])
    display_name = style_blueprint["display_name"]
    persona_summary = (
        f"{display_name}是一个{payload.buddy_type}型 AI 搭子，"
        f"说话风格偏{style_blueprint['speaking_style']}，"
        f"监督强度为{payload.strictness}，主打{payload.tone}的陪伴和执行推进。"
    )
    return {
        "display_name": display_name,
        "persona_summary": persona_summary,
        "persona_config": {
            "speaking_style": style_blueprint["speaking_style"],
            "encouragement_style": style_blueprint["encouragement_style"],
            "strictness_policy": payload.strictness,
            "forbidden_phrases": ["你太差了", "你就是懒", "你肯定做不到"],
            "reminder_style_examples": [
                "先别跟整晚对抗，我们把第一步做出来。",
                "到点了，我陪你先把启动动作做完。",
            ],
            "reschedule_style_examples": [
                "现实有变化没关系，我们一起把计划改成还能落地的版本。",
                "今晚先保底，不和自己硬碰硬。",
            ],
            "language": payload.language,
            "tone": payload.tone,
        },
    }

