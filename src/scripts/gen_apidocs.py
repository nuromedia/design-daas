"""
For the documentation site, autogenerate pages for API docs.

Inspired by:

* <https://mkdocstrings.github.io/recipes/#generate-pages-on-the-fly>
* <https://github.com/mkdocstrings/python/blob/main/scripts/gen_ref_nav.py>
"""

from pathlib import Path
import mkdocs_gen_files


def _gen_apidocs_stubs():
    nav = mkdocs_gen_files.Nav()  # pyright: ignore [reportPrivateImportUsage]

    for path in sorted(Path("src/app").rglob("*.py")):
        module_path = path.relative_to(".").with_suffix("")
        module_parts = tuple(module_path.parts)
        doc_path = Path().joinpath(*module_parts).with_suffix(".md")

        # handle "__init__.py" files more elegantly
        # That they are renamed to an "index.md" file
        # is necessary for the "navigation.indexes" theme option
        if module_parts[-1] == "__init__":
            module_parts = tuple(module_parts[:-1])
            doc_path = doc_path.with_name("index.md")

        # hide internal modules
        if module_parts[-1].startswith("_"):
            continue

        # hide stuff that doesn't look like a Python module, e.g. swapfiles
        if any(module_parts[-1].startswith(c) for c in ".#"):
            continue

        nav[module_parts] = doc_path.as_posix()

        full_doc_path = Path("reference", doc_path)

        with mkdocs_gen_files.open(full_doc_path, "w") as md_file:
            name = ".".join(module_parts)
            md_file.write(f"# `{name}` module\n\n")  # add explicit title
            md_file.write(f"::: {name}\n")
            md_file.write("    options:\n")
            md_file.write("      show_root_heading: false\n")

    # write SUMMARY file containing the navigation tree
    with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
        nav_file.writelines(nav.build_literate_nav())


_gen_apidocs_stubs()
