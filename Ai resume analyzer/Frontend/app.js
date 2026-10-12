const API_BASE = "http://127.0.0.1:8000";
let isLogin = true;

function toggleMode() {
    isLogin = !isLogin;
    document.getElementById("form-title").innerText = isLogin ? "Login" : "Signup";
    document.getElementById("submit-btn").innerText = isLogin ? "Login" : "Signup";
    document.getElementById("name").style.display = isLogin ? "none" : "block";
    document.getElementById("toggle-text").innerText = isLogin
        ? "Don't have an account? Signup"
        : "Already have an account? Login";
}

async function handleAuth() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const name = document.getElementById("name").value;
    const errorMsg = document.getElementById("error-msg");
    errorMsg.innerText = "";

    const endpoint = isLogin ? "/api/auth/login" : "/api/auth/signup";
    const body = isLogin ? { email, password } : { name, email, password };

    try {
        const res = await fetch(API_BASE + endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });
        const data = await res.json();

        if (!res.ok) throw new Error(data.detail || "Something went wrong");

        localStorage.setItem("token", data.access_token);
        localStorage.setItem("user_name", data.user.name);
        window.location.href = "dashboard.html";
    } catch (err) {
        errorMsg.innerText = err.message;
    }
}

function logout() {
    localStorage.removeItem("token");
    window.location.href = "index.html";
}

function getToken() {
    const token = localStorage.getItem("token");
    if (!token) window.location.href = "index.html";
    return token;
}

async function uploadResume() {
    const fileInput = document.getElementById("resume-file");
    const jobDesc = document.getElementById("job-desc").value;
    const msgEl = document.getElementById("upload-msg");

    if (!fileInput.files[0]) {
        msgEl.innerText = "Please select a file";
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {
        msgEl.innerText = "Uploading...";
        const uploadRes = await fetch(API_BASE + "/api/resume/upload", {
            method: "POST",
            headers: { Authorization: "Bearer " + getToken() },
            body: formData,
        });
        const uploadData = await uploadRes.json();
        if (!uploadRes.ok) throw new Error(uploadData.detail || "Upload failed");

        msgEl.innerText = "Analyzing...";
        const analysisRes = await fetch(API_BASE + `/api/analysis/${uploadData.id}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: "Bearer " + getToken(),
            },
            body: JSON.stringify({ job_description: jobDesc || null }),
        });
        const analysisData = await analysisRes.json();
        if (!analysisRes.ok) throw new Error(analysisData.detail || "Analysis failed");

        msgEl.innerText = "Done! Match Score: " + analysisData.match_score + "%";
        loadResumes();
    } catch (err) {
        msgEl.innerText = "Error: " + err.message;
    }
}

async function loadResumes() {
    const search = document.getElementById("search-box")?.value || "";
    const status = document.getElementById("status-filter")?.value || "";

    const params = new URLSearchParams();
    if (search) params.append("search", search);
    if (status) params.append("status", status);

    try {
        const res = await fetch(`${API_BASE}/api/resume/?${params}`, {
            headers: { Authorization: "Bearer " + getToken() },
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Failed to load");

        const listEl = document.getElementById("resume-list");
        listEl.innerHTML = "";

        data.resumes.forEach((r) => {
            const card = document.createElement("div");
            card.className = "resume-card";
            card.innerHTML = `
  <div>
    <strong>${r.file_name}</strong><br>
    <small>${new Date(r.uploaded_at).toLocaleString()}</small>
    ${r.match_score !== null ? `<br><small>Score: ${r.match_score}%</small>` : ""}
  </div>
 `;
            card.style.cursor = "pointer";
            card.onclick = () => openDetails(r.id, r.file_name);
            listEl.appendChild(card);
        });
    } catch (err) {
        console.error(err);
    }
}


let currentResumeId = null;

async function openDetails(resumeId, fileName) {
    currentResumeId = resumeId;
    try {
        const res = await fetch(`${API_BASE}/api/analysis/${resumeId}`, {
            headers: { Authorization: "Bearer " + getToken() },
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Failed to load analysis");

        document.getElementById("modal-title").innerText = fileName;
        document.getElementById("modal-score").innerText = data.match_score;
        document.getElementById("modal-skills").innerText = (data.skills_found || []).join(", ") || "N/A";
        document.getElementById("modal-missing").innerText = (data.missing_skills || []).join(", ") || "None";
        document.getElementById("modal-suggestions").innerText = data.suggestions || "N/A";

        const strengthsEl = document.getElementById("modal-strengths");
        strengthsEl.innerHTML = (data.strengths || []).map(s => `<li>${s}</li>`).join("");

        const weaknessesEl = document.getElementById("modal-weaknesses");
        weaknessesEl.innerHTML = (data.weaknesses || []).map(w => `<li>${w}</li>`).join("");

        document.getElementById("modal-overlay").style.display = "flex";
    } catch (err) {
        alert(err.message);
    }
}

function closeModal(event) {
    if (event && event.target.id !== "modal-overlay") return;
    document.getElementById("modal-overlay").style.display = "none";
}



function updateFileName() {
    const fileInput = document.getElementById("resume-file");
    const display = document.getElementById("file-name-display");
    display.innerText = fileInput.files[0] ? fileInput.files[0].name : "No file chosen";
  }