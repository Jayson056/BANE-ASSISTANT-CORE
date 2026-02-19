
import os

school_dir = "/home/user/BANE_CORE_Workspaces/USER-DATA/9eb397f15a125a6d/School"
subjects = [d for d in os.listdir(school_dir) if os.path.isdir(os.path.join(school_dir, d))]

print("Checking for Instructional Materials...")
found_subjects = []

for subject in sorted(subjects):
    subject_path = os.path.join(school_dir, subject)
    # Check common names
    materials_path = None
    for name in ["Instructional Materials", "Materials", "Notes", "Handouts"]:
        potential = os.path.join(subject_path, name)
        if os.path.isdir(potential):
            materials_path = potential
            break
    
    if materials_path:
        # Count files
        files = [f for f in os.listdir(materials_path) if os.path.isfile(os.path.join(materials_path, f))]
        file_count = len(files)
        found_subjects.append(f"✅ {subject} ({file_count} files)")
    else:
        # Check if there are loose PDF/PPT files in the root of the subject folder
        files = [f for f in os.listdir(subject_path) if f.lower().endswith(('.pdf', '.ppt', '.pptx', '.doc', '.docx'))]
        if files:
             found_subjects.append(f"⚠️ {subject} (No specific folder, but has {len(files)} loose files)")

if not found_subjects:
    print("No instructional materials found.")
else:
    print("\n".join(found_subjects))
