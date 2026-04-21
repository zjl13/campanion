package com.zjl13.campanion.core

import java.time.OffsetDateTime
import java.time.format.DateTimeFormatter


private val inputFormatter = DateTimeFormatter.ISO_OFFSET_DATE_TIME
private val outputFormatter = DateTimeFormatter.ofPattern("M月d日 HH:mm")


fun prettyDateTime(raw: String): String {
    return runCatching {
        OffsetDateTime.parse(raw, inputFormatter).format(outputFormatter)
    }.getOrElse { raw }
}


fun ratioLabel(value: Double): String = "${(value * 100).toInt()}%"

