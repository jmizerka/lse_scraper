import io
import pytest
import pandas as pd
from core.csv_handler import CSVHandler


def test_read_csv_from_path(tmp_path):
    file_path = tmp_path / "test.csv"
    pd.DataFrame([{"name": "Vodafone", "code": "VOD"}]).to_csv(file_path, index=False)
    result = CSVHandler.read_csv(file_path)
    assert result[0]["name"] == "Vodafone"


def test_read_csv_from_bytes():
    df = pd.DataFrame([{"name": "Vodafone", "code": "VOD"}])
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    result = CSVHandler.read_csv(buf.getvalue())
    assert result[0]["code"] == "VOD"


def test_write_csv_to_file(tmp_path):
    output_path = tmp_path / "out.csv"
    data = [{"name": "Vodafone", "code": "VOD"}]
    CSVHandler.write_csv(data, path=output_path)
    df = pd.read_csv(output_path)
    assert not df.empty
    assert df.iloc[0]["name"] == "Vodafone"


def test_write_csv_append(tmp_path):
    output_path = tmp_path / "append.csv"
    data = [{"name": "Vodafone", "code": "VOD"}]
    CSVHandler.write_csv(data, path=output_path)
    CSVHandler.write_csv(data, path=output_path, append=True)
    df = pd.read_csv(output_path)
    assert len(df) == 2


def test_write_csv_as_bytes():
    data = [{"name": "Vodafone", "code": "VOD"}]
    buf = CSVHandler.write_csv(data, as_bytes=True)
    assert isinstance(buf, io.BytesIO)
    assert b"Vodafone" in buf.getvalue()


def test_read_csv_invalid_type():
    with pytest.raises(TypeError):
        CSVHandler.read_csv(123)


def test_write_csv_missing_path():
    with pytest.raises(ValueError):
        CSVHandler.write_csv([{"a": 1}], as_bytes=False)
