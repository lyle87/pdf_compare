Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

strScriptPath = objShell.CurrentDirectory
objShell.CurrentDirectory = strScriptPath

' Display banner
WScript.Echo ""
WScript.Echo "PDF Compare Tool"
WScript.Echo "================="
WScript.Echo ""

' Check for Python
On Error Resume Next
Set objExec = objShell.Exec("python --version")
strOutput = objExec.StdOut.ReadAll()
On Error Goto 0

If Err.Number <> 0 Then
    WScript.Echo "Error: Python is not installed or not in PATH."
    WScript.Echo "Please install Python 3.8+ from https://www.python.org/downloads/"
    WScript.Echo "Make sure to check 'Add Python to PATH' during installation."
    WScript.Quit 1
End If

WScript.Echo "[OK] Python found"
WScript.Echo ""

' Create virtual environment if needed
If Not objFSO.FolderExists(strScriptPath & "\.venv") Then
    WScript.Echo "Creating virtual environment..."
    objShell.Run "python -m venv .venv", 1, True
    WScript.Echo "[OK] Virtual environment created"
End If

' Install dependencies
WScript.Echo "Installing dependencies..."
objShell.Run "python -m pip install --upgrade pip -q", 0, True
objShell.Run "python -m pip install -q -r requirements.txt", 1, True
WScript.Echo "[OK] Dependencies installed"
WScript.Echo ""

' Run app
WScript.Echo "Starting PDF Compare Tool..."
WScript.Echo "Open your browser to: http://localhost:5000"
WScript.Echo "Press Ctrl+C to stop the server"
WScript.Echo ""

objShell.Run "python app.py", 1, True
