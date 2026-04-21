from pydantic import BaseModel


def strict_json_schema(result_type: type[BaseModel]) -> dict:
    schema = result_type.model_json_schema()
    schema["additionalProperties"] = False
    return schema
