@echo off
REM release.cmd — Windows wrapper using native Poetry

REM Determine bump type (patch/minor/major)
set "BUMP=%~1"
if "%BUMP%"=="" set "BUMP=patch"

echo Bumping version (%BUMP%)...

REM --- Use delayed expansion to get the last line as version ---
for /f "delims=" %%V in ('poetry version --short %BUMP%') do set "NEW_VERSION=%%V"
echo → New version: %NEW_VERSION%
REM --- end of version extraction ---

echo Committing version bump...
git add pyproject.toml
git commit -m "Bump version to v%NEW_VERSION%"

echo Tagging v%NEW_VERSION%...
git tag "v%NEW_VERSION%"

echo Pushing commits and tags...
git push origin HEAD
git push origin "v%NEW_VERSION%"

echo Publishing to PyPI...
poetry publish --build --no-interaction

echo Release v%NEW_VERSION% complete!
exit /b 0
