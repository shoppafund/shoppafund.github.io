@echo off
REM Daily SHOPPA hub refresh: regenerate cockpit, run alerts, push to GitHub Pages.
cd /d "C:\SHOPPA\shoppafund-site"
"C:\Users\dptay\AppData\Local\Programs\Python\Python313\python.exe" deploy.py >> deploy.log 2>&1
