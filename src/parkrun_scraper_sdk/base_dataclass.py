# file: src/parkrun_scraper_sdk/base_dataclass.py

from dataclasses import dataclass, asdict, fields
import stat
from typing import Any, Dict, get_origin, get_args, Optional, Type, Union, List, Sequence
from datetime import datetime
import pyarrow as pa
import polars as pl

@dataclass
class BaseDataclass:
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    # @classmethod
    # def pyarrow_schema(cls: Type):

    #     schema_fields = []
    #     for field in fields(cls):
    #         field_type = cls.get_first_concrete_type(field.type)
    #         is_optional = field.type != field_type  # If they're different, it was Optional
            
    #         # Map Python types to PyArrow types
    #         if field_type is str:
    #             pa_type = pa.string()
    #         elif field_type is int:
    #             pa_type = pa.int64()
    #         elif field_type is float:
    #             pa_type = pa.float64()
    #         elif field_type is bool:
    #             pa_type = pa.bool_()
    #         elif field_type is datetime:
    #             pa_type = pa.timestamp('us')
    #         elif field_type is list:
    #             pa_type = pa.list_(pa.string())  # Assume list of strings by default
    #         elif field_type is dict:
    #             pa_type = pa.map_(pa.string(), pa.string())  # Assume dict of strings by default
    #         elif field_type is Any:
    #             pa_type = pa.null()
    #         else:
    #             raise ValueError(f"Unsupported type for field {field.name}: {field_type}")
            
    #         schema_fields.append(pa.field(field.name, pa_type, nullable=is_optional))
    
    #     return pa.schema(schema_fields)

    # @classmethod
    # def polars_schema(cls: Type) -> dict:
    #     schema = {}
    #     for field in fields(cls):
    #         field_type = cls.get_first_concrete_type(field.type)
            
    #         # Map Python types to Polars types
    #         if field_type is str:
    #             pl_type = pl.Utf8
    #         elif field_type is int:
    #             pl_type = pl.Int64
    #         elif field_type is float:
    #             pl_type = pl.Float64
    #         elif field_type is bool:
    #             pl_type = pl.Boolean
    #         elif field_type is datetime:
    #             pl_type = pl.Datetime
    #         elif field_type is list:
    #             pl_type = pl.List(pl.Utf8)  # Assume list of strings by default
    #         elif field_type is dict:
    #             pl_type = pl.Struct  # Polars doesn't have a direct map type, using Struct
    #         elif field_type is Any:
    #             pl_type = pl.Object
    #         else:
    #             raise ValueError(f"Unsupported type for field {field.name}: {field_type}")
            
    #         schema[field.name] = pl_type
        
    #     return schema
        
    #     return schema

    # @classmethod
    # def get_first_concrete_type(cls, type_hint: Any) -> type:
    #     """
    #     Recursively explore type hints to find the first concrete type.
        
    #     :param type_hint: The type hint to explore
    #     :return: The first concrete type found
    #     """
    #     # If it's a simple type (int, str, etc.), return it directly
    #     if isinstance(type_hint, type):
    #         return type_hint
        
    #     # Get the origin of the type hint (e.g., Union, List, etc.)
    #     origin = get_origin(type_hint)
        
    #     # If it's None (meaning it's a simple type), return the type hint itself
    #     if origin is None:
    #         return type_hint
        
    #     # Handle Union types (including Optional, which is Union[T, None])
    #     if origin is Union:
    #         args = get_args(type_hint)
    #         # Filter out NoneType from Union args
    #         concrete_args = [arg for arg in args if arg is not type(None)]
    #         if concrete_args:
    #             return cls.get_first_concrete_type(concrete_args[0])
        
    #     # Handle List, Dict, and other generic types
    #     elif issubclass(origin, (List, Sequence, Dict)):
    #         args = get_args(type_hint)
    #         if args:
    #             return cls.get_first_concrete_type(args[0])
        
    #     # For any other case, recurse into arguments
    #     args = get_args(type_hint)
    #     if args:
    #         return cls.get_first_concrete_type(args[0])
        
    #     # If we can't determine a concrete type, return Any
    #     return Any
