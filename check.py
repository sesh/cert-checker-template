import os
import ssl

import errno
import socket
import ssl

from datetime import datetime, date, timedelta, timezone
from thttp import request


CONNECTION_TIMEOUT = 5.0


class SSLConnectionFailed(Exception):
    pass


class UnknownSSLFailure(Exception):
    pass


class LookupFailed(Exception):
    pass


def get_ssl_expiry(domain):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(CONNECTION_TIMEOUT)

        context = ssl.create_default_context()
        ssl_sock = context.wrap_socket(sock, server_hostname=domain)
        ssl_sock.settimeout(CONNECTION_TIMEOUT)
        ssl_sock.connect((domain, 443))

        cert = ssl_sock.getpeercert()
        end = datetime.fromtimestamp(
            ssl.cert_time_to_seconds(cert["notAfter"]), tz=timezone.utc
        )
        ssl_sock.close()
        return end.date()
    except socket.gaierror:
        raise LookupFailed
    except socket.error as e:
        if e.errno == errno.ECONNREFUSED:
            # connection to port 443 was confused
            raise SSLConnectionFailed
        raise UnknownSSLFailure


if __name__ == "__main__":
    domains = []

    with open("domains.txt") as f:
        for l in f.readlines():
            if l.strip() and not l.strip().startswith("#"):
                domain = l.strip()

                try:
                    domains.append((domain, str(get_ssl_expiry(domain))))
                except Exception as e:
                    domains.append((domain, type(e).__name__))

    # Update README
    with open("README.md", "r") as f:
        readme = f.read().split("## Results")[0].strip()
        readme += "\n\n## Results\n\n"
        readme += "| Expiry    | Domain   |\n"
        readme += "|-----------|----------|\n"

        for domain, expiry in sorted(domains, key=lambda x: x[1]):
            readme += f"| {expiry} | {domain} |\n"

        with open("README.md", "w") as f:
            f.write(readme)

    # Open Github issues
    for domain, expiry in sorted(domains, key=lambda x: x[1]):
        if "-" not in expiry:
            continue

        d = date(*[int(x) for x in expiry.split("-")])
        if d < date.today() + timedelta(days=30):
            token = os.environ.get("GH_TOKEN")
            repo = os.environ.get("GH_REPO")

            if token and repo:
                if d < date.today() + timedelta(days=14):
                    title = f"{domain} expires in less than 14 days ({d})"
                elif d < date.today() + timedelta(days=30):
                    title = f"{domain} expires in less than 30 days ({d})"

                existing_issues = request(
                    f"https://api.github.com/repos/{repo}/issues",
                    params={"state": "open"},
                    headers={"Authorization": f"token {token}"},
                )

                needs_issue = True
                for issue in existing_issues.json:
                    if issue["title"] == title:
                        needs_issue = False
                        break

                if needs_issue:
                    request(
                        f"https://api.github.com/repos/{repo}/issues",
                        headers={"Authorization": f"token {token}"},
                        json={"title": title},
                        method="post",
                    )
