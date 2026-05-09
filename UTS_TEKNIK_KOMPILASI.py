Nama        : Zukhruf Gharrick Marius
Nim         : 231011401735
Kelas       : 06TPLE003
Matkul      : Ujian Tengah Semester Teknik Kompilasi

import re

class AST: pass

class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left; self.op = op; self.right = right

class Num(AST):
    def __init__(self, value): self.value = value

class Var(AST):
    def __init__(self, name): self.name = name

class ParserError(Exception): pass


class MiniCompiler:
    def __init__(self, source, env):
        # TUGAS 1: tambahkan ^ ke dalam character class
        self._tokens = iter(re.findall(r'[a-zA-Z_]\w*|\d+(?:\.\d+)?|[+*/()\-^]', source) + ['?'])
        self._current = None
        self._env = env
        self._temp_count = 0
        self.advance()

    def advance(self):
        try:
            self._current = next(self._tokens)
        except StopIteration:
            self._current = None

    def expect(self, expected):
        if self._current != expected and not (expected == "ID" and self._current.isalnum()):
            raise ParserError(f"Expected {expected}, found {self._current}")
        token = self._current
        self.advance()
        return token

    def factor(self):
        token = self._current
        if token is not None and token.replace('.', '', 1).isdigit():
            self.advance()
            return Num(float(token) if '.' in token else int(token))
        elif token and token.isalpha():
            if token not in self._env:
                raise ParserError(f"Semantic Error: Undefined variable '{token}'")
            self.advance()
            return Var(token)
        elif token == '(':
            self.advance()
            node = self.expr()
            self.expect(')')
            return node
        raise ParserError(f"Unexpected token: {token}")

    # TUGAS 2: power() menangani operator '^'
    def power(self):
        node = self.factor()
        while self._current == '^':
            op = self._current
            self.advance()
            node = BinOp(left=node, op=op, right=self.factor())
        return node

    # TUGAS 3: term() memanggil power(), bukan factor()
    def term(self):
        node = self.power()
        while self._current in ('*', '/'):
            op = self._current
            self.advance()
            node = BinOp(left=node, op=op, right=self.power())
        return node

    def expr(self):
        node = self.term()
        while self._current in ('+', '-'):
            op = self._current
            self.advance()
            node = BinOp(left=node, op=op, right=self.term())
        return node

    def generate_tac(self, node):
        if isinstance(node, Num): return str(node.value)
        if isinstance(node, Var): return node.name
        left_val = self.generate_tac(node.left)
        right_val = self.generate_tac(node.right)
        self._temp_count += 1
        temp_name = f"t{self._temp_count}"
        print(f"  {temp_name} = {left_val} {node.op} {right_val}")
        return temp_name


# --- Uji Coba ---
source_code = "a ^ 2 + b * c"
symbol_table = {'a': 5, 'b': 10, 'c': 2}

print(f"Input: {source_code}")
compiler = MiniCompiler(source_code, symbol_table)
ast_root = compiler.expr()
print("\n--- Output Three Address Code (TAC) ---")
compiler.generate_tac(ast_root)

# Input: a ^ 2 + b * c 
--- Output Three Address Code (TAC) ---
  t1 = a ^ 2
  t2 = b * c
  t3 = t1 + t2

// Pertanyaan Refleksi //
1. Mengapa power() dipanggil di dalam term(), bukan sebaliknya?
Power() dipanggil di dalam term() karena operator '^' memiliki prioritas lebih tinggi
daripada '*' dan '/'. Dengan memanggil power() terlebih dahulu, kita memastikan bahwa
ekspresi dengan operator '^' dievaluasi sebelum operator perkalian dan pembagian.
Jika sebaliknya, kita akan salah menginterpretasikan urutan operasi, misalnya 'a ^ 2 * b' 
akan dievaluasi sebagai '(a ^ 2) * b' alih-alih 'a ^ (2 * b)', yang tidak sesuai dengan aturan matematika.

2. Apa yang terjadi jika variabel z tidak ada di symbol_table?
Pada fungsi factor(), terdapat pengecekan semantik:
pythonif token not in self._env:
    raise ParserError(f"Semantic Error: Undefined variable '{token}'")
Maka program akan melempar exception ParserError dengan pesan:
Semantic Error: Undefined variable 'z'
Ini adalah contoh Analisis Semantik — setelah token dikenali secara sintaksis (huruf = identifier),
compiler memvalidasi makna-nya: apakah variabel itu sudah dideklarasikan? Jika tidak, eksekusi dihentikan sebelum menghasilkan TAC.

3. Mengapa instruksi a ^ 2 harus muncul sebelum + dalam TAC?
Karena TAC (Three Address Code) mengikuti prinsip post-order traversal pada AST — anak-anak node dihitung dulu sebelum node induknya.
Untuk ekspresi a ^ 2 + b * c, struktur AST-nya adalah:
        +
       / \
      ^   *
     / \ / \
    a  2 b  c
generate_tac() bersifat rekursif: ia harus mengetahui nilai dari t1 = a ^ 2 dan t2 = b * c sebelum bisa menulis t3 = t1 + t2. 
Ini mencerminkan prinsip dependency ordering — instruksi yang menjadi bahan baku harus tersedia sebelum instruksi yang memakainya.