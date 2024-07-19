package com.incept5

import io.quarkus.test.junit.QuarkusTest
import io.restassured.RestAssured.given
import org.hamcrest.CoreMatchers.`is`
import org.hamcrest.CoreMatchers.notNullValue
import org.junit.jupiter.api.Test

@QuarkusTest
class SystemTestResourceTest {

    @Test
    fun testRunSystemTestsEndpoint() {
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