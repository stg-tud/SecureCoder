package de.tuda.stg.securecoder.openaibridge

import de.tuda.stg.securecoder.engine.Engine
import de.tuda.stg.securecoder.engine.file.edit.Changes
import de.tuda.stg.securecoder.engine.workflow.GuardianRetryPolicy
import de.tuda.stg.securecoder.filesystem.InMemoryFileSystem
import io.ktor.http.HttpStatusCode
import kotlinx.coroutines.runBlocking
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith

class AgentServiceTests {
    @Test
    fun success_returns_single_file_content() = runBlocking {
        val service = AgentService(
            StubEngine(
                Engine.EngineResult.Success(
                    Changes(
                        listOf(
                            Changes.SearchReplace(
                                fileName = "app.py",
                                searchedText = Changes.SearchedText(""),
                                replaceText = "print('secure')\n",
                            )
                        )
                    )
                )
            )
        )

        val response = service.generateResponse(listOf(ChatMessage("user", "create one file")), "test-model")

        assertEquals("print('secure')\n", response.choices.single().message.content)
    }

    @Test
    fun validation_failure_throws_api_error() = runBlocking {
        val service = AgentService(
            StubEngine(
                Engine.EngineResult.Failure.ValidationFailure(
                    retryPolicy = GuardianRetryPolicy(),
                    attemptsUsed = 7,
                    reason = "hard_limit_exhausted",
                )
            )
        )

        val ex = assertFailsWith<OpenAiBridgeException> {
            service.generateResponse(listOf(ChatMessage("user", "create one file")), "test-model")
        }

        assertEquals(HttpStatusCode.UnprocessableEntity, ex.status)
        assertEquals("validation_failure", ex.code)
    }

    @Test
    fun generation_failure_throws_api_error() = runBlocking {
        val service = AgentService(StubEngine(Engine.EngineResult.Failure.GenerationFailure))

        val ex = assertFailsWith<OpenAiBridgeException> {
            service.generateResponse(listOf(ChatMessage("user", "create one file")), "test-model")
        }

        assertEquals(HttpStatusCode.BadGateway, ex.status)
        assertEquals("generation_failure", ex.code)
    }

    @Test
    fun multiple_files_throw_api_error() = runBlocking {
        val service = AgentService(
            StubEngine(
                Engine.EngineResult.Success(
                    Changes(
                        listOf(
                            Changes.SearchReplace("a.py", Changes.SearchedText(""), "print('a')\n"),
                            Changes.SearchReplace("b.py", Changes.SearchedText(""), "print('b')\n"),
                        )
                    )
                )
            )
        )

        val ex = assertFailsWith<OpenAiBridgeException> {
            service.generateResponse(listOf(ChatMessage("user", "create one file")), "test-model")
        }

        assertEquals(HttpStatusCode.BadGateway, ex.status)
        assertEquals("multiple_files", ex.code)
    }

    private class StubEngine(
        private val result: Engine.EngineResult,
    ) : Engine {
        override suspend fun run(
            prompt: String,
            filesystem: de.tuda.stg.securecoder.filesystem.FileSystem,
            onEvent: suspend (de.tuda.stg.securecoder.engine.stream.StreamEvent) -> Unit,
            context: Engine.Context?,
        ): Engine.EngineResult = result
    }
}
