"""Render all 7 TikZ diagrams for PRIESTS_ENGINE to high-res PNG."""
import subprocess, os, tempfile, shutil

DIR = os.path.dirname(os.path.abspath(__file__))

PREAMBLE = r"""\documentclass[tikz,border=14pt]{standalone}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,positioning,fit,calc,backgrounds,matrix}
\definecolor{Bgreen}{HTML}{1e4d1a}
\definecolor{Bblue}{HTML}{1e2e4d}
\definecolor{Bamber}{HTML}{4d3a1a}
\definecolor{Bred}{HTML}{4d1e1e}
\definecolor{Bpurple}{HTML}{3d1e4d}
\definecolor{Bteal}{HTML}{1a3d4a}
\definecolor{Bgray}{HTML}{28283a}
\definecolor{Bslate}{HTML}{2e3d50}
\definecolor{Bgold}{HTML}{4a3800}
\tikzset{
  bnode/.style={
    rectangle, rounded corners=5pt,
    minimum width=3.0cm, minimum height=0.85cm,
    align=center, font=\sffamily\small, text=white,
    draw=none, inner sep=7pt
  },
  B/.style    ={bnode, fill=Bgreen},
  T/.style    ={bnode, fill=Bblue},
  F/.style    ={bnode, fill=Bamber},
  N/.style    ={bnode, fill=Bred},
  special/.style={bnode, fill=Bpurple},
  result/.style ={bnode, fill=Bteal},
  neutral/.style={bnode, fill=Bgray},
  slate/.style  ={bnode, fill=Bslate},
  arr/.style={
    -{Stealth[length=6pt,width=5pt]}, thick, color=gray!60
  },
  darr/.style={
    -{Stealth[length=6pt,width=5pt]}, thick, dashed, color=gray!45
  },
  lbl/.style={font=\sffamily\tiny, text=gray!70},
}
\begin{document}"""

SUFFIX = r"\end{document}"

# ── individual diagrams ───────────────────────────────────────────────────────

FIGS = {}

# Fig 1 — Belnap FOUR lattice (truth order)
FIGS[1] = r"""
\begin{tikzpicture}[node distance=1.4cm and 2.8cm]
  \node[B] (B) {\textbf{B}\ \textemdash\ \textit{Both}\\[2pt]
    \tiny dialetheic fixed point};
  \node[T, below left=1.8cm and 1.8cm of B]  (T) {\textbf{T}\ \textemdash\ \textit{True}};
  \node[F, below right=1.8cm and 1.8cm of B] (F) {\textbf{F}\ \textemdash\ \textit{False}};
  \node[N, below right=1.8cm and 1.8cm of T] (N) {\textbf{N}\ \textemdash\ \textit{None}\\[2pt]
    \tiny no information};
  \draw[arr] (B) -- (T);
  \draw[arr] (B) -- (F);
  \draw[arr] (T) -- (N);
  \draw[arr] (F) -- (N);
\end{tikzpicture}"""

# Fig 2 — Frobenius kernel circular buffer
FIGS[2] = r"""
\begin{tikzpicture}[node distance=2.2cm]
  \node[B, minimum width=4.2cm] (A)
    {\texttt{ENGAGR \%r0}\\[2pt]\tiny force register to B};
  \node[slate, minimum width=4.2cm, right=3.2cm of A] (B)
    {\texttt{FSPLIT \%r0\ \%r1\ \%r2}\\[2pt]\tiny $\delta$: B $\to$ (T,\,F)};
  \node[B, minimum width=4.2cm, below=2.0cm of B] (C)
    {\texttt{FFUSE \%r1\ \%r2\ \%r0}\\[2pt]\tiny $\mu$: T\,$\vee$\,F $\to$ B};
  \node[neutral, minimum width=4.2cm, below=2.0cm of A] (D)
    {\texttt{JMP .loop}\\[2pt]\tiny repeat};
  \draw[arr] (A) -- (B);
  \draw[arr] (B) -- (C);
  \draw[arr] (C) -- (D);
  \draw[arr] (D) -- (A);
  \node[lbl, right=0.5cm of B, align=left]
    {only B splits\\non-trivially};
  \node[lbl, below=0.25cm of D, align=center]
    {$\eta = 4$ paradoxes/cycle\quad $P(n)=4n$};
\end{tikzpicture}"""

