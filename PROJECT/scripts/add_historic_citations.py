"""
Add landmark historic case citations to NirnayX Research Paper bibliography:
- State of Haryana v. Bhajan Lal, 1992 Supp (1) SCC 335 (Section 482 CrPC quashing)
- Gurbaksh Singh Sibbia v. State of Punjab, (1980) 2 SCC 565 (Section 438 Anticipatory Bail)
- Sushila Aggarwal v. State (NCT of Delhi), (2020) 5 SCC 1 (Duration of Anticipatory Bail)
- Arjun Panditrao Khotkar v. Kailash Kushanrao Gorantyal, (2020) 7 SCC 1 (Section 65B Electronic Evidence)
- Sharad Birdhichand Sarda v. State of Maharashtra, (1984) 4 SCC 116 (Circumstantial Evidence Panchsheel)
- Pulukuri Kottaya v. King-Emperor, (1947) LR 74 IA 65 (Section 27 Evidence Act Discovery)
- Maneka Gandhi v. Union of India, (1978) 1 SCC 248 (Article 21 Procedure Established by Law)
"""

from pathlib import Path

TARGET_FILES = [
    Path(r"C:\Users\rajat\Desktop\FINAL YEAR RESEARCH\synopsis\NirnayX_Research_Paper.tex"),
    Path(r"C:\Users\rajat\Desktop\FINAL YEAR RESEARCH\synopsis\nirnay_x_research_paper.tex"),
]

HISTORIC_BIBS = r"""\bibitem{bhajanlal1992}
Supreme Court of India, \textit{State of Haryana v. Bhajan Lal}, 1992 Supp (1) SCC 335.

\bibitem{sibbia1980}
Supreme Court of India, \textit{Gurbaksh Singh Sibbia v. State of Punjab}, (1980) 2 SCC 565.

\bibitem{sushila2020}
Supreme Court of India, \textit{Sushila Aggarwal v. State (NCT of Delhi)}, (2020) 5 SCC 1.

\bibitem{arjun2020}
Supreme Court of India, \textit{Arjun Panditrao Khotkar v. Kailash Kushanrao Gorantyal}, (2020) 7 SCC 1.

\bibitem{sharad1984}
Supreme Court of India, \textit{Sharad Birdhichand Sarda v. State of Maharashtra}, (1984) 4 SCC 116.

\bibitem{kottaya1947}
Privy Council, \textit{Pulukuri Kottaya v. King-Emperor}, (1947) LR 74 IA 65.

\bibitem{maneka1978}
Supreme Court of India, \textit{Maneka Gandhi v. Union of India}, (1978) 1 SCC 248.

\bibitem{constitution1950}"""

def add_historic_bibs(path: Path):
    if not path.exists():
        return
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if r"\bibitem{bhajanlal1992}" not in content and r"\bibitem{constitution1950}" in content:
        content = content.replace(r"\bibitem{constitution1950}", HISTORIC_BIBS)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Added historic legal precedents to bibliography in: {path}")
    else:
        print(f"Historic citations already present or placeholder not found in {path}")

def main():
    for p in TARGET_FILES:
        add_historic_bibs(p)

if __name__ == "__main__":
    main()
