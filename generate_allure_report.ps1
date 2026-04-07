$env:JAVA_HOME = 'C:\Program Files\Microsoft\jdk-17.0.18.8-hotspot'
$env:PATH = $env:PATH + ';' + "$env:JAVA_HOME\bin"
& "$PSScriptRoot\allure-2.24.1\bin\allure.bat" generate "$PSScriptRoot\allure-results" "-o" "$PSScriptRoot\allure-report" "--clean"