# Fig 3 — Frobenius round-trip δ/μ
FIGS[3] = r"""
\begin{tikzpicture}[node distance=0.9cm and 1.6cm]
  % column headers
  \node[lbl, font=\sffamily\footnotesize\bfseries, text=gray!80] at (0,0) {Input};
  \node[lbl, font=\sffamily\footnotesize\bfseries, text=gray!80] at (4.2,0) {$\delta$ (FSPLIT)};
  \node[lbl, font=\sffamily\footnotesize\bfseries, text=gray!80] at (8.4,0) {$\mu$ (FFUSE)};

  % Row B — special
  \node[B, minimum width=1.4cm] at (0,-1.2)   (bi) {B};
  \node[special, minimum width=2.8cm] at (4.2,-1.2) (tf) {(T,\ F) \textbf{\large$\star$}};
  \node[B, minimum width=1.4cm] at (8.4,-1.2)  (bo) {B};
  \draw[arr] (bi) -- node[lbl,above]{$\delta$} (tf);
  \draw[arr] (tf) -- node[lbl,above]{$\mu$} (bo);

  % Row T
  \node[T, minimum width=1.4cm] at (0,-2.5)   (ti) {T};
  \node[neutral, minimum width=2.8cm] at (4.2,-2.5) (tt) {(T,\ T)};
  \node[T, minimum width=1.4cm] at (8.4,-2.5)  (to) {T};
  \draw[arr] (ti) -- (tt); \draw[arr] (tt) -- (to);

  % Row F
  \node[F, minimum width=1.4cm] at (0,-3.8)   (fi) {F};
  \node[neutral, minimum width=2.8cm] at (4.2,-3.8) (ff) {(F,\ F)};
  \node[F, minimum width=1.4cm] at (8.4,-3.8)  (fo) {F};
  \draw[arr] (fi) -- (ff); \draw[arr] (ff) -- (fo);

  % Row N
  \node[N, minimum width=1.4cm] at (0,-5.1)   (ni) {N};
  \node[neutral, minimum width=2.8cm] at (4.2,-5.1) (nn) {(N,\ N)};
  \node[N, minimum width=1.4cm] at (8.4,-5.1)  (no) {N};
  \draw[arr] (ni) -- (nn); \draw[arr] (nn) -- (no);

  % star annotation
  \node[lbl, right=0.4cm of tf, align=left, text=Bpurple!80!white]
    {only B produces\\distinct components};
\end{tikzpicture}"""

# Fig 4 — Dialetheic Alignment Theorem
FIGS[4] = r"""
\begin{tikzpicture}[node distance=1.4cm and 0.8cm]
  \node[slate, minimum width=4.0cm, minimum height=2.0cm, align=center] (OP)
    {\textbf{Operational}\\[4pt]
     \tiny $\mu\circ\delta(B)=B$\\
     \tiny $\delta(B)=(T,F)$, $T\neq F$\\
     \tiny unique bifurcation point};
  \node[slate, minimum width=4.0cm, minimum height=2.0cm, align=center,
        right=1.0cm of OP] (LOG)
    {\textbf{Logical}\\[4pt]
     \tiny $B\wedge\neg B = B$\\
     \tiny $B$ designated, $\neg B$ designated\\
     \tiny unique dialetheic value};
  \node[slate, minimum width=4.0cm, minimum height=2.0cm, align=center,
        right=1.0cm of LOG] (ALG)
    {\textbf{Algebraic}\\[4pt]
     \tiny $B\wedge\neg B=B$ (not N)\\
     \tiny contradiction localised\\
     \tiny no explosion: B absorbs B};

  \node[B, minimum width=2.0cm, below=1.8cm of LOG] (B)
    {\textbf{B}};

  \node[result, minimum width=10.2cm, below=1.6cm of B, align=center] (R)
    {\textbf{Dialetheic Alignment Theorem}\\[3pt]
     \tiny Three independent characterisations converge on the same value};

  \draw[arr] (OP)  -- (B);
  \draw[arr] (LOG) -- (B);
  \draw[arr] (ALG) -- (B);
  \draw[arr] (B)   -- (R);
\end{tikzpicture}"""

