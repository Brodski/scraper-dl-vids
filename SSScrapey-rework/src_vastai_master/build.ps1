
# https://docs.aws.amazon.com/lambda/latest/dg/python-package.html
$files = @("configz.py", "print_extra.py", "emailer_vast.py", "vast_api.py", "vastai_master.py")
Copy-Item $files -Destination .\build\


Copy-Item venv\Lib\site-packages\* -Destination .\build\ -Recurse