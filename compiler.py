import re

MAX_VARS = 100
MAX_LEN = 8192
MAX_NAME = 31
INT_MIN = -(2 ** 31)
INT_MAX = (2 ** 31) - 1
MAX_RUNTIME_STEPS = 100000

class MiniCError(Exception):
    """Error reported by the Mini C interpreter."""

class Interpreter:
    def __init__(self):
        self.symbol_table = {}
        self.runtime_steps = 0
  
    @staticmethod
    def skip_spaces(source, position):
        while position < len(source) and source[position].isspace():
            position += 1
        return position

    @staticmethod
    def is_name_start(char):
        return char.isalpha() or char == "_"

    @staticmethod
    def is_name_char(char):
        return char.isalnum() or char == "_"

    def read_name(self, source, position):
        position = self.skip_spaces(source, position)

        if position >= len(source) or not self.is_name_start(source[position]):
            raise MiniCError("[Syntax Error] Expected an identifier")

        start = position
        while position < len(source) and self.is_name_char(source[position]):
            position += 1

        name = source[start:position]

        if len(name) > MAX_NAME:
            raise MiniCError("[Syntax Error] Identifier is too long")

        return name, position

    def find_var(self, name):
        return name if name in self.symbol_table else None

    def get_var(self, name):
        if name not in self.symbol_table:
            raise MiniCError(
                f"[Semantic Error] Undefined variable '{name}'"
            )
        return self.symbol_table[name]

    def set_var(self, name, value):
        value = self.check_int(value)

        if name not in self.symbol_table and len(self.symbol_table) >= MAX_VARS:
            raise MiniCError("[Semantic Error] Symbol table is full")

        self.symbol_table[name] = value

    @staticmethod
    def check_int(value):
        if value < INT_MIN or value > INT_MAX:
            raise MiniCError("[Runtime Error] Integer overflow")
        return int(value)

    def parse_primary(self, source, position):
        position = self.skip_spaces(source, position)

        if position >= len(source):
            raise MiniCError(
                "[Syntax Error] Expected a number, variable, or '('"
            )

        char = source[position]

        if char.isdigit():
            start = position
            while position < len(source) and source[position].isdigit():
                position += 1

            number = int(source[start:position])

            if number > INT_MAX:
                raise MiniCError(
                    "[Runtime Error] Integer literal is too large"
                )

            return number, position

        if self.is_name_start(char):
            name, position = self.read_name(source, position)
            return self.get_var(name), position

        if char == "(":
            value, position = self.parse_expression(source, position + 1)
            position = self.skip_spaces(source, position)

            if position >= len(source) or source[position] != ")":
                raise MiniCError("[Syntax Error] Expected ')'")

            return value, position + 1

        raise MiniCError(
            "[Syntax Error] Expected a number, variable, or '('"
        )

    def parse_unary(self, source, position):
        position = self.skip_spaces(source, position)

        if position < len(source) and source[position] == "+":
            return self.parse_unary(source, position + 1)

        if position < len(source) and source[position] == "-":
            value, position = self.parse_unary(source, position + 1)
            if value == INT_MIN:
                raise MiniCError("[Runtime Error] Integer overflow")
            return -value, position

        return self.parse_primary(source, position)

    def parse_term(self, source, position):
        value, position = self.parse_unary(source, position)

        while True:
            position = self.skip_spaces(source, position)

            if position >= len(source) or source[position] not in "*/":
                break

            operator = source[position]
            right, position = self.parse_unary(source, position + 1)

            if operator == "*":
                value = self.check_int(value * right)
            else:
                if right == 0:
                    raise MiniCError("[Runtime Error] Division by zero")
                if value == INT_MIN and right == -1:
                    raise MiniCError("[Runtime Error] Integer overflow")

                # C integer division truncates toward zero.
                value = int(value / right)

        return value, position

    def parse_expression(self, source, position=0):
        value, position = self.parse_term(source, position)

        while True:
            position = self.skip_spaces(source, position)

            if position >= len(source) or source[position] not in "+-":
                break

            operator = source[position]
            right, position = self.parse_term(source, position + 1)

            if operator == "+":
                value = self.check_int(value + right)
            else:
                value = self.check_int(value - right)

        return value, position

    # --------------------------------------------------------
    # Condition parser:
    # condition := expression [comparison expression]
    # --------------------------------------------------------

    def parse_condition(self, source, position=0):
        left, position = self.parse_expression(source, position)
        position = self.skip_spaces(source, position)

        operator = None
        for candidate in ("==", "!=", "<=", ">=", "<", ">"):
            if source.startswith(candidate, position):
                operator = candidate
                position += len(candidate)
                break

        if operator is None:
            return int(left != 0), position

        right, position = self.parse_expression(source, position)

        comparisons = {
            "==": left == right,
            "!=": left != right,
            "<": left < right,
            ">": left > right,
            "<=": left <= right,
            ">=": left >= right,
        }

        return int(comparisons[operator]), position

 
    def expect_char(self, source, position, expected):
        position = self.skip_spaces(source, position)

        if position >= len(source) or source[position] != expected:
            raise MiniCError(f"[Syntax Error] Expected '{expected}'")

        return position + 1

    def find_block_end(self, source, position):
        position = self.skip_spaces(source, position)

        if position >= len(source) or source[position] != "{":
            raise MiniCError("[Syntax Error] Expected '{'")

        depth = 0
        while position < len(source):
            if source[position] == "{":
                depth += 1
            elif source[position] == "}":
                depth -= 1
                if depth == 0:
                    return position + 1
            position += 1

        raise MiniCError("[Syntax Error] Unclosed block")

    def execute_block(self, source, position):
        position = self.expect_char(source, position, "{")

        while True:
            position = self.skip_spaces(source, position)

            if position < len(source) and source[position] == "}":
                return position + 1

            if position >= len(source):
                raise MiniCError("[Syntax Error] Unclosed block")

            before = position
            position = self.execute_statement(source, position)

            if position == before:
                raise MiniCError("[Syntax Error] Parser made no progress")

    def execute_statement(self, source, position=0):
        position = self.skip_spaces(source, position)

        if position >= len(source) or source[position] == "}":
            return position

        # int declaration
        if self.keyword_at(source, position, "int"):
            position += 3
            name, position = self.read_name(source, position)

            if name in self.symbol_table:
                raise MiniCError(
                    f"[Semantic Error] Variable '{name}' is already declared"
                )

            value = 0
            position = self.skip_spaces(source, position)

            if position < len(source) and source[position] == "=":
                value, position = self.parse_expression(source, position + 1)

            position = self.expect_char(source, position, ";")
            self.set_var(name, value)
            print(f">> [Declared] '{name}' = {value}")
            return position

        # print expression
        if self.keyword_at(source, position, "print"):
            position += 5
            position = self.skip_spaces(source, position)

            parenthesized = (
                position < len(source) and source[position] == "("
            )

            if parenthesized:
                position += 1

            value, position = self.parse_expression(source, position)

            if parenthesized:
                position = self.expect_char(source, position, ")")

            position = self.expect_char(source, position, ";")
            print(f"Output -> {value}")
            return position

        # if / else
        if self.keyword_at(source, position, "if"):
            position += 2
            position = self.expect_char(source, position, "(")

            condition, position = self.parse_condition(source, position)
            position = self.expect_char(source, position, ")")

            true_start = self.skip_spaces(source, position)
            true_end = self.find_block_end(source, true_start)

            # Locate optional else block, regardless of which branch runs.
            after_true = self.skip_spaces(source, true_end)
            else_start = None
            else_end = None

            if self.keyword_at(source, after_true, "else"):
                else_start = self.skip_spaces(source, after_true + 4)
                else_end = self.find_block_end(source, else_start)

            if condition:
                self.execute_block(source, true_start)
            elif else_start is not None:
                self.execute_block(source, else_start)

            return else_end if else_end is not None else true_end

        # while loop
        if self.keyword_at(source, position, "while"):
            position += 5
            position = self.expect_char(source, position, "(")

            condition_start = position
            condition, condition_end = self.parse_condition(
                source, condition_start
            )
            position = self.expect_char(source, condition_end, ")")

            body_start = self.skip_spaces(source, position)
            body_end = self.find_block_end(source, body_start)

            while condition and not False:
                self.runtime_steps += 1

                if self.runtime_steps > MAX_RUNTIME_STEPS:
                    raise MiniCError(
                        "[Runtime Error] Execution limit exceeded; "
                        "possible infinite loop"
                    )

                self.execute_block(source, body_start)

                condition, _ = self.parse_condition(
                    source, condition_start
                )

            return body_end

        # Assignment
        if self.is_name_start(source[position]):
            name, position = self.read_name(source, position)

            if name not in self.symbol_table:
                raise MiniCError(
                    f"[Semantic Error] Variable '{name}' is not declared"
                )

            position = self.expect_char(source, position, "=")
            value, position = self.parse_expression(source, position)
            position = self.expect_char(source, position, ";")

            self.set_var(name, value)
            print(f">> [Updated] '{name}' = {value}")
            return position

        raise MiniCError("[Syntax Error] Unknown statement")

    @staticmethod
    def keyword_at(source, position, word):
        end = position + len(word)

        return (
            source.startswith(word, position)
            and (
                end >= len(source)
                or not (source[end].isalnum() or source[end] == "_")
            )
        )

    def run(self):
        print("=" * 48)
        print("       MINI C INTERPRETER - TINY C LANGUAGE")
        print("=" * 48)
        print("Supported statements:")
        print("  int x = 10;")
        print("  int y;")
        print("  x = x + 1;")
        print("  print x;")
        print("  print(x + 1);")
        print("  if (x > 5) { ... } else { ... }")
        print("  while (x > 0) { ... }")
        print("Type 'exit' to quit.")
        print("-" * 48)

        while True:
            try:
                line = input("mini-c> ")
            except EOFError:
                break

            if line.strip() == "exit":
                print("Exiting Mini C. Goodbye!")
                break

            if not line.strip():
                continue

            buffer = line
            brace_depth = buffer.count("{") - buffer.count("}")
            input_failed = False

            # Collect a multi-line block while braces remain open.
            while brace_depth > 0:
                try:
                    extra_line = input("... ")
                except EOFError:
                    input_failed = True
                    break

                buffer += " " + extra_line
                brace_depth += (
                    extra_line.count("{") - extra_line.count("}")
                )

                if brace_depth < 0:
                    print("[Syntax Error] Unexpected '}'")
                    input_failed = True
                    break

                if len(buffer) >= MAX_LEN:
                    print("[Input Error] Program block is too large")
                    input_failed = True
                    break

            if input_failed:
                continue

            self.runtime_steps = 0

            try:
                position = 0

                while True:
                    position = self.skip_spaces(buffer, position)

                    if position >= len(buffer):
                        break

                    before = position
                    position = self.execute_statement(buffer, position)

                    if position == before:
                        raise MiniCError(
                            "[Syntax Error] Parser made no progress"
                        )

            except MiniCError as error:
                print(error)


if __name__ == "__main__":
    Interpreter().run()
