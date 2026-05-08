"""
LaTeX report rendering for specguard.

Called automatically from solve.py at the end of every run. The report
lands in reports/<stem>.tex where <stem> is the basename of the
requirements file. Compile with pdflatex.
"""

from pathlib import Path

import z3


# ── Path helpers ──


def display_path(path):
    s = str(path)
    marker = "specguard/"
    idx = s.rfind(marker)
    if idx >= 0:
        return s[idx:]
    try:
        return str(Path(path).resolve().relative_to(Path.cwd()))
    except (ValueError, OSError):
        return s


def report_path_for(source_path):
    src = Path(source_path)
    project_root = Path(__file__).parent
    return project_root / "reports" / (src.stem + ".tex")


# ── LaTeX rendering primitives ──


_LATEX_INFIX = {
    z3.Z3_OP_LE: r" \leq ",
    z3.Z3_OP_LT: r" < ",
    z3.Z3_OP_GE: r" \geq ",
    z3.Z3_OP_GT: r" > ",
    z3.Z3_OP_EQ: r" = ",
    z3.Z3_OP_DISTINCT: r" \neq ",
    z3.Z3_OP_ADD: r" + ",
    z3.Z3_OP_SUB: r" - ",
    z3.Z3_OP_MUL: r" \cdot ",
}


def _latex_name(name):
    return name.replace("_", r"\_")


def _format_number(num):
    try:
        if z3.is_rational_value(num):
            n = num.numerator_as_long()
            d = num.denominator_as_long()
            if d == 1:
                return str(n)
            f = n / d
            if abs(f) > 0 and (abs(f) < 1e-2 or abs(f) >= 1e4):
                exp = 0
                mantissa = f
                while abs(mantissa) >= 10:
                    mantissa /= 10
                    exp += 1
                while abs(mantissa) < 1:
                    mantissa *= 10
                    exp -= 1
                m_str = f"{mantissa:.4g}".rstrip("0").rstrip(".")
                if not m_str:
                    m_str = "0"
                return f"{m_str} \\times 10^{{{exp}}}"
            return f"{f:g}"
        if z3.is_int_value(num):
            return str(num.as_long())
    except Exception:
        pass
    return str(num)


def to_latex(expr):
    if z3.is_const(expr):
        decl = expr.decl()
        kind = decl.kind()
        if kind == z3.Z3_OP_TRUE:
            return r"\top"
        if kind == z3.Z3_OP_FALSE:
            return r"\bot"
        if z3.is_rational_value(expr) or z3.is_int_value(expr):
            return _format_number(expr)
        if kind == z3.Z3_OP_UNINTERPRETED:
            return rf"\text{{{_latex_name(decl.name())}}}"

    decl = expr.decl()
    kind = decl.kind()

    if kind == z3.Z3_OP_NOT:
        return rf"\neg {to_latex(expr.children()[0])}"
    if kind == z3.Z3_OP_IMPLIES:
        c0 = to_latex(expr.children()[0])
        c1 = to_latex(expr.children()[1])
        return rf"({c0} \Rightarrow {c1})"
    if kind == z3.Z3_OP_AND:
        children = [to_latex(c) for c in expr.children()]
        return "(" + r" \wedge ".join(children) + ")"
    if kind == z3.Z3_OP_OR:
        children = [to_latex(c) for c in expr.children()]
        return "(" + r" \vee ".join(children) + ")"
    if kind in _LATEX_INFIX:
        children = [to_latex(c) for c in expr.children()]
        return _LATEX_INFIX[kind].join(children)

    return rf"\text{{{_latex_name(str(expr))}}}"


def tex_escape(text):
    if text is None:
        return ""
    out = []
    for ch in text:
        if ch == "\\":
            out.append(r"\textbackslash{}")
        elif ch in "_$&#%{}":
            out.append("\\" + ch)
        elif ch == "~":
            out.append(r"\textasciitilde{}")
        elif ch == "^":
            out.append(r"\textasciicircum{}")
        else:
            out.append(ch)
    return "".join(out)


# ── Report assembly ──


