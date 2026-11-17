# Instructor Brief

Half-page summary for presenting web361lab to the course instructor. Written in English like all project documents. A Turkish version can be derived from it for the presentation.

## The problem

In the web course, assignments are uploaded to Teams as files. Students read the lesson in one place and write code in another. For beginners, the editor's autocomplete (IntelliSense) lets code get written without the syntax being learned. Copy-paste and AI-generated answers also make it hard to assess the learning process. The instructor has to open and read every submission one by one.

## The idea

One screen holding the assignment, the lesson content and the code editor, configurable by the instructor per assignment:

- The instructor writes the assignment in **natural language** (questions, items) and puts the lesson content in a side panel. Per assignment, the instructor turns **IntelliSense**, **pasting** and **live error display** on or off.
- The student sees a **live preview** while coding.
- If the instructor wants, the **checker** is turned on and required elements are selected, for example "the page must use a form, an `input type=email` and at least two `label` elements". On submission, it shows which ones were used.
- **Writing checks** report syntax and style problems (unclosed tags, inconsistent indentation, a hint to use `<em>` instead of `<i>`, and so on) to the instructor as a report.
- **Rubric:** made of automatic and manually scored criteria. The system calculates a **suggested score**, the instructor edits it and gives the final grade. Grades can be exported as CSV.
- The system records the typing process. The instructor can watch **how the code came to be** (replay). Signals such as blocked paste attempts are shown as "worth a look" markers.
- Later: an optional, instructor-only comment suggestion (readability, semantic tag choice), drag-and-drop logic assignments, and a small PHP interpreter.

## What the system does not do

It does not give the final grade, accuse anyone, or claim that code "works correctly". It only says "used / not used" and gives hints. The first version uses no AI.

## Why we start small

The first version (MVP) covers HTML/CSS/JS assignments, the checker, writing checks, the rubric, replay and submission. With a working demo we prove the idea, and if approved, integrate with the school's Teams environment and school accounts. There is no separate sign-up or password: everyone enrolled in the course logs in with their school account.

## What we need from the instructor

1. Feedback on the idea and scope.
2. One or two example assignments and how they are graded today.
3. After approval: a contact in the school's IT department.

## Transparency

The typing history is recorded, and students are clearly told so on first login.
