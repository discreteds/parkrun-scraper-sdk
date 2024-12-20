from cmath import polar
import os
from abc import ABC, abstractmethod
from tkinter import E
from typing import List, Dict, Any, Union, Optional, Sequence
import typing as t
import pyarrow as pa
import pyarrow.parquet as pq
from upath import UPath
import polars

from .base_dataclass import BaseDataclass


class BaseParquetHandler(ABC):

    domain_folder: str
    file_name_template: str
    partition_keys: List[str]

    base_path: UPath


    # @property
    # @abstractmethod
    # def domain_folder(self) -> str:
    #     pass

    # @property
    # @abstractmethod
    # def file_name_template(self) -> str:
    #     pass

    # @property
    # @abstractmethod
    # def partition_keys(self) -> List[str]:
    #     pass

    def get_file_path(self,
                       **kwargs) -> UPath:
        
        #add the partition keys to the file path. Preserve order!
        ordered_partitions = []
        for key in self.partition_keys:
            if key in kwargs:
                ordered_partitions.append(f"{key}={kwargs[key]}")        

        partition_path = '/'.join( ordered_partitions )       

        file_name = self.file_name_template.format(**kwargs)
        file_path =  os.path.join(self.base_path, self.domain_folder, partition_path, file_name)

        return UPath(file_path)


    def read_parquet(self, 
                     **kwargs) -> Optional[polars.LazyFrame]:

        file_path: UPath = self.get_file_path(**kwargs)

        # if not file_path.exists():
        #     print(f"File not found: {file_path}")
        #     return None

        try:
            return polars.scan_parquet(file_path)
        
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return None
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None


    def get_processed_ids(self, 
                          id_column: str,
                            **kwargs) -> List[str]:

        table: polars.LazyFrame|None = self.read_parquet(**kwargs)#.select(polars.col(id_column))

        if table is not None:

            try:
                #Just get unique values of the id column
                table_dicts =  table.select(id_column).unique().collect().to_dict()
                col = table_dicts[id_column]
                return [str(item) for item in col]
            except Exception as e:
                print(f"Error getting processed IDs: {e}")
                return []
        return []


    def file_exists(self, **kwargs) -> bool:

        file_path: UPath = self.get_file_path(**kwargs)
        return file_path.exists()
    

    def write_parquet(self, 
                      data: Sequence[BaseDataclass], 
                      **kwargs):

        items = [ item.to_dict() for item in data]
        table = pa.Table.from_pylist(items)

        output_path = self.get_file_path(**kwargs)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pq.write_table(table, output_path)
        
        print(f"Data written to {output_path}")
