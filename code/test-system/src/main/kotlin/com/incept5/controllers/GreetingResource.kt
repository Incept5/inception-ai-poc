package com.incept5.controllers

import jakarta.ws.rs.GET
import jakarta.ws.rs.Path
import jakarta.ws.rs.Produces
import jakarta.ws.rs.core.MediaType

@Path("/hello")
class GreetingResource {

    @GET
    @Produces(MediaType.TEXT_PLAIN)
    fun hello() = "Hello from test-system"

    @GET
    @Path("/system-tests")
    @Produces(MediaType.TEXT_PLAIN)
    fun systemTestsInfo() = "To run system tests, visit: /system-tests"
}