# Fig 5 — Four Millennium Problems
FIGS[5] = r"""
\begin{tikzpicture}[node distance=1.2cm and 1.0cm]
  \node[special, minimum width=4.4cm, minimum height=2.0cm, align=center] (RH)
    {\textbf{Riemann Hypothesis}\\[3pt]
     \tiny $\zeta(s)=\chi(s)\zeta(1{-}s)$\\
     \tiny $\mathtt{bnot}(B)=B$\\
     \tiny critical line = B-fixed point};
  \node[Bgold, bnode, minimum width=4.4cm, minimum height=2.0cm, align=center,
        right=1.2cm of RH] (YM)
    {\textbf{Yang-Mills Mass Gap}\\[3pt]
     \tiny $N < T$ covering relation\\
     \tiny $\Delta>0$ structural\\
     \tiny K-trap: confinement};
  \node[slate, minimum width=4.4cm, minimum height=2.0cm, align=center,
        below=1.8cm of RH] (PNP)
    {\textbf{P\,vs\,NP}\\[3pt]
     \tiny NP cert.\ = all-B circuit\\
     \tiny classical cannot reach B\\
     \tiny barrier: structural};
  \node[neutral, minimum width=4.4cm, minimum height=2.0cm, align=center,
        below=1.8cm of YM] (SIC)
    {\textbf{SIC-POVM} $(d{=}2)$\\[3pt]
     \tiny B satisfies all 4 axioms\\
     \tiny WH$_2$: B\,$\mapsto$\,$(1,1)=XZ$};

  \node[B, minimum width=3.2cm, minimum height=1.0cm,
        below right=2.0cm and 1.6cm of RH] (B)
    {\textbf{B}\ (Both)\\[2pt]\tiny unique dialetheic value};

  \node[result, minimum width=10.0cm, minimum height=1.1cm, below=1.6cm of B, align=center] (U)
    {\textbf{\texttt{millennium\_barriers\_unified() -> True}}\\[3pt]
     \tiny three barriers are three faces of the same structural fact};

  \draw[arr] (RH)  -- (B);
  \draw[arr] (YM)  -- (B);
  \draw[arr] (PNP) -- (B);
  \draw[arr] (SIC) -- (B);
  \draw[arr] (B)   -- (U);
\end{tikzpicture}"""

# Fig 6 — Belnap Shor pipeline
FIGS[6] = r"""
\begin{tikzpicture}[node distance=0.9cm and 1.0cm]
  \node[neutral, minimum width=3.6cm] (INIT)
    {Initial state\\[2pt]\tiny all registers N};
  \node[B, minimum width=3.6cm, right=1.4cm of INIT] (HAD)
    {Hadamard layer\\[2pt]\tiny $|T\rangle\to B$\quad cost: $n$};
  \node[special, minimum width=3.6cm, right=1.4cm of HAD] (MOD)
    {Modular exp.\\[2pt]\tiny B propagates unchanged\\cost: 0};

  \node[Bteal, bnode, minimum width=3.6cm,
        below right=1.6cm and 0.5cm of MOD] (P1)
    {B-bias measurement\\[2pt]\tiny B preserved\quad cost: $2n$};
  \node[slate, minimum width=3.6cm,
        above right=0.6cm and 0.5cm of P1] (P2)
    {T-bias measurement\\[2pt]\tiny $B\to T$\quad cost: $n$};

  \node[result, minimum width=2.8cm, right=1.4cm of P2] (R)
    {Ratio\\[2pt]\textbf{2\,:\,1}\\[2pt]\tiny $n$-invariant};

  \node[N, minimum width=3.0cm, below=1.4cm of R, align=center] (BOT)
    {$\Phi_\}\to\Phi_\{$ bottleneck\\[2pt]\tiny period extraction open};
  \node[B, minimum width=3.0cm, right=1.2cm of R, align=center] (PRV)
    {Proved: $O_1$ tier\\[2pt]\tiny \texttt{coherence\_ratio\_is\_two}\\$\forall\,n>0$};

  \draw[arr] (INIT) -- (HAD);
  \draw[arr] (HAD)  -- (MOD);
  \draw[arr] (MOD)  -- ++(0,-1.0) -| (P1);
  \draw[arr] (MOD)  -- ++(0, 0.8) -| (P2);
  \draw[arr] (P1)   -- (R);
  \draw[arr] (P2)   -- (R);
  \draw[arr] (R)    -- (BOT);
  \draw[arr] (R)    -- (PRV);
\end{tikzpicture}"""

