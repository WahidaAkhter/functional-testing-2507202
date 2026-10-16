import os
import subprocess
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import target

app = FastAPI(
    title="Target Functional Testing & Live Suite",
    description="Interactive web frontend and API for target.py with live CI/CD verification",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_current_commit_sha() -> str:
    """Resolve the deployed commit SHA from environment, file, or git."""
    for env_var in (
        "COMMIT_SHA",
        "RENDER_GIT_COMMIT",
        "RAILWAY_GIT_COMMIT_SHA",
        "VERCEL_GIT_COMMIT_SHA",
        "GITHUB_SHA",
    ):
        val = os.environ.get(env_var)
        if val and val.strip():
            return val.strip()

    sha_file = os.path.join(os.path.dirname(__file__), ".commit_sha")
    if os.path.exists(sha_file):
        try:
            with open(sha_file, "r", encoding="utf-8") as f:
                sha = f.read().strip()
                if sha:
                    return sha
        except Exception:
            pass

    try:
        sha = (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                stderr=subprocess.DEVNULL,
            )
            .decode("utf-8")
            .strip()
        )
        if sha:
            return sha
    except Exception:
        pass

    return "local-dev"


class ExecuteRequest(BaseModel):
    function_name: str
    arguments: Dict[str, Any]


@app.get("/health")
def health() -> Dict[str, Any]:
    """Health check endpoint required by Part 5 for CI/CD smoke test."""
    return {
        "status": "ok",
        "commit_sha": get_current_commit_sha(),
    }


