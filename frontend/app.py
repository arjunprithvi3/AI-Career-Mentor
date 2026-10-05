import requests
import streamlit as st

BACKEND_URL = "http://localhost:8000"
st.set_page_config(page_title="AI Career Mentor", page_icon="🧭", layout="wide")
st.title("🧭 AI Career Mentor")
st.write("Upload your resume and get a personalized career roadmap.")
# ===================================
# Resume Upload
# ===================================
st.header("📄 Upload Resume")
uploaded_file = st.file_uploader("Choose a PDF Resume", type=["pdf"])
if uploaded_file:  # noqa: SIM102
    if st.button("Upload Resume"):
        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                "application/pdf",
            )
        }
        try:
            response = requests.post(f"{BACKEND_URL}/upload", files=files)
            if response.status_code == 200:
                st.success("Resume uploaded successfully!")
                st.session_state["resume_uploaded"] = True
            else:
                st.error(response.text)
        except Exception as e:  # noqa: BLE001
            st.error(str(e))
# ===================================
# Ranked Career Assessment
# ===================================
st.header("📊 Compare Career Roles")
available_roles = [
    "AI Engineer",
    "Full-Stack Developer",
    "GenAI Engineer",
    "Java Developer",
    "Machine Learning Engineer",
]
selected_roles = st.multiselect(
    "Select job roles to compare",
    options=available_roles,
    default=available_roles,
)

if st.button("Rank Selected Roles"):
    if not selected_roles:
        st.warning("Select at least one job role.")
    else:
        try:
            with st.spinner("Assessing and ranking roles..."):
                response = requests.post(
                    f"{BACKEND_URL}/career-assessment",
                    params=[("roles", role) for role in selected_roles],
                    timeout=180,
                )
            if response.status_code != 200:
                st.error(response.text)
            else:
                st.session_state["career_assessment"] = response.json()
        except requests.RequestException as e:
            st.error(str(e))

if "career_assessment" in st.session_state:
    assessment = st.session_state["career_assessment"]
    st.subheader(f"Recommended role: {assessment['recommended_role']}")

    for ranked_role in assessment.get("ranked_roles", []):
        role_analysis = ranked_role.get("analysis", {})
        with st.expander(
            f"#{ranked_role['rank']} {ranked_role['role']} "
            f"({ranked_role['fit_percentage']:.1f}% fit)",
            expanded=ranked_role["rank"] == 1,
        ):
            st.write(role_analysis.get("suitability_summary", ""))
            st.write("**Matching skills**", role_analysis.get("matching_skills", []))
            st.write("**Missing skills**", role_analysis.get("missing_skills", []))
            st.write(
                "**Transferable skills**",
                role_analysis.get("transferable_skills", []),
            )
            st.write("**Evidence**", role_analysis.get("evidence", []))

    interview_coach = assessment.get("interview_coach", {})
    st.subheader(f"Interview preparation: {interview_coach.get('target_role', '')}")
    st.write("**Focus areas**", interview_coach.get("focus_areas", []))
    for question in interview_coach.get("questions", []):
        with st.expander(question.get("question", "Interview question")):
            st.write(f"Category: {question.get('category', '')}")
            st.write(f"Difficulty: {question.get('difficulty', '')}")
            st.write(f"Evaluates: {question.get('evaluates', '')}")
            st.write(f"Preparation: {question.get('preparation_hint', '')}")

    with st.expander("Full Career Assessment JSON", expanded=True):
        st.json(assessment, expanded=True)
# ===================================
# Career Goal
# ===================================
st.header("🎯 Career Goal")
career_query = st.text_input(
    "What career do you want?", placeholder="I want to become an AI Engineer"
)
if st.button("Generate Career Plan", type="primary"):
    if not career_query.strip():
        st.warning("Enter a career goal.")
    else:
        try:
            with st.spinner("Generating career plan..."):
                response = requests.post(
                    f"{BACKEND_URL}/career-agent", json={"message": career_query}
                )
            if response.status_code != 200:
                st.error(response.text)
            else:
                data = response.json()
                st.session_state["career_plan"] = data
        except Exception as e:  # noqa: BLE001
            st.error(str(e))
# ===================================
# Display Career Plan
# ===================================
if "career_plan" in st.session_state:
    result = st.session_state["career_plan"]
    st.divider()
    summary = result.get("career_summary") or {}
    st.header("📊 Career Assessment")
    if summary:
        st.write(summary.get("suitability_summary", ""))
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("✅ Matching Skills")
            for skill in summary.get("matching_skills", []):
                st.success(skill)
        with col2:
            st.subheader("❌ Missing Skills")
            for skill in summary.get("missing_skills", []):
                st.error(skill)
    else:
        st.info("No career assessment details were included in the backend response.")
    # ==========================
    # Projects
    # ==========================
    st.divider()
    st.header("🚀 Recommended Projects")
    for project in result.get("project_recommendations", []):
        project_name = project.get("project_name", "Project")
        with st.expander(project_name):
            st.write(project.get("problem_statement", ""))
    # ==========================
    # Resources
    # ==========================
    st.divider()
    st.header("📚 Learning Resources")
    for resource in result.get("resource_recommendations", []):
        title = resource.get("title", "")
        if title:
            st.write(f"📘 {title}")
    # ==========================
    # Next Steps
    # ==========================
    st.divider()
    st.header("🛣 Next Steps")
    for step in result.get("next_steps", []):
        st.write(f"{step['order']}. {step['title']}")
    # ==========================
    # Final Guidance
    # ==========================
    st.divider()
    st.header("🧠 Final Guidance")
    st.info(result.get("final_guidance", ""))
    # ==========================
    # Raw JSON
    # ==========================
    with st.expander("Raw Backend Response", expanded=True):
        st.json(result, expanded=True)
