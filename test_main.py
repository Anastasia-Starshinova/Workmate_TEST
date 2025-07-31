import json
import tempfile
import os
import pytest
from main import parse_file, print_report
import math


@pytest.fixture
def sample_log_file():
    data = [
        {'url': '/api/users', 'response_time': 0.2}, {'url': '/api/users', 'response_time': 0.4},
        {'url': '/api/posts', 'response_time': 1.0}, {'url': '/api/users'},
        {'response_time': 0.5}, 'NOT_JSON'
    ]

    with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as tmp:
        for entry in data:
            if isinstance(entry, dict):
                tmp.write(json.dumps(entry) + '\n')
            else:
                tmp.write(entry + '\n')
        tmp_path = tmp.name

    yield tmp_path
    os.remove(tmp_path)


def test_parse_file(sample_log_file):
    expected = {'/api/users': {'count': 2, 'time': 0.3}, '/api/posts': {'count': 1, 'time': 1.0}}

    result = parse_file(sample_log_file)

    for url in expected:
        assert result[url]['count'] == expected[url]['count']
        assert math.isclose(result[url]['time'], expected[url]['time'], rel_tol=1e-9)


def test_parse_file_empty(tmp_path):
    empty_file = tmp_path / "empty.log"
    empty_file.write_text("", encoding='utf-8')
    result = parse_file(str(empty_file))
    assert result == {}


def test_print_report_output(capsys):
    data = {'/api/test': {'count': 3, 'time': 1.5}, '/api/other': {'count': 1, 'time': 2.0}}
    print_report(data)
    captured = capsys.readouterr()

    assert 'Список всех эндпоинтов:' in captured.out
    assert '/api/test' in captured.out
    assert '/api/other' in captured.out
    assert '3' in captured.out
    assert '1.5' in captured.out
    assert '2' in captured.out


def test_parse_file_file_not_found():
    with pytest.raises(FileNotFoundError):
        parse_file("non_existent_file.log")


def test_parse_file_only_invalid_lines():
    data = ['{}', '{"url": "/api/onlyurl"}', '{"response_time": 0.3}', 'not a json', '']

    with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as tmp:
        for line in data:
            tmp.write(line + '\n')
        tmp_path = tmp.name

    result = parse_file(tmp_path)
    os.remove(tmp_path)

    assert result == {}


def test_parse_file_zero_response_time():
    data = [{'url': '/api/zero', 'response_time': 0.0}]

    with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as tmp:
        for entry in data:
            tmp.write(json.dumps(entry) + '\n')
        tmp_path = tmp.name

    result = parse_file(tmp_path)
    os.remove(tmp_path)

    assert result == {'/api/zero': {'count': 1, 'time': 0.0}}

