# MVP demo scenario

All identities in this scenario are fictional. The application uses demo login: choosing an identity does not verify who the person is, so this setup is for local demonstrations only.

1. Start PostgreSQL, apply the migrations, run `backend/seed.py`, and start the backend and frontend as described in the root README.
2. Sign in as the example instructor and open **Web Programlama**. Under **Öğrenci listesi yükle**, select `docs/examples/mock-students.csv` and upload it. The 150 fictional students become available at demo login. Uploading the same file again does not duplicate them.
3. Create an HTML assignment. Enable the checker, add a non-empty `h1` rule, and add an automatic criterion linked to it. Add a manual criterion and decide whether students may see criteria and check results. Save the assignment.
4. Sign out and choose one of the fictional students. Accept the recording notice, open the assignment, edit the HTML, and submit it.
5. Sign back in as the instructor, open the submission, inspect the code, observations, and replay. Adjust the automatic criterion if needed, enter the manual criterion, final score, and feedback, then save. Download the CSV.
6. Sign in as the same student again and check the final score and feedback. Criteria and check results appear only when their respective assignment settings permit it.
7. In the instructor assignment list, choose **Kopyala** to create a separate editable copy with the same settings and criteria.

The CSV upload expects UTF-8 columns `student_number,name,email`; student numbers are nine digits. It accepts at most 1,000 students and 256 KiB per file. An existing number must match the existing student's email; conflicting records are rejected without importing a partial list.

## Final checks

- External paste and drag-and-drop are blocked when paste is disabled; editor-internal copy/paste remains usable.
- The preview uses `sandbox="allow-scripts"`, and its content security policy blocks external resource requests.
- Replay play, pause, and seeking reconstruct the saved editor changes.
- With the checker off, no result is produced or shown; with student visibility off, the student cannot see check results.
- The instructor can grade a submission and download a CSV containing the final score.

The short usability trial described in `test-strategy.md` requires an actual instructor and should be recorded separately when available.
