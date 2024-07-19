package com.incept5.api.response

data class TestResults(
    val totalTests: Long,
    val successfulTests: Long,
    val failedTests: Long,
    val details: List<String>
)