# Fig 7 — Belnap as category
FIGS[7] = r"""
\begin{tikzpicture}[node distance=1.4cm and 2.8cm]
  \node[N] (N)
    {\textbf{N}\ \textemdash\ \textit{None}\\[2pt]
     \tiny initial object\\
     \tiny $\forall x:\;N\to x$ (unique)};
  \node[T, above left=1.8cm and 1.8cm of N]  (T) {\textbf{T}\ \textemdash\ \textit{True}};
  \node[F, above right=1.8cm and 1.8cm of N] (F) {\textbf{F}\ \textemdash\ \textit{False}};
  \node[B, above right=1.8cm and 1.8cm of T] (B)
    {\textbf{B}\ \textemdash\ \textit{Both}\\[2pt]
     \tiny terminal object\\
     \tiny $\forall x:\;x\to B$ (unique)};
  \draw[arr] (N) -- (T);
  \draw[arr] (N) -- (F);
  \draw[arr] (N) -- (B);
  \draw[arr] (T) -- (B);
  \draw[arr] (F) -- (B);
  \draw[darr] (T) -- node[lbl,above]{\textit{incomparable}} (F);
\end{tikzpicture}"""

# ── compile ───────────────────────────────────────────────────────────────────

def compile_fig(n, body):
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, f'fig{n}.tex')
        with open(src, 'w') as f:
            f.write(PREAMBLE + '\n' + body + '\n' + SUFFIX)
        r = subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', f'fig{n}.tex'],
            cwd=tmp, capture_output=True, text=True
        )
        pdf = os.path.join(tmp, f'fig{n}.pdf')
        if not os.path.exists(pdf):
            print(f'  ERROR fig{n}:\n{r.stdout[-800:]}')
            return
        # crop whitespace
        subprocess.run(['pdfcrop', f'fig{n}.pdf', f'fig{n}-crop.pdf'],
                       cwd=tmp, capture_output=True)
        cropped = os.path.join(tmp, f'fig{n}-crop.pdf')
        src_pdf = cropped if os.path.exists(cropped) else pdf
        # convert to high-res PNG
        out_png = os.path.join(DIR, f'fig{n}.png')
        subprocess.run(
            ['pdftoppm', '-r', '220', '-png', '-singlefile', src_pdf,
             os.path.join(tmp, f'fig{n}')],
            capture_output=True
        )
        tmp_png = os.path.join(tmp, f'fig{n}.png')
        if os.path.exists(tmp_png):
            shutil.copy(tmp_png, out_png)
            print(f'  fig{n}.png  ok  ({os.path.getsize(out_png)//1024} KB)')
        else:
            print(f'  fig{n}: pdftoppm produced no PNG')

if __name__ == '__main__':
    for n, body in sorted(FIGS.items()):
        print(f'Rendering fig{n}...')
        compile_fig(n, body)
    print('Done.')
