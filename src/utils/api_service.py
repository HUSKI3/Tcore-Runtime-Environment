from flask import Flask, request
import importlib
from types import FunctionType as function
from rich.console import Console
from rich.syntax import Syntax
import traceback
import sys, os

console = Console()

from utils.overload import overload

class Templates:

    def FakeAsgard(
        cog_name: str,
        cog_source: list[function],
        override: function = None
    ):
        """
        ### Single cog instance.
        This template takes one cog to be simulated.
        """

        # Run override if present
        if override is not None:
            override()

        # Construct, this requires the runtime to be installed
        def _internal():
            data = request.json

            syntax = Syntax(str(data), "auto")

            console.print("[bold red]REQUEST:[/bold red]")
            console.print("BODY:",syntax)

            if not (set(("hook","action","function","params")) <= data.keys()):
                print("Not all values loaded in body. Required: hook, action, function, params")
                return "Not all values loaded in body. Required: hook, action, function, params"

            if data['hook'] == cog_name:
                cogs_data = {_.__name__: _ for _ in cog_source}
                if data['action'] in cogs_data:
                    try:
                        resp = cogs_data[data['action']](data['params'])
                    except Exception as e:
                        traceback_str = ''.join(traceback.format_tb(e.__traceback__))
                        return traceback_str
                    console.print("[bold red]RESPONSE:[/bold red]", resp)
                    return resp
                else:
                    return "Unable to locate function"
            else:
                return f"No such cog: {cog_name}"

        return _internal


class Service:
    def __init__(self) -> None:
        self.app = Flask(__name__)

    def generate_route(
        self,
        template: function,
        route_name = "/asgard"
    ) -> function:
        """
        Generate route based on template
        """
        self.app.route(route_name)(template)

    def serve(
        self,
        host = '0.0.0.0',
        port = '8080',
        auto_restart = False
    ):
        """
        Rebuilds routes and starts Flask service
        """

        # Generic index
        self.generate_route(
            lambda: "Mobile runtime active",
            route_name="/"
        )

        self.app.run(host=host, port=port, debug=auto_restart)
