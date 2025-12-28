package de.tuda.stg.securecoder.engine.stream

import java.util.UUID

class ProposalId(val value: String) {
    override fun toString(): String = value

    companion object {
        fun newId(): ProposalId = ProposalId(UUID.randomUUID().toString())
    }
}
