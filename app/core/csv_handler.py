from pathlib import Path
from io import BytesIO
from typing import Optional, Union
import pandas as pd


class CSVHandler:

    @staticmethod
    def read_csv(path_or_bytes: Union[str, bytes]) -> list[dict]:
        if isinstance(path_or_bytes, (str, Path)):
            df = pd.read_csv(path_or_bytes).where(pd.notnull, None)
        elif isinstance(path_or_bytes, (bytes, BytesIO)):
            df = pd.read_csv(BytesIO(path_or_bytes)).where(pd.notnull, None)
        else:
            raise TypeError("Unsupported input type for CSV reading")
        return df.to_dict(orient="records")

    @staticmethod
    def write_csv(
        data: list[dict], path: Optional[Union[str, Path]] = None, append: bool = False, as_bytes: bool = False
    ) -> Optional[BytesIO]:
        df = pd.DataFrame(data)
        if as_bytes:
            buffer = BytesIO()
            df.to_csv(buffer, index=False)
            buffer.seek(0)
            return buffer
        if path is None:
            raise ValueError("path must be provided if as_bytes=False")
        mode = "a" if append else "w"
        header = not append or not Path(path).exists()
        df.to_csv(path, mode=mode, header=header, index=False)
        return None
