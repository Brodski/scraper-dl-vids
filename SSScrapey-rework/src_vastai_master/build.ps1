#################################################################
#
# This script is ran via Terraform at lambda_vastai.tf
# - code gets packaged and sent to lambda
#
#################################################################
#
# https://docs.aws.amazon.com/lambda/latest/dg/python-package.html
#
$ErrorActionPreference = "Stop"

# Always start clean
if (Test-Path ".\build") {
    Remove-Item ".\build" -Recurse -Force
}

New-Item -ItemType Directory -Path ".\build" | Out-Null

$files = @("Configz.py", "emailer_vast.py", "Instance_V.py", "print_extra.py", "vast_api.py", "vastai_master.py" )

Copy-Item $files -Destination .\build\


Copy-Item venv2\Lib\site-packages\* -Destination .\build\ -Recurse