FUNCTION_METADATA = [
    {
        "id": "is_adult",
        "name": "is_adult",
        "category": "Data-Type: Integer",
        "description": "True if age is 18 or more. Negative age raises ValueError.",
        "params": [
            {"name": "age", "type": "number", "default": 20, "label": "Age"}
        ],
        "presets": [
            {"label": "Adult (20)", "args": {"age": 20}},
            {"label": "Boundary (18)", "args": {"age": 18}},
            {"label": "Minor (17)", "args": {"age": 17}},
            {"label": "Error: Negative (-5)", "args": {"age": -5}},
        ],
    },
    {
        "id": "celsius_to_fahrenheit",
        "name": "celsius_to_fahrenheit",
        "category": "Data-Type: Float",
        "description": "Convert Celsius to Fahrenheit, rounded to 2 decimals.",
        "params": [
            {"name": "celsius", "type": "number", "default": 100, "label": "Celsius"}
        ],
        "presets": [
            {"label": "Boiling (100°C)", "args": {"celsius": 100}},
            {"label": "Freezing (0°C)", "args": {"celsius": 0}},
            {"label": "Crossover (-40°C)", "args": {"celsius": -40}},
            {"label": "Body Temp (37°C)", "args": {"celsius": 37}},
        ],
    },
    {
        "id": "count_vowels",
        "name": "count_vowels",
        "category": "Data-Type: String",
        "description": "Count vowels (a, e, i, o, u), ignoring case. Non-string raises TypeError.",
        "params": [
            {"name": "text", "type": "text", "default": "Hello, World!", "label": "Text"}
        ],
        "presets": [
            {"label": "Standard ('Hello, World!')", "args": {"text": "Hello, World!"}},
            {"label": "All Vowels ('aeiou AEIOU')", "args": {"text": "aeiou AEIOU"}},
            {"label": "Empty ('')", "args": {"text": ""}},
            {"label": "No Vowels ('sky rhythm')", "args": {"text": "sky rhythm"}},
        ],
    },
    {
        "id": "invert",
        "name": "invert",
        "category": "Data-Type: Boolean",
        "description": "Return the opposite of flag. Non-bool raises TypeError.",
        "params": [
            {
                "name": "flag",
                "type": "select",
                "options": ["true", "false"],
                "default": "true",
                "label": "Boolean Flag",
            }
        ],
        "presets": [
            {"label": "True -> False", "args": {"flag": True}},
            {"label": "False -> True", "args": {"flag": False}},
        ],
    },
    {
        "id": "greet",
        "name": "greet",
        "category": "Data-Type: None / Optional",
        "description": "Greet by name, or greet 'Guest' if name is None, empty or only spaces.",
        "params": [
            {"name": "name", "type": "text", "default": "Alice", "label": "Name (Optional)"}
        ],
        "presets": [
            {"label": "Name ('Alice')", "args": {"name": "Alice"}},
            {"label": "Whitespace ('   ')", "args": {"name": "   "}},
            {"label": "Empty ('')", "args": {"name": ""}},
            {"label": "None (null)", "args": {"name": None}},
        ],
    },
    {
        "id": "find_max",
        "name": "find_max",
        "category": "Data-Type: List",
        "description": "Return the largest number. Empty list raises ValueError.",
        "params": [
            {
                "name": "numbers",
                "type": "json",
                "default": "[3, 7, 2, 9, 5]",
                "label": "List of Numbers (JSON)",
            }
        ],
        "presets": [
            {"label": "Positive [3, 7, 2, 9, 5]", "args": {"numbers": [3, 7, 2, 9, 5]}},
            {"label": "Negatives [-10, -3, -50]", "args": {"numbers": [-10, -3, -50]}},
            {"label": "Single [42]", "args": {"numbers": [42]}},
            {"label": "Error: Empty []", "args": {"numbers": []}},
        ],
    },
    {
        "id": "get_price",
        "name": "get_price",
        "category": "Data-Type: Dictionary",
        "description": "Return the price of item. Missing item raises KeyError.",
        "params": [
            {
                "name": "prices",
                "type": "json",
                "default": '{"apple": 1.5, "banana": 0.75, "mango": 2.25}',
                "label": "Prices Dict (JSON)",
            },
            {"name": "item", "type": "text", "default": "apple", "label": "Item Name"},
        ],
        "presets": [
            {
                "label": "Found ('apple')",
                "args": {"prices": {"apple": 1.5, "banana": 0.75}, "item": "apple"},
            },
            {
                "label": "Error: Missing ('orange')",
                "args": {"prices": {"apple": 1.5}, "item": "orange"},
            },
        ],
    },
    {
        "id": "swap",
        "name": "swap",
        "category": "Data-Type: Tuple",
        "description": "Return the two values swapped. Not exactly 2 values raises ValueError.",
        "params": [
            {
                "name": "pair",
                "type": "json",
                "default": "[10, 20]",
                "label": "2-Element Pair (JSON)",
            }
        ],
        "presets": [
            {"label": "Pair [10, 20]", "args": {"pair": [10, 20]}},
            {"label": "Strings ['a', 'b']", "args": {"pair": ["a", "b"]}},
            {"label": "Error: 3 Items [1, 2, 3]", "args": {"pair": [1, 2, 3]}},
            {"label": "Error: Empty []", "args": {"pair": []}},
        ],
    },
    {
        "id": "common_items",
        "name": "common_items",
        "category": "Data-Type: Set",
        "description": "Return the items found in both sets.",
        "params": [
            {
                "name": "set_a",
                "type": "json",
                "default": "[1, 2, 3]",
                "label": "Set A (JSON list)",
            },
            {
                "name": "set_b",
                "type": "json",
                "default": "[2, 3, 4]",
                "label": "Set B (JSON list)",
            },
        ],
        "presets": [
            {
                "label": "Overlap [1, 2, 3] & [2, 3, 4]",
                "args": {"set_a": [1, 2, 3], "set_b": [2, 3, 4]},
            },
            {
                "label": "Disjoint [1, 2] & [3, 4]",
                "args": {"set_a": [1, 2], "set_b": [3, 4]},
            },
            {"label": "Empty [] & []", "args": {"set_a": [], "set_b": []}},
        ],
    },
    {
        "id": "is_leap_year",
        "name": "is_leap_year",
        "category": "Data-Type: Date / Calendar",
        "description": "True if year is a leap year. Year below 1 raises ValueError.",
        "params": [
            {"name": "year", "type": "number", "default": 2024, "label": "Year"}
        ],
        "presets": [
            {"label": "Leap (2024)", "args": {"year": 2024}},
            {"label": "Century Leap (2000)", "args": {"year": 2000}},
            {"label": "Century Non-Leap (1900)", "args": {"year": 1900}},
            {"label": "Non-Leap (2023)", "args": {"year": 2023}},
            {"label": "Error: Year 0", "args": {"year": 0}},
        ],
    },
    {
        "id": "to_int",
        "name": "to_int",
        "category": "Data-Type: Conversion",
        "description": "Convert value to int. A bool raises TypeError.",
        "params": [
            {"name": "value", "type": "text", "default": "42", "label": "Value (String, Number)"}
        ],
        "presets": [
            {"label": "String '42'", "args": {"value": "42"}},
            {"label": "Float 12.34", "args": {"value": 12.34}},
            {"label": "Error: Bool True", "args": {"value": True}},
            {"label": "Error: Invalid 'abc'", "args": {"value": "abc"}},
        ],
    },
    {
        "id": "divide",
        "name": "divide",
        "category": "Mathematics: Division",
        "description": "Return a / b. Dividing by zero raises ZeroDivisionError.",
        "params": [
            {"name": "a", "type": "number", "default": 10, "label": "Numerator (a)"},
            {"name": "b", "type": "number", "default": 2, "label": "Denominator (b)"},
        ],
        "presets": [
            {"label": "Exact (10 / 2)", "args": {"a": 10, "b": 2}},
            {"label": "Inexact (1 / 3)", "args": {"a": 1, "b": 3}},
            {"label": "Negative (-10 / 2)", "args": {"a": -10, "b": 2}},
            {"label": "Error: Zero Division (10 / 0)", "args": {"a": 10, "b": 0}},
        ],
    },
    {
        "id": "power",
        "name": "power",
        "category": "Mathematics: Exponentiation",
        "description": "Return base raised to exponent.",
        "params": [
            {"name": "base", "type": "number", "default": 2, "label": "Base"},
            {"name": "exponent", "type": "number", "default": 3, "label": "Exponent"},
        ],
        "presets": [
            {"label": "2^3 = 8", "args": {"base": 2, "exponent": 3}},
            {"label": "0^0 = 1", "args": {"base": 0, "exponent": 0}},
            {"label": "Negative Exp (2^-2 = 0.25)", "args": {"base": 2, "exponent": -2}},
            {"label": "Square Root via Exp (4^0.5)", "args": {"base": 4, "exponent": 0.5}},
        ],
    },
    {
        "id": "square_root",
        "name": "square_root",
        "category": "Mathematics: Square Root",
        "description": "Return the square root of x. Negative x raises ValueError.",
        "params": [
            {"name": "x", "type": "number", "default": 9, "label": "x"}
        ],
        "presets": [
            {"label": "Perfect (9 -> 3.0)", "args": {"x": 9}},
            {"label": "Zero (0 -> 0.0)", "args": {"x": 0}},
            {"label": "Inexact (2 -> 1.414...)", "args": {"x": 2}},
            {"label": "Error: Negative (-4)", "args": {"x": -4}},
        ],
    },
    {
        "id": "factorial",
        "name": "factorial",
        "category": "Mathematics: Factorial",
        "description": "Return n factorial. Negative n raises ValueError.",
        "params": [
            {"name": "n", "type": "number", "default": 5, "label": "n"}
        ],
        "presets": [
            {"label": "Boundary 0! = 1", "args": {"n": 0}},
            {"label": "Boundary 1! = 1", "args": {"n": 1}},
            {"label": "Standard 5! = 120", "args": {"n": 5}},
            {"label": "Error: Negative (-1)", "args": {"n": -1}},
        ],
    },
    {
        "id": "average",
        "name": "average",
        "category": "Mathematics: Average",
        "description": "Return the average of a list. Empty list raises ValueError.",
        "params": [
            {
                "name": "numbers",
                "type": "json",
                "default": "[10, 20, 30]",
                "label": "Numbers List (JSON)",
            }
        ],
        "presets": [
            {"label": "Positive [10, 20, 30]", "args": {"numbers": [10, 20, 30]}},
            {"label": "Decimals [1, 2]", "args": {"numbers": [1, 2]}},
            {"label": "Negatives [-10, 10]", "args": {"numbers": [-10, 10]}},
            {"label": "Error: Empty []", "args": {"numbers": []}},
        ],
    },
]


