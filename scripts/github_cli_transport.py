"""Use installed official gh for authentication and REST; never extract a token."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import threading
import urllib.parse

import enrich_catalog as e


def validate_url(url):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != 'https' or parsed.netloc != 'api.github.com' or parsed.fragment:
        raise ValueError('Only public api.github.com HTTPS endpoints are allowed')
    query = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
    if parsed.path == '/rate_limit' and not query:
        return url
    if parsed.path == '/search/repositories':
        if set(query) - {'q', 'per_page', 'page', 'sort', 'order'} or any(len(v) != 1 for v in query.values()):
            raise ValueError('Unexpected search arguments')
        q = query.get('q', [''])[0]
        if not q or len(q) > 256 or not re.search(r'(?:^| )is:public(?: |$)', q):
            raise ValueError('Search must explicitly target public repositories')
        if not 1 <= int(query.get('per_page', ['10'])[0]) <= 30 or not 1 <= int(query.get('page', ['1'])[0]) <= 3:
            raise ValueError('Search exceeds bounded page budget')
        if any(ord(c) < 32 for c in q) or re.search(r'(token|password|secret):', q, re.I):
            raise ValueError('Unsafe search text')
        return url
    return e.safe_api_url(url)


def parse_response(raw):
    """gh --include returns a status line, headers, a blank line and JSON."""
    match = re.match(rb'HTTP/\S+ (\d{3})[^\r\n]*\r?\n', raw)
    if not match:
        raise RuntimeError('GitHub CLI returned no HTTP response; check authorized CLI access')
    split = re.search(rb'\r?\n\r?\n', raw)
    if not split:
        raise RuntimeError('GitHub CLI response has no header boundary')
    headers = {}
    for line in raw[match.end():split.start()].splitlines():
        key, sep, value = line.partition(b':')
        if sep:
            headers[key.decode('ascii').lower()] = value.decode('utf-8', errors='replace').strip()
    return int(match[1]), headers, raw[split.end():]


class GitHubCLITransport:
    validate_url = staticmethod(validate_url)

    def __init__(self, executable=None):
        self.executable = executable or shutil.which('gh')
        if not self.executable:
            raise RuntimeError('GitHub CLI is required; no anonymous fallback')

    def __call__(self, url, timeout, max_bytes):
        validate_url(url)
        # No --paginate, --cache or --verbose: one explicit API operation per call.
        command = [self.executable, 'api', '--hostname', 'github.com', '--method', 'GET',
                   '--include', '--header', 'Accept: application/vnd.github+json',
                   '--header', 'X-GitHub-Api-Version:' + e.API_VERSION,
                   url.removeprefix(e.API)]
        environment = os.environ.copy()
        environment.pop('GH_DEBUG', None)
        environment.update(GH_PROMPT_DISABLED='1', GH_PAGER='cat', NO_COLOR='1')
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                   stdin=subprocess.DEVNULL, env=environment)
        expired = threading.Event()

        def stop():
            expired.set()
            process.kill()

        timer = threading.Timer(timeout, stop)
        timer.start()
        try:
            raw = process.stdout.read(max_bytes + 32769)
            if len(raw) > max_bytes + 32768:
                process.kill()
                process.wait()
                return 200, {}, b' ' * (max_bytes + 1)
            process.wait()
            if expired.is_set():
                raise TimeoutError('GitHub CLI request timed out')
            return parse_response(raw)
        finally:
            timer.cancel()
            if process.poll() is None:
                process.kill()
                process.wait()
            process.stdout.close()