def render_latex(source_path, collections, axioms, consistency, entailment, equivalence):
    short_source = display_path(source_path)
    L = []
    L.append(r"\documentclass[11pt,a4paper]{article}")
    L.append(r"\usepackage[T1]{fontenc}")
    L.append(r"\usepackage{lmodern}")
    L.append(r"\usepackage{amsmath}")
    L.append(r"\usepackage{amssymb}")
    L.append(r"\usepackage{breqn}")
    L.append(r"\usepackage{enumitem}")
    L.append(r"\usepackage[margin=2.5cm]{geometry}")
    L.append(r"\usepackage{microtype}")
    L.append(r"\usepackage{titlesec}")
    L.append(r"\usepackage{parskip}")
    L.append(r"\titleformat{\section}{\Large\bfseries\sffamily}{\thesection}{1em}{}")
    L.append(r"\titleformat{\subsection}{\large\bfseries\sffamily}{\thesubsection}{1em}{}")
    L.append(r"\setlength{\parindent}{0pt}")
    L.append(r"\setlist[itemize]{topsep=4pt,itemsep=2pt,leftmargin=*}")
    L.append(r"\title{\textsf{\textbf{\Huge specguard report}}}")
    L.append(rf"\author{{\texttt{{{tex_escape(short_source)}}}}}")
    L.append(r"\date{\today}")
    L.append(r"\begin{document}")
    L.append(r"\maketitle")

    # Encoded collections
    L.append(r"\section{Encoded collections}")
    for name, reqs in collections.items():
        L.append(rf"\subsection*{{\texttt{{{tex_escape(name)}}}}}")
        for r in reqs:
            L.append(rf"\noindent\textbf{{\texttt{{{tex_escape(r.id)}}}}}\quad {tex_escape(r.text)}")
            L.append(r"\begin{dmath*}")
            L.append(to_latex(r.constraint))
            L.append(r"\end{dmath*}")

    # Axioms
    if axioms:
        L.append(r"\section{Axioms}")
        for ax in axioms:
            L.append(r"\begin{dmath*}")
            L.append(to_latex(ax))
            L.append(r"\end{dmath*}")

    # Internal consistency
    L.append(r"\section{Internal consistency}")
    L.append(r"\begin{itemize}")
    for r in consistency:
        L.append(rf"\item \texttt{{{tex_escape(r['name'])}}}: \textsc{{{r['result']}}}")
        if r["core"]:
            L.append(r"\begin{itemize}")
            for c in r["core"]:
                L.append(rf"\item conflicting: \texttt{{{tex_escape(c)}}}")
            L.append(r"\end{itemize}")
    L.append(r"\end{itemize}")

    # Directional entailment
    if entailment:
        L.append(r"\section{Directional entailment}")
        for er in entailment:
            L.append(rf"\subsection*{{\texttt{{{tex_escape(er['entailer'])}}} entails each \texttt{{{tex_escape(er['target'])}}}}}")
            pass_count = sum(1 for i in er["items"] if i["passed"])
            fail_count = len(er["items"]) - pass_count
            L.append(r"\begin{itemize}")
            for item in er["items"]:
                if item["passed"]:
                    L.append(rf"\item \textbf{{\texttt{{{tex_escape(item['id'])}}}}}: PASS")
                else:
                    L.append(rf"\item \textbf{{\texttt{{{tex_escape(item['id'])}}}}}: FAIL \\")
                    L.append(rf"\textit{{text:}} {tex_escape(item['text'])} \\")
                    L.append(rf"\textit{{witness:}} \texttt{{{tex_escape(item['witness'])}}}")
            L.append(r"\end{itemize}")
            L.append(rf"\textbf{{Summary: {pass_count} passed, {fail_count} failed.}}")

    # Restatement equivalence
    if equivalence:
        L.append(r"\section{Restatement equivalence}")
        L.append(r"\begin{itemize}")
        eq = neq = 0
        for r in equivalence:
            if r["skipped"]:
                L.append(rf"\item \textbf{{\texttt{{{tex_escape(r['id_a'])}}} $\Leftrightarrow$ \texttt{{{tex_escape(r['id_b'])}}}}}: SKIPPED")
                continue
            if r["equivalent"]:
                L.append(rf"\item \textbf{{\texttt{{{tex_escape(r['id_a'])}}} $\Leftrightarrow$ \texttt{{{tex_escape(r['id_b'])}}}}}: EQUIVALENT")
                eq += 1
            else:
                L.append(rf"\item \textbf{{\texttt{{{tex_escape(r['id_a'])}}} $\Leftrightarrow$ \texttt{{{tex_escape(r['id_b'])}}}}}: NOT EQUIVALENT \\")
                L.append(rf"\texttt{{{tex_escape(r['id_a'])}}}: {tex_escape(r['text_a'])} \\")
                L.append(rf"\texttt{{{tex_escape(r['id_b'])}}}: {tex_escape(r['text_b'])} \\")
                a_to_b_str = "PASS" if r["a_to_b"] else "FAIL"
                b_to_a_str = "PASS" if r["b_to_a"] else "FAIL"
                line = rf"\texttt{{{tex_escape(r['id_a'])}}} entails \texttt{{{tex_escape(r['id_b'])}}}: {a_to_b_str}"
                if not r["a_to_b"]:
                    line += rf"; witness: \texttt{{{tex_escape(r['witness_ab'])}}}"
                line += r" \\"
                L.append(line)
                line = rf"\texttt{{{tex_escape(r['id_b'])}}} entails \texttt{{{tex_escape(r['id_a'])}}}: {b_to_a_str}"
                if not r["b_to_a"]:
                    line += rf"; witness: \texttt{{{tex_escape(r['witness_ba'])}}}"
                L.append(line)
                neq += 1
        L.append(r"\end{itemize}")
        L.append(rf"\textbf{{Summary: {eq} equivalent, {neq} not equivalent.}}")

    L.append(r"\end{document}")
    return "\n".join(L) + "\n"


def write_report(source_path, collections, axioms, consistency, entailment, equivalence):
    out_path = report_path_for(source_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    text = render_latex(source_path, collections, axioms, consistency, entailment, equivalence)
    out_path.write_text(text)
    return out_path
