# Use Cases

**UC-01 Instructor creates an assignment.** The instructor chooses "New assignment" and enters a title, the assignment text (questions and items, free Markdown), side panel content, starter code and a due date. They choose the settings: IntelliSense, paste, live error display. If they want, they turn on "Checker" and select the required elements. If they want, they choose the writing check rules. They build the rubric: automatic criteria coming from the checker rules, plus their own manual criteria. They save, and the assignment becomes visible to students.

**UC-02 Student works on an assignment.** The student opens the assignment. The editor shows the HTML, CSS and JavaScript tabs enabled by the instructor; the live preview and lesson panel appear alongside it. On first login they confirm the notice. As they type, the draft and events are saved.

**UC-03 Blocked paste.** If pasting is off for the assignment and the student tries to paste from outside, the action is cancelled, a short notice appears and a counter increases. Pasting text copied inside the editor works.

**UC-04 Student submits.** The student chooses "Submit" and sees a confirmation box. The submission is locked and goes to the instructor's list. The checker and linter run at this moment and their results are stored with the submission.

**UC-05 Instructor reviews a submission.** The instructor opens the submission list and selects a student. They see the final code and preview, the check result and the writing report, read the signals and play the replay.

**UC-06 Unauthorized access.** Someone not enrolled in the course who tries to enter sees the message "You are not enrolled in this course" (Turkish UI: "Bu derse kayıtlı değilsin").

**UC-07 Instructor grades.** The instructor opens the rubric panel on a submission. They see the automatic criteria results and change them if needed. They score the manual criteria. They see the system's suggested total, write the final score and short feedback, and save. All grades can be exported as CSV.

**UC-08 Student sees criteria and result.** If the instructor allows it, the student sees the grading criteria and (depending on the setting) the check result on the assignment page. After submission they read the instructor's feedback.
