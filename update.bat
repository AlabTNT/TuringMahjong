set version=%1

set description=%2

shift
shift

:loop
if "%1"=="" goto continue
set description=%description% %1
shift
goto loop

:continue
git add .

git commit -m "%version%" -m "%description%"

git push origin main