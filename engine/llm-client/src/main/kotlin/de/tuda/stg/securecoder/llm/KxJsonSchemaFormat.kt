package de.tuda.stg.securecoder.llm

import kotlinx.serialization.ExperimentalSerializationApi
import kotlinx.serialization.KSerializer
import kotlinx.serialization.descriptors.PolymorphicKind
import kotlinx.serialization.descriptors.PrimitiveKind
import kotlinx.serialization.descriptors.SerialDescriptor
import kotlinx.serialization.descriptors.SerialKind
import kotlinx.serialization.descriptors.StructureKind
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonObjectBuilder
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.buildJsonArray
import kotlinx.serialization.json.buildJsonObject

@OptIn(ExperimentalSerializationApi::class)
class KxJsonSchemaFormat {
    fun <T> format(serializer: KSerializer<T>): JsonObject =
        schemaForDescriptor(serializer.descriptor, seen = HashSet())

    private fun schemaForDescriptor(desc: SerialDescriptor, seen: MutableSet<String>): JsonObject {
        val key = desc.serialName
        if (!seen.add(key)) {
            throw IllegalStateException("Recursive type detected: $key")
        }
        val jsonType = when (desc.kind) {
            PrimitiveKind.BOOLEAN -> type("boolean")
            PrimitiveKind.BYTE, PrimitiveKind.SHORT, PrimitiveKind.INT, PrimitiveKind.LONG -> type("integer")
            PrimitiveKind.FLOAT, PrimitiveKind.DOUBLE -> type("number")
            PrimitiveKind.CHAR, PrimitiveKind.STRING -> type("string")
            SerialKind.ENUM -> type("string") {
                put("enum", buildJsonArray {
                    for (i in 0 until desc.elementsCount) {
                        add(JsonPrimitive(desc.getElementName(i)))
                    }
                })
            }
            StructureKind.LIST -> type("array") {
                put("items", schemaForDescriptor(desc.getElementDescriptor(0), seen))
            }
            StructureKind.MAP -> type("object") {
                val keyDesc = desc.getElementDescriptor(0)
                if (keyDesc.kind != PrimitiveKind.STRING) {
                    throw IllegalStateException("Map keys must be strings, but was ${keyDesc.serialName}")
                }
                put("additionalProperties", schemaForDescriptor(desc.getElementDescriptor(1), seen))
            }
            StructureKind.CLASS, StructureKind.OBJECT -> type("object") {
                put("properties", buildJsonObject {
                    for (i in 0 until desc.elementsCount) {
                        val name = desc.getElementName(i)
                        val childDesc = desc.getElementDescriptor(i)
                        val childSchema = schemaForDescriptor(childDesc, seen)
                        val propDesc = getDescription(desc.getElementAnnotations(i))
                        put(name, if (propDesc != null) addDescription(childSchema, propDesc) else childSchema)
                    }
                })
                val required = JsonArray(desc.requiredElements().map { name -> JsonPrimitive(name) })
                if (required.isNotEmpty()) put("required", required)
                put("additionalProperties", JsonPrimitive(false))
            }
            PolymorphicKind.SEALED, PolymorphicKind.OPEN, SerialKind.CONTEXTUAL
                -> throw IllegalStateException("Polymorphic types are not supported")
        }
        seen.remove(key)
        if (desc.isNullable) {
            throw IllegalStateException("Nullable types are not supported")
        }
        val selfDesc = getDescription(desc.annotations)
        return if (selfDesc != null) addDescription(jsonType, selfDesc) else jsonType
    }

    private fun type(name: String, builderAction: JsonObjectBuilder.() -> Unit = {}): JsonObject =
        buildJsonObject {
            put("type", JsonPrimitive(name))
            builderAction()
        }

    private fun SerialDescriptor.requiredElements(): List<String> = (0 until elementsCount)
        .filter { !isElementOptional(it) }
        .map { getElementName(it) }

    private fun JsonArray.isNotEmpty(): Boolean = this.size > 0

    private fun getDescription(annotations: List<Annotation>): String? =
        annotations.filterIsInstance<LLMDescription>().firstOrNull()?.text

    private fun addDescription(obj: JsonObject, text: String): JsonObject =
        buildJsonObject {
            obj.forEach { (k, v) -> put(k, v) }
            put("description", JsonPrimitive(text))
        }
}
