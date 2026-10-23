"""
AkshAI - Calculator Engine
Version: 1.0

Purpose:
    Safe and powerful mathematical calculation engine.

Designed for:
    - Pydroid 3
    - Standard Python library only
    - Future Brain + AI/LLM integration

Important:
    User input is NEVER passed directly to Python eval().
    Expressions are parsed using Python's AST module and only
    explicitly allowed mathematical operations/functions are used.
"""

from __future__ import annotations

import ast
import math
import operator
import re
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional


# ============================================================
# ENGINE INFORMATION
# ============================================================

CALCULATOR_ENGINE_NAME = "AkshAI Calculator Engine"
CALCULATOR_ENGINE_VERSION = "1.0"
CALCULATOR_ENGINE_READY = True


# ============================================================
# RESULT OBJECT
# ============================================================

@dataclass
class CalculationResult:
    success: bool
    expression: str
    result: Any = None
    formatted_result: str = ""
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================
# SAFE MATH FUNCTIONS
# ============================================================

SAFE_FUNCTIONS = {

    # Basic
    "abs": abs,
    "round": round,

    # Powers / roots
    "sqrt": math.sqrt,
    "cbrt": getattr(math, "cbrt", lambda x: x ** (1 / 3)),
    "pow": pow,

    # Exponential / logarithmic
    "exp": math.exp,
    "log": math.log,
    "log10": math.log10,
    "log2": math.log2,

    # Trigonometry - radians
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,

    # Hyperbolic
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,

    # Other
    "floor": math.floor,
    "ceil": math.ceil,
    "factorial": math.factorial,

    # Degree-based trigonometry
    "sind": lambda x: math.sin(math.radians(x)),
    "cosd": lambda x: math.cos(math.radians(x)),
    "tand": lambda x: math.tan(math.radians(x)),

    # Degree/radian conversion
    "radians": math.radians,
    "degrees": math.degrees,
}


# ============================================================
# SAFE CONSTANTS
# ============================================================

SAFE_CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
    "inf": math.inf,
}


# ============================================================
# ALLOWED OPERATORS
# ============================================================

BINARY_OPERATORS = {

    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,

}


UNARY_OPERATORS = {

    ast.UAdd: operator.pos,
    ast.USub: operator.neg,

}


# ============================================================
# SAFE AST EVALUATOR
# ============================================================

class SafeMathEvaluator(ast.NodeVisitor):
    """
    Safely evaluates mathematical AST expressions.

    Only explicitly allowed mathematical operations are accepted.
    """

    def visit_Expression(self, node):
        return self.visit(node.body)


    def visit_Constant(self, node):

        if isinstance(node.value, (int, float)):

            if isinstance(node.value, bool):
                raise ValueError("Boolean values are not allowed.")

            return node.value

        raise ValueError("Only numeric values are allowed.")


    def visit_Num(self, node):
        return node.n


    def visit_Name(self, node):

        if node.id in SAFE_CONSTANTS:
            return SAFE_CONSTANTS[node.id]

        raise ValueError(
            f"Unknown constant or variable: {node.id}"
        )


    def visit_BinOp(self, node):

        operation = BINARY_OPERATORS.get(type(node.op))

        if operation is None:
            raise ValueError(
                "This mathematical operator is not supported."
            )

        left = self.visit(node.left)
        right = self.visit(node.right)

        # Prevent dangerous exponent sizes.
        if isinstance(node.op, ast.Pow):

            if abs(right) > 10000:
                raise ValueError(
                    "Exponent is too large."
                )

            if abs(left) > 10**100:
                raise ValueError(
                    "Base is too large."
                )

        return operation(left, right)


    def visit_UnaryOp(self, node):

        operation = UNARY_OPERATORS.get(type(node.op))

        if operation is None:
            raise ValueError(
                "This unary operator is not supported."
            )

        return operation(
            self.visit(node.operand)
        )


    def visit_Call(self, node):

        if not isinstance(node.func, ast.Name):
            raise ValueError(
                "Only approved mathematical functions are allowed."
            )

        function_name = node.func.id

        if function_name not in SAFE_FUNCTIONS:
            raise ValueError(
                f"Function '{function_name}' is not supported."
            )

        if node.keywords:
            raise ValueError(
                "Keyword arguments are not supported."
            )

        function = SAFE_FUNCTIONS[function_name]

        arguments = [
            self.visit(argument)
            for argument in node.args
        ]

        return function(*arguments)


    def generic_visit(self, node):

        raise ValueError(
            f"Unsupported mathematical expression: "
            f"{type(node).__name__}"
        )