@app.get("/api/functions")
def list_functions() -> Dict[str, Any]:
    """Returns catalog of all 16 target functions with metadata and presets."""
    return {"functions": FUNCTION_METADATA}


@app.post("/api/run")
def execute_function(payload: ExecuteRequest) -> JSONResponse:
    """Execute any of the 16 target.py functions safely and return result or error."""
    fn_name = payload.function_name
    args = payload.arguments

    if not hasattr(target, fn_name):
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error_type": "NotFoundError",
                "error_message": f"Function '{fn_name}' does not exist in target.py",
            },
        )

    fn = getattr(target, fn_name)

    try:
        if fn_name == "is_adult":
            res = fn(args.get("age"))
        elif fn_name == "celsius_to_fahrenheit":
            res = fn(args.get("celsius"))
        elif fn_name == "count_vowels":
            res = fn(args.get("text"))
        elif fn_name == "invert":
            raw_flag = args.get("flag")
            if isinstance(raw_flag, str):
                if raw_flag.lower() == "true":
                    flag_val = True
                elif raw_flag.lower() == "false":
                    flag_val = False
                else:
                    flag_val = raw_flag
            else:
                flag_val = raw_flag
            res = fn(flag_val)
        elif fn_name == "greet":
            res = fn(args.get("name"))
        elif fn_name == "find_max":
            res = fn(args.get("numbers"))
        elif fn_name == "get_price":
            res = fn(args.get("prices"), args.get("item"))
        elif fn_name == "swap":
            res = fn(args.get("pair"))
        elif fn_name == "common_items":
            raw_a = args.get("set_a")
            raw_b = args.get("set_b")
            set_a = set(raw_a) if isinstance(raw_a, (list, set, tuple)) else raw_a
            set_b = set(raw_b) if isinstance(raw_b, (list, set, tuple)) else raw_b
            out = fn(set_a, set_b)
            res = list(out) if isinstance(out, set) else out
        elif fn_name == "is_leap_year":
            res = fn(args.get("year"))
        elif fn_name == "to_int":
            res = fn(args.get("value"))
        elif fn_name == "divide":
            res = fn(args.get("a"), args.get("b"))
        elif fn_name == "power":
            res = fn(args.get("base"), args.get("exponent"))
        elif fn_name == "square_root":
            res = fn(args.get("x"))
        elif fn_name == "factorial":
            res = fn(args.get("n"))
        elif fn_name == "average":
            res = fn(args.get("numbers"))
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error_type": "InvalidFunction",
                    "error_message": f"Unsupported function: {fn_name}",
                },
            )

        # Convert tuples/sets to JSON serializable formats
        serialized_res = list(res) if isinstance(res, (tuple, set)) else res
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "result": serialized_res,
                "result_type": type(res).__name__,
            },
        )
    except Exception as exc:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error_type": type(exc).__name__,
                "error_message": str(exc) if str(exc) else type(exc).__name__,
            },
        )


# Serve Static Frontend Files
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    """Serve the single page frontend application."""
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(
        content="<h1>Target Testing Suite</h1><p>Frontend static files not found.</p>"
    )
