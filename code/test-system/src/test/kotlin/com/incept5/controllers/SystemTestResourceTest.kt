package com.incept5.controllers

import com.incept5.api.response.TestResults
import io.quarkus.test.junit.QuarkusTest
import io.restassured.RestAssured
import io.restassured.RestAssured.given
import io.restassured.filter.log.LogDetail
import io.restassured.filter.log.RequestLoggingFilter
import io.restassured.filter.log.ResponseLoggingFilter
import org.hamcrest.CoreMatchers.notNullValue
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.TestInstance
import org.slf4j.LoggerFactory

@QuarkusTest
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class SystemTestResourceTest {

    companion object {
        private val logger = LoggerFactory.getLogger(SystemTestResourceTest::class.java)
    }

    @BeforeAll
    fun setup() {
        logger.info("Setting up SystemTestResourceTest")
        RestAssured.filters(
            RequestLoggingFilter(LogDetail.ALL),
            ResponseLoggingFilter(LogDetail.ALL)
        )
    }

    @Test
    fun testRunSystemTestsEndpoint() {
        logger.info("Running testRunSystemTestsEndpoint")
        given()
            .`when`().get("/system-tests")
            .then()
                .statusCode(200)
                .contentType("application/json")
                .body("totalTests", notNullValue())
                .body("successfulTests", notNullValue())
                .body("failedTests", notNullValue())
                .body("details", notNullValue())
    }

    @Test
    fun testRunSystemTestsEndpointResults() {
        logger.info("Running testRunSystemTestsEndpointResults")
        val response = given()
            .`when`().get("/system-tests")
            .then()
                .statusCode(200)
                .extract().body().`as`(TestResults::class.java)

        assert(response.totalTests >= 0)
        assert(response.successfulTests >= 0)
        assert(response.failedTests >= 0)
        assert(response.totalTests == response.successfulTests + response.failedTests)
    }
}