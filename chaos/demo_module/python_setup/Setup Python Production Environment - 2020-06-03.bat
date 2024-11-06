REM SETUP_PYTHON_ENVIRONMENT.bat
REM This script will setup and install after Anaconda is installed to allow environment based script runs.  Also installs the approved libraries.  Changes to this script must be authorized by BI Director for security purposes.  Safe run by any BI User.
REM CREATED 2019-08-21
REM 2019-08-21
REM 2020-06-04 Updated paths to search
ECHO ON

SETLOCAL enabledelayexpansion

REM Get anaconda path


if exist %LOCALAPPDATA%\Continuum\anaconda3\scripts\conda.exe (
    SET ANACONDA_PATH=%LOCALAPPDATA%\Continuum\anaconda3
) else (    
 
    if exist C:\ProgramData\Anaconda3\Scripts\conda.exe (
        SET ANACONDA_PATH=C:\ProgramData\Anaconda3
    ) else (    
        REM Exit with ERROR
        SET ANACONDA_PATH=""
        ECHO PYTHON NOT FOUND %ERRORLEVEL%
        choice /d y /t 10 > nul
        exit /b 3
    )
)


SET ENVIRONMENT_NAME=production
SET PYTHON_PATH=%ANACONDA_PATH%\python.exe
SET CONDA_PATH=%ANACONDA_PATH%\Scripts\conda.exe
SET ACTIVATE_PATH=%ANACONDA_PATH%\Scripts\activate.bat
SET DEACTIVATE_PATH=%ANACONDA_PATH%\Scripts\deactivate.bat
SET ENVIRONMENT_PATH=%ANACONDA_PATH%\envs\%ENVIRONMENT_NAME%
SET LOG_FILE=%~dp0..\logs\setup.bat.log

MKDIR "%~dp0..\logs"

ECHO "Starting" > %LOG_FILE%

REM Creating Environment
CALL %CONDA_PATH% create --name %ENVIRONMENT_NAME%

REM Installing Packages
CALL %CONDA_PATH% install -n %ENVIRONMENT_NAME% python=3.6.5 --yes
CALL %CONDA_PATH% install -n %ENVIRONMENT_NAME% pandas=0.23.0 --yes
CALL %CONDA_PATH% install -n %ENVIRONMENT_NAME% numpy=1.14.3 --yes
CALL %CONDA_PATH% install -n %ENVIRONMENT_NAME% pyodbc=4.0.23 --yes
CALL %CONDA_PATH% install -n %ENVIRONMENT_NAME% matplotlib=2.2.2 --yes
CALL %CONDA_PATH% install -n %ENVIRONMENT_NAME% openpyxl=2.6.2 --yes
CALL %CONDA_PATH% install -n %ENVIRONMENT_NAME% sqlalchemy=1.2.7 --yes
CALL %CONDA_PATH% install -n %ENVIRONMENT_NAME% conda --yes
CALL %CONDA_PATH% install -n %ENVIRONMENT_NAME% pywin32 --yes
CALL %CONDA_PATH% install -n %ENVIRONMENT_NAME% xlrd=1.2.0  --yes

ECHO "Done"
pause