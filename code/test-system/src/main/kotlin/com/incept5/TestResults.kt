package com.incept5

data class TestResults(
    val totalTests: Long,
    val successfulTests: Long,
    val failedTests: Long,
    val details: List<String>
)