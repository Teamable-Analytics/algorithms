# Runs
This directory contains simulation runs.
Try to be descriptive when naming new files here.

- Every file should have a "main clause" that allows them to be run from the terminal:
```python
if __name__ == "__main__":
    typer.run(<yourFunctionHere>)
```
- We use typer instead of just running the function because it provides positional argument hints when things go wrong, and provides greater flexibility in what your main can do. Consult the [typer docs for more information.](https://typer.tiangolo.com/)
### Tips
A good thing to know is that you can run nested python files from the root directory like so:
e.g. folder1/folder2/file_name.py
```bash
python3 -m folder1.folder2.file_name
# tldr; replace "/" with "." and drop the ".py"
```


todo: complete