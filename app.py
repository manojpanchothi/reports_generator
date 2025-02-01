import os
import json

BASE_DIR = "reports_generator"

# Function to generate personalized feedback, ensuring no NoneType errors
def generate_feedback(section_name, remark, responses):
    if remark is None or remark.strip() == "":  
        return f"No specific feedback available for {section_name}."  # Handle missing values

    normalized_remark = remark.strip().lower().replace(" ", "")

    for key in responses:
        if key.lower().replace(" ", "") == normalized_remark:
            return responses[key].replace("{section_name}", section_name)

    print(f"⚠️ No feedback found for: '{remark}' in section: '{section_name}'")
    return f"No specific feedback available for {section_name}."

# Iterate through each question folder
for question_folder in os.listdir(BASE_DIR):
    folder_path = os.path.join(BASE_DIR, question_folder)
    output_folder = os.path.join(folder_path, "output")

    if os.path.isdir(folder_path):
        inputs_file = os.path.join(folder_path, "inputs.json")
        template_file = os.path.join(folder_path, "template.json")
        responses_file = os.path.join(folder_path, "response.json")
        links_file = os.path.join(folder_path, "links.json")

        os.makedirs(output_folder, exist_ok=True)

        if not os.path.exists(inputs_file) or os.stat(inputs_file).st_size == 0:
            print(f"⚠️ Skipping {question_folder}: inputs.json is missing or empty!")
            continue

        with open(inputs_file, "r", encoding="utf-8") as f:
            students_data = json.load(f)

        with open(template_file, "r", encoding="utf-8") as f:
            question_template = json.load(f)

        with open(responses_file, "r", encoding="utf-8") as f:
            responses = json.load(f)

        # Load screenshot links for the folder (default values if missing)
        desktop_link, mobile_link = "#", "#"
        if os.path.exists(links_file) and os.stat(links_file).st_size > 0:
            try:
                with open(links_file, "r", encoding="utf-8") as f:
                    links_data = json.load(f)
                desktop_link = links_data.get("desktop", "#")
                mobile_link = links_data.get("mobile", "#")
            except json.JSONDecodeError:
                print(f"❌ Error: links.json in {question_folder} is not formatted correctly. Skipping link inclusion.")

        # Generate reports for each student
        for student in students_data:
            student_id = student.get("NIAT ID", "").strip()
            name = student.get("name", "Unknown Student").strip()

            # If NIAT ID is missing or invalid, skip generating report for this student
            if not student_id or student_id == "#N/A":
                print(f"⚠️ Skipping student {name} due to missing or invalid NIAT ID.")
                continue

            # File path with valid NIAT ID
            report_filename = os.path.join(output_folder, f"{student_id}_report.html")

            sections = question_template.get("sections", {})
            desktop_sections = sections.get("desktop", [])
            mobile_sections = sections.get("mobile", [])

            remarks = {"desktop": {}, "mobile": {}}
            student_normalized = {k.strip().lower().replace(" ", ""): v for k, v in student.items()}

            for section in desktop_sections:
                normalized_section = section.strip().lower().replace(" ", "")
                remark_key = student_normalized.get(normalized_section, "No remarks provided")
                remarks["desktop"][section] = generate_feedback(section, remark_key, responses)

            for section in mobile_sections:
                normalized_section = section.strip().lower().replace(" ", "")
                remark_key = student_normalized.get(normalized_section, "No remarks provided")
                remarks["mobile"][section] = generate_feedback(section, remark_key, responses)

            # Generate HTML report
            report_filename = os.path.join(output_folder, f"{student_id}_report.html")
            with open(report_filename, "w", encoding="utf-8") as file:
                file.write(f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Web Development Report - {student_id}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; padding: 20px; background-color: #f4f4f4; }}
                        .container {{ max-width: 900px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0px 0px 15px #aaa; }}
                        h1, h2 {{ color: #333; text-align: center; }}
                        table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
                        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
                        th {{ background-color: #3498db; color: white; }}
                        .screenshot-link {{ display: block; text-align: center; font-size: 18px; color: #007BFF; text-decoration: none; margin: 10px 0; }}
                        .screenshot-link:hover {{ text-decoration: underline; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Web Development Report</h1>
                        <p><strong>Name:</strong> {name}</p>
                        <p><strong>Student ID:</strong> {student_id}</p>

                        <h2>View Screenshots</h2>
                        <a class="screenshot-link" href="{desktop_link}" target="_blank">Desktop View</a>
                        <a class="screenshot-link" href="{mobile_link}" target="_blank">Mobile View</a>

                        <h2>Desktop Section Remarks</h2>
                        <table>
                            <tr><th>Section</th><th>Remarks</th></tr>
                """)

                for section, feedback in remarks["desktop"].items():
                    file.write(f"<tr><td>{section}</td><td>{feedback}</td></tr>")

                file.write("</table><h2>Mobile Section Remarks</h2><table><tr><th>Section</th><th>Remarks</th></tr>")

                for section, feedback in remarks["mobile"].items():
                    file.write(f"<tr><td>{section}</td><td>{feedback}</td></tr>")

                file.write("</table></div></body></html>")

            print(f"✅ Report generated: {report_filename}")
