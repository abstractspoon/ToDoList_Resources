# Replace '**your todolist install folder**' with your actual
# install folder path retaining the single quotation marks

# If the execution policy does not allow the running of 
# PowerShell scripts on your computer then simply open a 
# PowerShell window and copy and paste the entire script

$Url = 'http://abstractspoon.pbworks.com/f/todolist_exe.zip' 
$ZipFile = 'c:\temp\todolist_exe.zip' 

$Destination= '**your todolist install folder**' 
mkdir $Destination
 
Invoke-WebRequest -Uri $Url -OutFile $ZipFile 
$ExtractShell = New-Object -ComObject Shell.Application 
 
$Files = $ExtractShell.Namespace($ZipFile).Items() 
$ExtractShell.NameSpace($Destination).CopyHere($Files) 

del $ZipFile

Start-Process $Destination\todolist.exe
