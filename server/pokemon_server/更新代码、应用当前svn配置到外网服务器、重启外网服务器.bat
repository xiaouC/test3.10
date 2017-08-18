@echo off
set HOME=%HOMEDRIVE%%HOMEPATH%
set cwd=%~dp0
@echo "%cwd%"
set repo="..\server_git\"
set design=..\design_configs\
if exist ".git" (set repo=%cwd%) else ( cd %repo% )
@Rem 更新代码
echo "git reset --hard origin/develop"
git checkout develop
git reset --hard
git fetch origin
git reset --hard origin/develop

@Rem #覆盖配置文件夹
@Rem #echo "copy "%cwd%data" "%repo%data""
@Rem #copy "%cwd%data" "%repo%data"

@Rem 更新配置
cd %design%
svn revert
svn up

@Rem 导出配置
cd %repo%
echo %design%
python -mscripts.tocsv %design%

@Rem 提交代码
cd %repo%
echo "git commit -am "Robot update config""
git config --global core.autocrlf true
git commit --allow-empty -am "Robot update config"

@Rem 重启外网服务器
cd %repo%
python rtx.py
git push nezha@120.132.50.137:repo -f
pause
