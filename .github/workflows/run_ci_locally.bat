@echo off
REM run_ci_locally.bat - Windows本地CI检查

echo 🚀 开始本地CI检查...

echo.
echo ========================================
echo 📝 Step 1: 代码质量检查
echo ========================================
flake8 . --count --statistics
black --check .

echo.
echo ========================================
echo 🧪 Step 2: 单元测试
echo ========================================
pytest test_unit.py -v --cov=. --cov-report=term-missing
if errorlevel 1 (
    echo ❌ 单元测试失败
    exit /b 1
)

echo.
echo ========================================
echo 🔗 Step 3: 集成测试
echo ========================================
pytest test_integration.py -v --cov=. --cov-report=html
if errorlevel 1 (
    echo ❌ 集成测试失败
    exit /b 1
)

echo.
echo ========================================
echo 🎯 Step 4: 完整测试套件
echo ========================================
pytest test_unit.py test_integration.py -v ^
    --cov=. ^
    --cov-report=html ^
    --html=report.html ^
    --self-contained-html

if errorlevel 1 (
    echo ❌❌❌ 某些测试失败
    exit /b 1
) else (
    echo ✅✅✅ 所有检查通过！
    echo 可以安全推送到GitHub
    echo.
    echo 📊 覆盖率报告: htmlcov\index.html
    echo 📄 测试报告: report.html
)
