# Jack Compiler & Hack Computer — Coursework Portfolio

An educational collection of **Nand2Tetris / Digital Systems** implementations, including HDL components, Hack assembly programs, a Jack-to-VM compiler, and VM-to-Hack translators. Adapted from Reichman University coursework.

## Components

| Directory | Contents | Verification status |
| --- | --- | --- |
| `project01`–`project05` | Hack HDL logic, arithmetic, memory/CPU/computer; Hack assembly programs | Source prepared; simulator verification pending |
| `project07` | VM translator (arithmetic, push/pop) | Python source; limited smoke testing |
| `project08` | VM translator with branching/functions/calls | Python source; limited smoke testing |
| `project09` | Jack Breakout game and generated VM | Gameplay not verified |
| `project10` | Jack Analyzer: tokenizer and XML parse-tree generator | Basic XML smoke test included in CI |
| `project11` | Jack-to-VM compiler | Basic Jack smoke test passed locally |
| `legacy/project06` | Java Hack assembler coursework artifact | **Incomplete:** references missing helper classes; not a functioning assembler |

**Project 10 Jack Analyzer** is included in `project10/`, with a separate attribution note documenting the developer's account of its provenance.

## Quick start

From the repository root using Python 3:

```sh
python3 project10/Main.py examples/Main.jack
python3 project11/Main.py examples/Main.jack
python3 project08/Main.py examples/Simple.vm
python3 -m unittest discover -s tests -v
```

The commands generate `examples/Main.xml`, `examples/Main.vm` and `examples/Simple.asm`; generated outputs should not be committed. A working Nand2Tetris hardware/CPU simulator is needed for the HDL projects.

## Testing and scope

The smoke tests cover a minimal Jack analyzer XML parse tree, Jack class compilation, and basic VM translation. They do **not** demonstrate full compiler correctness, CPU hardware simulation, assembler operation, or tested gameplay. Automated checks run through GitHub Actions on each push.

## Attribution

**Code implementation:** Abedalsalam Akel (self-reported sole developer). The university coursework was submitted jointly under Abedalsalam Akel and Nadav Cohen; joint submission does not imply joint code authorship. Original Nand2Tetris course-provided specifications and scaffold headers are retained and credited to their respective authors. No overall open-source license is granted.