# ============================================================
# CALCULATOR ENGINE
# ============================================================

class CalculatorEngine:

    def __init__(self):

        self.name = CALCULATOR_ENGINE_NAME
        self.version = CALCULATOR_ENGINE_VERSION


    # ========================================================
    # NORMALIZE EXPRESSION
    # ========================================================

    @staticmethod
    def normalize_expression(
        expression: str
    ) -> str:

        if expression is None:
            return ""

        text = str(expression).strip()

        # Unicode multiplication/division signs
        text = text.replace("×", "*")
        text = text.replace("÷", "/")

        # Unicode minus
        text = text.replace("−", "-")

        # Power symbol
        text = text.replace("^", "**")

        # Square-root symbol:
        # √9 -> sqrt(9)
        text = re.sub(
            r"√\s*(\d+(?:\.\d+)?)",
            r"sqrt(\1)",
            text,
        )

        # Remove commas from numbers:
        # 1,000 -> 1000
        text = re.sub(
            r"(?<=\d),(?=\d)",
            "",
            text,
        )

        # Percentage:
        # 25% -> (25/100)
        text = re.sub(
            r"(\d+(?:\.\d+)?)\s*%",
            r"(\1/100)",
            text,
        )

        return text


    # ========================================================
    # PARSE EXPRESSION
    # ========================================================

    @staticmethod
    def parse_expression(
        expression: str
    ):

        normalized = (
            CalculatorEngine
            .normalize_expression(expression)
        )

        if not normalized:
            raise ValueError(
                "No mathematical expression provided."
            )

        if len(normalized) > 500:
            raise ValueError(
                "Expression is too long."
            )

        try:

            return ast.parse(
                normalized,
                mode="eval",
            )

        except SyntaxError:

            raise ValueError(
                "Invalid mathematical expression."
            )


    # ========================================================
    # CALCULATE
    # ========================================================

    def calculate(
        self,
        expression: str
    ) -> CalculationResult:

        original = (
            str(expression).strip()
            if expression is not None
            else ""
        )

        try:

            normalized = self.normalize_expression(
                original
            )

            tree = self.parse_expression(
                original
            )

            evaluator = SafeMathEvaluator()

            value = evaluator.visit(tree)

            # Reject NaN
            if isinstance(value, float):

                if math.isnan(value):
                    raise ValueError(
                        "Result is not a valid number."
                    )

            formatted = self.format_result(value)

            return CalculationResult(
                success=True,
                expression=original,
                result=value,
                formatted_result=formatted,
            )

        except ZeroDivisionError:

            return CalculationResult(
                success=False,
                expression=original,
                error="Cannot divide by zero.",
            )

        except OverflowError:

            return CalculationResult(
                success=False,
                expression=original,
                error="The result is too large.",
            )

        except ValueError as error:

            return CalculationResult(
                success=False,
                expression=original,
                error=str(error),
            )

        except Exception:

            return CalculationResult(
                success=False,
                expression=original,
                error="Unable to calculate this expression.",
            )


    # ========================================================
    # RESULT FORMATTING
    # ========================================================

    @staticmethod
    def format_result(
        value: Any
    ) -> str:

        if isinstance(value, bool):
            return str(value)

        if isinstance(value, int):
            return str(value)

        if isinstance(value, float):

            if math.isinf(value):
                return "∞" if value > 0 else "-∞"

            if value == 0:
                return "0"

            # Clean floating-point noise.
            if value.is_integer():
                return str(int(value))

            return f"{value:.12g}"

        return str(value)


    # ========================================================
    # PERCENTAGE
    # ========================================================

    @staticmethod
    def percentage(
        value: float,
        percent: float
    ) -> float:

        return value * percent / 100


    # ========================================================
    # PERCENTAGE INCREASE
    # ========================================================

    @staticmethod
    def percentage_increase(
        value: float,
        percent: float
    ) -> float:

        return value * (1 + percent / 100)


    # ========================================================
    # PERCENTAGE DECREASE
    # ========================================================

    @staticmethod
    def percentage_decrease(
        value: float,
        percent: float
    ) -> float:

        return value * (1 - percent / 100)


    # ========================================================
    # DISCOUNT
    # ========================================================

    @staticmethod
    def discount(
        price: float,
        percent: float
    ) -> Dict[str, float]:

        discount_amount = (
            price * percent / 100
        )

        final_price = (
            price - discount_amount
        )

        return {
            "original_price": price,
            "discount_percent": percent,
            "discount_amount": discount_amount,
            "final_price": final_price,
        }


    # ========================================================
    # GST
    # ========================================================

    @staticmethod
    def gst(
        price: float,
        gst_percent: float
    ) -> Dict[str, float]:

        gst_amount = (
            price * gst_percent / 100
        )

        total = price + gst_amount

        return {
            "base_price": price,
            "gst_percent": gst_percent,
            "gst_amount": gst_amount,
            "total": total,
        }


    # ========================================================
    # AVERAGE
    # ========================================================

    @staticmethod
    def average(*values: float) -> float:

        if not values:
            raise ValueError(
                "At least one value is required."
            )

        return sum(values) / len(values)


    # ========================================================
    # GCD
    # ========================================================

    @staticmethod
    def gcd(a: int, b: int) -> int:
        return math.gcd(a, b)


    # ========================================================
    # LCM
    # ========================================================

    @staticmethod
    def lcm(a: int, b: int) -> int:
        return math.lcm(a, b)


    # ========================================================
    # COMBINATION
    # ========================================================

    @staticmethod
    def combination(
        n: int,
        r: int
    ) -> int:

        return math.comb(n, r)


    # ========================================================
    # PERMUTATION
    # ========================================================

    @staticmethod
    def permutation(
        n: int,
        r: int
    ) -> int:

        return math.perm(n, r)


    # ========================================================
    # FACTORIAL
    # ========================================================

    @staticmethod
    def factorial(
        n: int
    ) -> int:

        return math.factorial(n)


    # ========================================================
    # QUICK CALCULATION
    # ========================================================

    def quick_calculate(
        self,
        expression: str
    ) -> Optional[Any]:

        result = self.calculate(expression)

        if result.success:
            return result.result

        return None


    # ========================================================
    # DICTIONARY API
    # ========================================================

    def calculate_dict(
        self,
        expression: str
    ) -> Dict[str, Any]:

        return self.calculate(
            expression
        ).to_dict()


    # ========================================================
    # ENGINE STATUS
    # ========================================================

    def get_status(self) -> Dict[str, Any]:

        return {
            "name": self.name,
            "version": self.version,
            "ready": CALCULATOR_ENGINE_READY,
            "safe_evaluator": True,
            "functions": sorted(
                SAFE_FUNCTIONS.keys()
            ),
            "constants": sorted(
                SAFE_CONSTANTS.keys()
            ),
        }


