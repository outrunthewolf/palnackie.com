#!/usr/bin/env python3
import sys
import json
import re
from urllib.parse import urlparse

ACCESS_LOG_RE = re.compile(r'"(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS) ([^ ]+) HTTP/[^"]*"')
AIOHTTP_RE = re.compile(r'""(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS) ([^ ]+) HTTP/[^"]*""')


def extract_from_json(line):
    try:
        obj = json.loads(line)
    except (json.JSONDecodeError, ValueError):
        return None

    # GCP LB structured log
    try:
        method = obj["http"]["method"].upper()
        request_url = obj["data"]["httpRequest"]["requestUrl"]
        parsed = urlparse(request_url)
        path = parsed.path
        if parsed.query:
            path += "?" + parsed.query
        return f"{method} {path}"
    except (KeyError, TypeError):
        pass

    return None


def extract_from_line(line):
    # aiohttp double-quoted format first (more specific)
    m = AIOHTTP_RE.search(line)
    if m:
        return f"{m.group(1)} {m.group(2)}"

    # Standard access log / Kafka connect log
    m = ACCESS_LOG_RE.search(line)
    if m:
        return f"{m.group(1)} {m.group(2)}"

    # JSON structured log
    result = extract_from_json(line)
    if result:
        return result

    return None


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "content.txt"
    with open(path) as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            result = extract_from_line(line)
            print(result if result else line)


if __name__ == "__main__":
    main()
