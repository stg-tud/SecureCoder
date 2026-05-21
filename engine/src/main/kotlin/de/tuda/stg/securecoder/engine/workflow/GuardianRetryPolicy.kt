package de.tuda.stg.securecoder.engine.workflow

data class GuardianRetryPolicy(
    val softLimit: Int = 7,
    val hardLimit: Int = 14,
    val enableMetaReview: Boolean = true,
) {
    init {
        require(softLimit > 0) { "softLimit must be > 0" }
        require(hardLimit > 0) { "hardLimit must be > 0" }
        require(softLimit <= hardLimit) { "softLimit must be <= hardLimit" }
    }

    fun reachedSoftLimit(attempt: Int): Boolean = attempt >= softLimit
}