# ============================================================
# GLOBAL INSTANCE
# ============================================================

calculator_engine = CalculatorEngine()


# ============================================================
# SIMPLE PUBLIC FUNCTIONS
# ============================================================

def calculate(
    expression: str
) -> CalculationResult:

    return calculator_engine.calculate(
        expression
    )


def calculate_dict(
    expression: str
) -> Dict[str, Any]:

    return calculator_engine.calculate_dict(
        expression
    )


def quick_calculate(
    expression: str
) -> Optional[Any]:

    return calculator_engine.quick_calculate(
        expression
    )


# ============================================================
# SELF TESTS
# ============================================================

def run_calculator_tests() -> bool:

    print("=" * 65)
    print("AkshAI Calculator Engine v1.0")
    print("=" * 65)

    tests = [

        ("2 + 3", 5),
        ("10 - 4", 6),
        ("6 * 7", 42),
        ("20 / 4", 5),
        ("2 ** 5", 32),
        ("2 ^ 5", 32),
        ("(10 + 5) * 2", 30),
        ("sqrt(81)", 9),
        ("cbrt(27)", 3),
        ("sin(0)", 0),
        ("sind(30)", 0.5),
        ("cosd(60)", 0.5),
        ("log10(100)", 2),
        ("log2(8)", 3),
        ("factorial(5)", 120),
        ("abs(-25)", 25),
        ("25%", 0.25),
        ("1,000 + 500", 1500),
        ("pi * 2", math.pi * 2),
        ("2 + 3 * 4", 14),
    ]

    passed = 0

    for expression, expected in tests:

        result = calculator_engine.calculate(
            expression
        )

        if result.success:

            actual = result.result

            if isinstance(
                expected,
                float
            ):

                correct = math.isclose(
                    actual,
                    expected,
                    rel_tol=1e-9,
                    abs_tol=1e-9,
                )

            else:

                correct = actual == expected

        else:
            correct = False

        if correct:

            print(
                f"✅ {expression!r} "
                f"-> {result.formatted_result}"
            )

            passed += 1

        else:

            print(
                f"❌ {expression!r} "
                f"-> {result.error or result.result!r} "
                f"(expected {expected!r})"
            )


    # --------------------------------------------------------
    # Special calculations
    # --------------------------------------------------------

    print("\nSpecial calculations:")

    gst_result = calculator_engine.gst(
        1000,
        18,
    )

    assert gst_result["gst_amount"] == 180
    assert gst_result["total"] == 1180

    print("✅ GST calculation")

    discount_result = calculator_engine.discount(
        2000,
        10,
    )

    assert discount_result["discount_amount"] == 200
    assert discount_result["final_price"] == 1800

    print("✅ Discount calculation")

    assert (
        calculator_engine.average(
            10,
            20,
            30,
        )
        == 20
    )

    print("✅ Average calculation")

    assert (
        calculator_engine.gcd(12, 18)
        == 6
    )

    print("✅ GCD calculation")

    assert (
        calculator_engine.lcm(4, 6)
        == 12
    )

    print("✅ LCM calculation")

    assert (
        calculator_engine.combination(5, 2)
        == 10
    )

    print("✅ Combination calculation")

    assert (
        calculator_engine.permutation(5, 2)
        == 20
    )

    print("✅ Permutation calculation")


    # --------------------------------------------------------
    # Safety tests
    # --------------------------------------------------------

    print("\nSafety tests:")

    dangerous_inputs = [
        "__import__('os')",
        "open('file.txt')",
        "exec('print(123)')",
        "eval('2+2')",
        "import os",
    ]

    safety_passed = 0

    for expression in dangerous_inputs:

        result = calculator_engine.calculate(
            expression
        )

        if not result.success:

            print(
                f"✅ Blocked: {expression!r}"
            )

            safety_passed += 1

        else:

            print(
                f"❌ NOT BLOCKED: {expression!r}"
            )


    print("\n" + "-" * 65)

    total = len(tests)

    print(
        f"Math tests passed: "
        f"{passed}/{total}"
    )

    print(
        f"Safety tests passed: "
        f"{safety_passed}/{len(dangerous_inputs)}"
    )


    all_passed = (
        passed == total
        and safety_passed == len(
            dangerous_inputs
        )
    )

    if all_passed:

        print(
            "\nCALCULATOR ENGINE TEST PASSED ✅"
        )

        print("=" * 65)

        return True

    print(
        "\nCALCULATOR ENGINE TEST FAILED ❌"
    )

    print("=" * 65)

    return False


# ============================================================
# MANUAL RUN
# ============================================================

if __name__ == "__main__":

    success = run_calculator_tests()

    if not success:
        raise SystemExit(1)

    print("\nExample:")

    result = calculator_engine.calculate(
        "sqrt(144) + sind(30) * 10"
    )

    print(
        result.to_dict()
    )