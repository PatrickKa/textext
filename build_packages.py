import shutil
import argparse
import tempfile
import os


class TmpDir:
    def __init__(self):
        self.path = None

    def __enter__(self):
        self.path = tempfile.mkdtemp()
        return self.path

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.path:
            shutil.rmtree(self.path)


if __name__ == "__main__":

    TexTextVersion = "0.8.1"

    parser = argparse.ArgumentParser(description="Build TexText distribution archive for selected platforms.")
    available_formats = [fmt for fmt, desc in shutil.get_archive_formats()]
    parser.add_argument('--linux',
                        type=str,
                        nargs="+",
                        choices=available_formats,
                        help="Build package for Linux with archive formats [%s]" % ", ".join(available_formats))
    parser.add_argument('--windows',
                        type=str,
                        nargs="+",
                        choices=available_formats,
                        help="Build package for Windows with archive formats [%s]" % ", ".join(available_formats))

    args = vars(parser.parse_args())
    if not any(args.values()):
        # ToDo Not nice to require optional arguments, smarter solution would be subparsers
        #      but for this little script...
        parser.error("At least one of the \"optional\" arguments is required.")

    for platform, formats in {p:f for p, f in args.items() if f}.items():
        PackageName = "TexText-%s-" % platform.capitalize() + TexTextVersion
        git_ignore_patterns = shutil.ignore_patterns(*open(".gitignore").read().split("\n"))

        with TmpDir() as tmpdir:
            shutil.copytree("./extension",
                            os.path.join(tmpdir, "extension"),
                            ignore=git_ignore_patterns  # exclude .gitignore files
                            )
            shutil.copy("setup.py", tmpdir)
            shutil.copy("LICENSE.txt", tmpdir)
            if platform == "Windows":
                shutil.copy("setup_win.bat", tmpdir)
            for fmt in formats:
                filename = shutil.make_archive(PackageName, fmt, tmpdir)
                print("Successfully created %s" % os.path.basename(filename))
