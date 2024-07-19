package com.incept5.controllers

import com.incept5.api.response.TestResults
import jakarta.ws.rs.GET
import jakarta.ws.rs.Path
import jakarta.ws.rs.Produces
import jakarta.ws.rs.core.MediaType
import org.junit.platform.engine.discovery.DiscoverySelectors
import org.junit.platform.launcher.core.LauncherDiscoveryRequestBuilder
import org.junit.platform.launcher.core.LauncherFactory
import org.junit.platform.launcher.listeners.SummaryGeneratingListener
import org.junit.platform.launcher.listeners.TestExecutionSummary

@Path("/system-tests")
class SystemTestResource {

    @GET
    @Produces(MediaType.APPLICATION_JSON)
    fun runSystemTests(): TestResults {
        val listener = SummaryGeneratingListener()

        val request = LauncherDiscoveryRequestBuilder.request()
            .selectors(DiscoverySelectors.selectPackage("com.incept5.systemtests"))
            .build()

        val launcher = LauncherFactory.create()
        launcher.execute(request, listener)

        val summary = listener.summary
        return TestResults(
            totalTests = summary.testsFoundCount,
            successfulTests = summary.testsSucceededCount,
            failedTests = summary.testsFailedCount,
            details = generateDetails(summary)
        )
    }

    private fun generateDetails(summary: TestExecutionSummary): List<String> {
        val details = mutableListOf<String>()
        summary.failures.forEach { failure ->
            details.add("Test failed: ${failure.testIdentifier.displayName}")
            details.add("Reason: ${failure.exception}")
        }
        return details
    }
}