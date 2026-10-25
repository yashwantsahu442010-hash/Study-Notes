# StudyAI — GitHub Actions Android build starter

Owner/profile label: `cg`
App title: `StudyAI`

## Upload from a phone
1. Download and extract this ZIP on your phone using a file manager.
2. Open https://github.com and create a **Private** repository named `StudyAI`.
3. In the repository, use **Add file → Upload files** and upload the project files/folders.
4. Make sure `.github/workflows/android.yml` is uploaded at exactly that path, and `main.py` plus `buildozer.spec` are in the repository root.
5. Commit the files to the `main` branch.
6. Open the repository's **Actions** tab. If prompted, enable workflows.
7. Open **Build StudyAI Android APK**. If no run started automatically, choose **Run workflow**.
8. Open the completed run, scroll to **Artifacts**, and download `StudyAI-debug-apk`. Unzip it to get the APK.

## Important
- This workflow is a best-effort starter and may need updates if dependencies or Android build tools change. A failed run will show logs under Actions.
- This builds a **debug APK for testing**, not a signed Play Store release.
- This starter's current app has placeholder AI answers; a secure backend is required for real AI.
- Android image selection/OCR and Hindi-capable PDF output need further integration/testing.
- Never upload API keys, passwords, or private personal documents to the repository.
- Keep the repository Private while developing.
