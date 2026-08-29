from collections.abc import Iterable
from dataclasses import dataclass

from jinja2 import Template
from mirror.aliases import Row
from mirror.s3.client import S3Repository


@dataclass
class AppState:
    s3_client: S3Repository


def home_page(iterable: Iterable[Row], parent_path: str) -> str:
    return Template("""
    <html>
    <head>
    <title>Index of /</title>
    <style>
    body {
        font-family: monospace;
        font-size: 14px;
        background: #fff;
        color: #000;
        padding: 0 8px;
    }
    h1 {
        font-size: 18px;
        font-weight: normal;
        margin: 8px 0;
    }
    hr {
        border: none;
        border-top: 1px solid #000;
        margin: 4px 0;
    }
    table {
        width: 100%;
        border-collapse: collapse;
    }
    th {
        text-align: left;
        font-weight: normal;
        padding: 0 16px 2px 0;
        border-bottom: 1px solid #000;
    }
    td {
        padding: 1px 16px 1px 0;
        white-space: nowrap;
    }
    td.size {
        text-align: right;
    }
    a {
        color: #00f;
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
    }
    address {
        font-style: normal;
        margin-top: 8px;
        font-size: 14px;
        color: #000;
    }
    </style>
    </head>
    <body>
    <h1>Index of /pub/</h1>
    <hr>
    <table>
    <thead>
    <tr>
        <th>Name</th>
        <th>Last modified</th>
        <th class="size">Size</th>
    </tr>
    </thead>
    <tbody>
    {% if parent_path %}
    <tr><td><a href="{{parent_path}}">../</a></td><td>-</td><td class="size">-</td></tr>
    {% endif %}
    {% for href, name, size, time in iterable %}
    <tr><td><a href="/{{href}}">{{name}}</a></td><td>{{time}}</td><td class="size">{{size}}</td></tr>
    {% endfor %}
    </tbody>
    </table>
    <hr>
    </body>
    </html>
    """, autoescape=True).render(iterable=iterable, parent_path=parent_path)
